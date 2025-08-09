// ===== FORMULADOR DE RACIONES - JAVASCRIPT =====
// Archivo corregido para solucionar errores de sintaxis

let contadorFilas = 1;
let contadorRequerimientos = 1;
let contadorNutrientes = 0;
let requerimientoSeleccionado = null;

// ===== CONFIGURACIÓN Y FORMATEO DINÁMICO =====

// Función para obtener el símbolo de moneda
function obtenerSimboloMoneda(moneda) {
  const simbolos = {
    'HNL': 'L',
    'GTQ': 'Q',
    'USD': '$',
    'CRC': '₡'
  };
  return simbolos[moneda] || moneda;
}

// Función para formatear precio con moneda
function formatearPrecio(valor, mostrarSimbolo = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarSimbolo) {
    const simbolo = obtenerSimboloMoneda(window.configUsuario.moneda);
    return `${simbolo} ${valorFormateado}`;
  }
  return valorFormateado;
}

// Función para formatear peso con unidad
function formatearPeso(valor, mostrarUnidad = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarUnidad) {
    return `${valorFormateado} ${window.configUsuario.unidad_medida}`;
  }
  return valorFormateado;
}

// Función para convertir entre unidades de peso
function convertirPeso(valor, unidadOrigen, unidadDestino) {
  if (unidadOrigen === unidadDestino) return valor;
  
  // Conversiones a kg como base
  const aKg = {
    'kg': 1,
    'lb': 0.453592,
    'ton': 1000
  };
  
  // Convertir a kg primero, luego a unidad destino
  const valorEnKg = valor * aKg[unidadOrigen];
  return valorEnKg / aKg[unidadDestino];
}

// Función para actualizar etiquetas dinámicamente
function actualizarEtiquetasDinamicas() {
  if (!window.configUsuario) return;
  
  // Actualizar etiquetas de encabezados de tabla si es necesario
  const headers = document.querySelectorAll('th');
  headers.forEach(header => {
    if (header.textContent.includes('Lps/kg')) {
      header.textContent = header.textContent.replace('Lps/kg', 
        `${window.configUsuario.moneda}/${window.configUsuario.unidad_medida}`);
    }
    if (header.textContent.includes('Lps)')) {
      header.textContent = header.textContent.replace('Lps)', 
        `${window.configUsuario.moneda})`);
    }
    if (header.textContent.includes('(kg)')) {
      header.textContent = header.textContent.replace('(kg)', 
        `(${window.configUsuario.unidad_medida})`);
    }
  });
  
  // Actualizar etiquetas de totales
  const totalLabel = document.querySelector('strong');
  if (totalLabel && totalLabel.textContent.includes('Total de la mezcla (Lps):')) {
    totalLabel.textContent = totalLabel.textContent.replace('(Lps):', 
      `(${window.configUsuario.moneda}):`);
  }
}

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

// ===== CÁLCULOS Y ACTUALIZACIONES =====

function actualizarValores(input) {
  const fila = input.closest("tr");
  const porcentaje = parseFloat(input.value) || 0;
  const tamanoBachada = parseFloat(document.getElementById("tamano-bachada").value) || 0;
  
  // Calcular peso en la unidad configurada
  let peso = tamanoBachada * porcentaje / 100;
  
  // Si la unidad configurada no es kg, convertir el tamaño de bachada
  if (window.configUsuario && window.configUsuario.unidad_medida !== 'kg') {
    // El tamaño de bachada se ingresa en la unidad configurada, mantener el cálculo directo
    peso = peso; // Ya está en la unidad correcta
  }
  
  const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]').value) || 0;
  const valorTotal = precio * peso;

  fila.querySelector('input[name^="peso_bachada_"]').value = formatearPeso(peso, false);
  fila.querySelector('input[name^="valor_"]').value = formatearPrecio(valorTotal, false);

  // Actualizar todos los cálculos automáticamente
  calcularSumaTotal();
  calcularSumaInclusion();
  calcularMinerales();
}

