// ===== FORMULADOR DE RACIONES - JAVASCRIPT OPTIMIZADO =====
// Versión optimizada para mejorar rendimiento

// ===== CACHE DE ELEMENTOS DOM =====
const DOMCache = {
  elements: {},
  
  get(selector) {
    if (!this.elements[selector]) {
      this.elements[selector] = document.querySelector(selector);
    }
    return this.elements[selector];
  },
  
  getAll(selector) {
    // Para querySelectorAll, no cacheamos ya que puede cambiar dinámicamente
    return document.querySelectorAll(selector);
  },
  
  clear() {
    this.elements = {};
  }
};

// ===== UTILIDADES DE DEBOUNCING =====
const DebounceUtils = {
  timers: {},
  
  debounce(func, delay, key = 'default') {
    clearTimeout(this.timers[key]);
    this.timers[key] = setTimeout(func, delay);
  },
  
  throttle(func, delay, key = 'default') {
    if (!this.timers[key]) {
      this.timers[key] = true;
      func();
      setTimeout(() => {
        this.timers[key] = false;
      }, delay);
    }
  }
};

// ===== VARIABLES GLOBALES =====
let contadorFilas = 1;
let contadorRequerimientos = 1;
let contadorNutrientes = 0;
let requerimientoSeleccionado = null;

// Variables para optimización
let calculosEnProceso = false;
let batchUpdatePending = false;

// ===== CONFIGURACIÓN Y FORMATEO DINÁMICO =====

function obtenerSimboloMoneda(moneda) {
  const simbolos = {
    'HNL': 'L',
    'GTQ': 'Q',
    'USD': '$',
    'CRC': '₡'
  };
  return simbolos[moneda] || moneda;
}

function formatearPrecio(valor, mostrarSimbolo = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarSimbolo) {
    const simbolo = obtenerSimboloMoneda(window.configUsuario.moneda);
    return `${simbolo} ${valorFormateado}`;
  }
  return valorFormateado;
}

function formatearPeso(valor, mostrarUnidad = true) {
  if (!window.configUsuario) return valor.toFixed(2);
  
  const valorFormateado = parseFloat(valor).toFixed(2);
  if (mostrarUnidad) {
    return `${valorFormateado} ${window.configUsuario.unidad_medida}`;
  }
  return valorFormateado;
}

function convertirPeso(valor, unidadOrigen, unidadDestino) {
  if (unidadOrigen === unidadDestino) return valor;
  
  const aKg = {
    'kg': 1,
    'lb': 0.453592,
    'ton': 1000
  };
  
  const valorEnKg = valor * aKg[unidadOrigen];
  return valorEnKg / aKg[unidadDestino];
}

function actualizarEtiquetasDinamicas() {
  if (!window.configUsuario) return;
  
  const headers = DOMCache.getAll('th');
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
  
  const totalLabel = DOMCache.get('strong');
  if (totalLabel && totalLabel.textContent.includes('Total de la mezcla (Lps):')) {
    totalLabel.textContent = totalLabel.textContent.replace('(Lps):', 
      `(${window.configUsuario.moneda}):`);
  }
}

// ===== GESTIÓN DE INGREDIENTES OPTIMIZADA =====

function agregarFila(select) {
  if (select.value === "") return;

  const selectedIngredientId = select.value;
  const tabla = DOMCache.get("#tabla-ingredientes");
  const existingSelects = tabla.querySelectorAll('.select-ingrediente');
  
  // Optimización: usar Array.from y some() en lugar de forEach con flag
  const duplicateFound = Array.from(existingSelects).some(existingSelect => 
    existingSelect !== select && existingSelect.value === selectedIngredientId
  );

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
  const selectOriginal = DOMCache.get('.select-ingrediente');
  const selectNuevo = nuevaFila.querySelector('.select-ingrediente');
  selectNuevo.innerHTML = selectOriginal.innerHTML;

  // Optimización: usar un solo loop para todos los elementos
  const elementos = nuevaFila.querySelectorAll("input, select");
  elementos.forEach(el => {
    const nuevoNombre = el.name.replace(/\d+$/, contadorFilas);
    el.name = nuevoNombre;
    
    if (el.tagName === "SELECT") {
      el.selectedIndex = 0;
      el.onchange = function() { agregarFila(this); };
    } else {
      el.value = "";
    }
    
    // Optimización: usar startsWith una sola vez
    const nombreInicia = el.name.split('_')[0];
    if (['peso', 'valor', 'costo'].includes(nombreInicia)) {
      el.readOnly = true;
    }
    
    if (nombreInicia === 'inclusion') {
      el.oninput = function() { 
        DebounceUtils.debounce(() => actualizarValores(this), 300, 'inclusion_' + contadorFilas);
      };
    }
  });

  tabla.appendChild(nuevaFila);
  contadorFilas++;
}

