/**
 * Electron Main Process
 * 
 * Responsibilities:
 * - Create and manage the browser window
 * - Spawn and manage the Python backend process
 * - Handle IPC communication between renderer and backend
 * - Manage application lifecycle (startup, shutdown, updates)
 */

import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { autoUpdater } from 'electron-updater';
import axios from 'axios';

// Configuration
// Detect development vs production mode
// app.isPackaged is the most reliable way - it's false during development, true when packaged
const IS_DEV = !app.isPackaged;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const FRONTEND_DEV_URL = 'http://localhost:5173';

// Global references
let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;
let authToken: string | null = null;

/**
 * Generate a random authentication token for backend communication
 */
function generateAuthToken(): string {
  return require('crypto').randomBytes(32).toString('hex');
}

/**
 * Check if Python 3 is available and has required packages
 */
async function checkPythonAvailability(pythonCmd: string, requirementsPath?: string): Promise<{ available: boolean; version?: string; error?: string }> {
  return new Promise((resolve) => {
    const proc = spawn(pythonCmd, ['--version']);
    let output = '';

    proc.stdout?.on('data', (data) => {
      output += data.toString();
    });

    proc.stderr?.on('data', (data) => {
      output += data.toString();
    });

    proc.on('close', (code) => {
      if (code === 0 && output.includes('Python 3.')) {
        const versionMatch = output.match(/Python (\d+\.\d+\.\d+)/);
        resolve({ available: true, version: versionMatch?.[1] });
      } else {
        resolve({ available: false, error: 'Python 3 not found' });
      }
    });

    proc.on('error', () => {
      resolve({ available: false, error: `Command '${pythonCmd}' not found` });
    });

    setTimeout(() => {
      proc.kill();
      resolve({ available: false, error: 'Python check timed out' });
    }, 5000);
  });
}

/**
 * Get the path to the Python backend
 * In dev: use the source directory
 * In production: use the packaged binary in extraResources
 */
function getBackendPath(): { command: string; args: string[]; cwd: string } {
  if (IS_DEV) {
    // Development: run uvicorn directly from source
    const projectRoot = path.join(__dirname, '..');
    return {
      command: 'python3',
      args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
      cwd: projectRoot
    };
  } else {
    // Production: use bundled Python environment
    const resourcesPath = process.resourcesPath;
    const backendPath = path.join(resourcesPath, 'backend');
    const pythonPath = path.join(resourcesPath, 'python');
    
    // Get bundled Python executable
    const pythonExe = process.platform === 'win32'
      ? path.join(pythonPath, 'Scripts', 'python.exe')
      : path.join(pythonPath, 'bin', 'python');
    
    return {
      command: pythonExe,
      args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
      cwd: resourcesPath
    };
  }
}

/**
 * Check if the backend is ready by polling the health endpoint
 */
async function waitForBackend(maxRetries = 30, delayMs = 1000): Promise<boolean> {
  console.log(`Waiting for backend to be ready (checking ${BACKEND_URL}/health)...`);
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios.get(`${BACKEND_URL}/health`, { timeout: 1000 });
      
      if (response.status === 200) {
        const healthData = response.data;
        console.log('Backend health check response:', JSON.stringify(healthData, null, 2));
        
        if (healthData.status === 'healthy') {
          console.log('✓ Backend is ready and healthy!');
          return true;
        } else if (healthData.status === 'degraded') {
          console.warn('⚠ Backend is running but degraded:', healthData.components);
          // Still return true for degraded - app can function with warnings
          return true;
        } else {
          console.error('✗ Backend unhealthy:', healthData);
          // Continue retrying for unhealthy status
        }
      }
    } catch (error) {
      // Backend not ready yet - only log every 5 attempts to reduce noise
      if ((i + 1) % 5 === 0) {
        console.log(`  Attempt ${i + 1}/${maxRetries}: Backend not responding yet...`);
      }
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
  
  console.error(`✗ Backend failed to start within ${maxRetries * delayMs / 1000}s timeout`);
  console.error('Troubleshooting tips:');
  console.error('  1. Check if Python executable exists at the expected path');
  console.error('  2. Review backend process logs above for errors');
  console.error('  3. Verify backend dependencies are properly bundled');
  console.error(`  4. Try accessing ${BACKEND_URL}/health in a browser`);
  return false;
}

