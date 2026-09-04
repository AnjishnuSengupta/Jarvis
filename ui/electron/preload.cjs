const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // We can add IPC methods here later if needed.
  // For now, the renderer communicates with Flask over HTTP/WebSockets.
});