function eliminarFila(boton) {
  const fila = boton.closest("tr");
  const tabla = DOMCache.get("#tabla-ingredientes");
  if (tabla.rows.length > 1) {
    tabla.removeChild(fila);
    // Usar debounce para recálculos después de eliminar
    DebounceUtils.debounce(() => {
      batchCalculateAll();
    }, 200, 'eliminar_fila');
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
      const contenidoDiv = DOMCache.get("#contenidoInfoIngrediente");
      if (data.error) {
        contenidoDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
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
        contenidoDiv.innerHTML = html;
      }

      const modal = new bootstrap.Modal(DOMCache.get('#infoIngredienteModal'));
      modal.show();
    })
    .catch(error => {
      console.error('Error:', error);
      DOMCache.get("#contenidoInfoIngrediente").innerHTML = `<div class="alert alert-danger">Error al obtener la información.</div>`;
      const modal = new bootstrap.Modal(DOMCache.get('#infoIngredienteModal'));
      modal.show();
    });
}

// ===== CÁLCULOS OPTIMIZADOS =====

function actualizarValores(input) {
  if (calculosEnProceso) return;
  
  const fila = input.closest("tr");
  const porcentaje = parseFloat(input.value) || 0;
  const tamanoBachada = parseFloat(DOMCache.get("#tamano-bachada").value) || 0;
  
  let peso = tamanoBachada * porcentaje / 100;
  
  if (window.configUsuario && window.configUsuario.unidad_medida !== 'kg') {
    peso = peso;
  }
  
  const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]').value) || 0;
  const valorTotal = precio * peso;

  // Batch DOM updates
  requestAnimationFrame(() => {
    fila.querySelector('input[name^="peso_bachada_"]').value = formatearPeso(peso, false);
    fila.querySelector('input[name^="valor_"]').value = formatearPrecio(valorTotal, false);
    
    // Debounce los cálculos pesados
    DebounceUtils.debounce(() => {
      batchCalculateAll();
    }, 300, 'actualizar_valores');
  });
}

// Función optimizada para cálculos en lote
function batchCalculateAll() {
  if (batchUpdatePending) return;
  
  batchUpdatePending = true;
  requestAnimationFrame(() => {
    calculosEnProceso = true;
    
    try {
      calcularSumaTotal();
      calcularSumaInclusion();
      calcularMineralesOptimizado();
    } finally {
      calculosEnProceso = false;
      batchUpdatePending = false;
    }
  });
}

function calcularSumaTotal() {
  const inputs = DOMCache.getAll('input[name^="valor_"]');
  let total = 0;
  
  // Optimización: usar for loop en lugar de forEach para mejor rendimiento
  for (let i = 0; i < inputs.length; i++) {
    total += parseFloat(inputs[i].value) || 0;
  }
  
  DOMCache.get("#suma-total").textContent = formatearPrecio(total, false);
}

