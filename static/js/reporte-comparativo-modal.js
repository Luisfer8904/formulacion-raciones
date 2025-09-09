// Variables globales para el reporte comparativo
let formulasDisponiblesComparativo = [];
let nutrientesDisponiblesComparativo = [];
let composicionFormula1 = null;
let composicionFormula2 = null;

// Utilidad: notificación segura (usa mostrarNotificacion si existe)
function notifyComparativo(mensaje, tipo = 'info') {
    if (typeof mostrarNotificacion === 'function') {
        mostrarNotificacion(mensaje, tipo);
        return;
    }
    const toast = document.createElement('div');
    toast.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 4000);
}

// Abrir modal del reporte comparativo
function abrirReporteComparativoModal() {
    const modalHtml = `
        <div class="modal fade" id="reporteComparativoModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-balance-scale me-2"></i>Reporte Comparativo de Fórmulas</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row g-3">
                            <!-- Columna izquierda: Selección de fórmulas y composición -->
                            <div class="col-md-6">
                                <h6>1. Seleccionar Fórmulas a Comparar</h6>
                                <div class="mb-3">
                                    <label class="form-label">Fórmula A</label>
                                    <select class="form-select" id="formula1SelectModal" onchange="cargarComposicionModal(1)">
                                        <option value="">-- Seleccione la primera fórmula --</option>
                                    </select>
                                    <div id="infoFormula1Modal" class="formula-info mt-2 d-none">
                                        <small class="text-muted">
                                            <i class="fas fa-info-circle me-1"></i>
                                            <span id="detallesFormula1Modal"></span>
                                        </small>
                                    </div>
                                    <div id="composicionFormula1Container" class="mt-2 border rounded p-2" style="max-height: 200px; overflow-y: auto;">
                                        <div class="text-center text-muted small">
                                            <i class="fas fa-arrow-up"></i>
                                            <div>Seleccione una fórmula para ver su composición</div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label">Fórmula B</label>
                                    <select class="form-select" id="formula2SelectModal" onchange="cargarComposicionModal(2)">
                                        <option value="">-- Seleccione la segunda fórmula --</option>
                                    </select>
                                    <div id="infoFormula2Modal" class="formula-info mt-2 d-none">
                                        <small class="text-muted">
                                            <i class="fas fa-info-circle me-1"></i>
                                            <span id="detallesFormula2Modal"></span>
                                        </small>
                                    </div>
                                    <div id="composicionFormula2Container" class="mt-2 border rounded p-2" style="max-height: 200px; overflow-y: auto;">
                                        <div class="text-center text-muted small">
                                            <i class="fas fa-arrow-up"></i>
                                            <div>Seleccione una fórmula para ver su composición</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Columna derecha: Selección de nutrientes -->
                            <div class="col-md-6">
                                <h6>2. Seleccionar Nutrientes a Comparar</h6>
                                <div class="mb-2 d-flex gap-2">
                                    <button type="button" class="btn btn-outline-primary btn-sm" onclick="seleccionarTodosNutrientesComparativo()">
                                        <i class="fas fa-check-double"></i> Seleccionar Todos
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="deseleccionarTodosNutrientesComparativo()">
                                        <i class="fas fa-times"></i> Deseleccionar Todos
                                    </button>
                                </div>
                                <div id="nutrientesComparativoContainer" style="max-height: 480px; overflow-y: auto; border: 1px solid #dee2e6; padding: 12px; border-radius: 6px;">
                                    <div class="text-center">
                                        <div class="spinner-border spinner-border-sm" role="status">
                                            <span class="visualmente-hidden">Cargando...</span>
                                        </div>
                                        <div class="small mt-2">Cargando nutrientes...</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Resultados -->
                        <div id="resultadosComparativoContainer" class="mt-4 d-none">
                            <hr>
                            <h6>Resultados de la Comparación</h6>
                            <div id="resumenComparativo" class="row g-3 mb-3"></div>
                            <div id="tablaComparativoContainer" class="table-responsive"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" id="btnCompararFormulas" onclick="compararFormulas()">
                            <i class="fas fa-balance-scale me-1"></i>Comparar Fórmulas
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remover modal existente si existe
    const existing = document.getElementById('reporteComparativoModal');
    if (existing) existing.remove();

    // Insertar modal y cargar datos
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    cargarFormulasDisponiblesModal();
    cargarNutrientesDisponiblesModal();

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('reporteComparativoModal'));
    modal.show();
}

// Cargar fórmulas del usuario
function cargarFormulasDisponiblesModal() {
    const select1 = document.getElementById('formula1SelectModal');
    const select2 = document.getElementById('formula2SelectModal');
    [select1, select2].forEach(sel => sel && (sel.disabled = true));

    fetch('/api/obtener_formulas_usuario')
        .then(r => r.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || 'No se pudieron cargar fórmulas');
            formulasDisponiblesComparativo = data.formulas || [];

            // Limpiar opciones (mantener placeholder)
            select1.innerHTML = '<option value="">-- Seleccione la primera fórmula --</option>';
            select2.innerHTML = '<option value="">-- Seleccione la segunda fórmula --</option>';

            formulasDisponiblesComparativo.forEach(f => {
                const label = `${f.nombre} (${(f.num_ingredientes ?? f.total_ingredientes) || 0} ingredientes)${f.tipo_animales ? ' - ' + f.tipo_animales : ''}`;
                const opt1 = new Option(label, f.id);
                const opt2 = new Option(label, f.id);
                select1.add(opt1);
                select2.add(opt2);
            });
        })
        .catch(err => {
            console.error('Error cargando fórmulas:', err);
            notifyComparativo('Error al cargar fórmulas', 'danger');
        })
        .finally(() => {
            [select1, select2].forEach(sel => sel && (sel.disabled = false));
        });
}

// Cargar nutrientes disponibles
function cargarNutrientesDisponiblesModal() {
    const container = document.getElementById('nutrientesComparativoContainer');
    fetch('/api/obtener_nutrientes_disponibles')
        .then(r => r.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || 'No se pudieron cargar nutrientes');
            nutrientesDisponiblesComparativo = data.nutrientes || [];
            let html = '<div class="mb-2"><strong>Seleccione nutrientes:</strong></div>';
            nutrientesDisponiblesComparativo.forEach(n => {
                const id = `nutriente_cmp_${n.id}`;
                // Usamos el NOMBRE como valor, requerido por el backend en /api/comparar_formulas
                html += `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" value="${n.nombre}" id="${id}">
                        <label class="form-check-label" for="${id}">
                            ${n.nombre} ${n.unidad ? '(' + n.unidad + ')' : ''}
                        </label>
                    </div>
                `;
            });
            container.innerHTML = html;
        })
        .catch(err => {
            console.error('Error cargando nutrientes:', err);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle me-1"></i>
                    Error al cargar nutrientes
                </div>
            `;
        });
}

