const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const path = require("path");
const { spawn, exec } = require("child_process");

let pythonProcess;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, "assets/icons/windows/securedash.ico"),
  });
  mainWindow.loadFile("index.html");
  Menu.setApplicationMenu(null);
  var splash = new BrowserWindow({
    width: 500,
    height: 300,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    icon: path.join(__dirname, "assets/icons/windows/securedash.ico"),
  });

  splash.loadFile("splash.html");
  splash.center();
  setTimeout(function () {
    splash.close();
    mainWindow.center();
    mainWindow.show();
  }, 3000);

ipcMain.on("start-python", (event, arg) => {
  const scriptPath = path.join(__dirname, "scripts", "data_to_powerbi_main.py");
  pythonProcess = spawn("python", [scriptPath], {
    env: { ...process.env, PYTHONIOENCODING: "utf-8", TF_ENABLE_ONEDNN_OPTS: "0" }});

  pythonProcess.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`child process exited with code ${code}`);
  });
});

ipcMain.on("stop-python", (event, arg) => {
  if (pythonProcess) {
    process.kill(pythonProcess.pid);
    pythonProcess = null;
  }
});


}
app.whenReady().then(() => {
  createWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});
