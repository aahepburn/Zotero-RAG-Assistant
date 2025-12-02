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
const IS_DEV = process.env.NODE_ENV === 'development' || !app.isPackaged;
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
    // Production: run Python backend from extraResources
    const resourcesPath = process.resourcesPath;
    const backendPath = path.join(resourcesPath, 'backend');
    
    // Check for python3 or python command
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    return {
      command: pythonCmd,
      args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
      cwd: path.dirname(backendPath)
    };
  }
}

/**
 * Check if the backend is ready by polling the health endpoint
 */
async function waitForBackend(maxRetries = 30, delayMs = 1000): Promise<boolean> {
  console.log('Waiting for backend to be ready...');
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios.get(`${BACKEND_URL}/`, { timeout: 500 });
      if (response.status === 200) {
        console.log('Backend is ready!');
        return true;
      }
    } catch (error) {
      // Backend not ready yet, wait and retry
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
  
  console.error('Backend failed to start within timeout period');
  return false;
}

/**
 * Spawn the Python backend process
 */
async function startBackend(): Promise<boolean> {
  const { command, args, cwd } = getBackendPath();
  
  console.log(`Starting backend: ${command} ${args.join(' ')}`);
  console.log(`Working directory: ${cwd}`);
  
  try {
    backendProcess = spawn(command, args, {
      cwd,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        // Pass auth token to backend if needed in future
        // AUTH_TOKEN: authToken
      }
    });
    
    // Log backend output
    backendProcess.stdout?.on('data', (data) => {
      console.log(`[Backend] ${data.toString().trim()}`);
    });
    
    backendProcess.stderr?.on('data', (data) => {
      console.error(`[Backend Error] ${data.toString().trim()}`);
    });
    
    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      dialog.showErrorBox(
        'Backend Error',
        `Failed to start backend process: ${error.message}`
      );
    });
    
    backendProcess.on('exit', (code, signal) => {
      console.log(`Backend process exited with code ${code} and signal ${signal}`);
      backendProcess = null;
      
      // If backend crashes unexpectedly, notify user
      if (code !== 0 && code !== null && mainWindow && !mainWindow.isDestroyed()) {
        dialog.showErrorBox(
          'Backend Crashed',
          `The backend process exited unexpectedly (code: ${code}). The app may not function correctly.`
        );
      }
    });
    
    // Wait for backend to be ready
    const isReady = await waitForBackend();
    return isReady;
    
  } catch (error) {
    console.error('Error starting backend:', error);
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
    mainWindow.webContents.openDevTools();
  } else {
    // Production: load from built files
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
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
  console.log('App is ready, starting initialization...');
  
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