function calcularSumaTotal() {
  let total = 0;
  document.querySelectorAll('input[name^="valor_"]').forEach(input => {
    total += parseFloat(input.value) || 0;
  });
  document.getElementById("suma-total").textContent = formatearPrecio(total, false);
}

function calcularMinerales() {
  // Limpiar todos los resultados
  document.querySelectorAll('[id^="resultado-"]').forEach(span => {
    const unidad = span.textContent.replace(/[0-9.\s\-]+/g, "");
    span.textContent = "0.0000 " + unidad;
  });

  const filas = document.querySelectorAll("#tabla-ingredientes tr");
  const resultados = {};

  filas.forEach(fila => {
    const select = fila.querySelector("select");
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0);
    if (!select?.value || inclusion === 0) return;

    const selectedOption = select.options[select.selectedIndex];
    const ms = parseFloat(selectedOption.getAttribute("data-ms")) || 100;
    const nutrientesJson = selectedOption.getAttribute("data-nutrientes");
    let nutrientes = [];
    if (nutrientesJson) {
      try {
        nutrientes = JSON.parse(nutrientesJson);
      } catch (e) {
        console.error("❌ Error al parsear nutrientes:", e);
      }
    }

    if (Array.isArray(nutrientes)) {
      nutrientes.forEach(n => {
        const valorNutriente = parseFloat(n.valor) || 0;
        if (valorNutriente === 0) return;
        const aporte = (inclusion * ms * valorNutriente) / 10000;
        resultados[n.id] = (resultados[n.id] || 0) + aporte;
      });
    }
  });

  // Actualizar la tabla de resultados antigua
  for (const nutrienteId in resultados) {
    const span = document.getElementById(`resultado-${nutrienteId}`);
    if (span) {
      const unidad = span.textContent.replace(/[0-9.\s\-]+/g, "");
      span.textContent = resultados[nutrienteId].toFixed(4) + " " + unidad;
    }
  }

  // Actualizar la tabla de nutrientes nueva
  const filasNutrientes = document.querySelectorAll('#tabla-nutrientes tr');
  filasNutrientes.forEach((fila) => {
    const select = fila.querySelector('select');
    if (!select) return;

    const nameAttr = select.getAttribute('name') || '';
    const indexMatch = nameAttr.match(/_(\d+)$/);
    if (!indexMatch) return;
    const index = indexMatch[1];

    const idNutriente = select.value;
    const spanResultadoBS = fila.querySelector(`#resultado-bs-${index}`);
    const spanResultadoTC = fila.querySelector(`#resultado-tc-${index}`);

    const valorBS = resultados[idNutriente] || 0;

    // Cálculo corregido para Resultado TC: usar inclusión (%) * valor nutriente / 100 (sin MS)
    let aporteTC = 0;

    document.querySelectorAll('#tabla-ingredientes tr').forEach(f => {
      const sel = f.querySelector('select');
      const inclusionInput = f.querySelector('input[name^="inclusion_"]');
      const inclusionVal = parseFloat(inclusionInput?.value) || 0;

      if (sel && sel.value && inclusionVal > 0) {
        const selectedOption = sel.options[sel.selectedIndex];
        const nutrientesData = selectedOption.getAttribute('data-nutrientes');
        let valorNutriente = 0;

        try {
          const nutrientesList = JSON.parse(nutrientesData);
          const nutrienteEncontrado = nutrientesList.find(n => n.id == idNutriente);
          if (nutrienteEncontrado) valorNutriente = parseFloat(nutrienteEncontrado.valor) || 0;
        } catch (e) {
          console.error("Error parseando nutrientes:", e);
        }

        let aporteParcial = (inclusionVal * valorNutriente) / 100;
        aporteTC += aporteParcial;
      }
    });

    if (spanResultadoTC) spanResultadoTC.textContent = aporteTC.toFixed(4);
    if (spanResultadoBS) spanResultadoBS.textContent = valorBS.toFixed(4);
  });

  calcularSumaTotal();
}

function actualizarValoresBachada() {
  document.querySelectorAll('input[name^="inclusion_"]').forEach(input => {
    actualizarValores(input);
  });
  calcularSumaInclusion();
  calcularMinerales();
}

