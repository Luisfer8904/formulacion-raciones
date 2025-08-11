// ===== UTILIDADES =====

function imprimirTabla() {
  const nombre = document.getElementById("nombre-mezcla").value || 'Sin nombre';
  const tipo = document.getElementById("tipo-animales").value || 'No especificado';
  const etapa = document.getElementById("etapa-produccion").value || 'No especificado';
  const observaciones = document.getElementById("observaciones").value || 'Sin observaciones';
  const tamanoBachada = parseFloat(document.getElementById("tamano-bachada").value) || 100;
  const totalCosto = document.getElementById("suma-total").textContent || "0.00";
  const sumaInclusion = document.getElementById("suma-inclusion").textContent || "0";
  
  // Obtener fecha actual
  const fechaActual = new Date().toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Recopilar ingredientes
  let ingredientesHTML = '';
  let filaIndex = 1;
  let totalPeso = 0;
  
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombreIngrediente = select?.options[select.selectedIndex]?.text || '';
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0);
    const peso = parseFloat(fila.querySelector('input[name^="peso_bachada_"]')?.value || 0);
    const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0);
    const total = parseFloat(fila.querySelector('input[name^="valor_"]')?.value || 0);
    
    if (select && select.value && inclusion > 0) {
      totalPeso += peso;
      ingredientesHTML += `
        <tr>
          <td>
            <select class="form-select form-select-sm" disabled>
              <option selected>${nombreIngrediente}</option>
            </select>
          </td>
          <td><input type="number" class="form-control form-control-sm" value="${inclusion.toFixed(2)}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="-" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="-" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${peso.toFixed(2)}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${precio.toFixed(2)}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${total.toFixed(2)}" readonly></td>
          <td>
            <div class="btn-action-container">
              <button type="button" class="btn-action btn-action-danger" disabled>
                <i class="fas fa-times"></i>
              </button>
              <button type="button" class="btn-action btn-action-info" disabled>
                <i class="fas fa-info"></i>
              </button>
            </div>
          </td>
        </tr>`;
      filaIndex++;
    }
  });

  // Recopilar nutrientes
  let nutrientesHTML = '';
  let nutrientesCount = 0;
  document.querySelectorAll('#tabla-nutrientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombreNutriente = select?.options[select.selectedIndex]?.text || '';
    const unidad = fila.querySelector('input[name^="unidad_"]')?.value || '';
    const sugerido = fila.querySelector('input[name^="sugerido_"]')?.value || '';
    const minimo = fila.querySelector('input[name^="min_"]')?.value || '';
    const maximo = fila.querySelector('input[name^="max_"]')?.value || '';
    const resultadoTC = fila.querySelector('span[id^="resultado-tc-"]')?.textContent || '0.00';
    const resultadoBS = fila.querySelector('span[id^="resultado-bs-"]')?.textContent || '0.00';
    
    if (select && select.value && nombreNutriente.trim() !== '') {
      nutrientesCount++;
      nutrientesHTML += `
        <tr>
          <td>
            <select class="form-select form-select-sm" disabled>
              <option selected>${nombreNutriente}</option>
            </select>
          </td>
          <td><input type="text" class="form-control form-control-sm" value="${unidad}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${sugerido || ''}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${minimo || ''}" readonly></td>
          <td><input type="number" class="form-control form-control-sm" value="${maximo || ''}" readonly></td>
          <td class="text-end"><span class="badge bg-primary">${resultadoTC}</span></td>
          <td class="text-end"><span class="badge bg-secondary">${resultadoBS}</span></td>
          <td class="text-center">
            <div class="btn-action-container">
              <button type="button" class="btn-action btn-action-danger" disabled>
                <i class="fas fa-times"></i>
              </button>
            </div>
          </td>
        </tr>`;
    }
  });

  const contenidoHTML = `
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Formulación - ${nombre}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @media print {
                @page { margin: 1cm; size: A4; }
                .no-print { display: none !important; }
                body { font-size: 12px; }
            }
            
            body {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .print-header {
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            
            .print-header h2 {
                margin: 0;
                font-weight: 700;
            }
            
            .print-header small {
                opacity: 0.8;
            }
            
            .info-section {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .section-title {
                color: #7CB342;
                font-weight: 700;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #7CB342;
            }
            
            .table {
                margin-bottom: 0;
            }
            
            .table th {
                background: #7CB342;
                color: white;
                border: none;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 0.5px;
            }
            
            .btn-action-container {
                display: flex;
                gap: 4px;
                align-items: center;
                justify-content: center;
            }
            
            .btn-action {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                padding: 0;
                border-radius: 4px;
                font-size: 12px;
                border: 1px solid transparent;
                opacity: 0.6;
            }
            
            .btn-action-danger {
                background-color: #dc3545;
                border-color: #dc3545;
                color: #fff;
            }
            
            .btn-action-info {
                background-color: #17a2b8;
                border-color: #17a2b8;
                color: #fff;
            }
            
            .summary-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .summary-card {
                background: linear-gradient(135deg, #7CB342, #8BC34A);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            
            .summary-card h5 {
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }
            
            .summary-card small {
                opacity: 0.9;
            }
            
            .print-footer {
                margin-top: 30px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
                border-top: 1px solid #dee2e6;
                padding-top: 15px;
            }
            
            .no-print {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn btn-primary" onclick="window.print()">
                <i class="fas fa-print me-2"></i>Imprimir
            </button>
            <button class="btn btn-secondary ms-2" onclick="window.close()">
                <i class="fas fa-times me-2"></i>Cerrar
            </button>
        </div>
        
        <div class="container-fluid py-4">
            <div class="print-header">
                <h2><i class="fas fa-balance-scale me-2"></i>Formulación y Control de Mezclas</h2>
                <small>Generado el ${fechaActual}</small>
            </div>
            
            <div class="info-section">
                <h5 class="section-title"><i class="fas fa-info-circle me-2"></i>Información de la Mezcla</h5>
                <div class="row">
                    <div class="col-md-3">
                        <label class="form-label">Nombre de la Mezcla:</label>
                        <input type="text" class="form-control form-control-sm" value="${nombre}" readonly>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Tipo de Animales:</label>
                        <input type="text" class="form-control form-control-sm" value="${tipo}" readonly>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Etapa de Producción:</label>
                        <input type="text" class="form-control form-control-sm" value="${etapa}" readonly>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Tamaño de Bachada (kg):</label>
                        <input type="number" class="form-control form-control-sm" value="${tamanoBachada}" readonly>
                    </div>
                </div>
                <div class="mt-3">
                    <label class="form-label">Observaciones:</label>
                    <textarea class="form-control form-control-sm" rows="2" readonly>${observaciones}</textarea>
                </div>
            </div>

            <div class="summary-cards">
                <div class="summary-card">
                    <h5>$${totalCosto}</h5>
                    <small>Costo Total</small>
                </div>
                <div class="summary-card">
                    <h5>${sumaInclusion}%</h5>
                    <small>Suma Inclusión</small>
                </div>
                <div class="summary-card">
                    <h5>${filaIndex - 1}</h5>
                    <small>Ingredientes</small>
                </div>
                <div class="summary-card">
                    <h5>${nutrientesCount}</h5>
                    <small>Nutrientes</small>
                </div>
            </div>
            
            <div class="info-section">
                <h5 class="section-title"><i class="fas fa-seedling me-2"></i>Ingredientes Disponibles</h5>
                <div class="table-responsive">
                    <table class="table table-bordered table-sm">
                        <thead>
                            <tr>
                                <th>Ingrediente</th>
                                <th>Inclusión (%)</th>
                                <th>Límite Mín. (%)</th>
                                <th>Límite Máx. (%)</th>
                                <th>Peso en Bachada (kg)</th>
                                <th>Costo Ingrediente ($/kg)</th>
                                <th>Valor Total ($)</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${ingredientesHTML}
                        </tbody>
                    </table>
                </div>
            </div>
            
            ${nutrientesHTML ? `
            <div class="info-section">
                <h5 class="section-title"><i class="fas fa-pills me-2"></i>Nutrientes y Requerimientos</h5>
                <div class="table-responsive">
                    <table class="table table-bordered table-sm">
                        <thead>
                            <tr>
                                <th>Nutriente</th>
                                <th>Unidad</th>
                                <th>Sugerido</th>
                                <th>Mínimo</th>
                                <th>Máximo</th>
                                <th>Resultado TC</th>
                                <th>Resultado BS</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${nutrientesHTML}
                        </tbody>
                    </table>
                </div>
            </div>
            ` : ''}
            
            <div class="print-footer">
                <p><strong>Sistema de Formulación Nutricional</strong></p>
                <p>Documento generado automáticamente - ${fechaActual}</p>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
  `;

  const ventana = window.open('', '_blank', 'width=1200,height=800');
  ventana.document.write(contenidoHTML);
  ventana.document.close();
}

