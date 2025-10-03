// Funcionalidad para las pestañas de categorías
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#categoriasTabs .nav-link').forEach(tab => {
        tab.addEventListener('click', function(e) {
            // Remover clase active de todas las pestañas
            document.querySelectorAll('#categoriasTabs .nav-link').forEach(t => {
                t.classList.remove('active');
            });
            
            // Agregar clase active a la pestaña seleccionada
            e.target.classList.add('active');
            
            // Obtener la categoría seleccionada
            const categoriaSeleccionada = e.target.getAttribute('data-categoria');
            
            // Ocultar todos los contenidos de categoría
            document.querySelectorAll('.categoria-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Mostrar el contenido de la categoría seleccionada
            document.querySelector(`.categoria-content[data-categoria="${categoriaSeleccionada}"]`).classList.add('active');
        });
    });
});