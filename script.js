// Cargar navbar y vista inicial
document.addEventListener("DOMContentLoaded", function () {
    // Cargar el navbar
    fetch("componentes/navbar.html")
        .then(res => res.text())
        .then(html => {
            document.getElementById("navbar-container").innerHTML = html;

            // Cargar la pantalla de bienvenida
            cargarVista("ventanas/Bienvenida.html");

            // Luego de 3 segundos, cambiar a Inventario
            setTimeout(() => cargarVista("ventanas/Inventario.html"), 3000);
        })
        .catch(err => console.error("Error al cargar navbar:", err));
});

// Función para cargar cualquier vista en el contenedor principal
function cargarVista(url) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            document.getElementById("contenido-principal").innerHTML = html;

            // Re-ejecutar lógica para la vista de inventario
            if (url.includes("Inventario")) {
                inicializarInventario();
            }
        })
        .catch(err => console.error("Error al cargar vista:", err));
}


// Escuchar delegadamente el clic del botón flotante, ya que puede no existir aún al cargar
document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'btnAgregarProducto') {
        const { ipcRenderer } = require('electron');
        ipcRenderer.send('abrir-ventana-agregar-producto');
    }
});

function inicializarInventario() {
    const boton = document.getElementById('btnAgregarProducto');
    if (boton) {
        boton.addEventListener('click', () => {
            ipcRenderer.send('abrir-ventana-agregar-producto');
        });
    }

    async function cargarProductos() {
        try {
            const response = await fetch('http://localhost:5000/productos');
            const productos = await response.json();

            const tabla = document.getElementById('inventoryBody');
            tabla.innerHTML = "";

            productos.forEach(prod => {
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${prod.id_producto}</td>
                    <td>${prod.nombre_producto}</td>
                    <td>${prod.genero}</td>
                    <td>${prod.marca}</td>
                    <td>${prod.modelo}</td>
                    <td>${prod.talla}</td>
                    <td>${prod.stock_actual}</td>
                    <td>$${parseFloat(prod.precio_unitario).toFixed(2)}</td>
                `;
                tabla.appendChild(fila);
            });
        } catch (error) {
            console.error("Error al cargar productos:", error);
            alert("No se pudieron cargar los productos.");
        }
    }

    cargarProductos();
}
