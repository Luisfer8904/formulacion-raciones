// ===== GESTIÓN DE INGREDIENTES =====

function agregarFila(select) {
  if (select.value === "") return;

  // Duplicado: Prevenir ingredientes repetidos
  const selectedIngredientId = select.value;
  const tabla = document.getElementById("tabla-ingredientes");
  const existingSelects = tabla.querySelectorAll('.select-ingrediente');
  let duplicateFound = false;

  existingSelects.forEach(existingSelect => {
    if (existingSelect !== select && existingSelect.value === selectedIngredientId) {
      duplicateFound = true;
    }
  });

  if (duplicateFound) {
    alert('Este ingrediente ya ha sido agregado.');
    select.selectedIndex = 0;
    return;
  }

  const selectedOption = select.options[select.selectedIndex];
  const precio = selectedOption.getAttribute("data-precio");
  const fila = select.closest("tr");
  const inputPrecio = fila.querySelector('input[name^="costo_ingrediente_"]');
  if (inputPrecio && precio) inputPrecio.value = precio;

  select.onchange = null;

  const nuevaFila = fila.cloneNode(true);

  // Copiar las opciones del select original al nuevo select
  const selectOriginal = document.querySelector('.select-ingrediente');
  const selectNuevo = nuevaFila.querySelector('.select-ingrediente');
  selectNuevo.innerHTML = selectOriginal.innerHTML;

  nuevaFila.querySelectorAll("input, select").forEach(el => {
    const nuevoNombre = el.name.replace(/\d+$/, contadorFilas);
    el.name = nuevoNombre;
    if (el.tagName === "SELECT") {
      el.selectedIndex = 0;
      el.onchange = function() { agregarFila(this); };
    } else {
      el.value = "";
    }
    if (el.name.startsWith("peso_bachada_") || el.name.startsWith("valor_") || el.name.startsWith("costo_ingrediente_")) {
      el.readOnly = true;
    }
    if (el.name.startsWith("inclusion_")) {
      el.oninput = function() { actualizarValores(this); };
    }
  });

  tabla.appendChild(nuevaFila);
  contadorFilas++;
}

function eliminarFila(boton) {
  const fila = boton.closest("tr");
  const tabla = document.getElementById("tabla-ingredientes");
  if (tabla.rows.length > 1) {
    tabla.removeChild(fila);
    // Recalcular después de eliminar
    calcularSumaInclusion();
    calcularMinerales();
    calcularSumaTotal();
  }
}

