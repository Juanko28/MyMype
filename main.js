const { app, BrowserWindow } = require('electron');

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 1000,
        autoHideMenuBar:true,
        webPreferences: {
            nodeIntegration: true
        }
    });
    mainWindow.maximize();
    mainWindow.loadFile('index.html');
});
