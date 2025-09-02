// Variables globales
let mezclasDisponibles = [];
let nutrientesDisponibles = [];
let ingredientesMezclaSeleccionada = [];

// Función principal para abrir la calculadora de aportes mejorada
function abrirCalculadoraAportesMejorada() {
    const modalHtml = `
        <div class="modal fade" id="calculadoraAportesMejoradaModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-calculator me-2"></i>Calculadora de Aportes Nutricionales</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <!-- Columna izquierda: Selección de fórmula y parámetros -->
                            <div class="col-md-6">
                                <h6>1. Seleccionar Fórmula</h6>
                                <div class="mb-3">
                                    <label class="form-label">Fórmulas Disponibles</label>
                                    <select class="form-select" id="selectMezclaAportes" onchange="cargarIngredientesMezcla()">
                                        <option value="">-- Seleccionar fórmula --</option>
                                    </select>
                                    <small class="form-text text-muted">Solo se muestran fórmulas con ingredientes</small>
                                </div>
                                
                                <h6>2. Parámetros de Cálculo</h6>
                                <div class="mb-3">
                                    <label class="form-label">Consumo por Animal (kg/día)</label>
                                    <input type="number" class="form-control" id="consumoAnimalAportes" step="0.1" min="0.1" value="3.0">
                                </div>
                                <div class="alert alert-info">
                                    <h6><i class="fas fa-info-circle"></i> Valores Base Seca (BS)</h6>
                                    <p class="mb-0">Los cálculos utilizan valores nutricionales en Base Seca (BS) para mayor precisión, eliminando la necesidad de ajustes por materia seca.</p>
                                </div>
                                
                                <h6>3. Ingredientes de la Fórmula</h6>
                                <div id="ingredientesMezclaContainer" class="border rounded p-3" style="max-height: 200px; overflow-y: auto;">
                                    <div class="text-center text-muted">
                                        <i class="fas fa-arrow-up"></i>
                                        <p class="mb-0">Seleccione una fórmula para ver sus ingredientes</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Columna derecha: Selección de nutrientes -->
                            <div class="col-md-6">
                                <h6>4. Seleccionar Nutrientes a Analizar</h6>
                                <div class="mb-3">
                                    <div id="nutrientesSeleccionContainer" style="max-height: 400px; overflow-y: auto; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px;">
                                        <div class="text-center">
                                            <div class="spinner-border spinner-border-sm" role="status">
                                                <span class="visually-hidden">Cargando...</span>
                                            </div>
                                            <p class="mt-2">Cargando nutrientes...</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="d-flex gap-2">
                                    <button type="button" class="btn btn-outline-primary btn-sm" onclick="seleccionarTodosNutrientes()">
                                        <i class="fas fa-check-double"></i> Seleccionar Todos
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="deseleccionarTodosNutrientes()">
                                        <i class="fas fa-times"></i> Deseleccionar Todos
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Área de resultados -->
                        <div id="resultadosAportesContainer" class="mt-4 d-none">
                            <hr>
                            <h6>Resultados del Análisis</h6>
                            <div id="resultadosAportesContent"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="calcularAportesMejorado()" id="btnCalcularAportes">
                            <i class="fas fa-calculator me-1"></i>Calcular Aportes
                        </button>
                        <button type="button" class="btn btn-success d-none" id="btnImprimirAportesMejorado" onclick="imprimirAportesMejorado()">
                            <i class="fas fa-print me-1"></i>Imprimir Reporte
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si existe
    const existingModal = document.getElementById('calculadoraAportesMejoradaModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Cargar datos iniciales
    cargarDatosIniciales();
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('calculadoraAportesMejoradaModal'));
    modal.show();
}

// Cargar datos iniciales
function cargarDatosIniciales() {
    // Cargar fórmulas/mezclas
    fetch('/api/obtener_mezclas_para_aportes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mezclasDisponibles = data.mezclas;
                mostrarMezclasEnSelect();
            } else {
                console.error('Error cargando mezclas:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    
    // Cargar nutrientes
    fetch('/api/obtener_nutrientes_para_aportes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                nutrientesDisponibles = data.nutrientes;
                mostrarNutrientesDisponibles();
            } else {
                console.error('Error cargando nutrientes:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Mostrar mezclas en el select
function mostrarMezclasEnSelect() {
    const select = document.getElementById('selectMezclaAportes');
    
    mezclasDisponibles.forEach(mezcla => {
        const option = document.createElement('option');
        option.value = mezcla.id;
        option.textContent = `${mezcla.nombre} (${mezcla.total_ingredientes} ingredientes)`;
        if (mezcla.tipo_animales) {
            option.textContent += ` - ${mezcla.tipo_animales}`;
        }
        select.appendChild(option);
    });
}

// Mostrar nutrientes disponibles
function mostrarNutrientesDisponibles() {
    const container = document.getElementById('nutrientesSeleccionContainer');
    let html = '<div class="mb-2"><strong>Seleccione los nutrientes a analizar:</strong></div>';
    
    nutrientesDisponibles.forEach(nutriente => {
        html += `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="${nutriente.id}" id="nutriente_${nutriente.id}">
                <label class="form-check-label" for="nutriente_${nutriente.id}">
                    ${nutriente.nombre} (${nutriente.unidad})
                </label>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Cargar ingredientes de la mezcla seleccionada
function cargarIngredientesMezcla() {
    const selectMezcla = document.getElementById('selectMezclaAportes');
    const mezclaId = selectMezcla.value;
    const container = document.getElementById('ingredientesMezclaContainer');
    
    if (!mezclaId) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-arrow-up"></i>
                <p class="mb-0">Seleccione una fórmula para ver sus ingredientes</p>
            </div>
        `;
        return;
    }
    
    // Mostrar loading
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Cargando ingredientes...</p>
        </div>
    `;
    
    fetch(`/api/obtener_ingredientes_de_mezcla/${mezclaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                ingredientesMezclaSeleccionada = data.ingredientes;
                mostrarIngredientesMezcla(data.mezcla_nombre, data.ingredientes);
            } else {
                container.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        Error: ${data.error}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle"></i>
                    Error al cargar ingredientes
                </div>
            `;
        });
}

