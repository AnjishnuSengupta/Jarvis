const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let flaskProcess;

const isDev = !app.isPackaged;

function startFlaskBackend() {
  const pythonExecutable = isDev ? 'python3' : path.join(process.resourcesPath, 'backend', 'server');
  const serverScript = path.join(__dirname, '..', '..', 'server.py');
  
  // Use the virtual environment Python if in dev
  const pythonPath = isDev ? path.join(__dirname, '..', '..', 'venv', 'bin', 'python3') : pythonExecutable;
  
  if (isDev) {
    flaskProcess = spawn(pythonPath, [serverScript], {
      cwd: path.join(__dirname, '..', '..'),
      stdio: 'inherit'
    });
  } else {
    // In production, run the bundled executable
    flaskProcess = spawn(pythonExecutable, [], {
      stdio: 'inherit'
    });
  }

  flaskProcess.on('error', (err) => {
    console.error('Failed to start Flask backend:', err);
  });
}

function checkFlaskHealth(callback) {
  const req = http.get('http://127.0.0.1:5000/api/health', (res) => {
    if (res.statusCode === 200) {
      callback(true);
    } else {
      callback(false);
    }
  });

  req.on('error', () => {
    callback(false);
  });
}

function pollBackendUntilReady(callback) {
  checkFlaskHealth((isReady) => {
    if (isReady) {
      callback();
    } else {
      setTimeout(() => pollBackendUntilReady(callback), 500);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (isDev) {
    // Load Vite dev server
    mainWindow.loadURL('http://localhost:5173');
  } else {
    // Load built static files
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startFlaskBackend();
  
  pollBackendUntilReady(() => {
    console.log("Flask backend is ready. Creating window...");
    createWindow();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
});