function mostrarInfo(boton) {
  const fila = boton.closest("tr");
  const select = fila.querySelector("select");
  const ingredienteId = select.value;

  if (!ingredienteId) {
    alert("Selecciona un ingrediente primero.");
    return;
  }

  fetch(`/api/ingrediente/${ingredienteId}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        document.getElementById("contenidoInfoIngrediente").innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
      } else {
        let html = `
          <div class="row">
            <div class="col-md-6">
              <h5 class="text-success"><i class="fas fa-seedling me-2"></i>Información General</h5>
              <table class="table table-sm">
                <tr><td><strong>Nombre:</strong></td><td>${data.nombre}</td></tr>
                <tr><td><strong>Tipo:</strong></td><td>${data.tipo || 'No especificado'}</td></tr>
                <tr><td><strong>Materia Seca:</strong></td><td>${data.ms || 100}%</td></tr>
                <tr><td><strong>Precio:</strong></td><td>${data.precio || 0}</td></tr>
              </table>
            </div>
            <div class="col-md-6">
              <h5 class="text-primary"><i class="fas fa-chart-bar me-2"></i>Composición Básica</h5>
              <div id="composicion-basica">
                <!-- Se llenará con los nutrientes básicos -->
              </div>
            </div>
          </div>
        `;
        
        if (data.nutrientes && data.nutrientes.length > 0) {
          // Categorizar nutrientes
          const categorias = {
            'Energía': [],
            'Proteína': [],
            'Minerales': [],
            'Aminoácidos': [],
            'Vitaminas': [],
            'Otros': []
          };
          
          data.nutrientes.forEach(n => {
            const nombre = n.nombre.toLowerCase();
            if (nombre.includes('energía') || nombre.includes('energia') || nombre.includes('em') || nombre.includes('ed')) {
              categorias['Energía'].push(n);
            } else if (nombre.includes('proteína') || nombre.includes('proteina') || nombre.includes('pc') || nombre.includes('pb')) {
              categorias['Proteína'].push(n);
            } else if (nombre.includes('calcio') || nombre.includes('fósforo') || nombre.includes('fosforo') || 
                      nombre.includes('sodio') || nombre.includes('potasio') || nombre.includes('magnesio') ||
                      nombre.includes('hierro') || nombre.includes('zinc') || nombre.includes('cobre') ||
                      nombre.includes('manganeso') || nombre.includes('selenio') || nombre.includes('yodo')) {
              categorias['Minerales'].push(n);
            } else if (nombre.includes('lisina') || nombre.includes('metionina') || nombre.includes('treonina') ||
                      nombre.includes('triptófano') || nombre.includes('triptofano') || nombre.includes('arginina') ||
                      nombre.includes('histidina') || nombre.includes('isoleucina') || nombre.includes('leucina') ||
                      nombre.includes('fenilalanina') || nombre.includes('valina') || nombre.includes('cistina')) {
              categorias['Aminoácidos'].push(n);
            } else if (nombre.includes('vitamina') || nombre.includes('retinol') || nombre.includes('tocoferol') ||
                      nombre.includes('tiamina') || nombre.includes('riboflavina') || nombre.includes('niacina') ||
                      nombre.includes('ácido fólico') || nombre.includes('acido folico') || nombre.includes('biotina') ||
                      nombre.includes('colina') || nombre.includes('caroteno')) {
              categorias['Vitaminas'].push(n);
            } else {
              categorias['Otros'].push(n);
            }
          });
          
          // Mostrar composición básica (Energía y Proteína)
          let composicionBasica = '';
          if (categorias['Energía'].length > 0 || categorias['Proteína'].length > 0) {
            composicionBasica += '<table class="table table-sm">';
            [...categorias['Energía'], ...categorias['Proteína']].forEach(n => {
              composicionBasica += `<tr><td><strong>${n.nombre}:</strong></td><td>${n.valor} ${n.unidad}</td></tr>`;
            });
            composicionBasica += '</table>';
          } else {
            composicionBasica = '<p class="text-muted">No hay información básica disponible</p>';
          }
          
          html += `<div class="mt-4">`;
          
          // Mostrar cada categoría con nutrientes
          Object.keys(categorias).forEach(categoria => {
            if (categorias[categoria].length > 0) {
              const iconos = {
                'Energía': 'fas fa-bolt text-warning',
                'Proteína': 'fas fa-dna text-info', 
                'Minerales': 'fas fa-gem text-primary',
                'Aminoácidos': 'fas fa-link text-success',
                'Vitaminas': 'fas fa-pills text-danger',
                'Otros': 'fas fa-list text-secondary'
              };
              
              html += `
                <div class="mb-3">
                  <h6 class="text-${categoria === 'Minerales' ? 'primary' : categoria === 'Aminoácidos' ? 'success' : categoria === 'Vitaminas' ? 'danger' : 'secondary'}">
                    <i class="${iconos[categoria]} me-2"></i>${categoria}
                  </h6>
                  <div class="table-responsive">
                    <table class="table table-sm table-bordered">
                      <thead class="table-light">
                        <tr><th>Nutriente</th><th>Valor</th><th>Unidad</th></tr>
                      </thead>
                      <tbody>`;
              
              categorias[categoria].forEach(n => {
                const valor = parseFloat(n.valor) || 0;
                const valorFormateado = valor > 0 ? valor.toFixed(4) : '0.0000';
                const claseValor = valor > 0 ? 'text-success fw-bold' : 'text-muted';
                html += `<tr><td>${n.nombre}</td><td class="${claseValor}">${valorFormateado}</td><td>${n.unidad}</td></tr>`;
              });
              
              html += `
                      </tbody>
                    </table>
                  </div>
                </div>`;
            }
          });
          
          html += `</div>`;
          
          // Actualizar composición básica
          setTimeout(() => {
            const composicionDiv = document.getElementById('composicion-basica');
            if (composicionDiv) {
              composicionDiv.innerHTML = composicionBasica;
            }
          }, 100);
          
        } else {
          html += `<div class="alert alert-info mt-3">
            <i class="fas fa-info-circle me-2"></i>
            Este ingrediente no tiene nutrientes registrados para tu usuario.
          </div>`;
        }
        
        document.getElementById("contenidoInfoIngrediente").innerHTML = html;
      }

      const modal = new bootstrap.Modal(document.getElementById('infoIngredienteModal'));
      modal.show();
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById("contenidoInfoIngrediente").innerHTML = `<div class="alert alert-danger">Error al obtener la información.</div>`;
      const modal = new bootstrap.Modal(document.getElementById('infoIngredienteModal'));
      modal.show();
    });
}

// Función para agregar fila desde datos precargados
function agregarFilaDesdeDatos(ing, index) {
  const tabla = document.getElementById('tabla-ingredientes');
  const fila = document.createElement('tr');

  const tamanoBachada = parseFloat(document.getElementById('tamano-bachada').value) || 100;
  const inclusion = typeof ing.inclusion !== "undefined" ? ing.inclusion : 0;
  const pesoBachada = (inclusion * tamanoBachada) / 100;

  // Buscar el ingrediente en los minerales disponibles
  const ingrediente = typeof window.mineralesTemplate !== 'undefined' ? 
    window.mineralesTemplate.find(i => i.id === ing.ingrediente_id) : null;
  const precioIngrediente = ingrediente ? ingrediente.precio : (ing.precio || 0);
  const valorTotal = pesoBachada * precioIngrediente;

  let opcionesSelect = `<option value="">-- Seleccionar --</option>`;
  if (typeof window.mineralesTemplate !== 'undefined') {
    window.mineralesTemplate.forEach(m => {
      const selected = m.id === ing.ingrediente_id ? 'selected' : '';
      const nutrientesData = JSON.stringify(m.nutrientes);
      let nutrientesAttr = '';
      // Agregar atributos data-id-{nutriente_id} para cada nutriente
      if (m.nutrientes && Array.isArray(m.nutrientes)) {
        m.nutrientes.forEach(n => {
          nutrientesAttr += ` data-id-${n.id}="${n.valor}"`;
        });
      }
      opcionesSelect += `<option value="${m.id}" ${selected} 
          data-precio="${m.precio}"
          data-ms="${m.ms}"
          ${nutrientesAttr}
          data-nutrientes='${nutrientesData}'>
          ${m.nombre}
      </option>`;
    });
  }

  fila.innerHTML = `
      <td>
          <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${index}" onchange="agregarFila(this)">
              ${opcionesSelect}
          </select>
      </td>
      <td><input type="number" class="form-control form-control-sm" name="inclusion_${index}" value="${formatearInclusion(inclusion)}" step="0.0001" oninput="actualizarValores(this)"></td>
      <td><input type="number" class="form-control form-control-sm" name="min_${index}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="max_${index}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${index}" value="${formatearPeso(pesoBachada, false)}" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${index}" value="${formatearPrecio(precioIngrediente, false)}" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="valor_${index}" value="${formatearPrecio(valorTotal, false)}" readonly></td>
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

  tabla.appendChild(fila);
}

// Función para precargar ingredientes cuando se carga una mezcla
function precargarIngredientes() {
  if (typeof window.ingredientesPrecargados !== 'undefined' && Array.isArray(window.ingredientesPrecargados) && window.ingredientesPrecargados.length > 0) {
    console.log("🔄 Precargando ingredientes:", window.ingredientesPrecargados);
    
    // Limpiar tabla actual
    const tabla = document.getElementById('tabla-ingredientes');
    tabla.innerHTML = '';
    contadorFilas = 0;
    
    // Agregar ingredientes precargados
    window.ingredientesPrecargados.forEach((ing, index) => {
      agregarFilaDesdeDatos(ing, index);
      contadorFilas++;
    });
    
    // Agregar una fila vacía al final
    const fila = document.createElement('tr');
    let opcionesSelect = `<option value="">-- Seleccionar --</option>`;
    if (typeof window.mineralesTemplate !== 'undefined') {
      window.mineralesTemplate.forEach(m => {
        const nutrientesData = JSON.stringify(m.nutrientes);
        opcionesSelect += `<option value="${m.id}" 
            data-precio="${m.precio}"
            data-ms="${m.ms}"
            data-nutrientes="${nutrientesData}">
            ${m.nombre}
        </option>`;
      });
    }

    let opcionesSelectVacia = `<option value="">-- Seleccionar --</option>`;
    if (typeof window.mineralesTemplate !== 'undefined') {
      window.mineralesTemplate.forEach(m => {
        const nutrientesData = JSON.stringify(m.nutrientes);
        let nutrientesAttr = '';
        // Agregar atributos data-id-{nutriente_id} para cada nutriente
        if (m.nutrientes && Array.isArray(m.nutrientes)) {
          m.nutrientes.forEach(n => {
            nutrientesAttr += ` data-id-${n.id}="${n.valor}"`;
          });
        }
        opcionesSelectVacia += `<option value="${m.id}" 
            data-precio="${m.precio}"
            data-ms="${m.ms}"
            ${nutrientesAttr}
            data-nutrientes='${nutrientesData}'>
            ${m.nombre}
        </option>`;
      });
    }

    fila.innerHTML = `
        <td>
            <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${contadorFilas}" onchange="agregarFila(this)">
                ${opcionesSelectVacia}
            </select>
        </td>
        <td><input type="number" class="form-control form-control-sm" name="inclusion_${contadorFilas}" min="0" max="100" step="0.0001" oninput="actualizarValores(this)"></td>
        <td><input type="number" class="form-control form-control-sm" name="min_${contadorFilas}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="max_${contadorFilas}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${contadorFilas}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${contadorFilas}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="valor_${contadorFilas}" step="0.01" readonly></td>
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
    
    tabla.appendChild(fila);
    contadorFilas++;
    
    // Recalcular todos los valores después de cargar
    setTimeout(() => {
      actualizarValoresBachada();
      calcularMinerales();
      calcularSumaInclusion();
      calcularSumaTotal();
    }, 300);
  }
}