// Cargar composición de una fórmula seleccionada
function cargarComposicionModal(num) {
    const select1 = document.getElementById('formula1SelectModal');
    const select2 = document.getElementById('formula2SelectModal');
    const sel = num === 1 ? select1 : select2;
    const otherSel = num === 1 ? select2 : select1;
    const id = sel.value;

    if (!id) {
        actualizarPanelComposicion(num, null);
        return;
    }

    // Validar que no sean iguales
    if (otherSel && otherSel.value && otherSel.value === id) {
        notifyComparativo('Las fórmulas A y B deben ser diferentes', 'warning');
        sel.value = '';
        actualizarPanelComposicion(num, null);
        return;
    }

    actualizarPanelComposicion(num, { loading: true });

    fetch(`/api/obtener_composicion_formula/${id}`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || 'No se pudo cargar la composición');
            if (num === 1) composicionFormula1 = data; else composicionFormula2 = data;
            actualizarPanelComposicion(num, data);
        })
        .catch(err => {
            console.error('Error composición:', err);
            notifyComparativo('Error al cargar la composición', 'danger');
            actualizarPanelComposicion(num, { error: true });
        });
}

function actualizarPanelComposicion(num, data) {
    const info = document.getElementById(num === 1 ? 'infoFormula1Modal' : 'infoFormula2Modal');
    const infoText = document.getElementById(num === 1 ? 'detallesFormula1Modal' : 'detallesFormula2Modal');
    const cont = document.getElementById(num === 1 ? 'composicionFormula1Container' : 'composicionFormula2Container');

    if (!data) {
        info?.classList.add('d-none');
        cont.innerHTML = `
            <div class="text-center text-muted small">
                <i class="fas fa-arrow-up"></i>
                <div>Seleccione una fórmula para ver su composición</div>
            </div>
        `;
        return;
    }

    if (data.loading) {
        info?.classList.add('d-none');
        cont.innerHTML = `
            <div class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <div class="small mt-2">Calculando composición...</div>
            </div>
        `;
        return;
    }

    if (data.error) {
        info?.classList.add('d-none');
        cont.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="fas fa-times-circle me-1"></i>
                Error al cargar composición
            </div>
        `;
        return;
    }

    // Mostrar info básica
    const numIng = (data.ingredientes || []).length;
    infoText.textContent = `${data.formula?.nombre || 'Fórmula'} • ${numIng} ingrediente${numIng !== 1 ? 's' : ''}`;
    info?.classList.remove('d-none');

    // Mostrar tabla de composición (top 12 nutrientes por valor)
    const entries = Object.entries(data.composicion_nutricional || {});
    // Ordenar descendente por valor y limitar
    entries.sort((a,b) => (b[1]?.valor || 0) - (a[1]?.valor || 0));
    const top = entries.slice(0, 12);

    if (top.length === 0) {
        cont.innerHTML = '<div class="text-muted small">Sin datos de composición para mostrar</div>';
        return;
    }

    let html = `
        <div class="table-responsive">
            <table class="table table-sm table-striped align-middle mb-0">
                <thead>
                    <tr>
                        <th>Nutriente</th>
                        <th class="text-end">Valor</th>
                        <th class="text-center">Unidad</th>
                    </tr>
                </thead>
                <tbody>
    `;
    top.forEach(([nombre, v]) => {
        html += `
            <tr>
                <td>${nombre}</td>
                <td class="text-end">${Number(v.valor || 0).toFixed(4)}</td>
                <td class="text-center">${v.unidad || ''}</td>
            </tr>
        `;
    });
    html += `
                </tbody>
            </table>
        </div>
    `;
    cont.innerHTML = html;
}

// Seleccionar/Deseleccionar nutrientes
function seleccionarTodosNutrientesComparativo() {
    document.querySelectorAll('#nutrientesComparativoContainer input[type="checkbox"]').forEach(cb => cb.checked = true);
}
function deseleccionarTodosNutrientesComparativo() {
    document.querySelectorAll('#nutrientesComparativoContainer input[type="checkbox"]').forEach(cb => cb.checked = false);
}

// Ejecutar comparación
function compararFormulas() {
    const id1 = document.getElementById('formula1SelectModal').value;
    const id2 = document.getElementById('formula2SelectModal').value;
    const btn = document.getElementById('btnCompararFormulas');

    if (!id1 || !id2) {
        notifyComparativo('Seleccione ambas fórmulas', 'warning');
        return;
    }
    if (id1 === id2) {
        notifyComparativo('Las fórmulas A y B deben ser diferentes', 'warning');
        return;
    }

    const nutrientes = Array.from(document.querySelectorAll('#nutrientesComparativoContainer input[type="checkbox"]:checked'))
        .map(cb => cb.value);
    if (nutrientes.length === 0) {
        notifyComparativo('Seleccione al menos un nutriente', 'warning');
        return;
    }

    // Loading en botón
    const original = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Comparando...';
    btn.disabled = true;

    fetch('/api/comparar_formulas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            formula1_id: parseInt(id1),
            formula2_id: parseInt(id2),
            nutrientes_seleccionados: nutrientes
        })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) throw new Error(data.error || 'No se pudo comparar');
        mostrarResultadosComparativo(data.comparacion);
        notifyComparativo('Comparación completada', 'success');
    })
    .catch(err => {
        console.error('Error comparando:', err);
        notifyComparativo(`Error: ${err.message}`, 'danger');
    })
    .finally(() => {
        btn.innerHTML = original;
        btn.disabled = false;
    });
}

function mostrarResultadosComparativo(comparacion) {
    const container = document.getElementById('resultadosComparativoContainer');
    const resumenDiv = document.getElementById('resumenComparativo');
    const tablaDiv = document.getElementById('tablaComparativoContainer');

    // Calcular promedios adicionales
    const diffs = Object.values(comparacion.diferencias || {});
    const promedioAbs = diffs.length ? diffs.reduce((a,b)=>a+Math.abs(b.diferencia_absoluta||0),0)/diffs.length : 0;
    const promedioPct = diffs.length ? diffs.reduce((a,b)=>a+Math.abs(b.diferencia_porcentual||0),0)/diffs.length : 0;

    const res = comparacion.resumen || { nutrientes_comparados: diffs.length, formula1_mejor: 0, formula2_mejor: 0, iguales: 0 };

    resumenDiv.innerHTML = `
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number">${res.nutrientes_comparados}</div>
                <div class="stat-label">Nutrientes comparados</div>
            </div>
        </div>
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number text-primary">${res.formula1_mejor}</div>
                <div class="stat-label">Mejor en Fórmula A</div>
            </div>
        </div>
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number text-success">${res.formula2_mejor}</div>
                <div class="stat-label">Mejor en Fórmula B</div>
            </div>
        </div>
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number text-muted">${res.iguales}</div>
                <div class="stat-label">Prácticamente iguales</div>
            </div>
        </div>
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number">${promedioAbs.toFixed(4)}</div>
                <div class="stat-label">Promedio diferencia absoluta</div>
            </div>
        </div>
        <div class="col-sm-6 col-md-3">
            <div class="stat-card text-center">
                <div class="stat-number">${promedioPct.toFixed(2)}%</div>
                <div class="stat-label">Promedio diferencia porcentual</div>
            </div>
        </div>
    `;

    // Construir tabla comparativa
    const f1 = comparacion.formula1?.formula?.nombre || 'Fórmula A';
    const f2 = comparacion.formula2?.formula?.nombre || 'Fórmula B';

    let html = `
        <table class="table table-bordered table-striped">
            <thead class="table-dark">
                <tr>
                    <th>Nutriente</th>
                    <th class="text-end">${f1}</th>
                    <th class="text-end">${f2}</th>
                    <th class="text-end">Diferencia</th>
                    <th class="text-end">Diferencia %</th>
                    <th class="text-center">Unidad</th>
                </tr>
            </thead>
            <tbody>
    `;

    const keys = Object.keys(comparacion.diferencias || {}).sort((a,b)=>a.localeCompare(b));
    keys.forEach(nom => {
        const d = comparacion.diferencias[nom];
        const v1 = comparacion.formula1?.nutrientes?.[nom]?.valor ?? 0;
        const v2 = comparacion.formula2?.nutrientes?.[nom]?.valor ?? 0;
        const unidad = d.unidad || comparacion.formula1?.nutrientes?.[nom]?.unidad || '';
        const cls = d.diferencia_absoluta > 0 ? 'text-success' : (d.diferencia_absoluta < 0 ? 'text-primary' : 'text-muted');
        html += `
            <tr>
                <td><strong>${nom}</strong></td>
                <td class="text-end">${Number(v1).toFixed(4)}</td>
                <td class="text-end">${Number(v2).toFixed(4)}</td>
                <td class="text-end ${cls}">${Number(d.diferencia_absoluta).toFixed(4)}</td>
                <td class="text-end ${cls}">${Number(d.diferencia_porcentual).toFixed(2)}%</td>
                <td class="text-center">${unidad}</td>
            </tr>
        `;
    });
    html += `</tbody></table>`;
    tablaDiv.innerHTML = html;

    container.classList.remove('d-none');
}

