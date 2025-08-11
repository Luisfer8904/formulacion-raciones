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
          <td class="text-center">${filaIndex}</td>
          <td>${nombreIngrediente}</td>
          <td class="text-center">${inclusion.toFixed(2)}%</td>
          <td class="text-center">${peso.toFixed(2)} kg</td>
          <td class="text-right">$${precio.toFixed(2)}</td>
          <td class="text-right">$${total.toFixed(2)}</td>
        </tr>`;
      filaIndex++;
    }
  });

  // Recopilar nutrientes
  let nutrientesHTML = '';
  document.querySelectorAll('#tabla-nutrientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombreNutriente = select?.options[select.selectedIndex]?.text || '';
    const unidad = fila.querySelector('input[name^="unidad_"]')?.value || '';
    const minimo = fila.querySelector('input[name^="min_"]')?.value || '';
    const maximo = fila.querySelector('input[name^="max_"]')?.value || '';
    const resultadoTC = fila.querySelector('span[id^="resultado-tc-"]')?.textContent || '0.00';
    const resultadoBS = fila.querySelector('span[id^="resultado-bs-"]')?.textContent || '0.00';
    
    if (select && select.value) {
      nutrientesHTML += `
        <tr>
          <td>${nombreNutriente}</td>
          <td class="text-center">${unidad}</td>
          <td class="text-center">${minimo || '-'}</td>
          <td class="text-center">${maximo || '-'}</td>
          <td class="text-center">${resultadoTC}</td>
          <td class="text-center">${resultadoBS}</td>
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
        <style>
            @media print {
                @page {
                    margin: 1cm;
                    size: A4;
                }
                body { margin: 0; }
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.4;
                color: #333;
                max-width: 210mm;
                margin: 0 auto;
                padding: 20px;
                background: white;
            }
            
            .header {
                text-align: center;
                border-bottom: 3px solid #7CB342;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            
            .logo {
                font-size: 28px;
                font-weight: bold;
                color: #7CB342;
                margin-bottom: 5px;
            }
            
            .subtitle {
                font-size: 16px;
                color: #666;
                margin-bottom: 10px;
            }
            
            .fecha {
                font-size: 12px;
                color: #888;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .info-card {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #7CB342;
            }
            
            .info-card h3 {
                margin: 0 0 10px 0;
                color: #7CB342;
                font-size: 16px;
            }
            
            .info-item {
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .info-label {
                font-weight: 600;
                color: #555;
            }
            
            .section-title {
                font-size: 18px;
                font-weight: bold;
                color: #7CB342;
                margin: 30px 0 15px 0;
                padding-bottom: 5px;
                border-bottom: 2px solid #e9ecef;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                font-size: 12px;
            }
            
            th {
                background: #7CB342;
                color: white;
                padding: 12px 8px;
                text-align: center;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            td {
                padding: 10px 8px;
                border-bottom: 1px solid #e9ecef;
                vertical-align: middle;
            }
            
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            tr:hover {
                background-color: #e8f5e8;
            }
            
            .text-center { text-align: center; }
            .text-right { text-align: right; }
            
            .summary-box {
                background: linear-gradient(135deg, #7CB342, #8BC34A);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }
            
            .summary-item {
                display: inline-block;
                margin: 0 20px;
                font-size: 16px;
            }
            
            .summary-value {
                font-size: 24px;
                font-weight: bold;
                display: block;
            }
            
            .observaciones {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }
            
            .firma-section {
                margin-top: 40px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
            }
            
            .firma-box {
                text-align: center;
                padding-top: 30px;
                border-top: 2px solid #333;
            }
            
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 10px;
                color: #888;
                border-top: 1px solid #e9ecef;
                padding-top: 15px;
            }
            
            @media print {
                .no-print { display: none; }
                body { font-size: 11px; }
                .summary-box { background: #7CB342 !important; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🌾 FeedPro</div>
            <div class="subtitle">Sistema de Formulación Nutricional</div>
            <div class="fecha">Generado el ${fechaActual}</div>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <h3>📋 Información de la Mezcla</h3>
                <div class="info-item">
                    <span class="info-label">Nombre:</span> ${nombre}
                </div>
                <div class="info-item">
                    <span class="info-label">Especie:</span> ${tipo}
                </div>
                <div class="info-item">
                    <span class="info-label">Etapa:</span> ${etapa}
                </div>
            </div>
            
            <div class="info-card">
                <h3>⚖️ Datos de Producción</h3>
                <div class="info-item">
                    <span class="info-label">Tamaño de bachada:</span> ${tamanoBachada} kg
                </div>
                <div class="info-item">
                    <span class="info-label">Peso total:</span> ${totalPeso.toFixed(2)} kg
                </div>
                <div class="info-item">
                    <span class="info-label">Suma inclusión:</span> ${sumaInclusion}%
                </div>
            </div>
        </div>

        <div class="section-title">🥬 Composición de Ingredientes</div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Ingrediente</th>
                    <th>Inclusión (%)</th>
                    <th>Peso (kg)</th>
                    <th>Precio Unitario</th>
                    <th>Valor Total</th>
                </tr>
            </thead>
            <tbody>
                ${ingredientesHTML}
            </tbody>
        </table>

        <div class="summary-box">
            <div class="summary-item">
                <span class="summary-value">$${totalCosto}</span>
                <span>Costo Total</span>
            </div>
            <div class="summary-item">
                <span class="summary-value">${sumaInclusion}%</span>
                <span>Inclusión Total</span>
            </div>
            <div class="summary-item">
                <span class="summary-value">${totalPeso.toFixed(1)} kg</span>
                <span>Peso Total</span>
            </div>
        </div>

        ${nutrientesHTML ? `
        <div class="section-title">🧪 Análisis Nutricional</div>
        <table>
            <thead>
                <tr>
                    <th>Nutriente</th>
                    <th>Unidad</th>
                    <th>Mínimo</th>
                    <th>Máximo</th>
                    <th>Resultado TC</th>
                    <th>Resultado BS</th>
                </tr>
            </thead>
            <tbody>
                ${nutrientesHTML}
            </tbody>
        </table>
        ` : ''}

        ${observaciones !== 'Sin observaciones' ? `
        <div class="observaciones">
            <strong>📝 Observaciones:</strong><br>
            ${observaciones}
        </div>
        ` : ''}

        <div class="firma-section">
            <div class="firma-box">
                <strong>Elaborado por</strong><br>
                <small>Nutricionista</small>
            </div>
            <div class="firma-box">
                <strong>Revisado por</strong><br>
                <small>Supervisor</small>
            </div>
        </div>

        <div class="footer">
            <p>Documento generado por FeedPro - Sistema de Formulación Nutricional</p>
            <p>© ${new Date().getFullYear()} - Todos los derechos reservados</p>
        </div>

        <script>
            window.onload = function() {
                setTimeout(function() {
                    window.print();
                }, 500);
            }
        </script>
    </body>
    </html>
  `;

  const ventana = window.open('', '_blank', 'width=800,height=600');
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
