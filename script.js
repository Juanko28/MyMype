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


// Función para mostrar el mensaje de bienvenida
function mostrarBienvenida() {
    const bienvenidaContainer = document.getElementById("bienvenida-container");
    if (bienvenidaContainer) {
        bienvenidaContainer.style.display = 'flex';
    }
}

// Función para cargar cualquier vista en el contenedor principal
function cargarVista(url) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            document.getElementById("contenido-principal").innerHTML = html;

            // Re-ejecutar cualquier JS que venga de esa vista
            if (url.includes("Inventario")) {
                inicializarInventario();
            }
            // Agregar más condiciones si tienes otras vistas, por ejemplo:
            // if (url.includes("Reportes")) { inicializarReportes(); }
        })
        .catch(err => console.error("Error al cargar vista:", err));
}

// ========== LÓGICA DEL INVENTARIO ==========

function inicializarInventario() {
    window.agregarProducto = function () {
        let producto = document.getElementById("producto").value;
        let cantidad = document.getElementById("cantidad").value;
        let precio = document.getElementById("precio").value;

        if (producto && cantidad && precio) {
            let table = document.getElementById("inventoryBody");
            let row = table.insertRow();
            let id = table.rows.length;

            row.innerHTML = `
                <td>${id}</td>
                <td>${producto}</td>
                <td>${cantidad}</td>
                <td>$${precio}</td>
                <td>
                    <button class="btn edit" onclick="editarFila(this)">Editar</button>
                    <button class="btn delete" onclick="eliminarFila(this)">Eliminar</button>
                </td>
            `;
        } else {
            alert("Completa todos los campos.");
        }
    };

    window.eliminarFila = function (button) {
        let row = button.parentElement.parentElement;
        row.remove();
    };

    window.editarFila = function (button) {
        let row = button.parentElement.parentElement;
        let cells = row.getElementsByTagName("td");

        let nuevoProducto = prompt("Nuevo nombre:", cells[1].innerText);
        let nuevaCantidad = prompt("Nueva cantidad:", cells[2].innerText);
        let nuevoPrecio = prompt("Nuevo precio:", cells[3].innerText.replace("$", ""));

        if (nuevoProducto && nuevaCantidad && nuevoPrecio) {
            cells[1].innerText = nuevoProducto;
            cells[2].innerText = nuevaCantidad;
            cells[3].innerText = `$${nuevoPrecio}`;
        }
    };

    window.buscarProducto = function () {
        let filtro = document.getElementById("search").value.toLowerCase();
        let filas = document.querySelectorAll("#inventoryBody tr");

        filas.forEach(fila => {
            let producto = fila.getElementsByTagName("td")[1].innerText.toLowerCase();
            fila.style.display = producto.includes(filtro) ? "" : "none";
        });
    };
}
