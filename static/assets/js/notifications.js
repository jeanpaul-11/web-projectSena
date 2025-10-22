// Función para mostrar notificaciones estilizadas
function mostrarNotificacion(mensaje, tipo = 'info', duracion = 5000) {
    // Asegurar que existe el contenedor de notificaciones
    let container = document.getElementById('notificacionContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificacionContainer';
        container.className = 'notificacion-container';
        document.body.appendChild(container);
    }

    // Crear la notificación
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion ${tipo}`;
    
    // Determinar el ícono según el tipo
    let icono = 'ti-info-alt';
    switch(tipo) {
        case 'success':
            icono = 'ti-check';
            break;
        case 'error':
            icono = 'ti-close';
            break;
        case 'warning':
            icono = 'ti-alert';
            break;
    }
    
    // Construir el contenido de la notificación
    notificacion.innerHTML = `
        <div class="mensaje">
            <i class="${icono}"></i>
            <span>${mensaje}</span>
        </div>
        <button class="cerrar" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Agregar la notificación al contenedor
    container.appendChild(notificacion);
    
    // Remover la notificación después del tiempo especificado
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (notificacion.parentElement) {
                    notificacion.remove();
                }
            }, 300);
        }
    }, duracion);

    // Retornar la notificación por si se necesita manipular
    return notificacion;
}