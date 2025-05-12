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
            if (url.includes("Ventas")) {
                inicializarVentas();
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

document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'btnNuevaVenta') {
        const { ipcRenderer } = require('electron');
        ipcRenderer.send('abrir-ventana-nueva-venta');
    }
});

function inicializarVentas() {
    const boton = document.getElementById('btnNuevaVenta');
    if (boton) {
        boton.addEventListener('click', () => {
            ipcRenderer.send('abrir-ventana-nueva-venta');
        });
    }

    async function cargarVentas() {
        try {
            const response = await fetch('http://localhost:5000/ventas'); 
            const ventas = await response.json();

            const tabla = document.getElementById('ventasBody');
            tabla.innerHTML = "";

            ventas.forEach(venta => {
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${venta.id_venta}</td>
                    <td>${new Date(venta.fecha_venta).toLocaleDateString()}</td>
                    <td>$${parseFloat(venta.total_con_impuesto).toFixed(2)}</td>
                    <td><button onclick="mostrarDetalle(${venta.id_venta}, this)">Ver Detalle</button></td>
                `;
                tabla.appendChild(fila);
            });
        } catch (error) {
            console.error("Error al cargar ventas:", error);
            alert("No se pudieron cargar las ventas.");
        }
    }

    cargarVentas();
}

// Función para mostrar el detalle al hacer clic en el botón
async function mostrarDetalle(id_venta, btn) {
    try {
        const res = await fetch(`http://localhost:5000/ventas/${id_venta}/detalle`);
        const detalles = await res.json();

        let detalleHTML = `
            <tr class="detalle">
                <td colspan="4">
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Marca</th>
                                <th>Modelo</th>
                                <th>Color</th>
                                <th>Talla</th>
                                <th>Género</th>
                                <th>Cantidad</th>
                                <th>Precio Unitario</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        detalles.forEach(d => {
            detalleHTML += `
                <tr>
                    <td>${d.nombre_producto}</td>
                    <td>${d.marca}</td>
                    <td>${d.modelo}</td>
                    <td>${d.color}</td>
                    <td>${d.talla}</td>
                    <td>${d.genero}</td>
                    <td>${d.cantidad}</td>
                    <td>$${parseFloat(d.precio_unitario).toFixed(2)}</td>
                    <td>$${parseFloat(d.subtotal).toFixed(2)}</td>
                </tr>
            `;
        });

        detalleHTML += `
                        </tbody>
                    </table>
                </td>
            </tr>
        `;

        btn.closest('tr').insertAdjacentHTML('afterend', detalleHTML);
        btn.disabled = true;
    } catch (error) {
        console.error("Error al cargar detalle de venta:", error);
        alert("No se pudo cargar el detalle de la venta.");
    }
}

