const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getDesktopState: () => ipcRenderer.invoke('get-desktop-state'),
  toggleTracking: (enabled) => ipcRenderer.invoke('toggle-tracking', enabled),
  pauseTracking: (minutes) => ipcRenderer.invoke('pause-tracking', minutes),
  login: (credentials) => ipcRenderer.invoke('login', credentials),
  purgeLocalData: () => ipcRenderer.invoke('purge-local-data'),
  onStateUpdate: (callback) => ipcRenderer.on('state-update', (event, state) => callback(state))
});