// Mostrar ingredientes de la mezcla
function mostrarIngredientesMezcla(nombreMezcla, ingredientes) {
    const container = document.getElementById('ingredientesMezclaContainer');
    
    let html = `
        <div class="mb-2">
            <strong>Ingredientes de: ${nombreMezcla}</strong>
        </div>
        <div class="table-responsive">
            <table class="table table-sm table-striped">
                <thead>
                    <tr>
                        <th>Ingrediente</th>
                        <th>Inclusión (%)</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    ingredientes.forEach(ingrediente => {
        html += `
            <tr>
                <td>${ingrediente.nombre}</td>
                <td class="text-end">${ingrediente.porcentaje}%</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}

// Seleccionar todos los nutrientes
function seleccionarTodosNutrientes() {
    const checkboxes = document.querySelectorAll('#nutrientesSeleccionContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}

// Deseleccionar todos los nutrientes
function deseleccionarTodosNutrientes() {
    const checkboxes = document.querySelectorAll('#nutrientesSeleccionContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

// Calcular aportes nutricionales mejorado
function calcularAportesMejorado() {
    const mezclaId = document.getElementById('selectMezclaAportes').value;
    const consumoAnimal = parseFloat(document.getElementById('consumoAnimalAportes').value);
    
    // Obtener nutrientes seleccionados
    const nutrientesSeleccionados = [];
    document.querySelectorAll('#nutrientesSeleccionContainer input[type="checkbox"]:checked').forEach(checkbox => {
        nutrientesSeleccionados.push(parseInt(checkbox.value));
    });
    
    // Validaciones
    if (!mezclaId) {
        mostrarNotificacion('Por favor seleccione una fórmula', 'warning');
        return;
    }
    
    if (isNaN(consumoAnimal) || consumoAnimal <= 0) {
        mostrarNotificacion('Por favor ingrese un consumo por animal válido', 'warning');
        return;
    }
    
    if (nutrientesSeleccionados.length === 0) {
        mostrarNotificacion('Por favor seleccione al menos un nutriente', 'warning');
        return;
    }
    
    // Deshabilitar botón y mostrar loading
    const btnCalcular = document.getElementById('btnCalcularAportes');
    const originalText = btnCalcular.innerHTML;
    btnCalcular.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Calculando...';
    btnCalcular.disabled = true;
    
    // Realizar cálculo (la materia seca se calcula automáticamente en el backend)
    const datos = {
        mezcla_id: mezclaId,
        consumo_animal: consumoAnimal,
        nutrientes_seleccionados: nutrientesSeleccionados
    };
    
    fetch('/api/calcular_aportes_completo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarResultadosAportes(data);
            document.getElementById('btnImprimirAportesMejorado').classList.remove('d-none');
            mostrarNotificacion('Cálculo completado exitosamente', 'success');
        } else {
            mostrarNotificacion(`Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion(`Error: ${error.message}`, 'danger');
    })
    .finally(() => {
        // Restaurar botón
        btnCalcular.innerHTML = originalText;
        btnCalcular.disabled = false;
    });
}

// Mostrar resultados de aportes
function mostrarResultadosAportes(data) {
    const container = document.getElementById('resultadosAportesContainer');
    const content = document.getElementById('resultadosAportesContent');
    
    let html = `
        <div class="alert alert-success">
            <div class="row">
                <div class="col-md-4">
                    <strong>Fórmula:</strong><br>${data.mezcla.nombre}
                </div>
                <div class="col-md-4">
                    <strong>Consumo:</strong><br>${data.consumo_animal} kg/día
                </div>
                <div class="col-md-4">
                    <strong>Nutrientes:</strong><br>${data.total_nutrientes} analizados
                </div>
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table table-bordered table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>Nutriente</th>
                        <th>Unidad Original</th>
                        <th>Cantidad en la Dieta</th>
                        <th>Aporte Total</th>
                        <th>Cálculo</th>
                        <th>Detalle</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.resultados.forEach((resultado, index) => {
        html += `
            <tr>
                <td><strong>${resultado.nutriente_nombre}</strong></td>
                <td>${resultado.unidad_original}</td>
                <td class="text-center">
                    <span class="badge bg-primary">${resultado.cantidad_total_dieta}</span>
                </td>
                <td class="text-center">
                    <span class="badge bg-success">${resultado.aporte_total_final} ${resultado.unidad_final}</span>
                </td>
                <td>
                    <small>
                        ${resultado.calculo_explicacion}
                    </small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-info" type="button" data-bs-toggle="collapse" data-bs-target="#detalle_${index}">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
            <tr class="collapse" id="detalle_${index}">
                <td colspan="6">
                    <div class="p-3 bg-light">
                        <h6>Detalle por Ingrediente - ${resultado.nutriente_nombre}</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-borderless">
                                <thead>
                                    <tr>
                                        <th>Ingrediente</th>
                                        <th>% en Fórmula</th>
                                        <th>Valor BS</th>
                                        <th>Cantidad en Dieta</th>
                                    </tr>
                                </thead>
                                <tbody>
        `;
        
        resultado.detalle_ingredientes.forEach(detalle => {
            html += `
                <tr>
                    <td>${detalle.nombre}</td>
                    <td>${detalle.porcentaje_en_formula}%</td>
                    <td>${detalle.valor_nutricional_bs} ${resultado.unidad_original}</td>
                    <td><strong>${detalle.cantidad_en_dieta} ${resultado.unidad_original}</strong></td>
                </tr>
            `;
        });
        
        html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        
        <div class="alert alert-info mt-3">
            <h6><i class="fas fa-info-circle"></i> Conversiones de Unidades:</h6>
            <p class="mb-0">
                <strong>ppm:</strong> ppm × kg = mg<br>
                <strong>%:</strong> % × kg ÷ 100 = kg<br>
                <strong>Kcal/kg:</strong> Kcal/kg × kg = Kcal<br>
                <small>Los valores utilizados son en Base Seca (BS) para mayor precisión</small>
            </p>
        </div>
    `;
    
    content.innerHTML = html;
    container.classList.remove('d-none');
}

// Imprimir reporte mejorado
function imprimirAportesMejorado() {
    const mezclaId = document.getElementById('selectMezclaAportes').value;
    const consumoAnimal = document.getElementById('consumoAnimalAportes').value;
    
    if (!mezclaId || !consumoAnimal) {
        mostrarNotificacion('Seleccione una fórmula y configure el consumo', 'warning');
        return;
    }
    
    // Obtener nutrientes seleccionados (solo los que tienen check)
    const nutrientesSeleccionados = [];
    document.querySelectorAll('#nutrientesSeleccionContainer input[type="checkbox"]:checked').forEach(checkbox => {
        nutrientesSeleccionados.push(parseInt(checkbox.value));
    });
    
    if (nutrientesSeleccionados.length === 0) {
        mostrarNotificacion('Debe seleccionar al menos un nutriente para imprimir', 'warning');
        return;
    }
    
    // Construir URL con parámetros incluyendo nutrientes seleccionados
    const params = new URLSearchParams({
        mezcla_id: mezclaId,
        consumo_animal: consumoAnimal,
        nutrientes_seleccionados: nutrientesSeleccionados.join(',')
    });
    
    // Abrir nueva ventana para impresión con la ruta mejorada
    const url = `/imprimir_aportes_mejorado?${params.toString()}`;
    window.open(url, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
}

// Función de utilidad para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo) {
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
    }, 4000);
}