function calcularSumaInclusion() {
  let suma = 0;
  document.querySelectorAll('input[name^="inclusion_"]').forEach(input => {
    suma += parseFloat(input.value) || 0;
  });
  document.getElementById("suma-inclusion").textContent = suma.toFixed(0);
}

// ===== OPTIMIZACIÓN =====

function optimizarMezcla() {
  // Recopilar ingredientes desde la tabla
  const filas = document.querySelectorAll("#tabla-ingredientes tr");
  let ingredientes = [];

  filas.forEach(fila => {
    const select = fila.querySelector("select");
    if (!select.value) return;
    const selectedOption = select.options[select.selectedIndex];
    const nombre = selectedOption.textContent.trim();
    const limite_min = parseFloat(fila.querySelector('input[name^="min_"]')?.value || 0);
    const limite_max = parseFloat(fila.querySelector('input[name^="max_"]')?.value || 100);
    const costo = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0);
    // Recopilar aportes de nutrientes
    let aporte = {};
    const nutrientesJson = selectedOption.getAttribute("data-nutrientes");
    if (nutrientesJson) {
      try {
        const nutrientes = JSON.parse(nutrientesJson);
        if (Array.isArray(nutrientes)) {
          nutrientes.forEach(n => {
            // Usar nombre de nutriente como clave
            aporte[n.nombre] = parseFloat(n.valor) || 0;
          });
        }
      } catch (e) {
        console.error("❌ Error al parsear nutrientes para", nombre, ":", e);
        console.warn("⚠️ Se asignará estructura vacía de nutrientes para", nombre);
      }
    } else {
      console.warn("⚠️ No se encontraron datos de nutrientes para", nombre);
    }
    
    // Asegurar que aporte tenga al menos una estructura básica
    if (Object.keys(aporte).length === 0) {
      console.warn("⚠️ Ingrediente", nombre, "no tiene nutrientes. Se asignará estructura vacía.");
      // Agregar nutrientes con valor 0 para todos los requerimientos que se van a procesar
      // Esto se hará dinámicamente en el backend, pero aquí aseguramos que aporte no esté vacío
      aporte = {};
    }
    ingredientes.push({
      nombre: nombre,
      limite_min: limite_min,
      limite_max: limite_max,
      costo: costo,
      aporte: aporte
    });
  });

  // Recopilar requerimientos desde la tabla de nutrientes
  const requerimientos = [];
  document.querySelectorAll("#tabla-nutrientes tr").forEach(fila => {
    const select = fila.querySelector("select");
    if (!select || !select.value) return;
    const nombre = select.options[select.selectedIndex].textContent.trim();
    const min = fila.querySelector('input[name^="min_"]')?.value;
    const max = fila.querySelector('input[name^="max_"]')?.value;
    const unidad = fila.querySelector('input[name^="unidad_"]')?.value || "";
    requerimientos.push({
      nombre: nombre,
      min: min !== "" ? parseFloat(min) : null,
      max: max !== "" ? parseFloat(max) : null,
      unidad: unidad
    });
  });

  // Depuración: imprimir datos que se envían al backend
  const data = { ingredientes, requerimientos };
  console.log("🟢 Datos enviados a backend (optimizarMezcla):", data);

  fetch("/optimizar_formulacion", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    console.log("🔍 Respuesta del backend:", data);
    if (!data.resultado) {
      alert(data.error || "No se pudo optimizar la mezcla.");
      return;
    }
    const inclusiones = data.resultado;
    filas.forEach((fila, i) => {
      if (!fila.querySelector("select").value) return;
      fila.querySelector('input[name^="inclusion_"]').value = inclusiones[i].inclusion.toFixed(2);
      actualizarValores(fila.querySelector('input[name^="inclusion_"]'));
    });
    calcularMinerales();
  })
  .catch(error => {
    console.error('Error en optimizarMezcla:', error);
    alert('No se pudo optimizar la mezcla.');
  });
}

// ===== GESTIÓN DE NUTRIENTES =====

