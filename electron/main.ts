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
let updateDownloaded = false;
let updateInfo: { version: string; releaseNotes?: string } | null = null;

/**
 * Generate a random authentication token for backend communication
 */
function generateAuthToken(): string {
  return require('crypto').randomBytes(32).toString('hex');
}

/**
 * Check if Python 3 is available
 */
async function checkPythonAvailability(pythonCmd: string): Promise<{ available: boolean; version?: string; error?: string }> {
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
 * Find the bundled Python interpreter (production only)
 * Returns the full path to the bundled Python 3 interpreter
 * Supports both traditional venv bundles and PyInstaller executables
 */
async function findBundledPython(): Promise<{ path: string; version?: string; source: string; isPyInstaller?: boolean } | null> {
  const resourcesPath = process.resourcesPath;
  
  // First check for PyInstaller bundle (preferred method)
  const pyInstallerPaths = [
    // macOS/Linux - PyInstaller backend executable
    path.join(resourcesPath, 'python', 'backend_server'),
    path.join(resourcesPath, 'python', 'backend_server.exe'), // Windows
  ];
  
  console.log('Looking for PyInstaller bundled backend...');
  for (const execPath of pyInstallerPaths) {
    console.log(`  Checking: ${execPath}`);
    if (fs.existsSync(execPath)) {
      // Check if it's a real file (not a symlink to system Python)
      const stats = fs.lstatSync(execPath);
      if (stats.isSymbolicLink()) {
        console.warn(`  ✗ Found but it's a symlink (invalid bundle)`);
        continue;
      }
      
      console.log(`  ✓ Found PyInstaller bundle at ${execPath}`);
      return {
        path: execPath,
        version: 'PyInstaller bundle',
        source: 'bundled-pyinstaller',
        isPyInstaller: true
      };
    } else {
      console.log(`  ✗ Not found`);
    }
  }
  
  // Fallback: Check for traditional venv-style Python bundle
  const bundledPythonPaths = [
    // Linux/macOS - Standard locations for bundled Python
    path.join(resourcesPath, 'python', 'bin', 'python3'),
    path.join(resourcesPath, 'python', 'bin', 'python'),
    // Windows
    path.join(resourcesPath, 'python', 'Scripts', 'python.exe'),
    path.join(resourcesPath, 'python', 'python.exe'),
  ];
  
  console.log('Looking for traditional venv-style bundled Python interpreter...');
  for (const pythonPath of bundledPythonPaths) {
    console.log(`  Checking: ${pythonPath}`);
    if (fs.existsSync(pythonPath)) {
      // Check if it's a symlink (which would be invalid for distribution)
      const stats = fs.lstatSync(pythonPath);
      if (stats.isSymbolicLink()) {
        const linkTarget = fs.readlinkSync(pythonPath);
        // If it's an absolute symlink outside our bundle, it's invalid
        if (path.isAbsolute(linkTarget) && !linkTarget.startsWith(resourcesPath)) {
          console.warn(`  ✗ Found but it's an invalid symlink to: ${linkTarget}`);
          continue;
        }
      }
      
      console.log(`  ✓ Found bundled Python at ${pythonPath}`);
      // Verify it's a working Python 3 interpreter
      const result = await checkPythonAvailability(pythonPath);
      if (result.available) {
        console.log(`  ✓ Verified Python ${result.version}`);
        return {
          path: pythonPath,
          version: result.version,
          source: 'bundled-venv',
          isPyInstaller: false
        };
      } else {
        console.warn(`  ✗ Found file but not a working Python: ${result.error}`);
      }
    } else {
      console.log(`  ✗ Not found`);
    }
  }
  
  return null;
}

/**
 * Find the best Python interpreter to use (development only)
 * Returns the full path to a working Python 3 interpreter
 */
async function findSystemPython(): Promise<{ path: string; version?: string; source: string } | null> {
  const candidates: { path: string; source: string }[] = [];
  
  // Add system Python candidates
  // On Linux/macOS, prefer python3 over python
  if (process.platform !== 'win32') {
    candidates.push(
      { path: 'python3', source: 'system' },
      { path: 'python', source: 'system' },
      { path: '/usr/bin/python3', source: 'system' },
      { path: '/usr/local/bin/python3', source: 'system' }
    );
  } else {
    candidates.push(
      { path: 'python', source: 'system' },
      { path: 'python3', source: 'system' }
    );
  }
  
  // Test each candidate
  console.log('Looking for system Python interpreter...');
  for (const candidate of candidates) {
    console.log(`  Testing: ${candidate.path}`);
    const result = await checkPythonAvailability(candidate.path);
    
    if (result.available) {
      console.log(`  ✓ Found working Python ${result.version} at ${candidate.path}`);
      return {
        path: candidate.path,
        version: result.version,
        source: candidate.source
      };
    } else {
      console.log(`  ✗ ${candidate.path}: ${result.error}`);
    }
  }
  
  return null;
}

/**
 * Setup Linux virtual environment on first run
 * Creates venv in ~/.config/zotero-rag-assistant/venv and installs dependencies
 */
async function setupLinuxVenv(onProgress?: (message: string, progress?: number) => void): Promise<{ pythonPath: string; venvPath: string } | null> {
  const os = require('os');
  const configDir = path.join(os.homedir(), '.config', 'zotero-rag-assistant');
  const venvPath = path.join(configDir, 'venv');
  const pythonBin = path.join(venvPath, 'bin', 'python3');
  
  // Check if venv already exists and is valid
  if (fs.existsSync(pythonBin)) {
    console.log(`Found existing venv at: ${venvPath}`);
    
    // Verify uvicorn is installed (critical dependency check)
    const hasUvicorn = await new Promise<boolean>((resolve) => {
      const proc = spawn(pythonBin, ['-m', 'uvicorn', '--version']);
      proc.on('close', (code) => resolve(code === 0));
      proc.on('error', () => resolve(false));
      setTimeout(() => { proc.kill(); resolve(false); }, 3000);
    });
    
    if (hasUvicorn) {
      console.log(`✓ Linux venv valid with all dependencies at: ${venvPath}`);
      return { pythonPath: pythonBin, venvPath };
    } else {
      console.warn('⚠ Existing venv missing dependencies (uvicorn not found)');
      console.log('Reinstalling dependencies...');
      
      // Try to repair by reinstalling dependencies
      try {
        const requirementsPath = path.join(process.resourcesPath, 'requirements.txt');
        if (fs.existsSync(requirementsPath)) {
          onProgress?.('Updating Python dependencies...', 50);
          const pipBin = path.join(venvPath, 'bin', 'pip');
          await new Promise<void>((resolve, reject) => {
            const proc = spawn(pipBin, ['install', '--no-cache-dir', '-r', requirementsPath]);
            proc.stdout?.on('data', (data) => console.log(data.toString()));
            proc.stderr?.on('data', (data) => console.error(data.toString()));
            proc.on('close', (code) => code === 0 ? resolve() : reject(new Error('Dependency install failed')));
            proc.on('error', reject);
          });
          console.log('✓ Dependencies reinstalled successfully');
          onProgress?.('Dependencies updated!', 100);
          return { pythonPath: pythonBin, venvPath };
        }
      } catch (error) {
        console.error('✗ Failed to repair venv:', error);
        console.log('Will recreate venv from scratch...');
        // Fall through to recreate venv
      }
    }
  }
  
  console.log('================================================================================');
  console.log('Linux: First run setup - creating virtual environment');
  console.log('================================================================================');
  
  // Find system Python
  const systemPython = await findSystemPython();
  if (!systemPython) {
    console.error('✗ System Python 3.8+ not found');
    console.error('Please install: sudo apt install python3 python3-pip python3-venv');
    if (mainWindow) {
      dialog.showErrorBox(
        'Python Required',
        'Python 3.8 or later is required.\n\nPlease install:\nsudo apt install python3 python3-pip python3-venv\n\nThen restart the application.'
      );
    }
    return null;
  }
  
  try {
    // Create config directory
    onProgress?.('Creating configuration directory...', 10);
    fs.mkdirSync(configDir, { recursive: true });
    console.log(`✓ Created config directory: ${configDir}`);
    
    // Create virtual environment
    onProgress?.('Creating Python virtual environment...', 20);
    console.log(`Creating venv with ${systemPython.path}...`);
    await new Promise<void>((resolve, reject) => {
      const proc = spawn(systemPython.path, ['-m', 'venv', venvPath]);
      let stderr = '';
      
      proc.stderr?.on('data', (data) => { stderr += data.toString(); });
      
      proc.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`venv creation failed: ${stderr}`));
      });
      
      proc.on('error', reject);
    });
    console.log('✓ Virtual environment created');
    
    // Upgrade pip
    onProgress?.('Upgrading pip...', 40);
    console.log('Upgrading pip...');
    await new Promise<void>((resolve, reject) => {
      const pipBin = path.join(venvPath, 'bin', 'pip');
      const proc = spawn(pipBin, ['install', '--upgrade', 'pip']);
      
      proc.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error('pip upgrade failed'));
      });
      
      proc.on('error', reject);
    });
    console.log('✓ pip upgraded');
    
    // Install dependencies
    onProgress?.('Installing Python dependencies (this may take 2-5 minutes)...', 50);
    console.log('Installing dependencies from requirements.txt...');
    const requirementsPath = path.join(process.resourcesPath, 'requirements.txt');
    
    if (!fs.existsSync(requirementsPath)) {
      throw new Error(`requirements.txt not found at: ${requirementsPath}`);
    }
    
    await new Promise<void>((resolve, reject) => {
      const pipBin = path.join(venvPath, 'bin', 'pip');
      const proc = spawn(pipBin, ['install', '--no-cache-dir', '-r', requirementsPath]);
      let lastOutput = '';
      
      proc.stdout?.on('data', (data) => {
        lastOutput = data.toString();
        console.log(lastOutput);
        
        // Parse progress from pip output
        const match = lastOutput.match(/Downloading.*\((\d+)\/(\d+)\)/);
        if (match) {
          const current = parseInt(match[1]);
          const total = parseInt(match[2]);
          const progress = 50 + Math.floor((current / total) * 40);
          onProgress?.(`Installing dependencies (${current}/${total})...`, progress);
        }
      });
      
      proc.stderr?.on('data', (data) => { console.error(data.toString()); });
      
      proc.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error('Dependency installation failed'));
      });
      
      proc.on('error', reject);
    });
    
    onProgress?.('Setup complete!', 100);
    console.log('✓ Dependencies installed successfully');
    console.log('================================================================================');
    
    return { pythonPath: pythonBin, venvPath };
  } catch (error) {
    console.error('✗ Linux venv setup failed:', error);
    if (mainWindow) {
      dialog.showErrorBox(
        'Setup Failed',
        `Failed to set up Python environment:\n\n${error}\n\nPlease check the console for details.`
      );
    }
    return null;
  }
}

