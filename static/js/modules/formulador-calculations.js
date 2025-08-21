/**
 * Módulo de Cálculos del Formulador
 * Contiene todas las funciones matemáticas y de cálculo nutricional
 */

import { obtenerConfigUsuario, convertirUnidades, esNumeroValido, obtenerElemento } from './formulador-config.js';

/**
 * Calcula el peso de bachada para un ingrediente
 * @param {number} inclusion - Porcentaje de inclusión
 * @param {number} tamanoBachada - Tamaño total de la bachada
 * @returns {number} Peso calculado
 */
export function calcularPesoBachada(inclusion, tamanoBachada) {
    if (!esNumeroValido(inclusion) || !esNumeroValido(tamanoBachada)) {
        return 0;
    }
    return (inclusion * tamanoBachada) / 100;
}

/**
 * Calcula el valor total de un ingrediente
 * @param {number} peso - Peso del ingrediente
 * @param {number} precio - Precio por unidad
 * @returns {number} Valor total calculado
 */
export function calcularValorTotal(peso, precio) {
    if (!esNumeroValido(peso) || !esNumeroValido(precio)) {
        return 0;
    }
    return peso * precio;
}

/**
 * Calcula la suma total de inclusiones
 * @returns {number} Suma total de inclusiones
 */
export function calcularSumaInclusiones() {
    const tabla = obtenerElemento('#tabla-ingredientes');
    if (!tabla) return 0;
    
    let suma = 0;
    const filas = tabla.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
        if (inputInclusion && inputInclusion.value) {
            const valor = parseFloat(inputInclusion.value);
            if (esNumeroValido(valor)) {
                suma += valor;
            }
        }
    });
    
    return suma;
}

/**
 * Calcula el costo total de la mezcla
 * @returns {number} Costo total calculado
 */
export function calcularCostoTotal() {
    const tabla = obtenerElemento('#tabla-ingredientes');
    if (!tabla) return 0;
    
    let total = 0;
    const filas = tabla.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        const inputValor = fila.querySelector('input[name^="valor_"]');
        if (inputValor && inputValor.value) {
            const valor = parseFloat(inputValor.value);
            if (esNumeroValido(valor)) {
                total += valor;
            }
        }
    });
    
    return total;
}

/**
 * Calcula los aportes nutricionales de la mezcla
 * @returns {Object} Objeto con los aportes calculados por nutriente
 */
export function calcularAportesNutricionales() {
    const tabla = obtenerElemento('#tabla-ingredientes');
    const tablaNutrientes = obtenerElemento('#tabla-nutrientes');
    
    if (!tabla || !tablaNutrientes) return {};
    
    const aportes = {};
    const filas = tabla.querySelectorAll('tbody tr');
    
    // Obtener lista de nutrientes activos
    const filasNutrientes = tablaNutrientes.querySelectorAll('tbody tr');
    const nutrientesActivos = [];
    
    filasNutrientes.forEach(fila => {
        const select = fila.querySelector('select[name^="nutriente_"]');
        if (select && select.value) {
            const nutrienteId = select.value;
            const nutrienteNombre = select.options[select.selectedIndex].text;
            nutrientesActivos.push({
                id: nutrienteId,
                nombre: nutrienteNombre
            });
        }
    });
    
    // Calcular aportes para cada nutriente
    nutrientesActivos.forEach(nutriente => {
        let aporteTotal = 0;
        
        filas.forEach(fila => {
            const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
            const select = fila.querySelector('select[name^="ingrediente_"]');
            
            if (inputInclusion && select && inputInclusion.value && select.value) {
                const inclusion = parseFloat(inputInclusion.value);
                const ingredienteData = JSON.parse(select.selectedOptions[0].dataset.nutrientes || '[]');
                
                // Buscar el valor del nutriente en el ingrediente
                const nutrienteEnIngrediente = ingredienteData.find(n => n.id == nutriente.id);
                if (nutrienteEnIngrediente && esNumeroValido(inclusion)) {
                    const valorNutriente = parseFloat(nutrienteEnIngrediente.valor || 0);
                    aporteTotal += (inclusion * valorNutriente) / 100;
                }
            }
        });
        
        aportes[nutriente.id] = {
            nombre: nutriente.nombre,
            valor: aporteTotal
        };
    });
    
    return aportes;
}

/**
 * Actualiza los resultados nutricionales en la tabla
 * @param {Object} aportes - Aportes calculados
 */