function agregarFilaNutriente() {
  const tabla = document.getElementById('tabla-nutrientes');
  const fila = document.createElement('tr');

  // Obtener la lista de nutrientes desde el template
  let opciones = '<option value="">-- Seleccionar --</option>';
  if (typeof window.nutrientesTemplate !== 'undefined' && Array.isArray(window.nutrientesTemplate)) {
    window.nutrientesTemplate.forEach(n => {
      opciones += `<option value="${n.id}" data-unidad="${n.unidad || ''}" data-sugerido="${n.sugerido || 0}">${n.nombre}</option>`;
    });
  }

  fila.innerHTML = `
    <td>
        <select class="form-select form-select-sm" name="nutriente_${contadorNutrientes}" onchange="actualizarUnidadSugerido(this, ${contadorNutrientes}); verificarUltimaFilaNutriente(${contadorNutrientes}); calcularMinerales();">
        ${opciones}
      </select>
    </td>
    <td><input type="text" class="form-control form-control-sm" name="unidad_${contadorNutrientes}" value="" readonly></td>
    <td><input type="number" class="form-control form-control-sm" name="sugerido_${contadorNutrientes}" value="" step="0.0001" readonly></td>
    <td><input type="number" class="form-control form-control-sm" name="min_${contadorNutrientes}" step="0.0001" oninput="calcularMinerales();"></td>
    <td><input type="number" class="form-control form-control-sm" name="max_${contadorNutrientes}" step="0.0001" oninput="calcularMinerales();"></td>
    <td class="text-end"><span id="resultado-tc-${contadorNutrientes}">0.00</span></td>
    <td class="text-end"><span id="resultado-bs-${contadorNutrientes}">0.00</span></td>
    <td class="text-center"><button type="button" class="btn btn-sm btn-danger" onclick="eliminarFilaNutriente(this); calcularMinerales();">✖</button></td>
  `;

  tabla.appendChild(fila);
  contadorNutrientes++;
}

function actualizarUnidadSugerido(select, index) {
  const selectedOption = select.options[select.selectedIndex];
  const unidad = selectedOption.getAttribute('data-unidad') || '';
  const sugerido = selectedOption.getAttribute('data-sugerido') || '';

  // Buscar los inputs en la misma fila que el select para evitar conflictos de ID
  const fila = select.closest('tr');
  const unidadInput = fila.querySelector(`input[name="unidad_${index}"]`);
  const sugeridoInput = fila.querySelector(`input[name="sugerido_${index}"]`);
  
  // Asegurar que los valores se asignen correctamente
  if (unidadInput) {
    unidadInput.value = unidad;
  }
  if (sugeridoInput) {
    sugeridoInput.value = sugerido;
  }
  
  // Asegurarse que verificarUltimaFilaNutriente se llama siempre
  if (typeof verificarUltimaFilaNutriente === "function") {
    verificarUltimaFilaNutriente(index);
  }
}

function eliminarFilaNutriente(boton) {
  const fila = boton.closest('tr');
  fila.remove();
  // Recalcular después de eliminar
  calcularMinerales();
}

function verificarUltimaFilaNutriente(index) {
  const tabla = document.getElementById('tabla-nutrientes');
  const filas = tabla.querySelectorAll('tr');
  const ultimaFila = filas[filas.length - 1];
  const select = ultimaFila.querySelector('select');
  if (select && select.value !== "") {
    agregarFilaNutriente();
  }
}

