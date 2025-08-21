/**
 * Módulo de Interfaz de Usuario del Formulador
 * Contiene funciones para manejo de DOM, eventos y interacciones de usuario
 */

import { obtenerElemento, debounce, obtenerConfigUsuario } from './formulador-config.js';
import { calcularConOptimizacion, validarSumaInclusiones } from './formulador-calculations.js';

/**
 * Contador global para generar IDs únicos
 */
let contadorFilas = 0;
let contadorNutrientes = 0;

/**
 * Agrega una nueva fila de ingrediente a la tabla
 * @param {HTMLElement} selectElement - Elemento select que disparó la acción
 */
export function agregarFila(selectElement) {
    if (!selectElement || !selectElement.value) return;
    
    const tabla = obtenerElemento('#tabla-ingredientes tbody');
    if (!tabla) return;
    
    // Verificar si el ingrediente ya está seleccionado
    const selectsExistentes = tabla.querySelectorAll('select[name^="ingrediente_"]');
    const ingredienteYaSeleccionado = Array.from(selectsExistentes).some(select => 
        select !== selectElement && select.value === selectElement.value
    );
    
    if (ingredienteYaSeleccionado) {
        mostrarAlerta('Este ingrediente ya está seleccionado en la mezcla', 'warning');
        selectElement.value = '';
        return;
    }
    
    contadorFilas++;
    const nuevaFila = crearFilaIngrediente(contadorFilas);
    tabla.appendChild(nuevaFila);
    
    // Enfocar el input de inclusión de la nueva fila
    const inputInclusion = nuevaFila.querySelector('input[name^="inclusion_"]');
    if (inputInclusion) {
        inputInclusion.focus();
    }
}

/**
 * Crea una nueva fila de ingrediente
 * @param {number} indice - Índice de la fila
 * @returns {HTMLElement} Elemento TR de la nueva fila
 */
function crearFilaIngrediente(indice) {
    const fila = document.createElement('tr');
    fila.innerHTML = `
        <td>
            <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${indice}" onchange="agregarFila(this)">
                <option value="">-- Seleccionar --</option>
                ${generarOpcionesIngredientes()}
            </select>
        </td>
        <td><input type="number" class="form-control form-control-sm" name="inclusion_${indice}" min="0" max="100" step="0.0001" oninput="calcularConOptimizacion()"></td>
        <td><input type="number" class="form-control form-control-sm" name="min_${indice}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="max_${indice}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${indice}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${indice}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="valor_${indice}" step="0.01" readonly></td>
        <td>
            <div class="btn-action-container">
                <button type="button" class="btn-action btn-action-danger" onclick="eliminarFila(this)" title="Eliminar ingrediente">
                    <i class="fas fa-times"></i>
                </button>
                <button type="button" class="btn-action btn-action-info" onclick="mostrarInfo(this)" title="Ver información">
                    <i class="fas fa-info"></i>
                </button>
            </div>
        </td>
    `;
    
    return fila;
}

/**
 * Genera las opciones HTML para el select de ingredientes
 * @returns {string} HTML de las opciones
 */
function generarOpcionesIngredientes() {
    if (typeof window.mineralesTemplate === 'undefined' || !Array.isArray(window.mineralesTemplate)) {
        return '<option disabled>No hay ingredientes disponibles</option>';
    }
    
    return window.mineralesTemplate.map(ingrediente => {
        const nutrientesData = JSON.stringify(ingrediente.nutrientes || []);
        return `
            <option value="${ingrediente.id}"
                data-precio="${ingrediente.precio || 0}"
                data-ms="${ingrediente.ms || 0}"
                data-nutrientes='${nutrientesData}'>
                ${ingrediente.nombre}
            </option>
        `;
    }).join('');
}

/**
 * Elimina una fila de ingrediente
 * @param {HTMLElement} boton - Botón que disparó la acción
 */