/**
 * Get the path to the Python backend
 * In dev: use the source directory with system Python
 * In production: use the packaged backend with bundled PyInstaller executable (all platforms)
 */
async function getBackendPath(): Promise<{ command: string; args: string[]; cwd: string; pythonInfo?: { version?: string; source: string } } | null> {
  if (IS_DEV) {
    // Development: run uvicorn directly from source using system Python
    // In dev, __dirname is typically dist/electron/, so go up two levels to project root
    const projectRoot = path.resolve(__dirname, '..', '..');
    
    console.log('Development mode: finding Python interpreter...');
    const pythonInfo = await findSystemPython();
    
    if (!pythonInfo) {
      console.error('✗ No Python 3 interpreter found on system');
      console.error('Please install Python 3.8+ for development');
      return null;
    }
    
    console.log(`Using system Python: ${pythonInfo.path} (${pythonInfo.version || 'unknown version'})`);
    
    return {
      command: pythonInfo.path,
      args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
      cwd: projectRoot,
      pythonInfo
    };
  } else {
    // Production
    const resourcesPath = process.resourcesPath;
    
    // Linux: Use venv approach (smaller packages, uses system Python)
    if (process.platform === 'linux') {
      console.log('Production mode (Linux): Setting up virtual environment...');
      const venvSetup = await setupLinuxVenv();
      
      if (!venvSetup) {
        console.error('================================================================================');
        console.error('✗ FATAL: Failed to set up Linux virtual environment');
        console.error('================================================================================');
        console.error('  Please ensure Python 3.8+ is installed:');
        console.error('    sudo apt install python3 python3-pip python3-venv');
        console.error('================================================================================');
        return null;
      }
      
      console.log(`Using Linux venv: ${venvSetup.pythonPath}`);
      return {
        command: venvSetup.pythonPath,
        args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
        cwd: resourcesPath,
        pythonInfo: { version: 'venv', source: 'linux-venv' }
      };
    }
    
    // Windows/macOS: Use bundled PyInstaller executable
    console.log('Production mode: looking for bundled Python interpreter...');
    const pythonInfo = await findBundledPython();
    
    if (!pythonInfo) {
      console.error('================================================================================');
      console.error('✗ FATAL: Bundled Python interpreter not found');
      console.error('================================================================================');
      console.error(`  Resources path: ${resourcesPath}`);
      console.error(`  Expected Python locations (PyInstaller):`);
      console.error(`    - ${path.join(resourcesPath, 'python', 'backend_server')}`);
      console.error(`  Expected Python locations (venv fallback):`);
      console.error(`    - ${path.join(resourcesPath, 'python', 'bin', 'python3')}`);
      console.error(`    - ${path.join(resourcesPath, 'python', 'bin', 'python')}`);
      if (process.platform === 'win32') {
        console.error(`    - ${path.join(resourcesPath, 'python', 'Scripts', 'python.exe')}`);
        console.error(`    - ${path.join(resourcesPath, 'python', 'python.exe')}`);
      }
      console.error('');
      console.error('  This is a packaging error. The application should be self-contained.');
      console.error('  Please contact support or reinstall the application.');
      console.error('================================================================================');
      return null;
    }
    
    console.log(`Using bundled Python: ${pythonInfo.path} (${pythonInfo.version || 'unknown version'})`);
    
    // PyInstaller bundles are standalone executables that don't need uvicorn arguments
    if (pythonInfo.isPyInstaller) {
      console.log('Using PyInstaller bundle - running standalone backend executable');
      return {
        command: pythonInfo.path,
        args: ['--port', BACKEND_PORT.toString()],
        cwd: resourcesPath,
        pythonInfo
      };
    } else {
      // Traditional venv-style bundle
      console.log('Using venv-style bundle - running uvicorn with Python interpreter');
      return {
        command: pythonInfo.path,
        args: ['-m', 'uvicorn', 'backend.main:app', '--port', BACKEND_PORT.toString()],
        cwd: resourcesPath,
        pythonInfo
      };
    }
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
  const backendConfig = await getBackendPath();
  
  if (!backendConfig) {
    console.error('================================================================================');
    console.error('✗ FATAL: Could not find Python interpreter');
    console.error('================================================================================');
    
    if (IS_DEV) {
      // Development mode: guide user to install Python
      const platform = process.platform;
      let instructions = 'Please install Python 3.8 or later.';
      
      if (platform === 'linux') {
        instructions = 'Please install Python 3:\n\n' +
          'Ubuntu/Debian: sudo apt install python3\n' +
          'Fedora/RHEL: sudo dnf install python3\n' +
          'Arch: sudo pacman -S python';
      } else if (platform === 'darwin') {
        instructions = 'Please install Python 3:\n\n' +
          'Using Homebrew: brew install python3\n' +
          'Or download from: https://www.python.org/downloads/';
      } else if (platform === 'win32') {
        instructions = 'Please install Python 3 from:\nhttps://www.python.org/downloads/\n\n' +
          'Make sure to check "Add Python to PATH" during installation.';
      }
      
      dialog.showErrorBox(
        'Python Not Found',
        `The application requires Python 3 to run the backend service.\n\n${instructions}`
      );
    } else {
      // Production mode: this is a packaging error
      dialog.showErrorBox(
        'Application Installation Error',
        `The bundled Python interpreter is missing from this installation.\n\n` +
        `This is a packaging error. The application should be self-contained and not require Python to be installed on your system.\n\n` +
        `Please try:\n` +
        `1. Reinstalling the application\n` +
        `2. Downloading a fresh copy from the official source\n` +
        `3. Contacting support if the problem persists\n\n` +
        `Expected Python location:\n${path.join(process.resourcesPath, 'python', 'bin', 'python3')}`
      );
    }
    return false;
  }
  
  const { command, args, cwd, pythonInfo } = backendConfig;
  
  console.log('================================================================================');
  console.log('Starting backend...');
  console.log(`  Python: ${command}`);
  if (pythonInfo) {
    console.log(`  Version: ${pythonInfo.version || 'unknown'}`);
    console.log(`  Source: ${pythonInfo.source}`);
  }
  console.log(`  Args: ${args.join(' ')}`);
  console.log(`  Working directory: ${cwd}`);
  console.log('================================================================================');
  
  // Validate backend structure (in production)
  if (!IS_DEV) {
    console.log('================================================================================');
    console.log('Backend Structure Validation:');
    console.log(`  - Resources path: ${process.resourcesPath}`);
    console.log(`  - Python command: ${command}`);
    console.log(`  - Python source: ${pythonInfo?.source || 'unknown'}`);
    
    // Only check if Python exists if it's a full path (bundled or absolute system path)
    const isPythonFullPath = path.isAbsolute(command) || command.includes(path.sep);
    if (isPythonFullPath) {
      console.log(`  - Python exists: ${fs.existsSync(command)}`);
    } else {
      console.log(`  - Python command (will use PATH): ${command}`);
    }
    
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
    
    // Validate Python executable (only if it's a full path)
    if (isPythonFullPath && !fs.existsSync(command)) {
      console.error('✗ WARNING: Bundled Python executable not found, using system Python');
      console.error(`  Expected bundled Python at: ${command}`);
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
    
    // Spawn in a new process group so we can kill all child processes
    const spawnOptions: any = {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'], // Explicitly pipe stdout and stderr
      env: backendEnv
    };
    
    // On Unix, create a new process group (detached but we keep reference)
    if (process.platform !== 'win32') {
      spawnOptions.detached = false; // Keep attached but in new group
      // By default on Unix, spawn creates new process group when shell: false
    }
    
    backendProcess = spawn(command, args, spawnOptions);
    
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
    
    const pid = backendProcess.pid;
    
    // Kill entire process tree (Python spawns child processes like ChromaDB)
    if (pid) {
      try {
        if (process.platform === 'win32') {
          // Windows: use taskkill to kill process tree
          spawn('taskkill', ['/pid', pid.toString(), '/T', '/F']);
        } else {
          // Unix: kill process group (negative PID kills the group)
          process.kill(-pid, 'SIGTERM');
          
          // Force kill after timeout
          setTimeout(() => {
            try {
              process.kill(-pid, 'SIGKILL');
            } catch (e) {
              // Process already dead
            }
          }, 2000);
        }
        console.log('✓ Backend process tree killed');
      } catch (error) {
        console.error('Error killing backend:', error);
        // Fallback to normal kill
        backendProcess.kill('SIGKILL');
      }
    }
    
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
    title: 'Zotero RAG Assistant',
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
  autoUpdater.autoDownload = false; // Don't auto-download, let user decide
  autoUpdater.autoInstallOnAppQuit = true; // Install on quit after download
  
  // Disable update checks in development
  if (IS_DEV) {
    console.log('Auto-updater disabled in development mode');
    return;
  }
  
  // Check for updates on startup (after a delay to let app fully load)
  setTimeout(() => {
    console.log('Checking for updates on startup...');
    autoUpdater.checkForUpdates().catch(err => {
      console.error('Failed to check for updates on startup:', err);
    });
  }, 10000); // Wait 10 seconds after startup
  
  // Check for updates periodically (every 4 hours)
  setInterval(() => {
    console.log('Periodic update check...');
    autoUpdater.checkForUpdates().catch(err => {
      console.error('Failed to check for updates periodically:', err);
    });
  }, 4 * 60 * 60 * 1000);
  
  // Update event handlers
  autoUpdater.on('checking-for-update', () => {
    console.log('Checking for updates...');
    updateDownloaded = false;
    updateInfo = null;
    
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-checking');
    }
  });
  
  autoUpdater.on('update-available', (info) => {
    console.log('Update available:', info.version);
    updateInfo = {
      version: info.version,
      releaseNotes: typeof info.releaseNotes === 'string' ? info.releaseNotes : undefined
    };
    
    // Notify renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-available', updateInfo);
    }
  });
  
  autoUpdater.on('update-not-available', (info) => {
    console.log('No updates available. Current version:', info.version);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-not-available', {
        version: info.version
      });
    }
  });
  
  autoUpdater.on('error', (error) => {
    console.error('Auto-updater error:', error);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-error', {
        message: error instanceof Error ? error.message : String(error)
      });
    }
  });
  
  autoUpdater.on('download-progress', (progress) => {
    const percent = progress.percent.toFixed(2);
    console.log(`Download progress: ${percent}% (${progress.transferred}/${progress.total} bytes)`);
    
    // Notify renderer of download progress
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-download-progress', {
        percent: progress.percent,
        transferred: progress.transferred,
        total: progress.total,
        bytesPerSecond: progress.bytesPerSecond
      });
    }
  });
  
  autoUpdater.on('update-downloaded', (info) => {
    console.log('Update downloaded and ready to install:', info.version);
    updateDownloaded = true;
    updateInfo = {
      version: info.version,
      releaseNotes: typeof info.releaseNotes === 'string' ? info.releaseNotes : undefined
    };
    
    // Notify renderer that update is ready to install
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('update-downloaded', updateInfo);
    }
  });
  
  // IPC handlers for update actions
  ipcMain.handle('check-for-updates', async () => {
    try {
      if (IS_DEV) {
        return {
          success: false,
          error: 'Updates are not available in development mode'
        };
      }
      
      const result = await autoUpdater.checkForUpdates();
      return {
        success: true,
        updateInfo: result?.updateInfo ? {
          version: result.updateInfo.version,
          releaseDate: result.updateInfo.releaseDate
        } : null
      };
    } catch (error) {
      console.error('Check for updates error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  });
  
  ipcMain.handle('download-update', async () => {
    try {
      if (IS_DEV) {
        return {
          success: false,
          error: 'Updates are not available in development mode'
        };
      }
      
      if (!updateInfo) {
        return {
          success: false,
          error: 'No update available to download'
        };
      }
      
      await autoUpdater.downloadUpdate();
      return { success: true };
    } catch (error) {
      console.error('Download update error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  });
  
  ipcMain.handle('install-update', () => {
    if (IS_DEV) {
      return {
        success: false,
        error: 'Updates are not available in development mode'
      };
    }
    
    if (!updateDownloaded) {
      return {
        success: false,
        error: 'No update has been downloaded yet'
      };
    }
    
    // This will quit the app and install the update
    setImmediate(() => {
      autoUpdater.quitAndInstall(false, true);
    });
    
    return { success: true };
  });
  
  ipcMain.handle('get-update-status', () => {
    return {
      updateAvailable: updateInfo !== null,
      updateDownloaded: updateDownloaded,
      updateInfo: updateInfo,
      currentVersion: app.getVersion()
    };
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
  
  // In development, backend is started separately by npm run dev:backend
  // Only start backend in production mode
  if (!IS_DEV) {
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
  } else {
    console.log('Development mode: Skipping backend startup (handled by npm run dev:backend)');
    console.log('Waiting for backend to be available...');
    
    // Wait for backend to be ready (started by separate process)
    const backendReady = await waitForBackend(30, 1000);
    
    if (!backendReady) {
      console.warn('⚠ Backend not detected - make sure "npm run dev:backend" is running');
      const response = await dialog.showMessageBox({
        type: 'warning',
        title: 'Backend Not Detected',
        message: 'Could not connect to backend at http://localhost:8000.\n\nMake sure you\'re running "npm run dev" which starts the backend automatically.',
        buttons: ['Exit', 'Continue Anyway'],
        defaultId: 1
      });
      
      if (response.response === 0) {
        app.quit();
        return;
      }
    } else {
      console.log('✓ Connected to development backend');
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
