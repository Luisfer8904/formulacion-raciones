/**
 * JavaScript mejorado para herramientas con APIs backend
 * Versión: 2.0
 * Fecha: 2024
 */

// Funciones de utilidad
function mostrarNotificacion(mensaje, tipo = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function mostrarLoading(elemento, mostrar = true) {
    if (mostrar) {
        elemento.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Procesando...</div>';
    }
}

// Conversión de unidades mejorada con API
function convertirUnidadesAPI() {
    const valor = parseFloat(document.getElementById('valorConvertir').value);
    const origen = document.getElementById('unidadOrigen').value;
    const destino = document.getElementById('unidadDestino').value;
    const resultadoDiv = document.getElementById('resultadoConversion');
    
    if (!valor || valor <= 0) {
        resultadoDiv.innerHTML = '<div class="alert alert-warning">Por favor ingrese un valor válido mayor a 0</div>';
        return;
    }
    
    mostrarLoading(resultadoDiv);
    
    fetch('/api/convertir_unidades', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            valor: valor,
            origen: origen,
            destino: destino
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resultadoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><strong>Resultado de Conversión</strong></h6>
                    <p class="mb-0">${data.mensaje}</p>
                    <small class="text-muted">Resultado: ${data.resultado}</small>
                </div>
            `;
            mostrarNotificacion('Conversión realizada exitosamente', 'success');
        } else {
            resultadoDiv.innerHTML = `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
            mostrarNotificacion(`Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultadoDiv.innerHTML = `<div class="alert alert-danger">❌ Error de conexión: ${error.message}</div>`;
        mostrarNotificacion('Error de conexión con el servidor', 'danger');
    });
}

// Cálculo de nutrientes mejorado con API
function calcularNutrienteAPI() {
    const tipoNutriente = document.getElementById('tipoNutriente').value;
    const porcentajeNutriente = parseFloat(document.getElementById('porcentajeNutriente').value);
    const materiaSeca = parseFloat(document.getElementById('materiaSeca').value);
    const cantidad = parseFloat(document.getElementById('cantidad').value);
    const resultadoDiv = document.getElementById('resultadoProteina');
    
    if (!porcentajeNutriente || !materiaSeca || !cantidad) {
        resultadoDiv.innerHTML = '<div class="alert alert-warning">Por favor complete todos los campos</div>';
        return;
    }
    
    if (cantidad <= 0 || materiaSeca <= 0 || materiaSeca > 100) {
        resultadoDiv.innerHTML = '<div class="alert alert-warning">Valores inválidos. Verifique los datos ingresados.</div>';
        return;
    }
    
    mostrarLoading(resultadoDiv);
    
    fetch('/api/calcular_nutriente', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tipo_nutriente: tipoNutriente,
            porcentaje_nutriente: porcentajeNutriente,
            materia_seca: materiaSeca,
            cantidad: cantidad
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resultadoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><strong>Cálculo de ${data.nombre_nutriente}</strong></h6>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Cálculo paso a paso:</strong><br>
                            1. ${data.calculo.paso1}<br>
                            2. ${data.calculo.paso2}
                        </div>
                        <div class="col-md-6">
                            <div class="text-center p-3 bg-light rounded">
                                <h5 class="text-success mb-0">${data.resultado} ${data.unidad}</h5>
                                <small class="text-muted">Total de ${data.nombre_nutriente}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            mostrarNotificacion(`Cálculo completado: ${data.resultado} ${data.unidad}`, 'success');
        } else {
            resultadoDiv.innerHTML = `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
            mostrarNotificacion(`Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultadoDiv.innerHTML = `<div class="alert alert-danger">❌ Error de conexión: ${error.message}</div>`;
        mostrarNotificacion('Error de conexión con el servidor', 'danger');
    });
}

// Cargar ingredientes con límites
function cargarIngredientesConLimites() {
    return fetch('/api/ingredientes_con_limites')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.ingredientes;
            } else {
                throw new Error(data.error || 'Error al cargar ingredientes');
            }
        });
}

// Actualizar límites de ingrediente
function actualizarLimitesIngrediente(ingredienteId, limiteMin, limiteMax) {
    return fetch('/api/actualizar_limites_ingrediente', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ingrediente_id: ingredienteId,
            limite_min: limiteMin,
            limite_max: limiteMax
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion(data.mensaje, 'success');
            return true;
        } else {
            mostrarNotificacion(`Error: ${data.error}`, 'danger');
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión con el servidor', 'danger');
        return false;
    });
}

// Calculadora de aportes nutricionales mejorada
function calcularAportesNutricionalesAPI(ingredientes, consumo, tipoCalculo = 'base_humeda') {
    return fetch('/api/calcular_aportes_nutricionales', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ingredientes: ingredientes,
            consumo: consumo,
            tipo_calculo: tipoCalculo
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || 'Error en el cálculo');
        }
    });
}

// Modal de gestión de límites de ingredientes
function abrirGestionLimites() {
    const modalHtml = `
        <div class="modal fade" id="gestionLimitesModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-sliders-h me-2"></i>Gestión de Límites de Ingredientes</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            Configure los límites mínimos y máximos de inclusión para cada ingrediente en las formulaciones.
                        </div>
                        <div id="tablaLimites">
                            <div class="text-center">
                                <i class="fas fa-spinner fa-spin"></i> Cargando ingredientes...
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="guardarTodosLosLimites()">
                            <i class="fas fa-save me-1"></i>Guardar Cambios
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si existe
    const existingModal = document.getElementById('gestionLimitesModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('gestionLimitesModal'));
    modal.show();
    
    // Cargar datos
    cargarTablaLimites();
}

function cargarTablaLimites() {
    const tablaDiv = document.getElementById('tablaLimites');
    
    cargarIngredientesConLimites()
        .then(ingredientes => {
            if (ingredientes.length === 0) {
                tablaDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No se encontraron ingredientes. Agregue ingredientes primero.
                    </div>
                `;
                return;
            }
            
            let tablaHtml = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Ingrediente</th>
                                <th>Precio</th>
                                <th>MS (%)</th>
                                <th>Límite Mín (%)</th>
                                <th>Límite Máx (%)</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            ingredientes.forEach(ing => {
                tablaHtml += `
                    <tr data-ingrediente-id="${ing.id}">
                        <td>
                            <strong>${ing.nombre}</strong>
                            ${ing.comentario ? `<br><small class="text-muted">${ing.comentario}</small>` : ''}
                        </td>
                        <td>$${parseFloat(ing.precio || 0).toFixed(2)}</td>
                        <td>${parseFloat(ing.ms || 100).toFixed(1)}%</td>
                        <td>
                            <input type="number" class="form-control form-control-sm limite-min" 
                                   value="${parseFloat(ing.limite_min || 0).toFixed(2)}" 
                                   min="0" max="100" step="0.01">
                        </td>
                        <td>
                            <input type="number" class="form-control form-control-sm limite-max" 
                                   value="${parseFloat(ing.limite_max || 100).toFixed(2)}" 
                                   min="0" max="100" step="0.01">
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="guardarLimiteIndividual(${ing.id})">
                                <i class="fas fa-save"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            tablaHtml += `
                        </tbody>
                    </table>
                </div>
            `;
            
            tablaDiv.innerHTML = tablaHtml;
        })
        .catch(error => {
            console.error('Error:', error);
            tablaDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error al cargar ingredientes: ${error.message}
                </div>
            `;
        });
}

function guardarLimiteIndividual(ingredienteId) {
    const fila = document.querySelector(`tr[data-ingrediente-id="${ingredienteId}"]`);
    const limiteMin = parseFloat(fila.querySelector('.limite-min').value);
    const limiteMax = parseFloat(fila.querySelector('.limite-max').value);
    
    if (limiteMin > limiteMax) {
        mostrarNotificacion('El límite mínimo no puede ser mayor al máximo', 'warning');
        return;
    }
    
    actualizarLimitesIngrediente(ingredienteId, limiteMin, limiteMax);
}

function guardarTodosLosLimites() {
    const filas = document.querySelectorAll('tr[data-ingrediente-id]');
    let promesas = [];
    
    filas.forEach(fila => {
        const ingredienteId = parseInt(fila.dataset.ingredienteId);
        const limiteMin = parseFloat(fila.querySelector('.limite-min').value);
        const limiteMax = parseFloat(fila.querySelector('.limite-max').value);
        
        if (limiteMin <= limiteMax) {
            promesas.push(actualizarLimitesIngrediente(ingredienteId, limiteMin, limiteMax));
        }
    });
    
    Promise.all(promesas)
        .then(resultados => {
            const exitosos = resultados.filter(r => r === true).length;
            mostrarNotificacion(`Se actualizaron ${exitosos} ingredientes exitosamente`, 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al guardar algunos límites', 'danger');
        });
}

// Reemplazar funciones originales
function convertirUnidades() {
    convertirUnidadesAPI();
}

function calcularNutrienteConMS() {
    calcularNutrienteAPI();
}

// Función para agregar botón de gestión de límites
function agregarBotonGestionLimites() {
    const toolsGrid = document.querySelector('.tools-grid');
    if (toolsGrid) {
        const limitesCard = `
            <div class="tool-card" onclick="abrirGestionLimites()">
                <div class="tool-icon bg-warning">
                    <i class="fas fa-sliders-h"></i>
                </div>
                <div class="tool-content">
                    <h5>Gestión de Límites</h5>
                    <p>Configure límites mínimos y máximos de inclusión para ingredientes</p>
                    <div class="tool-features">
                        <span class="feature-tag">Límites</span>
                        <span class="feature-tag">Ingredientes</span>
                        <span class="feature-tag">Optimización</span>
                    </div>
                </div>
                <div class="tool-status">
                    <span class="status-badge status-active">Activo</span>
                </div>
            </div>
        `;
        
        toolsGrid.insertAdjacentHTML('beforeend', limitesCard);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Herramientas mejoradas cargadas');
    
    // Agregar botón de gestión de límites
    agregarBotonGestionLimites();
    
    // Actualizar estadísticas
    const statItems = document.querySelectorAll('.stat-number');
    if (statItems.length > 0) {
        statItems[0].textContent = '6'; // Herramientas activas (incluyendo gestión de límites)
    }
});
