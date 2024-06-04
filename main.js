const { app, BrowserWindow, Menu } = require("electron");
const path = require("path");

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
    icon: path.join(__dirname, "assets/icons/windows/securedash.ico"),
  });
  Menu.setApplicationMenu(null);
  mainWindow.loadFile("index.html");
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