/**
 * Spawn the Python backend process
 */
async function startBackend(): Promise<boolean> {
  const { command, args, cwd } = getBackendPath();
  
  console.log('================================================================================');
  console.log('Starting backend...');
  console.log(`  Command: ${command}`);
  console.log(`  Args: ${args.join(' ')}`);
  console.log(`  Working directory: ${cwd}`);
  console.log('================================================================================');
  
  // Validate backend structure (in production)
  if (!IS_DEV) {
    console.log('================================================================================');
    console.log('Backend Structure Validation:');
    console.log(`  - Resources path: ${process.resourcesPath}`);
    console.log(`  - Python command: ${command}`);
    console.log(`  - Python exists: ${fs.existsSync(command)}`);
    console.log(`  - Backend directory: ${cwd}`);
    console.log(`  - Backend exists: ${fs.existsSync(cwd)}`);
    
    // List Resources directory
    try {
      const resourceContents = fs.readdirSync(process.resourcesPath);
      console.log(`  - Resources contents: ${resourceContents.filter(f => !f.endsWith('.lproj')).join(', ')}`);
      
      if (fs.existsSync(path.join(process.resourcesPath, 'python'))) {
        const pythonBinPath = path.join(process.resourcesPath, 'python', 'bin');
        if (fs.existsSync(pythonBinPath)) {
          const pythonBinContents = fs.readdirSync(pythonBinPath);
          console.log(`  - python/bin/ contents: ${pythonBinContents.slice(0, 10).join(', ')}${pythonBinContents.length > 10 ? '...' : ''}`);
        }
      }
      
      const backendDir = path.join(process.resourcesPath, 'backend');
      if (fs.existsSync(backendDir)) {
        const backendContents = fs.readdirSync(backendDir);
        console.log(`  - backend/ contents: ${backendContents.join(', ')}`);
      }
    } catch (e) {
      console.error(`  - Error listing directories: ${e}`);
    }
    
    // Validate Python executable
    if (!fs.existsSync(command)) {
      console.error('✗ FATAL: Python executable not found');
      console.error('================================================================================');
      
      dialog.showErrorBox(
        'Backend Missing - Python Not Found',
        `The Python interpreter is missing from the application bundle.\n\nExpected: ${command}\n\nSee console logs for directory structure details.`
      );
      return false;
    }
    
    // Validate backend directory
    if (!fs.existsSync(cwd)) {
      console.error('✗ FATAL: Backend directory not found');
      console.error('================================================================================');
      
      dialog.showErrorBox(
        'Backend Missing - Source Not Found',
        `The backend source directory is missing.\n\nExpected: ${cwd}\n\nSee console logs for directory structure details.`
      );
      return false;
    }
    
    // Validate main.py exists
    const mainPyPath = path.join(cwd, 'backend', 'main.py');
    if (!fs.existsSync(mainPyPath)) {
      console.error(`✗ FATAL: Backend main.py not found at: ${mainPyPath}`);
      console.error('================================================================================');
      
      dialog.showErrorBox(
        'Backend Missing - main.py Not Found',
        `The backend entry point is missing.\n\nExpected: ${mainPyPath}\n\nSee console logs for directory structure details.`
      );
      return false;
    }
    
    console.log('✓ Backend structure validation passed');
    console.log('================================================================================');
  }
  
  try {
    // Store backend output for diagnostics
    let backendOutput: string[] = [];
    let backendErrors: string[] = [];
    
    // Enhanced environment for backend process
    const backendEnv = {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      PYTHONIOENCODING: 'utf-8',
      // Ensure Python can find the bundled libraries in production
      ...((!IS_DEV && process.platform === 'darwin') ? {
        DYLD_LIBRARY_PATH: path.join(process.resourcesPath, 'python', 'lib')
      } : {}),
      // Pass auth token to backend if needed in future
      // AUTH_TOKEN: authToken
    };
    
    console.log('Backend environment:');
    console.log(`  - PYTHONUNBUFFERED: ${backendEnv.PYTHONUNBUFFERED}`);
    console.log(`  - PYTHONIOENCODING: ${backendEnv.PYTHONIOENCODING}`);
    if (backendEnv.DYLD_LIBRARY_PATH) {
      console.log(`  - DYLD_LIBRARY_PATH: ${backendEnv.DYLD_LIBRARY_PATH}`);
    }
    console.log('Spawning process...');
    
    backendProcess = spawn(command, args, {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'], // Explicitly pipe stdout and stderr
      env: backendEnv
    });
    
    console.log(`✓ Process spawned with PID: ${backendProcess.pid}`);
    
    // Log backend output with timestamps
    backendProcess.stdout?.on('data', (data) => {
      const output = data.toString().trim();
      backendOutput.push(output);
      const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
      console.log(`[Backend ${timestamp}] ${output}`);
    });
    
    backendProcess.stderr?.on('data', (data) => {
      const output = data.toString().trim();
      backendErrors.push(output);
      const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
      
      // Some stderr output is just warnings, not fatal errors
      if (output.includes('WARNING') || output.includes('DeprecationWarning')) {
        console.warn(`[Backend Warning ${timestamp}] ${output}`);
      } else {
        console.error(`[Backend Error ${timestamp}] ${output}`);
      }
    });
    
    backendProcess.on('error', (error) => {
      console.error('================================================================================');
      console.error('✗ FATAL: Failed to spawn backend process');
      console.error(`  Error: ${error.message}`);
      console.error(`  Code: ${(error as any).code}`);
      console.error(`  Command: ${command} ${args.join(' ')}`);
      console.error(`  Working directory: ${cwd}`);
      console.error('================================================================================');
      
      dialog.showErrorBox(
        'Backend Process Failed',
        `Failed to start backend process: ${error.message}\n\nCommand: ${command}\nSee console logs for details.`
      );
    });
    
    backendProcess.on('exit', (code, signal) => {
      const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
      console.log(`[Backend ${timestamp}] Process exited with code ${code}, signal ${signal}`);
      
      // Log final output if process crashed
      if (code !== 0 && code !== null) {
        console.error('Backend crash diagnostics:');
        console.error(`  Last 20 stdout lines:\n    ${backendOutput.slice(-20).join('\n    ')}`);
        console.error(`  Last 20 stderr lines:\n    ${backendErrors.slice(-20).join('\n    ')}`);
      }
      
      backendProcess = null;
      
      // If backend crashes unexpectedly after startup, notify user
      if (code !== 0 && code !== null && mainWindow && !mainWindow.isDestroyed()) {
        dialog.showErrorBox(
          'Backend Crashed',
          `The backend process exited unexpectedly (code: ${code}).\n\nCheck the console logs for details. Recent errors:\n\n${backendErrors.slice(-5).join('\n')}`
        );
      }
    });
    
    console.log('Waiting for immediate startup errors...');
    
    // Wait a moment for immediate errors
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Check if process died immediately
    if (!backendProcess || backendProcess.killed || backendProcess.exitCode !== null) {
      console.error('================================================================================');
      console.error('✗ FATAL: Backend process died immediately');
      console.error(`  Exit code: ${backendProcess?.exitCode}`);
      console.error(`  Signal: ${backendProcess?.signalCode}`);
      console.error(`  Killed: ${backendProcess?.killed}`);
      console.error(`  Output (${backendOutput.length} lines):\n    ${backendOutput.join('\n    ')}`);
      console.error(`  Errors (${backendErrors.length} lines):\n    ${backendErrors.join('\n    ')}`);
      console.error('================================================================================');
      return false;
    }
    
    console.log('✓ Process survived initial startup, checking health endpoint...');
    
    // Wait for backend to be ready with retry logic
    // Try quick checks first (500ms delay), then slower checks (2s delay)
    let isReady = await waitForBackend(10, 500);
    if (!isReady) {
      console.log('Quick startup failed, trying longer intervals...');
      isReady = await waitForBackend(10, 2000);
      
      // If still not ready, dump comprehensive diagnostics
      if (!isReady) {
        console.error('================================================================================');
        console.error('✗ FATAL: Backend failed to become ready');
        console.error('Final diagnostics:');
        console.error(`  Process alive: ${backendProcess && !backendProcess.killed && backendProcess.exitCode === null}`);
        console.error(`  PID: ${backendProcess?.pid}`);
        console.error(`  Exit code: ${backendProcess?.exitCode}`);
        console.error(`  All stdout (${backendOutput.length} lines):\n    ${backendOutput.join('\n    ')}`);
        console.error(`  All stderr (${backendErrors.length} lines):\n    ${backendErrors.join('\n    ')}`);
        console.error('================================================================================');
      }
    }
    
    return isReady;
    
  } catch (error) {
    console.error('================================================================================');
    console.error('✗ EXCEPTION in startBackend:');
    console.error(error);
    console.error('================================================================================');
    return false;
  }
}

