const { app, BrowserWindow, ipcMain } = require('electron');

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 1000,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // ¡Importante para que funcione ipcRenderer!
        }
    });

    mainWindow.maximize();
    mainWindow.loadFile('inicio-res.html'); // Tu login o pantalla inicial

    // Espera el mensaje desde la vista para cambiar de página
    ipcMain.on('login-exitoso', () => {
        mainWindow.loadFile('index.html');
    });
});