// Versión optimizada de calcularMinerales
function calcularMineralesOptimizado() {
  // Limpiar resultados de forma más eficiente
  const resultadoSpans = DOMCache.getAll('[id^="resultado-"]');
  for (let i = 0; i < resultadoSpans.length; i++) {
    const span = resultadoSpans[i];
    const unidad = span.textContent.replace(/[0-9.\s\-]+/g, "");
    span.textContent = "0.0000 " + unidad;
  }

  const filas = DOMCache.getAll("#tabla-ingredientes tr");
  const resultados = {};
  
  // Cache de elementos DOM para evitar búsquedas repetitivas
  const filasData = [];
  for (let i = 0; i < filas.length; i++) {
    const fila = filas[i];
    const select = fila.querySelector("select");
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    
    if (select && select.value && inclusionInput) {
      const inclusion = parseFloat(inclusionInput.value) || 0;
      if (inclusion > 0) {
        const selectedOption = select.options[select.selectedIndex];
        filasData.push({
          inclusion,
          ms: parseFloat(selectedOption.getAttribute("data-ms")) || 100,
          nutrientesJson: selectedOption.getAttribute("data-nutrientes")
        });
      }
    }
  }

  // Procesar datos cacheados
  filasData.forEach(data => {
    if (!data.nutrientesJson) return;
    
    try {
      const nutrientes = JSON.parse(data.nutrientesJson);
      if (Array.isArray(nutrientes)) {
        nutrientes.forEach(n => {
          const valorNutriente = parseFloat(n.valor) || 0;
          if (valorNutriente !== 0) {
            const aporte = (data.inclusion * data.ms * valorNutriente) / 10000;
            resultados[n.id] = (resultados[n.id] || 0) + aporte;
          }
        });
      }
    } catch (e) {
      console.error("❌ Error al parsear nutrientes:", e);
    }
  });

  // Actualizar resultados en lote
  const updates = [];
  for (const nutrienteId in resultados) {
    const span = document.getElementById(`resultado-${nutrienteId}`);
    if (span) {
      const unidad = span.textContent.replace(/[0-9.\s\-]+/g, "");
      updates.push({
        element: span,
        content: resultados[nutrienteId].toFixed(4) + " " + unidad
      });
    }
  }
  
  // Aplicar actualizaciones en un solo frame
  requestAnimationFrame(() => {
    updates.forEach(update => {
      update.element.textContent = update.content;
    });
  });

  // Actualizar tabla de nutrientes nueva (optimizado)
  actualizarTablaNutrientesOptimizada(resultados, filasData);
}

function actualizarTablaNutrientesOptimizada(resultados, filasData) {
  const filasNutrientes = DOMCache.getAll('#tabla-nutrientes tr');
  const updates = [];
  
  for (let i = 0; i < filasNutrientes.length; i++) {
    const fila = filasNutrientes[i];
    const select = fila.querySelector('select');
    if (!select) continue;

    const nameAttr = select.getAttribute('name') || '';
    const indexMatch = nameAttr.match(/_(\d+)$/);
    if (!indexMatch) continue;
    
    const index = indexMatch[1];
    const idNutriente = select.value;
    const spanResultadoBS = fila.querySelector(`#resultado-bs-${index}`);
    const spanResultadoTC = fila.querySelector(`#resultado-tc-${index}`);

    const valorBS = resultados[idNutriente] || 0;
    let aporteTC = 0;

    // Calcular aporte TC de forma optimizada
    filasData.forEach(data => {
      if (!data.nutrientesJson) return;
      
      try {
        const nutrientesList = JSON.parse(data.nutrientesJson);
        const nutrienteEncontrado = nutrientesList.find(n => n.id == idNutriente);
        if (nutrienteEncontrado) {
          const valorNutriente = parseFloat(nutrienteEncontrado.valor) || 0;
          aporteTC += (data.inclusion * valorNutriente) / 100;
        }
      } catch (e) {
        console.error("Error parseando nutrientes:", e);
      }
    });

    if (spanResultadoTC) {
      updates.push({
        element: spanResultadoTC,
        content: aporteTC.toFixed(4)
      });
    }
    if (spanResultadoBS) {
      updates.push({
        element: spanResultadoBS,
        content: valorBS.toFixed(4)
      });
    }
  }
  
  // Aplicar todas las actualizaciones en un solo frame
  requestAnimationFrame(() => {
    updates.forEach(update => {
      update.element.textContent = update.content;
    });
  });
}