/**
 * Stop the backend process gracefully
 */
function stopBackend(): void {
  if (backendProcess) {
    console.log('Stopping backend process...');
    
    // Try graceful shutdown first
    backendProcess.kill('SIGTERM');
    
    // Force kill after timeout
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        console.log('Force killing backend process...');
        backendProcess.kill('SIGKILL');
      }
    }, 5000);
    
    backendProcess = null;
  }
}

/**
 * Create the main application window
 */
function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    title: 'Zotero LLM Assistant',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    },
    // Optional: custom icon
    // icon: path.join(__dirname, '../assets/icon.png')
  });
  
  // Load the frontend
  if (IS_DEV) {
    // Development: load from Vite dev server
    mainWindow.loadURL(FRONTEND_DEV_URL);
    // Only open DevTools in development (and only if not explicitly disabled)
    if (process.env.DISABLE_DEVTOOLS !== 'true') {
      mainWindow.webContents.openDevTools();
    }
  } else {
    // Production: load from built files
    const appPath = app.getAppPath();
    const indexPath = path.join(appPath, 'frontend', 'dist', 'index.html');
    
    console.log('================================================================================');
    console.log('Frontend Path Resolution:');
    console.log(`  - App path (getAppPath): ${appPath}`);
    console.log(`  - Resolved index.html: ${indexPath}`);
    console.log(`  - Index exists: ${fs.existsSync(indexPath)}`);
    
    // Check alternate paths to help diagnose any mismatch
    const altPaths = [
      path.join(appPath, 'dist', 'frontend', 'dist', 'index.html'),
      path.join(appPath, 'index.html'),
      path.join(appPath, 'dist', 'index.html')
    ];
    console.log('  - Alternate path checks:');
    altPaths.forEach(p => {
      console.log(`      ${p}: ${fs.existsSync(p)}`);
    });
    
    // List app directory contents for diagnostics
    try {
      const appContents = fs.readdirSync(appPath);
      console.log(`  - App directory contents: ${appContents.join(', ')}`);
      
      if (fs.existsSync(path.join(appPath, 'frontend'))) {
        const frontendContents = fs.readdirSync(path.join(appPath, 'frontend'));
        console.log(`  - frontend/ contents: ${frontendContents.join(', ')}`);
        
        if (fs.existsSync(path.join(appPath, 'frontend', 'dist'))) {
          const distContents = fs.readdirSync(path.join(appPath, 'frontend', 'dist'));
          console.log(`  - frontend/dist/ contents: ${distContents.join(', ')}`);
        }
      }
    } catch (e) {
      console.error(`  - Error listing directories: ${e}`);
    }
    console.log('================================================================================');
    
    // Validate frontend files exist
    if (!fs.existsSync(indexPath)) {
      console.error(`✗ FATAL: Frontend index.html not found at: ${indexPath}`);
      
      dialog.showErrorBox(
        'Frontend Files Missing',
        `The frontend application files are missing.\n\nExpected location: ${indexPath}\n\nSee console logs for directory structure details.`
      );
      app.quit();
      return;
    }
    
    console.log('✓ Frontend validation passed, loading window...');
    mainWindow.loadFile(indexPath);
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Handle navigation to external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });
}

