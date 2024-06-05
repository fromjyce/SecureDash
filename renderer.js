const { ipcRenderer } = require("electron");

window.onload = () => {
  
  const playButton = document.getElementById("play-button");
  const stopButton = document.getElementById("stop-button");

  stopButton.classList.add("disabled");

  window.startPython = () => {
    ipcRenderer.send("start-python");
    playButton.classList.add("disabled");
    stopButton.classList.remove("disabled");
  };

  window.stopPython = () => {
    ipcRenderer.send("stop-python");
    stopButton.classList.add("disabled");
    playButton.classList.remove("disabled");
  };
};