function actualizarValoresBachada() {
  const inputs = DOMCache.getAll('input[name^="inclusion_"]');
  inputs.forEach(input => {
    actualizarValores(input);
  });
  
  DebounceUtils.debounce(() => {
    batchCalculateAll();
  }, 300, 'bachada');
}

function calcularSumaInclusion() {
  const inputs = DOMCache.getAll('input[name^="inclusion_"]');
  let suma = 0;
  
  for (let i = 0; i < inputs.length; i++) {
    suma += parseFloat(inputs[i].value) || 0;
  }
  
  DOMCache.get("#suma-inclusion").textContent = suma.toFixed(0);
}

// ===== OPTIMIZACIÓN =====

function optimizarMezcla() {
  const filas = DOMCache.getAll("#tabla-ingredientes tr");
  let ingredientes = [];

  // Optimización: procesar filas de forma más eficiente
  for (let i = 0; i < filas.length; i++) {
    const fila = filas[i];
    const select = fila.querySelector("select");
    if (!select.value) continue;
    
    const selectedOption = select.options[select.selectedIndex];
    const nombre = selectedOption.textContent.trim();
    const limite_min = parseFloat(fila.querySelector('input[name^="min_"]')?.value || 0);
    const limite_max = parseFloat(fila.querySelector('input[name^="max_"]')?.value || 100);
    const costo = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0);
    
    let aporte = {};
    const nutrientesJson = selectedOption.getAttribute("data-nutrientes");
    if (nutrientesJson) {
      try {
        const nutrientes = JSON.parse(nutrientesJson);
        if (Array.isArray(nutrientes)) {
          nutrientes.forEach(n => {
            aporte[n.nombre] = parseFloat(n.valor) || 0;
          });
        }
      } catch (e) {
        console.error("❌ Error al parsear nutrientes para", nombre, ":", e);
      }
    }
    
    ingredientes.push({
      nombre: nombre,
      limite_min: limite_min,
      limite_max: limite_max,
      costo: costo,
      aporte: aporte
    });
  }

  // Recopilar requerimientos
  const requerimientos = [];
  const filasNutrientes = DOMCache.getAll("#tabla-nutrientes tr");
  
  for (let i = 0; i < filasNutrientes.length; i++) {
    const fila = filasNutrientes[i];
    const select = fila.querySelector("select");
    if (!select || !select.value) continue;
    
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
  }

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
    for (let i = 0; i < filas.length; i++) {
      const fila = filas[i];
      if (!fila.querySelector("select").value) continue;
      
      const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
      if (inclusionInput && inclusiones[i]) {
        inclusionInput.value = inclusiones[i].inclusion.toFixed(2);
        actualizarValores(inclusionInput);
      }
    }
    
    DebounceUtils.debounce(() => {
      calcularMineralesOptimizado();
    }, 200, 'optimizar');
  })
  .catch(error => {
    console.error('Error en optimizarMezcla:', error);
    alert('No se pudo optimizar la mezcla.');
  });
}

// ===== GESTIÓN DE NUTRIENTES OPTIMIZADA =====

