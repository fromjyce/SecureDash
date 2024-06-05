const { ipcRenderer } = require("electron");

window.onload = () => {
  const playButton = document.getElementById("play-button");
  const stopButton = document.getElementById("stop-button");
  const checkPowerBiButton = document.getElementById("check-power-bi");

  stopButton.classList.add("disabled");
  checkPowerBiButton.disabled = true;

  window.startPython = () => {
    ipcRenderer.send("start-python");
    playButton.classList.add("disabled");
    stopButton.classList.remove("disabled");
    checkPowerBiButton.disabled = false;
  };

  window.stopPython = () => {
    ipcRenderer.send("stop-python");
    stopButton.classList.add("disabled");
    playButton.classList.remove("disabled");
    checkPowerBiButton.disabled = true;
  };
};