export function eliminarFila(boton) {
    const fila = boton.closest('tr');
    const tabla = obtenerElemento('#tabla-ingredientes');
    
    if (!fila || !tabla) return;
    
    // Confirmar eliminación si la fila tiene datos
    const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
    if (inputInclusion && inputInclusion.value) {
        if (!confirm('¿Estás seguro de que deseas eliminar este ingrediente de la mezcla?')) {
            return;
        }
    }
    
    fila.remove();
    calcularConOptimizacion();
    
    // Si no quedan filas con datos, agregar una fila vacía
    const filasConDatos = tabla.querySelectorAll('tbody tr select[name^="ingrediente_"]');
    const hayFilasConDatos = Array.from(filasConDatos).some(select => select.value);
    
    if (!hayFilasConDatos) {
        contadorFilas++;
        const nuevaFila = crearFilaIngrediente(contadorFilas);
        tabla.querySelector('tbody').appendChild(nuevaFila);
    }
}

/**
 * Muestra información detallada de un ingrediente
 * @param {HTMLElement} boton - Botón que disparó la acción
 */
export function mostrarInfo(boton) {
    const fila = boton.closest('tr');
    const select = fila.querySelector('select');
    
    if (!select || !select.value) {
        mostrarAlerta('Selecciona un ingrediente primero', 'warning');
        return;
    }
    
    const opcionSeleccionada = select.selectedOptions[0];
    const ingredienteId = select.value;
    
    // Intentar obtener datos del dataset primero
    if (opcionSeleccionada.dataset.nutrientes) {
        try {
            const nutrientes = JSON.parse(opcionSeleccionada.dataset.nutrientes);
            mostrarModalInfo(opcionSeleccionada.text, nutrientes);
        } catch (error) {
            console.error('Error al parsear nutrientes:', error);
            obtenerInfoIngredienteAPI(ingredienteId);
        }
    } else {
        obtenerInfoIngredienteAPI(ingredienteId);
    }
}

/**
 * Obtiene información del ingrediente desde la API
 * @param {string} ingredienteId - ID del ingrediente
 */
function obtenerInfoIngredienteAPI(ingredienteId) {
    fetch(`/api/ingrediente/${ingredienteId}`)
        .then(response => response.json())
        .then(data => {
            mostrarModalInfo(data.nombre, data.nutrientes || []);
        })
        .catch(error => {
            console.error('Error al obtener información del ingrediente:', error);
            mostrarAlerta('Error al cargar la información del ingrediente', 'error');
        });
}

/**
 * Muestra el modal con información del ingrediente
 * @param {string} nombre - Nombre del ingrediente
 * @param {Array} nutrientes - Array de nutrientes
 */