function agregarFilaNutriente() {
  const tabla = DOMCache.get('#tabla-nutrientes');
  const fila = document.createElement('tr');

  let opciones = '<option value="">-- Seleccionar --</option>';
  if (typeof window.nutrientesTemplate !== 'undefined' && Array.isArray(window.nutrientesTemplate)) {
    // Optimización: usar map y join en lugar de forEach con concatenación
    const opcionesArray = window.nutrientesTemplate.map(n => 
      `<option value="${n.id}" data-unidad="${n.unidad || ''}" data-sugerido="${n.sugerido || 0}">${n.nombre}</option>`
    );
    opciones += opcionesArray.join('');
  }

  fila.innerHTML = `
    <td>
        <select class="form-select form-select-sm" name="nutriente_${contadorNutrientes}" onchange="actualizarUnidadSugerido(this, ${contadorNutrientes}); verificarUltimaFilaNutriente(${contadorNutrientes}); DebounceUtils.debounce(() => calcularMineralesOptimizado(), 200, 'nutriente_change');">
        ${opciones}
      </select>
    </td>
    <td><input type="text" class="form-control form-control-sm" name="unidad_${contadorNutrientes}" value="" readonly></td>
    <td><input type="number" class="form-control form-control-sm" name="sugerido_${contadorNutrientes}" value="" step="0.0001" readonly></td>
    <td><input type="number" class="form-control form-control-sm" name="min_${contadorNutrientes}" step="0.0001" oninput="DebounceUtils.debounce(() => calcularMineralesOptimizado(), 300, 'min_nutriente');"></td>
    <td><input type="number" class="form-control form-control-sm" name="max_${contadorNutrientes}" step="0.0001" oninput="DebounceUtils.debounce(() => calcularMineralesOptimizado(), 300, 'max_nutriente');"></td>
    <td class="text-end"><span id="resultado-tc-${contadorNutrientes}">0.00</span></td>
    <td class="text-end"><span id="resultado-bs-${contadorNutrientes}">0.00</span></td>
    <td class="text-center"><button type="button" class="btn btn-sm btn-danger" onclick="eliminarFilaNutriente(this); DebounceUtils.debounce(() => calcularMineralesOptimizado(), 200, 'eliminar_nutriente');">✖</button></td>
  `;

  tabla.appendChild(fila);
  contadorNutrientes++;
}

function actualizarUnidadSugerido(select, index) {
  const selectedOption = select.options[select.selectedIndex];
  const unidad = selectedOption.getAttribute('data-unidad') || '';
  const sugerido = selectedOption.getAttribute('data-sugerido') || '';

  const fila = select.closest('tr');
  const unidadInput = fila.querySelector(`input[name="unidad_${index}"]`);
  const sugeridoInput = fila.querySelector(`input[name="sugerido_${index}"]`);
  
  if (unidadInput) unidadInput.value = unidad;
  if (sugeridoInput) sugeridoInput.value = sugerido;
  
  if (typeof verificarUltimaFilaNutriente === "function") {
    verificarUltimaFilaNutriente(index);
  }
}

function eliminarFilaNutriente(boton) {
  const fila = boton.closest('tr');
  fila.remove();
  DebounceUtils.debounce(() => {
    calcularMineralesOptimizado();
  }, 200, 'eliminar_nutriente');
}

function verificarUltimaFilaNutriente(index) {
  const tabla = DOMCache.get('#tabla-nutrientes');
  const filas = tabla.querySelectorAll('tr');
  const ultimaFila = filas[filas.length - 1];
  const select = ultimaFila.querySelector('select');
  if (select && select.value !== "") {
    agregarFilaNutriente();
  }
}

// ===== FUNCIONES DE PRECARGA OPTIMIZADAS =====