// ===== FUNCIONES DE PRECARGA =====

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
      opcionesSelect += `<option value="${m.id}" ${selected} 
          data-precio="${m.precio}"
          data-ms="${m.ms}"
          data-nutrientes="${nutrientesData}">
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
          <button type="button" class="btn btn-sm btn-danger" onclick="eliminarFila(this)">✖</button>
          <button type="button" class="btn btn-sm btn-info" onclick="mostrarInfo(this)">ℹ️</button>
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

    fila.innerHTML = `
        <td>
            <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${contadorFilas}" onchange="agregarFila(this)">
                ${opcionesSelect}
            </select>
        </td>
        <td><input type="number" class="form-control form-control-sm" name="inclusion_${contadorFilas}" min="0" max="100" step="0.1" oninput="actualizarValores(this)"></td>
        <td><input type="number" class="form-control form-control-sm" name="min_${contadorFilas}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="max_${contadorFilas}" step="0.0001"></td>
        <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${contadorFilas}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${contadorFilas}" step="0.01" readonly></td>
        <td><input type="number" class="form-control form-control-sm" name="valor_${contadorFilas}" step="0.01" readonly></td>
        <td>
            <button type="button" class="btn btn-sm btn-danger" onclick="eliminarFila(this)">✖</button>
            <button type="button" class="btn btn-sm btn-info" onclick="mostrarInfo(this)">ℹ️</button>
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

// ===== GUARDAR Y CARGAR =====

function guardarMezcla() {
  const nombreMezcla = document.getElementById('nombre-mezcla').value.trim();
  const tipoAnimales = document.getElementById('tipo-animales').value.trim();
  const etapaProduccion = document.getElementById('etapa-produccion').value.trim();
  const observaciones = document.getElementById('observaciones').value.trim();

  if (!nombreMezcla) {
    alert('Por favor ingresa un nombre para la mezcla.');
    return;
  }

  const ingredientes = [];
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    const inclusion = parseFloat(inclusionInput?.value || 0);

    if (select && select.value && inclusion > 0) {
      ingredientes.push({
        ingrediente_id: parseInt(select.value),
        inclusion: inclusion
      });
    }
  });

  // Capturar nutrientes seleccionados de la tabla de nutrientes
  const nutrientesSeleccionados = [];
  document.querySelectorAll('#tabla-nutrientes tr').forEach(row => {
    // Buscar el select de nutriente en la fila
    const select = row.querySelector('select');
    if (select && select.value) {
      nutrientesSeleccionados.push({
        nutriente_id: parseInt(select.value)
      });
    }
  });

  if (ingredientes.length === 0) {
    alert('Agrega al menos un ingrediente antes de guardar.');
    return;
  }

  console.log('Datos a enviar:', {
    nombre: nombreMezcla,
    tipo_animales: tipoAnimales,
    etapa_produccion: etapaProduccion,
    observaciones: observaciones,
    ingredientes: ingredientes,
    nutrientes: nutrientesSeleccionados
  });

  fetch('/guardar_mezcla', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      nombre: nombreMezcla,
      tipo_animales: tipoAnimales,
      etapa_produccion: etapaProduccion,
      observaciones: observaciones,
      ingredientes: ingredientes,
      nutrientes: nutrientesSeleccionados
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor:', data);
    if (data.mensaje) {
      alert(data.mensaje);
      if (!data.error) {
        // Marcar como guardado exitosamente
        marcarComoGuardado();
      }
      // Removed automatic redirection - user stays in formulador
    } else {
      alert('Error al guardar la mezcla.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error al guardar la mezcla.');
  });
}

function guardarComo() {
  const modal = new bootstrap.Modal(document.getElementById('modalGuardarComo'));
  modal.show();
}

