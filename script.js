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

            // Aquí podrías incluir lógica adicional si necesitas inicializar vistas específicas
            // if (url.includes("Reportes")) { inicializarReportes(); }
        })
        .catch(err => console.error("Error al cargar vista:", err));
}