/**
 * Setup IPC handlers for communication with renderer process
 */
function setupIpcHandlers(): void {
  // Send backend configuration to renderer
  ipcMain.handle('get-backend-config', () => {
    return {
      backendUrl: BACKEND_URL,
      authToken: authToken
    };
  });
  
  // Check if backend is healthy
  ipcMain.handle('check-backend-health', async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/`, { timeout: 2000 });
      return { healthy: true, status: response.status };
    } catch (error) {
      return { healthy: false, error: error instanceof Error ? error.message : String(error) };
    }
  });
  
  // Get app version
  ipcMain.handle('get-app-version', () => {
    return app.getVersion();
  });
  
  // Open external links
  ipcMain.handle('open-external', (event, url: string) => {
    require('electron').shell.openExternal(url);
  });
}

/**
 * Setup auto-updater for automatic updates from GitHub Releases
 */
function setupAutoUpdater(): void {
  // Configure auto-updater
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;
  
  // Check for updates on startup (after a delay)
  setTimeout(() => {
    if (!IS_DEV) {
      console.log('Checking for updates...');
      autoUpdater.checkForUpdates();
    }
  }, 10000); // Wait 10 seconds after startup
  
  // Check for updates periodically (every 4 hours)
  setInterval(() => {
    if (!IS_DEV) {
      autoUpdater.checkForUpdates();
    }
  }, 4 * 60 * 60 * 1000);
  
  // Update event handlers
  autoUpdater.on('checking-for-update', () => {
    console.log('Checking for updates...');
  });
  
  autoUpdater.on('update-available', (info) => {
    console.log('Update available:', info.version);
    
    // Notify renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-available', {
        version: info.version,
        releaseNotes: info.releaseNotes
      });
    }
  });
  
  autoUpdater.on('update-not-available', () => {
    console.log('No updates available');
  });
  
  autoUpdater.on('error', (error) => {
    console.error('Auto-updater error:', error);
  });
  
  autoUpdater.on('download-progress', (progress) => {
    console.log(`Download progress: ${progress.percent.toFixed(2)}%`);
    
    // Notify renderer of download progress
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-download-progress', {
        percent: progress.percent,
        transferred: progress.transferred,
        total: progress.total
      });
    }
  });
  
  autoUpdater.on('update-downloaded', (info) => {
    console.log('Update downloaded:', info.version);
    
    // Notify renderer that update is ready
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-downloaded', {
        version: info.version
      });
    }
  });
  
  // IPC handlers for update actions
  ipcMain.handle('download-update', async () => {
    try {
      await autoUpdater.downloadUpdate();
      return { success: true };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : String(error) };
    }
  });
  
  ipcMain.handle('install-update', () => {
    autoUpdater.quitAndInstall(false, true);
  });
}

/**
 * Application ready event
 */
app.on('ready', async () => {
  console.log('================================================================================');
  console.log('App is ready, starting initialization...');
  console.log('================================================================================');
  console.log('Environment Information:');
  console.log(`  - IS_DEV: ${IS_DEV}`);
  console.log(`  - app.isPackaged: ${app.isPackaged}`);
  console.log(`  - Platform: ${process.platform}`);
  console.log(`  - Architecture: ${process.arch}`);
  console.log(`  - Electron version: ${process.versions.electron}`);
  console.log(`  - Node version: ${process.versions.node}`);
  console.log(`  - App version: ${app.getVersion()}`);
  console.log(`  - App path: ${app.getAppPath()}`);
  console.log(`  - Resources path: ${process.resourcesPath}`);
  console.log(`  - User data path: ${app.getPath('userData')}`);
  console.log('================================================================================');
  
  // Generate auth token
  authToken = generateAuthToken();
  
  // Setup IPC handlers
  setupIpcHandlers();
  
  // Setup auto-updater
  setupAutoUpdater();
  
  // Start backend
  const backendStarted = await startBackend();
  
  if (!backendStarted) {
    const response = await dialog.showMessageBox({
      type: 'error',
      title: 'Backend Failed to Start',
      message: 'The backend service failed to start. The application may not work correctly.',
      buttons: ['Exit', 'Continue Anyway'],
      defaultId: 0
    });
    
    if (response.response === 0) {
      app.quit();
      return;
    }
  }
  
  // Create window
  createWindow();
});

/**
 * All windows closed event
 */
app.on('window-all-closed', () => {
  // On macOS, keep app running until explicitly quit
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * Activate event (macOS)
 */
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

/**
 * Before quit event - cleanup
 */
app.on('before-quit', () => {
  console.log('App is quitting, cleaning up...');
  stopBackend();
});

/**
 * Handle uncaught exceptions
 */
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  dialog.showErrorBox('Application Error', `An unexpected error occurred: ${error.message}`);
});