function confirmarGuardarComo() {
  const nombreMezcla = document.getElementById('nombre-existente').value.trim() || document.getElementById('nombre-mezcla').value.trim();
  const tipoAnimales = document.getElementById('tipo-animales').value.trim();
  const etapaProduccion = document.getElementById('etapa-produccion').value.trim();
  const observaciones = document.getElementById('observaciones').value.trim();

  if (!nombreMezcla) {
    alert('Por favor ingresa un nombre válido.');
    return;
  }

  const ingredientes = [];
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    const inclusion = parseFloat(inclusionInput?.value || 0);
    if (select && select.value && inclusion > 0) {
      ingredientes.push({
        ingrediente_id: parseInt(select.value),
        inclusion: inclusion
      });
    }
  });

  // Capturar nutrientes seleccionados
  const nutrientesSeleccionados = [];
  document.querySelectorAll('#tabla-nutrientes tr').forEach(row => {
    const select = row.querySelector('select');
    if (select && select.value) {
      nutrientesSeleccionados.push({
        id: parseInt(select.value)
      });
    }
  });

  if (ingredientes.length === 0) {
    alert('Agrega al menos un ingrediente antes de guardar.');
    return;
  }

  console.log('Datos a enviar (Guardar Como):', {
    nombre: nombreMezcla,
    tipo_animales: tipoAnimales,
    etapa_produccion: etapaProduccion,
    observaciones: observaciones,
    ingredientes: ingredientes,
    nutrientes: nutrientesSeleccionados
  });

  fetch('/guardar_mezcla_como', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      nombre: nombreMezcla,
      tipo_animales: tipoAnimales,
      etapa_produccion: etapaProduccion,
      observaciones: observaciones,
      ingredientes: ingredientes,
      nutrientes: nutrientesSeleccionados
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor (Guardar Como):', data);
    if (data.mensaje) {
      alert(data.mensaje);
      if (!data.error) {
        // Marcar como guardado exitosamente
        marcarComoGuardado();
        // Cerrar modal pero no redirigir - user stays in formulador
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalGuardarComo'));
        modal.hide();
      }
    } else {
      alert('Error al guardar la mezcla.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('No se pudo guardar la mezcla.');
  });
}

// ===== UTILIDADES =====

function imprimirTabla() {
  const nombre = document.getElementById("nombre-mezcla").value || '';
  const tipo = document.getElementById("tipo-animales").value || '';
  const etapa = document.getElementById("etapa-produccion").value || '';
  const observaciones = document.getElementById("observaciones").value || '';
  const tamanoBachada = parseFloat(document.getElementById("tamano-bachada").value) || 100;
  const totalCosto = document.getElementById("suma-total").textContent || "0.00";

  let contenido = `
    <h3 style="text-align:center">Resumen de Mezcla</h3>
    <p><strong>Elaborado por:</strong> Luis Fernando Rivera</p>
    <p><strong>Propietario:</strong> _______________________</p>
    <p><strong>Especie:</strong> ${tipo}</p>
    <p><strong>Tipo de Dieta:</strong> ${etapa}</p>
    <p><strong>Nombre Mezcla:</strong> ${nombre}</p>
    <p><strong>Tamaño de la bachada:</strong> ${tamanoBachada} kg</p>
    <table border="1" cellspacing="0" cellpadding="5" width="100%">
      <thead>
        <tr>
          <th>#</th>
          <th>Ingrediente</th>
          <th>Cant. (%)</th>
          <th>Peso (kg)</th>
          <th>Precio Lps/kg</th>
          <th>Precio Total</th>
        </tr>
      </thead>
      <tbody>
  `;

  let filaIndex = 1;
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombre = select?.options[select.selectedIndex]?.text || '';
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0).toFixed(2);
    const peso = parseFloat(fila.querySelector('input[name^="peso_bachada_"]')?.value || 0).toFixed(2);
    const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0).toFixed(2);
    const total = parseFloat(fila.querySelector('input[name^="valor_"]')?.value || 0).toFixed(2);
    if (select && select.value) {
      contenido += `<tr>
        <td>${filaIndex}</td>
        <td>${nombre}</td>
        <td>${inclusion}</td>
        <td>${peso}</td>
        <td>${precio}</td>
        <td>${total}</td>
      </tr>`;
      filaIndex++;
    }
  });

  contenido += `
      </tbody>
    </table>
    <p><strong>Total Lps: </strong>${totalCosto}</p>
    <br>
    <p><strong>Observaciones:</strong> ${observaciones}</p>
    <br><br>
    <p>___________________________<br>Firma del Elaborado</p>
  `;

  const ventana = window.open('', '_blank');
  ventana.document.write('<html><head><title>Impresión de Mezcla</title></head><body>');
  ventana.document.write(contenido);
  ventana.document.write('</body></html>');
  ventana.document.close();
  ventana.print();
}

// ===== EVENTOS Y INICIALIZACIÓN =====

