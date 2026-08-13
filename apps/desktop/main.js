const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const http = require('http');
const MacosTracker = require('./src/tracking/macos_tracker');
const OfflineQueueManager = require('./src/queue/offline_queue');

let mainWindow = null;
let tray = null;
const tracker = new MacosTracker();
const queueMgr = new OfflineQueueManager();

// Desktop State
const state = {
  isTracking: true,
  isPaused: false,
  pauseUntil: null,
  activeApp: 'Finder',
  focusScore: 85,
  isOnline: true,
  queuedEventsCount: 0,
  token: 'mock_valid_token_desktop_mac'
};

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 380,
    height: 520,
    resizable: false,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'src/ui/index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function broadcastState() {
  state.queuedEventsCount = queueMgr.getQueue().length;
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('state-update', {
      ...state,
      pauseRemainingMins: state.pauseUntil ? Math.max(0, Math.ceil((state.pauseUntil - Date.now()) / 60000)) : 0
    });
  }
}

// Check FastAPI Backend Health
function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:8000/health', { timeout: 1500 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

// Send Single Event to FastAPI Backend
function postEventToApi(eventData) {
  return new Promise((resolve) => {
    const dataStr = JSON.stringify({
      application_name: eventData.application_name,
      session_duration: eventData.duration || 60,
      app_switch_count: eventData.app_switch_count || 1,
      idle_seconds: eventData.idle_seconds || 0,
      device_type: 'desktop_mac'
    });

    const req = http.request({
      hostname: '127.0.0.1',
      port: 8000,
      path: '/api/events',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`,
        'Content-Length': Buffer.byteLength(dataStr)
      },
      timeout: 2000
    }, (res) => {
      resolve(res.statusCode === 201 || res.statusCode === 200);
    });

    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
    req.write(dataStr);
    req.end();
  });
}

// Background Native Application Telemetry Poller (Runs every 10 seconds)
setInterval(async () => {
  if (!state.isTracking) return;

  if (state.isPaused) {
    if (Date.now() >= state.pauseUntil) {
      state.isPaused = false;
      state.pauseUntil = null;
    } else {
      broadcastState();
      return;
    }
  }

  // 1. Query Active Application Metadata ONLY
  const activeApp = tracker.getActiveApplication();
  const idleSecs = tracker.getIdleTimeSeconds();
  state.activeApp = activeApp;

  const eventPayload = {
    application_name: activeApp,
    duration: 10,
    app_switch_count: 1,
    idle_seconds: idleSecs,
    timestamp: new Date().toISOString()
  };

  // 2. Check Connection & Post or Queue
  const isOnline = await checkBackendHealth();
  state.isOnline = isOnline;

  if (isOnline) {
    const success = await postEventToApi(eventPayload);
    if (!success) {
      queueMgr.enqueueEvent(eventPayload);
    }
    // Sync offline queue if present
    await queueMgr.syncQueue(postEventToApi, checkBackendHealth);
  } else {
    queueMgr.enqueueEvent(eventPayload);
  }

  broadcastState();
}, 10000);

// IPC Handlers
ipcMain.handle('get-desktop-state', () => {
  state.queuedEventsCount = queueMgr.getQueue().length;
  return {
    ...state,
    pauseRemainingMins: state.pauseUntil ? Math.max(0, Math.ceil((state.pauseUntil - Date.now()) / 60000)) : 0
  };
});

ipcMain.handle('toggle-tracking', (evt, enabled) => {
  state.isTracking = enabled;
  if (!enabled) {
    state.isPaused = false;
    state.pauseUntil = null;
  }
  broadcastState();
  return true;
});

ipcMain.handle('pause-tracking', (evt, minutes) => {
  state.isPaused = true;
  state.pauseUntil = Date.now() + (minutes * 60000);
  broadcastState();
  return true;
});

ipcMain.handle('purge-local-data', () => {
  queueMgr.clearQueue();
  broadcastState();
  return true;
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
