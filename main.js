const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const path = require('path'); // Para manejar rutas de manera más flexible

let mainWindow;

app.whenReady().then(() => {
    // Función para iniciar el backend de Python
    function startBackend() {
        const backendPath = path.join(__dirname, 'Backend', 'app.py');  // Ruta absoluta a app.py
        exec(`python "${backendPath}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error ejecutando el backend: ${error.message}`);
                return;
            }
            if (stderr) {
                console.error(`stderr: ${stderr}`);
                return;
            }
            console.log(`stdout: ${stdout}`);
        });
    }

    // Iniciar el backend cuando la aplicación esté lista
    startBackend();

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

    // 👉 Mueve este bloque AQUÍ dentro
    ipcMain.on('abrir-ventana-agregar-producto', () => {
        const ventanaAgregar = new BrowserWindow({
            width: 1300,
            height: 1000,
            title: "Agregar Producto",
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
            }
        });

        ventanaAgregar.loadFile('ventanas/NuevoMovimiento.html'); // Ajusta si tu archivo está en otra ruta
    });

    // 👉 Mueve este bloque AQUÍ dentro ventana ventas
    ipcMain.on('abrir-ventana-nueva-venta', () => {
        const ventanaVenta = new BrowserWindow({
            width: 1300,
            height: 1000,
            title: "Nueva Venta",
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
            }
        });

        ventanaVenta.loadFile('ventanas/NuevaVenta.html'); // Ajusta si tu archivo está en otra ruta
    });
});
