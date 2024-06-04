const { ipcRenderer } = require("electron");

function startPython() {
  ipcRenderer.send("start-python");
}

function stopPython() {
  ipcRenderer.send("stop-python");
}
