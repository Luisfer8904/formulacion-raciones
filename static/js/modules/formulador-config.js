/**
 * Módulo de Configuración del Formulador
 * Contiene configuraciones globales, conversiones de unidades y utilidades básicas
 */

// Configuraciones globales
export const FORMULADOR_CONFIG = {
    // Conversiones de unidades a kg como base
    UNIT_CONVERSIONS: {
        'kg': 1,
        'lb': 0.453592,
        'ton': 1000
    },
    
    // Configuración de timeouts y delays
    TIMEOUTS: {
        DEBOUNCE_DELAY: 300,
        CALCULATION_DELAY: 100,
        API_TIMEOUT: 30000
    },
    
    // Configuración de UI
    UI: {
        ANIMATION_DURATION: 300,
        MODAL_FADE_TIME: 150
    }
};

/**
 * Convierte valores entre diferentes unidades de peso
 * @param {number} valor - Valor a convertir
 * @param {string} unidadOrigen - Unidad de origen
 * @param {string} unidadDestino - Unidad de destino
 * @returns {number} Valor convertido
 */
export function convertirUnidades(valor, unidadOrigen, unidadDestino) {
    if (!valor || unidadOrigen === unidadDestino) return valor;
    
    const conversiones = FORMULADOR_CONFIG.UNIT_CONVERSIONS;
    
    // Convertir a kg primero, luego a unidad destino
    const valorEnKg = valor * conversiones[unidadOrigen];
    return valorEnKg / conversiones[unidadDestino];
}

/**
 * Obtiene la configuración del usuario desde window.configUsuario
 * @returns {Object} Configuración del usuario con valores por defecto
 */
export function obtenerConfigUsuario() {
    return window.configUsuario || {
        moneda: 'USD',
        unidad_medida: 'kg',
        simbolo_moneda: '$'
    };
}

/**
 * Actualiza las etiquetas de la interfaz con la configuración del usuario
 */
export function actualizarEtiquetasUI() {
    const config = obtenerConfigUsuario();
    
    // Actualizar headers de tablas
    const headers = document.querySelectorAll('th');
    headers.forEach(header => {
        if (header.textContent.includes('Lps/kg')) {
            header.textContent = header.textContent.replace('Lps/kg',
                `${config.moneda}/${config.unidad_medida}`);
        }
        if (header.textContent.includes('(kg)')) {
            header.textContent = header.textContent.replace('(kg)',
                `(${config.unidad_medida})`);
        }
    });
    
    // Actualizar etiquetas de totales
    const totalLabel = document.querySelector('strong');
    if (totalLabel && totalLabel.textContent.includes('Total de la mezcla (Lps):')) {
        totalLabel.textContent = totalLabel.textContent.replace('Total de la mezcla (Lps):',
            `Total de la mezcla (${config.moneda}):`);
    }
}

/**
 * Formatea un número como moneda según la configuración del usuario
 * @param {number} valor - Valor a formatear
 * @param {boolean} incluirSimbolo - Si incluir el símbolo de moneda
 * @returns {string} Valor formateado
 */
export function formatearMoneda(valor, incluirSimbolo = true) {
    const config = obtenerConfigUsuario();
    const valorFormateado = parseFloat(valor).toFixed(2);
    
    return incluirSimbolo ? 
        `${config.simbolo_moneda}${valorFormateado}` : 
        valorFormateado;
}

/**
 * Formatea un peso según la unidad de medida del usuario
 * @param {number} valor - Valor a formatear
 * @param {boolean} incluirUnidad - Si incluir la unidad
 * @returns {string} Valor formateado
 */
export function formatearPeso(valor, incluirUnidad = true) {
    const config = obtenerConfigUsuario();
    const valorFormateado = parseFloat(valor).toFixed(3);
    
    return incluirUnidad ? 
        `${valorFormateado} ${config.unidad_medida}` : 
        valorFormateado;
}

/**
 * Debounce function para optimizar llamadas frecuentes
 * @param {Function} func - Función a ejecutar
 * @param {number} wait - Tiempo de espera en ms
 * @param {boolean} immediate - Si ejecutar inmediatamente
 * @returns {Function} Función con debounce aplicado
 */
export function debounce(func, wait = FORMULADOR_CONFIG.TIMEOUTS.DEBOUNCE_DELAY, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Valida si un valor es un número válido
 * @param {any} valor - Valor a validar
 * @returns {boolean} True si es un número válido
 */
export function esNumeroValido(valor) {
    return !isNaN(parseFloat(valor)) && isFinite(valor) && valor >= 0;
}

/**
 * Obtiene un elemento del DOM con cache para optimizar rendimiento
 */
const elementCache = new Map();

export function obtenerElemento(selector) {
    if (elementCache.has(selector)) {
        const element = elementCache.get(selector);
        // Verificar si el elemento aún existe en el DOM
        if (document.contains(element)) {
            return element;
        } else {
            elementCache.delete(selector);
        }
    }
    
    const element = document.querySelector(selector);
    if (element) {
        elementCache.set(selector, element);
    }
    return element;
}

/**
 * Limpia el cache de elementos DOM
 */
export function limpiarCacheElementos() {
    elementCache.clear();
}

// Inicialización del módulo
export function inicializarConfiguracion() {
    console.log('🔧 Módulo de configuración del formulador inicializado');
    
    // Actualizar UI al cargar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', actualizarEtiquetasUI);
    } else {
        actualizarEtiquetasUI();
    }
}