export function actualizarResultadosNutricionales(aportes) {
    const tablaNutrientes = obtenerElemento('#tabla-nutrientes');
    if (!tablaNutrientes) return;
    
    const filas = tablaNutrientes.querySelectorAll('tbody tr');
    
    filas.forEach((fila, index) => {
        const select = fila.querySelector('select[name^="nutriente_"]');
        if (select && select.value) {
            const nutrienteId = select.value;
            const aporte = aportes[nutrienteId];
            
            if (aporte) {
                // Actualizar resultado TC (tal como viene)
                const spanTC = fila.querySelector(`#resultado-tc-${index}`);
                if (spanTC) {
                    spanTC.textContent = aporte.valor.toFixed(4);
                }
                
                // Actualizar resultado BS (base seca) - aquí podrías aplicar conversión si es necesario
                const spanBS = fila.querySelector(`#resultado-bs-${index}`);
                if (spanBS) {
                    spanBS.textContent = aporte.valor.toFixed(4);
                }
            }
        }
    });
}

/**
 * Actualiza todos los valores calculados en la interfaz
 */
export function actualizarTodosLosCalculos() {
    const tamanoBachada = parseFloat(obtenerElemento('#tamano-bachada')?.value || 100);
    
    // Actualizar cada fila de ingredientes
    const tabla = obtenerElemento('#tabla-ingredientes');
    if (tabla) {
        const filas = tabla.querySelectorAll('tbody tr');
        
        filas.forEach(fila => {
            const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
            const inputPeso = fila.querySelector('input[name^="peso_bachada_"]');
            const inputCosto = fila.querySelector('input[name^="costo_ingrediente_"]');
            const inputValor = fila.querySelector('input[name^="valor_"]');
            const select = fila.querySelector('select[name^="ingrediente_"]');
            
            if (inputInclusion && inputInclusion.value && select && select.value) {
                const inclusion = parseFloat(inputInclusion.value);
                const precio = parseFloat(select.selectedOptions[0].dataset.precio || 0);
                
                // Calcular peso
                const peso = calcularPesoBachada(inclusion, tamanoBachada);
                if (inputPeso) inputPeso.value = peso.toFixed(2);
                
                // Actualizar precio (ya viene del ingrediente)
                if (inputCosto) inputCosto.value = precio.toFixed(2);
                
                // Calcular valor total
                const valorTotal = calcularValorTotal(peso, precio);
                if (inputValor) inputValor.value = valorTotal.toFixed(2);
            }
        });
    }
    
    // Actualizar totales
    actualizarTotales();
    
    // Actualizar aportes nutricionales
    const aportes = calcularAportesNutricionales();
    actualizarResultadosNutricionales(aportes);
}

/**
 * Actualiza los totales en la interfaz
 */
export function actualizarTotales() {
    // Actualizar suma de inclusiones
    const sumaInclusion = calcularSumaInclusiones();
    const spanSumaInclusion = obtenerElemento('#suma-inclusion');
    if (spanSumaInclusion) {
        spanSumaInclusion.textContent = sumaInclusion.toFixed(2);
        
        // Cambiar color según si está cerca del 100%
        if (Math.abs(sumaInclusion - 100) < 0.1) {
            spanSumaInclusion.style.color = '#28a745'; // Verde
        } else if (sumaInclusion > 100) {
            spanSumaInclusion.style.color = '#dc3545'; // Rojo
        } else {
            spanSumaInclusion.style.color = '#ffc107'; // Amarillo
        }
    }
    
    // Actualizar costo total
    const costoTotal = calcularCostoTotal();
    const spanCostoTotal = obtenerElemento('#suma-total');
    if (spanCostoTotal) {
        spanCostoTotal.textContent = costoTotal.toFixed(2);
    }
}

/**
 * Valida que la suma de inclusiones no exceda el 100%
 * @returns {Object} Resultado de la validación
 */
export function validarSumaInclusiones() {
    const suma = calcularSumaInclusiones();
    
    return {
        valida: suma <= 100,
        suma: suma,
        exceso: Math.max(0, suma - 100),
        mensaje: suma > 100 ? 
            `La suma de inclusiones (${suma.toFixed(2)}%) excede el 100%. Exceso: ${(suma - 100).toFixed(2)}%` :
            suma < 99 ?
            `La suma de inclusiones (${suma.toFixed(2)}%) está por debajo del 100%. Falta: ${(100 - suma).toFixed(2)}%` :
            'La suma de inclusiones es correcta'
    };
}

/**
 * Optimiza los cálculos usando requestAnimationFrame para mejor rendimiento
 */
let calculosPendientes = false;

export function calcularConOptimizacion() {
    if (calculosPendientes) return;
    
    calculosPendientes = true;
    requestAnimationFrame(() => {
        actualizarTodosLosCalculos();
        calculosPendientes = false;
    });
}

// Inicialización del módulo
export function inicializarCalculos() {
    console.log('🧮 Módulo de cálculos del formulador inicializado');
    
    // Configurar eventos de cálculo automático
    document.addEventListener('input', (event) => {
        if (event.target.matches('input[name^="inclusion_"], #tamano-bachada')) {
            calcularConOptimizacion();
        }
    });
    
    document.addEventListener('change', (event) => {
        if (event.target.matches('select[name^="ingrediente_"]')) {
            calcularConOptimizacion();
        }
    });
}