// Variable para rastrear si hay cambios sin guardar
let hayCambiosSinGuardar = false;
let formularioGuardadoRecientemente = false;
let navegacionInternaEnProceso = false;

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

// Interceptar clics en enlaces de navegación
function interceptarNavegacion() {
  // Interceptar enlaces del menú lateral y otros enlaces de navegación
  const selectoresEnlaces = [
    '.sidebar .nav-link',  // Enlaces del menú lateral
    'a[href*="panel"]',    // Enlaces al panel
    'a[href*="ingredientes"]', // Enlaces a ingredientes
    'a[href*="nutrientes"]',   // Enlaces a nutrientes
    'a[href*="requerimientos"]', // Enlaces a requerimientos
    'a[href*="mezclas"]',      // Enlaces a mezclas
    'a[href*="opciones"]',     // Enlaces a opciones
    'a[href*="logout"]'        // Enlaces de logout
  ];
  
  selectoresEnlaces.forEach(selector => {
    document.addEventListener('click', function(e) {
      const enlace = e.target.closest(selector);
      if (!enlace) return;
      
      const href = enlace.getAttribute('href') || '';
      
      // No interceptar si es el formulador actual o enlaces vacíos
      if (href === '' || 
          href === '#' || 
          href.includes('formulacion_minerales') ||
          href.includes('panelformulador') ||
          href.startsWith('javascript:')) {
        return;
      }
      
      // Solo interceptar si hay cambios sin guardar
      if (hayCambiosSinGuardar) {
        navegacionInternaEnProceso = true;
        
        let mensaje = "¿Estás seguro de que deseas salir del formulador? Los cambios no guardados se perderán.";
        
        // Mensaje específico para logout
        if (href.includes('logout')) {
          mensaje = "¿Estás seguro de que deseas cerrar sesión? Los cambios no guardados en el formulador se perderán.";
        }
        
        if (!confirmarSalida(mensaje)) {
          navegacionInternaEnProceso = false;
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
        
        // Si el usuario confirmó, permitir la navegación y resetear la bandera
        navegacionInternaEnProceso = false;
      }
    }, true); // Usar capture para interceptar antes que otros handlers
  });
}

// Interceptar el evento beforeunload solo para navegación del navegador (cerrar pestaña, etc.)
window.addEventListener('beforeunload', function(e) {
  if (hayCambiosSinGuardar && !navegacionInternaEnProceso) {
    // Solo establecer returnValue para mostrar el diálogo nativo del navegador
    // No usar confirm() aquí para evitar doble confirmación
    e.returnValue = '';
    return '';
  }
});

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
  // Precargar ingredientes si existen
  precargarIngredientes();
  
  // Agregar una fila inicial de nutriente si no hay ninguna
  if (document.querySelectorAll('#tabla-nutrientes tr').length === 0) {
    agregarFilaNutriente();
  }
  
  // Configurar interceptores de navegación
  interceptarNavegacion();
  
  // Agregar event listeners para detectar cambios en el formulario
  const formulario = document.body;
  
  // Detectar cambios en inputs
  formulario.addEventListener('input', function(e) {
    if (e.target.matches('input, select, textarea')) {
      marcarCambiosSinGuardar();
    }
  });
  
  // Detectar cambios específicos en selects
  formulario.addEventListener('change', function(e) {
    if (e.target.matches('select')) {
      marcarCambiosSinGuardar();
    }
  });
  
  // Observar cambios dinámicos en las tablas
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList' && 
          (mutation.target.id === 'tabla-ingredientes' || 
           mutation.target.id === 'tabla-nutrientes')) {
        marcarCambiosSinGuardar();
      }
    });
  });
  
  // Observar las tablas principales
  const tablaIngredientes = document.getElementById('tabla-ingredientes');
  const tablaNutrientes = document.getElementById('tabla-nutrientes');
  
  if (tablaIngredientes) {
    observer.observe(tablaIngredientes, { childList: true, subtree: true });
  }
  
  if (tablaNutrientes) {
    observer.observe(tablaNutrientes, { childList: true, subtree: true });
  }
});