// Función para marcar que hay cambios sin guardar
function marcarCambiosSinGuardar() {
  if (!formularioGuardadoRecientemente) {
    hayCambiosSinGuardar = true;
  }
}

// Función para marcar que se ha guardado
function marcarComoGuardado() {
  hayCambiosSinGuardar = false;
  formularioGuardadoRecientemente = true;
  // Resetear la bandera después de un breve período
  setTimeout(() => {
    formularioGuardadoRecientemente = false;
  }, 1000);
}

// Función para confirmar salida
function confirmarSalida(mensaje = "¿Estás seguro de que deseas salir del formulador? Los cambios no guardados se perderán.") {
  if (hayCambiosSinGuardar) {
    return confirm(mensaje);
  }
  return true;
}

// ===== GESTIÓN DE REQUERIMIENTOS =====

function mostrarSelectorRequerimientos() {
  const modal = new bootstrap.Modal(document.getElementById('selectorRequerimientosModal'));
  
  // Mostrar loading
  document.getElementById('loading-requerimientos').style.display = 'block';
  document.getElementById('lista-requerimientos').innerHTML = '';
  document.getElementById('preview-nutrientes').style.display = 'none';
  document.getElementById('aplicar-requerimientos').disabled = true;
  
  // Cargar requerimientos del usuario
  fetch('/api/requerimientos_usuario')
    .then(response => response.json())
    .then(data => {
      document.getElementById('loading-requerimientos').style.display = 'none';
      
      if (data.error) {
        document.getElementById('lista-requerimientos').innerHTML = `
          <div class="alert alert-warning">
            <strong>No hay requerimientos disponibles</strong><br>
            ${data.error}
          </div>`;
      } else if (Array.isArray(data) && data.length > 0) {
        let html = '<div class="list-group">';
        data.forEach(req => {
          html += `
            <button type="button" class="list-group-item list-group-item-action" onclick="seleccionarRequerimiento(${req.id}, '${req.nombre.replace(/'/g, "\\'")}')">
              <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${req.nombre}</h6>
                <small class="text-muted">${req.tipo_especie || 'Sin especificar'}</small>
              </div>
              <p class="mb-1">${req.comentario || 'Sin comentarios'}</p>
            </button>`;
        });
        html += '</div>';
        document.getElementById('lista-requerimientos').innerHTML = html;
      } else {
        document.getElementById('lista-requerimientos').innerHTML = `
          <div class="alert alert-info">
            <strong>No hay requerimientos disponibles</strong><br>
            Crea primero algunos requerimientos en la sección de Requerimientos.
          </div>`;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('loading-requerimientos').style.display = 'none';
      document.getElementById('lista-requerimientos').innerHTML = `
        <div class="alert alert-danger">Error al cargar requerimientos</div>`;
    });
  
  modal.show();
}

let requerimientoSeleccionado = null;

function seleccionarRequerimiento(id, nombre) {
  requerimientoSeleccionado = { id, nombre };
  
  // Mostrar preview
  fetch(`/api/requerimiento/${id}/nutrientes`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        document.getElementById('preview-nutrientes').style.display = 'none';
        alert('Error al cargar nutrientes del requerimiento: ' + data.error);
        return;
      }
      
      if (!Array.isArray(data) || data.length === 0) {
        document.getElementById('preview-nutrientes-body').innerHTML = `
          <tr>
            <td colspan="3" class="text-center text-muted">Este requerimiento no tiene nutrientes configurados</td>
          </tr>`;
        document.getElementById('preview-nutrientes').style.display = 'block';
        document.getElementById('aplicar-requerimientos').disabled = true;
      } else {
        let html = '';
        data.forEach(nutriente => {
          html += `
            <tr>
              <td>${nutriente.nombre}</td>
              <td>${nutriente.unidad || 'N/A'}</td>
              <td>${nutriente.valor_sugerido || 'N/A'}</td>
            </tr>`;
        });
        
        document.getElementById('preview-nutrientes-body').innerHTML = html;
        document.getElementById('preview-nutrientes').style.display = 'block';
        document.getElementById('aplicar-requerimientos').disabled = false;
      }
      
      // Highlight selected requirement
      document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
      });
      
      // Buscar el elemento que fue clickeado usando el event
      const clickedElement = document.querySelector(`[onclick="seleccionarRequerimiento(${id}, '${nombre.replace(/'/g, "\\'")}')"]`);
      if (clickedElement) {
        clickedElement.classList.add('active');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al cargar los nutrientes');
      document.getElementById('preview-nutrientes').style.display = 'none';
      document.getElementById('aplicar-requerimientos').disabled = true;
    });
}

