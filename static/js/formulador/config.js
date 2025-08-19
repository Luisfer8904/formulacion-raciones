// ===== CONFIGURACIÓN Y FORMATEO DINÁMICO =====

// Variables globales
let contadorFilas = 1;
let contadorRequerimientos = 1;
let contadorNutrientes = 0;
let requerimientoSeleccionado = null;

// Variables para rastrear cambios sin guardar
let hayCambiosSinGuardar = false;
let formularioGuardadoRecientemente = false;
let navegacionInternaEnProceso = false;

// Función para obtener el símbolo de moneda
function obtenerSimboloMoneda(moneda) {
  const simbolos = {
    'HNL': 'L',
    'GTQ': 'Q',
    'USD': '$',
    'CRC': '₡'
  };
  return simbolos[moneda] || moneda;
}

// Función para formatear inclusiones con decimales inteligentes
function formatearInclusion(valor) {
  const num = parseFloat(valor);
  if (isNaN(num)) return "0.00";
  
  // Si el valor es menor a 0.01, usar 4 decimales
  if (num < 0.01 && num > 0) {
    return num.toFixed(4);
  }
  // Si el valor es menor a 0.1, usar 3 decimales
  else if (num < 0.1) {
    return num.toFixed(3);
  }
  // Para valores mayores, usar 2 decimales
  else {
    return num.toFixed(2);
  }
}

// Función para formatear precio con moneda
function formatearPrecio(valor, mostrarSimbolo = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarSimbolo) {
    const simbolo = obtenerSimboloMoneda(window.configUsuario.moneda);
    return `${simbolo} ${valorFormateado}`;
  }
  return valorFormateado;
}

// Función para formatear peso con unidad
function formatearPeso(valor, mostrarUnidad = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarUnidad) {
    return `${valorFormateado} ${window.configUsuario.unidad_medida}`;
  }
  return valorFormateado;
}

// Función para convertir entre unidades de peso
function convertirPeso(valor, unidadOrigen, unidadDestino) {
  if (unidadOrigen === unidadDestino) return valor;
  
  // Conversiones a kg como base
  const aKg = {
    'kg': 1,
    'lb': 0.453592,
    'ton': 1000
  };
  
  // Convertir a kg primero, luego a unidad destino
  const valorEnKg = valor * aKg[unidadOrigen];
  return valorEnKg / aKg[unidadDestino];
}

// Función para actualizar etiquetas dinámicamente
function actualizarEtiquetasDinamicas() {
  if (!window.configUsuario) return;
  
  // Actualizar etiquetas de encabezados de tabla si es necesario
  const headers = document.querySelectorAll('th');
  headers.forEach(header => {
    if (header.textContent.includes('Lps/kg')) {
      header.textContent = header.textContent.replace('Lps/kg', 
        `${window.configUsuario.moneda}/${window.configUsuario.unidad_medida}`);
    }
    if (header.textContent.includes('Lps)')) {
      header.textContent = header.textContent.replace('Lps)', 
        `${window.configUsuario.moneda})`);
    }
    if (header.textContent.includes('(kg)')) {
      header.textContent = header.textContent.replace('(kg)', 
        `(${window.configUsuario.unidad_medida})`);
    }
  });
  
  // Actualizar etiquetas de totales
  const totalLabel = document.querySelector('strong');
  if (totalLabel && totalLabel.textContent.includes('Total de la mezcla (Lps):')) {
    totalLabel.textContent = totalLabel.textContent.replace('(Lps):', 
      `(${window.configUsuario.moneda}):`);
  }
}
