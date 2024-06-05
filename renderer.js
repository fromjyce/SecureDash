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

  checkPowerBiButton.addEventListener("click", () => {
    if (!checkPowerBiButton.disabled) {
      const url =
        "https://app.powerbi.com/groups/me/dashboards/3182bc43-4271-4a61-8df8-e86f978c90f1?experience=power-bi";
      window.open(url, "_blank");
    }
  });
};