function mostrarModalInfo(nombre, nutrientes) {
    const modal = obtenerElemento('#infoIngredienteModal');
    const contenido = obtenerElemento('#contenidoInfoIngrediente');
    
    if (!modal || !contenido) return;
    
    let html = `<strong>Ingrediente:</strong> ${nombre}<br><br>`;
    
    if (nutrientes && nutrientes.length > 0) {
        html += '<div class="row">';
        
        const grupos = {
            'Composición Básica': ['MATERIA_SECA', 'HUMEDAD', 'CENIZAS', 'PB', 'EE', 'FB'],
            'Energía': ['EM_RTES_Kcal_kg', 'EMA_AVES_Kcal_kg', 'ED_PORC_Kcal_kg'],
            'Minerales': ['Ca', 'P', 'Na', 'Cl', 'Mg', 'K', 'S'],
            'Aminoácidos': ['LYS', 'MET', 'M_C', 'THR', 'TRP', 'ILE', 'VAL', 'ARG']
        };
        
        for (const [grupo, campos] of Object.entries(grupos)) {
            const nutrientesGrupo = nutrientes.filter(n => campos.includes(n.nombre));
            
            if (nutrientesGrupo.length > 0) {
                html += `
                    <div class="col-md-6 mb-3">
                        <h6 class="text-primary">${grupo}</h6>
                        <table class="table table-sm table-striped">
                            <tbody>
                `;
                
                nutrientesGrupo.forEach(nutriente => {
                    if (nutriente.valor !== null && nutriente.valor !== undefined) {
                        html += `
                            <tr>
                                <td>${nutriente.nombre}</td>
                                <td class="text-end">${parseFloat(nutriente.valor).toFixed(3)}</td>
                                <td class="text-muted">${nutriente.unidad || '%'}</td>
                            </tr>
                        `;
                    }
                });
                
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
            }
        }
        
        html += '</div>';
    } else {
        html += '<p class="text-muted">No hay información nutricional disponible para este ingrediente.</p>';
    }
    
    contenido.innerHTML = html;
    
    // Mostrar modal usando Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Agrega una nueva fila de nutriente
 * @param {HTMLElement} selectElement - Elemento select que disparó la acción
 */
export function agregarFilaNutriente(selectElement) {
    if (!selectElement || !selectElement.value) return;
    
    const tabla = obtenerElemento('#tabla-nutrientes tbody');
    if (!tabla) return;
    
    contadorNutrientes++;
    const nuevaFila = crearFilaNutriente(contadorNutrientes);
    tabla.appendChild(nuevaFila);
}

/**
 * Crea una nueva fila de nutriente
 * @param {number} indice - Índice de la fila
 * @returns {HTMLElement} Elemento TR de la nueva fila
 */
function crearFilaNutriente(indice) {
    const fila = document.createElement('tr');
    fila.innerHTML = `
        <td>
            <select class="form-select form-select-sm" name="nutriente_${indice}" onchange="actualizarUnidadSugerido(this, ${indice}); verificarUltimaFilaNutriente(${indice}); calcularConOptimizacion();">
                <option value="">-- Seleccionar --</option>
                ${generarOpcionesNutrientes()}
            </select>
        </td>
        <td><input type="text" class="form-control form-control-sm" name="unidad_${indice}" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="sugerido_${indice}" step="0.0001" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="min_${indice}" step="0.0001" oninput="calcularConOptimizacion();"></td>
        <td><input type="number" class="form-control form-control-sm" name="max_${indice}" step="0.0001" oninput="calcularConOptimizacion();"></td>
        <td class="text-end"><span id="resultado-tc-${indice}">0.00</span></td>
        <td class="text-end"><span id="resultado-bs-${indice}">0.00</span></td>
        <td class="text-center">
            <div class="btn-action-container">
                <button type="button" class="btn-action btn-action-danger" onclick="eliminarFilaNutriente(this); calcularConOptimizacion();" title="Eliminar nutriente">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </td>
    `;
    
    return fila;
}

/**
 * Genera las opciones HTML para el select de nutrientes
 * @returns {string} HTML de las opciones
 */
function generarOpcionesNutrientes() {
    if (typeof window.nutrientesTemplate === 'undefined' || !Array.isArray(window.nutrientesTemplate)) {
        return '<option disabled>No hay nutrientes disponibles</option>';
    }
    
    return window.nutrientesTemplate.map(nutriente => `
        <option value="${nutriente.id}" data-unidad="${nutriente.unidad || ''}" data-sugerido="${nutriente.sugerido || 0}">
            ${nutriente.nombre}
        </option>
    `).join('');
}

/**
 * Elimina una fila de nutriente
 * @param {HTMLElement} boton - Botón que disparó la acción
 */
export function eliminarFilaNutriente(boton) {
    const fila = boton.closest('tr');
    if (fila) {
        fila.remove();
        calcularConOptimizacion();
    }
}

/**
 * Actualiza la unidad y valor sugerido cuando se selecciona un nutriente
 * @param {HTMLElement} select - Select de nutriente
 * @param {number} indice - Índice de la fila
 */
export function actualizarUnidadSugerido(select, indice) {
    if (!select.value) return;
    
    const opcionSeleccionada = select.selectedOptions[0];
    const unidad = opcionSeleccionada.dataset.unidad || '';
    const sugerido = opcionSeleccionada.dataset.sugerido || '0';
    
    const inputUnidad = document.querySelector(`input[name="unidad_${indice}"]`);
    const inputSugerido = document.querySelector(`input[name="sugerido_${indice}"]`);
    
    if (inputUnidad) inputUnidad.value = unidad;
    if (inputSugerido) inputSugerido.value = sugerido;
}

/**
 * Muestra una alerta temporal en la interfaz
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de alerta (success, warning, error, info)
 * @param {number} duracion - Duración en milisegundos
 */
export function mostrarAlerta(mensaje, tipo = 'info', duracion = 5000) {
    const alertaContainer = obtenerElemento('#alertas-container') || crearContainerAlertas();
    
    const tiposBootstrap = {
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-danger',
        'info': 'alert-info'
    };
    
    const iconos = {
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'info': 'fas fa-info-circle'
    };
    
    const alerta = document.createElement('div');
    alerta.className = `alert ${tiposBootstrap[tipo]} alert-dismissible fade show`;
    alerta.innerHTML = `
        <i class="${iconos[tipo]} me-2"></i>${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertaContainer.appendChild(alerta);
    
    // Auto-eliminar después de la duración especificada
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.remove();
        }
    }, duracion);
}

/**
 * Crea el container para alertas si no existe
 * @returns {HTMLElement} Container de alertas
 */
function crearContainerAlertas() {
    const container = document.createElement('div');
    container.id = 'alertas-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.maxWidth = '400px';
    
    document.body.appendChild(container);
    return container;
}

/**
 * Actualiza el tamaño de bachada y recalcula todos los valores
 */
export function actualizarValoresBachada() {
    calcularConOptimizacion();
    
    // Mostrar validación de suma de inclusiones
    const validacion = validarSumaInclusiones();
    if (!validacion.valida) {
        mostrarAlerta(validacion.mensaje, 'warning');
    }
}

/**
 * Inicializa los eventos de la interfaz de usuario
 */
export function inicializarEventosUI() {
    console.log('🎨 Módulo de UI del formulador inicializado');
    
    // Event delegation para botones dinámicos
    document.addEventListener('click', (event) => {
        if (event.target.matches('.btn-action-danger') || event.target.closest('.btn-action-danger')) {
            const boton = event.target.matches('.btn-action-danger') ? event.target : event.target.closest('.btn-action-danger');
            if (boton.closest('#tabla-ingredientes')) {
                eliminarFila(boton);
            } else if (boton.closest('#tabla-nutrientes')) {
                eliminarFilaNutriente(boton);
            }
        }
        
        if (event.target.matches('.btn-action-info') || event.target.closest('.btn-action-info')) {
            const boton = event.target.matches('.btn-action-info') ? event.target : event.target.closest('.btn-action-info');
            mostrarInfo(boton);
        }
    });
    
    // Eventos para selects de ingredientes y nutrientes
    document.addEventListener('change', (event) => {
        if (event.target.matches('select[name^="ingrediente_"]')) {
            agregarFila(event.target);
        }
        
        if (event.target.matches('select[name^="nutriente_"]')) {
            const match = event.target.name.match(/nutriente_(\d+)/);
            if (match) {
                const indice = parseInt(match[1]);
                actualizarUnidadSugerido(event.target, indice);
            }
            agregarFilaNutriente(event.target);
        }
    });
    
    // Evento para cambio de tamaño de bachada
    const inputBachada = obtenerElemento('#tamano-bachada');
    if (inputBachada) {
        inputBachada.addEventListener('input', debounce(actualizarValoresBachada, 300));
    }
}

// Exponer funciones globalmente para compatibilidad con código existente
window.agregarFila = agregarFila;
window.eliminarFila = eliminarFila;
window.mostrarInfo = mostrarInfo;
window.eliminarFilaNutriente = eliminarFilaNutriente;
window.actualizarUnidadSugerido = actualizarUnidadSugerido;
window.actualizarValoresBachada = actualizarValoresBachada;