function agregarFilaDesdeDatos(ing, index) {
  const tabla = DOMCache.get('tabla-ingredientes');
  const fila = document.createElement('tr');

  const tamanoBachada = parseFloat(DOMCache.get('tamano-bachada').value) || 100;
  const inclusion = typeof ing.inclusion !== "undefined" ? ing.inclusion : 0;
  const pesoBachada = (inclusion * tamanoBachada) / 100;

  const ingrediente = typeof window.mineralesTemplate !== 'undefined' ? 
    window.mineralesTemplate.find(i => i.id === ing.ingrediente_id) : null;
  const precioIngrediente = ingrediente ? ingrediente.precio : (ing.precio || 0);
  const valorTotal = pesoBachada * precioIngrediente;

  let opcionesSelect = `<option value="">-- Seleccionar --</option>`;
  if (typeof window.mineralesTemplate !== 'undefined') {
    // Optimización: usar map y join
    const opciones = window.mineralesTemplate.map(m => {
      const selected = m.id === ing.ingrediente_id ? 'selected' : '';
      const nutrientesData = JSON.stringify(m.nutrientes);
      return `<option value="${m.id}" ${selected} 
          data-precio="${m.precio}"
          data-ms="${m.ms}"
          data-nutrientes="${nutrientesData}">
          ${m.nombre}
      </option>`;
    });
    opcionesSelect += opciones.join('');
  }

  fila.innerHTML = `
      <td>
          <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${index}" onchange="agregarFila(this)">
              ${opcionesSelect}
          </select>
      </td>
      <td><input type="number" class="form-control form-control-sm" name="inclusion_${index}" value="${inclusion}" oninput="DebounceUtils.debounce(() => actualizarValores(this), 300, 'inclusion_${index}')"></td>
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

function precargarIngredientes() {
  if (typeof window.ingredientesPrecargados !== 'undefined' && Array.isArray(window.ingredientesPrecargados) && window.ingredientesPrecargados.length > 0) {
    console.log("🔄 Precargando ingredientes:", window.ingredientesPrecargados);
    
    const tabla = DOMCache.get('#tabla-ingredientes');
    tabla.innerHTML = '';
    contadorFilas = 0;
    
    // Usar DocumentFragment para optimizar DOM insertions
    const fragment = document.createDocumentFragment();
    
    window.ingredientesPrecargados.forEach((ing, index) => {
      const tamanoBachada = parseFloat(DOMCache.get('#tamano-bachada').value) || 100;
      const inclusion = typeof ing.inclusion !== "undefined" ? ing.inclusion : 0;
      const pesoBachada = (inclusion * tamanoBachada) / 100;

      const ingrediente = typeof window.mineralesTemplate !== 'undefined' ? 
        window.mineralesTemplate.find(i => i.id === ing.ingrediente_id) : null;
      const precioIngrediente = ingrediente ? ingrediente.precio : (ing.precio || 0);
      const valorTotal = pesoBachada * precioIngrediente;

      let opcionesSelect = `<option value="">-- Seleccionar --</option>`;
      if (typeof window.mineralesTemplate !== 'undefined') {
        const opciones = window.mineralesTemplate.map(m => {
          const selected = m.id === ing.ingrediente_id ? 'selected' : '';
          const nutrientesData = JSON.stringify(m.nutrientes);
          return `<option value="${m.id}" ${selected} 
              data-precio="${m.precio}"
              data-ms="${m.ms}"

// ===== GUARDAR Y CARGAR OPTIMIZADO =====

function guardarMezcla() {
  const nombreMezcla = DOMCache.get('#nombre-mezcla').value.trim();
  const tipoAnimales = DOMCache.get('#tipo-animales').value.trim();
  const etapaProduccion = DOMCache.get('#etapa-produccion').value.trim();
  const observaciones = DOMCache.get('#observaciones').value.trim();

  if (!nombreMezcla) {
    alert('Por favor ingresa un nombre para la mezcla.');
    return;
  }

  const ingredientes = [];
  const filas = DOMCache.getAll('#tabla-ingredientes tr');
  
  // Optimización: usar for loop y cache de elementos
  for (let i = 0; i < filas.length; i++) {
    const fila = filas[i];
    const select = fila.querySelector('select');
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    const inclusion = parseFloat(inclusionInput?.value || 0);

    if (select && select.value && inclusion > 0) {
      ingredientes.push({
        ingrediente_id: parseInt(select.value),
        inclusion: inclusion
      });
    }
  }

  const nutrientesSeleccionados = [];
  const filasNutrientes = DOMCache.getAll('#tabla-nutrientes tr');
  
  for (let i = 0; i < filasNutrientes.length; i++) {
    const row = filasNutrientes[i];
    const select = row.querySelector('select');
    if (select && select.value) {
      nutrientesSeleccionados.push({
        nutriente_id: parseInt(select.value)
      });
    }
  }

  if (ingredientes.length === 0) {
    alert('Agrega al menos un ingrediente antes de guardar.');
    return;
  }

  const datosGuardar = {
    nombre: nombreMezcla,
    tipo_animales: tipoAnimales,
    etapa_produccion: etapaProduccion,
    observaciones: observaciones,
    ingredientes: ingredientes,
    nutrientes: nutrientesSeleccionados
  };

  console.log('Datos a enviar:', datosGuardar);

  fetch('/guardar_mezcla', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datosGuardar)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor:', data);
    if (data.mensaje) {
      alert(data.mensaje);
      if (!data.error) {
        marcarComoGuardado();
      }
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
  const modal = new bootstrap.Modal(DOMCache.get('#modalGuardarComo'));
  modal.show();
}

function confirmarGuardarComo() {
  const nombreMezcla = DOMCache.get('#nombre-existente').value.trim() || DOMCache.get('#nombre-mezcla').value.trim();
  const tipoAnimales = DOMCache.get('#tipo-animales').value.trim();
  const etapaProduccion = DOMCache.get('#etapa-produccion').value.trim();
  const observaciones = DOMCache.get('#observaciones').value.trim();

  if (!nombreMezcla) {
    alert('Por favor ingresa un nombre válido.');
    return;
  }

  const ingredientes = [];
  const filas = DOMCache.getAll('#tabla-ingredientes tr');
  
  for (let i = 0; i < filas.length; i++) {
    const fila = filas[i];
    const select = fila.querySelector('select');
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    const inclusion = parseFloat(inclusionInput?.value || 0);
    if (select && select.value && inclusion > 0) {
      ingredientes.push({
        ingrediente_id: parseInt(select.value),
        inclusion: inclusion
      });
    }
  }

  const nutrientesSeleccionados = [];
  const filasNutrientes = DOMCache.getAll('#tabla-nutrientes tr');
  
  for (let i = 0; i < filasNutrientes.length; i++) {
    const row = filasNutrientes[i];
    const select = row.querySelector('select');
    if (select && select.value) {
      nutrientesSeleccionados.push({
        id: parseInt(select.value)
      });
    }
  }

  if (ingredientes.length === 0) {
    alert('Agrega al menos un ingrediente antes de guardar.');
    return;
  }

  const datosGuardar = {
    nombre: nombreMezcla,
    tipo_animales: tipoAnimales,
    etapa_produccion: etapaProduccion,
    observaciones: observaciones,
    ingredientes: ingredientes,
    nutrientes: nutrientesSeleccionados
  };

  console.log('Datos a enviar (Guardar Como):', datosGuardar);

  fetch('/guardar_mezcla_como', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(datosGuardar)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor (Guardar Como):', data);
    if (data.mensaje) {
      alert(data.mensaje);
      if (!data.error) {
        marcarComoGuardado();
        const modal = bootstrap.Modal.getInstance(DOMCache.get('#modalGuardarComo'));
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

// ===== UTILIDADES OPTIMIZADAS =====

function imprimirTabla() {
  const nombre = DOMCache.get("#nombre-mezcla").value || '';
  const tipo = DOMCache.get("#tipo-animales").value || '';
  const etapa = DOMCache.get("#etapa-produccion").value || '';
  const observaciones = DOMCache.get("#observaciones").value || '';
  const tamanoBachada = parseFloat(DOMCache.get("#tamano-bachada").value) || 100;
  const totalCosto = DOMCache.get("#suma-total").textContent || "0.00";

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
  const filas = DOMCache.getAll('#tabla-ingredientes tr');
  
  // Optimización: usar for loop y cache de elementos
  for (let i = 0; i < filas.length; i++) {
    const fila = filas[i];
    const select = fila.querySelector('select');
    if (!select || !select.value) continue;
    
    const nombre = select.options[select.selectedIndex].text || '';
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0).toFixed(2);
    const peso = parseFloat(fila.querySelector('input[name^="peso_bachada_"]')?.value || 0).toFixed(2);
    const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0).toFixed(2);
    const total = parseFloat(fila.querySelector('input[name^="valor_"]')?.value || 0).toFixed(2);
    
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

// ===== EVENTOS Y INICIALIZACIÓN OPTIMIZADA =====

let hayCambiosSinGuardar = false;
let formularioGuardadoRecientemente = false;
let navegacionInternaEnProceso = false;

function marcarCambiosSinGuardar() {
  if (!formularioGuardadoRecientemente) {
    hayCambiosSinGuardar = true;
  }
}

function marcarComoGuardado() {
  hayCambiosSinGuardar = false;
  formularioGuardadoRecientemente = true;
  setTimeout(() => {
    formularioGuardadoRecientemente = false;
  }, 1000);
}

function confirmarSalida(mensaje = "¿Estás seguro de que deseas salir del formulador? Los cambios no guardados se perderán.") {
  if (hayCambiosSinGuardar) {
    return confirm(mensaje);
  }
  return true;
}

// Versión optimizada de interceptar navegación
function interceptarNavegacion() {
  const selectoresEnlaces = [
    '.sidebar .nav-link',
    'a[href*="panel"]',
    'a[href*="ingredientes"]',
    'a[href*="nutrientes"]',
    'a[href*="requerimientos"]',
    'a[href*="mezclas"]',
    'a[href*="opciones"]',
    'a[href*="logout"]'
  ];
  
  // Usar event delegation para mejor rendimiento
  document.addEventListener('click', function(e) {
    const enlace = e.target.closest(selectoresEnlaces.join(', '));
    if (!enlace) return;
    
    const href = enlace.getAttribute('href') || '';
    
    if (href === '' || 
        href === '#' || 
        href.includes('formulacion_minerales') ||
        href.includes('panelformulador') ||
        href.startsWith('javascript:')) {
      return;
    }
    
    if (hayCambiosSinGuardar) {
      navegacionInternaEnProceso = true;
      
      let mensaje = "¿Estás seguro de que deseas salir del formulador? Los cambios no guardados se perderán.";
      
      if (href.includes('logout')) {
        mensaje = "¿Estás seguro de que deseas cerrar sesión? Los cambios no guardados en el formulador se perderán.";
      }
      
      if (!confirmarSalida(mensaje)) {
        navegacionInternaEnProceso = false;
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
      
      navegacionInternaEnProceso = false;
    }
  }, true);
}

window.addEventListener('beforeunload', function(e) {
  if (hayCambiosSinGuardar && !navegacionInternaEnProceso) {
    e.returnValue = '';
    return '';
  }
});

// Inicialización optimizada
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 Iniciando formulador optimizado...');
  
  // Precargar ingredientes si existen
  precargarIngredientes();
  
  // Agregar fila inicial de nutriente si no hay ninguna
  const tablaNutrientes = DOMCache.get('#tabla-nutrientes');
  if (tablaNutrientes && tablaNutrientes.querySelectorAll('tr').length === 0) {
    agregarFilaNutriente();
  }
  
  // Configurar interceptores de navegación
  interceptarNavegacion();
  
  // Event delegation optimizado para detectar cambios
  document.body.addEventListener('input', function(e) {
    if (e.target.matches('input, select, textarea')) {
      marcarCambiosSinGuardar();
    }
  });
  
  document.body.addEventListener('change', function(e) {
    if (e.target.matches('select')) {
      marcarCambiosSinGuardar();
    }
  });
  
  // Observer optimizado con throttling
  const observer = new MutationObserver(DebounceUtils.throttle(function(mutations) {
    const relevantMutation = mutations.some(mutation => 
      mutation.type === 'childList' && 
      (mutation.target.id === 'tabla-ingredientes' || 
       mutation.target.id === 'tabla-nutrientes')
    );
    
    if (relevantMutation) {
      marcarCambiosSinGuardar();
    }
  }, 100, 'mutation_observer'));
  
  // Observar las tablas principales
  const tablaIngredientes = DOMCache.get('#tabla-ingredientes');
  const tablaNutrientesObs = DOMCache.get('#tabla-nutrientes');
  
  if (tablaIngredientes) {
    observer.observe(tablaIngredientes, { childList: true, subtree: true });
  }
  
  if (tablaNutrientesObs) {
    observer.observe(tablaNutrientesObs, { childList: true, subtree: true });
  }
  
  console.log('✅ Formulador optimizado cargado correctamente');
});

// ===== FUNCIONES DE LIMPIEZA =====

// Función para limpiar recursos cuando sea necesario
function limpiarRecursos() {
  DOMCache.clear();
  DebounceUtils.timers = {};
  console.log('🧹 Recursos limpiados');
}

// Limpiar recursos al salir de la página
window.addEventListener('beforeunload', limpiarRecursos);

console.log('📦 Formulador optimizado v2.0 cargado');
