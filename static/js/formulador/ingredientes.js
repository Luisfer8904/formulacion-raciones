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
        let html = `<strong>Ingrediente:</strong> ${data.nombre}<br>`;
        if (data.nutrientes && data.nutrientes.length > 0) {
          html += `<table class="table table-sm table-bordered mt-3"><thead><tr><th>Nutriente</th><th>Valor</th><th>Unidad</th></tr></thead><tbody>`;
          data.nutrientes.forEach(n => {
            html += `<tr><td>${n.nombre}</td><td>${n.valor}</td><td>${n.unidad}</td></tr>`;
          });
          html += `</tbody></table>`;
        } else {
          html += `<p class="text-muted">Este ingrediente no tiene nutrientes registrados para tu usuario.</p>`;
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
      <td><input type="number" class="form-control form-control-sm" name="inclusion_${index}" value="${inclusion}" oninput="actualizarValores(this)"></td>
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
        <td><input type="number" class="form-control form-control-sm" name="inclusion_${contadorFilas}" min="0" max="100" step="0.1" oninput="actualizarValores(this)"></td>
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