function aplicarRequerimientosSeleccionados() {
  if (!requerimientoSeleccionado) {
    alert('Selecciona un requerimiento primero');
    return;
  }
  
  // Cargar nutrientes del requerimiento seleccionado
  fetch(`/api/requerimiento/${requerimientoSeleccionado.id}/nutrientes`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert('Error al cargar nutrientes: ' + data.error);
        return;
      }
      
      if (!Array.isArray(data) || data.length === 0) {
        alert('Este requerimiento no tiene nutrientes configurados');
        return;
      }
      
      // Limpiar tabla actual
      const tabla = document.getElementById('tabla-nutrientes');
      tabla.innerHTML = '';
      contadorNutrientes = 0;
      
      // Agregar nutrientes del requerimiento
      data.forEach(nutriente => {
        agregarFilaNutriente();
        const ultimaFila = tabla.lastElementChild;
        const select = ultimaFila.querySelector('select');
        const sugeridoInput = ultimaFila.querySelector(`input[name="sugerido_${contadorNutrientes-1}"]`);
        
        // Seleccionar el nutriente
        select.value = nutriente.nutriente_id;
        
        // Actualizar la unidad y sugerido
        actualizarUnidadSugerido(select, contadorNutrientes-1);
        
        // Sobrescribir el valor sugerido con el del requerimiento
        if (sugeridoInput && nutriente.valor_sugerido) {
          sugeridoInput.value = nutriente.valor_sugerido;
        }
      });
      
      // Agregar una fila vacía al final
      agregarFilaNutriente();
      
      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('selectorRequerimientosModal'));
      modal.hide();
      
      // Recalcular
      if (typeof calcularMinerales === 'function') {
        calcularMinerales();
      }
      
      alert(`✅ Requerimientos "${requerimientoSeleccionado.nombre}" aplicados correctamente`);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al aplicar requerimientos');
    });
}
