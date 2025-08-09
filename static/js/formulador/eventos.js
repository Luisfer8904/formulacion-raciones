// ===== EVENTOS Y INICIALIZACIÓN =====

// Interceptar clics en enlaces de navegación
function interceptarNavegacion() {
  // Interceptar enlaces del menú lateral y otros enlaces de navegación
  const selectoresEnlaces = [
    '.sidebar .nav-link',  // Enlaces del menú lateral
    'a[href*="panel"]',    // Enlaces al panel
    'a[href*="ingredientes"]', // Enlaces a ingredientes
    'a[href*="nutrientes"]',   // Enlaces a nutrientes
    'a[href*="requerimientos"]', // Enlaces a requerimientos
    'a[href*="mezclas"]',      // Enlaces a mezclas
    'a[href*="opciones"]',     // Enlaces a opciones
    'a[href*="logout"]'        // Enlaces de logout
  ];
  
  selectoresEnlaces.forEach(selector => {
    document.addEventListener('click', function(e) {
      const enlace = e.target.closest(selector);
      if (!enlace) return;
      
      const href = enlace.getAttribute('href') || '';
      
      // No interceptar si es el formulador actual o enlaces vacíos
      if (href === '' || 
          href === '#' || 
          href.includes('formulacion_minerales') ||
          href.includes('panelformulador') ||
          href.startsWith('javascript:')) {
        return;
      }
      
      // Solo interceptar si hay cambios sin guardar
      if (hayCambiosSinGuardar) {
        navegacionInternaEnProceso = true;
        
        let mensaje = "¿Estás seguro de que deseas salir del formulador? Los cambios no guardados se perderán.";
        
        // Mensaje específico para logout
        if (href.includes('logout')) {
          mensaje = "¿Estás seguro de que deseas cerrar sesión? Los cambios no guardados en el formulador se perderán.";
        }
        
        if (!confirmarSalida(mensaje)) {
          navegacionInternaEnProceso = false;
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
        
        // Si el usuario confirmó, permitir la navegación y resetear la bandera
        navegacionInternaEnProceso = false;
      }
    }, true); // Usar capture para interceptar antes que otros handlers
  });
}

// Interceptar el evento beforeunload solo para navegación del navegador (cerrar pestaña, etc.)
window.addEventListener('beforeunload', function(e) {
  if (hayCambiosSinGuardar && !navegacionInternaEnProceso) {
    // Solo establecer returnValue para mostrar el diálogo nativo del navegador
    // No usar confirm() aquí para evitar doble confirmación
    e.returnValue = '';
    return '';
  }
});

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
  // Precargar ingredientes si existen
  precargarIngredientes();
  
  // Agregar una fila inicial de nutriente si no hay ninguna
  if (document.querySelectorAll('#tabla-nutrientes tr').length === 0) {
    agregarFilaNutriente();
  }
  
  // Configurar interceptores de navegación
  interceptarNavegacion();
  
  // Agregar event listeners para detectar cambios en el formulario
  const formulario = document.body;
  
  // Detectar cambios en inputs
  formulario.addEventListener('input', function(e) {
    if (e.target.matches('input, select, textarea')) {
      marcarCambiosSinGuardar();
    }
  });
  
  // Detectar cambios específicos en selects
  formulario.addEventListener('change', function(e) {
    if (e.target.matches('select')) {
      marcarCambiosSinGuardar();
    }
  });
  
  // Observar cambios dinámicos en las tablas
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList' && 
          (mutation.target.id === 'tabla-ingredientes' || 
           mutation.target.id === 'tabla-nutrientes')) {
        marcarCambiosSinGuardar();
      }
    });
  });
  
  // Observar las tablas principales
  const tablaIngredientes = document.getElementById('tabla-ingredientes');
  const tablaNutrientes = document.getElementById('tabla-nutrientes');
  
  if (tablaIngredientes) {
    observer.observe(tablaIngredientes, { childList: true, subtree: true });
  }
  
  if (tablaNutrientes) {
    observer.observe(tablaNutrientes, { childList: true, subtree: true });
  }
});
