const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

let pythonProcess;
let flaskProcess;
let mainWindow;
let flaskWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
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

  const splash = new BrowserWindow({
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
    const scriptPath = path.join(
      __dirname,
      "scripts",
      "main.py"
    );
    pythonProcess = spawn("python", [scriptPath], {
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
        TF_ENABLE_ONEDNN_OPTS: "0",
      },
    });
  });

  ipcMain.on("stop-python", (event, arg) => {
    if (pythonProcess) {
      const { pid } = pythonProcess;
      process.kill(pid);
      pythonProcess = null;
    }
  });

  ipcMain.on("open-database-window", () => {
    if (!flaskProcess) {
      flaskProcess = spawn("python", ["app.py"], {
        cwd: path.join(__dirname, "database-app"),
        env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      });

      flaskProcess.on("close", (code) => {
        console.log(`Flask process exited with code ${code}`);
        flaskProcess = null;
        if (flaskWindow) {
          flaskWindow.close();
          flaskWindow = null;
        }
      });

      const checkServer = (retryCount = 5) => {
        http
          .get("http://127.0.0.1:5000", (res) => {
            if (res.statusCode === 200) {
              if (!flaskWindow) {
                flaskWindow = new BrowserWindow({
                  width: 800,
                  height: 600,
                  webPreferences: {
                    nodeIntegration: true,
                    contextIsolation: false,
                  },
                });
              }
              flaskWindow.loadURL("http://127.0.0.1:5000");
              flaskWindow.show();

              flaskWindow.on("closed", () => {
                flaskWindow = null;
                if (flaskProcess) {
                  const { pid } = flaskProcess;
                  process.kill(pid);
                  flaskProcess = null;
                }
              });
            } else if (retryCount > 0) {
              setTimeout(() => checkServer(retryCount - 1), 500);
            }
          })
          .on("error", () => {
            if (retryCount > 0) {
              setTimeout(() => checkServer(retryCount - 1), 500);
            }
          });
      };

      checkServer();
    } else {
      if (!flaskWindow) {
        flaskWindow = new BrowserWindow({
          width: 800,
          height: 600,
          webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
          },
        });

        flaskWindow.loadURL("http://127.0.0.1:5000");
        flaskWindow.show();

        flaskWindow.on("closed", () => {
          flaskWindow = null;
          if (flaskProcess) {
            const { pid } = flaskProcess;
            process.kill(pid);
            flaskProcess = null;
          }
        });
      }
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
