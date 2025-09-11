// PATCH para agregar funcionalidad de límites al formulador
// Este archivo complementa formulador.js con la funcionalidad de límites

// Función mejorada para agregar fila desde datos precargados (CON LÍMITES)
function agregarFilaDesdeDatosConLimites(ing, index) {
  const tabla = document.getElementById('tabla-ingredientes');
  const fila = document.createElement('tr');

  const tamanoBachada = parseFloat(document.getElementById('tamano-bachada').value) || 100;
  const inclusion = typeof ing.inclusion !== "undefined" ? ing.inclusion : 0;
  const pesoBachada = (inclusion * tamanoBachada) / 100;
  
  // CORREGIDO: Solo usar límites si están definidos y no son los valores por defecto problemáticos
  let limiteMin = "";
  let limiteMax = "";
  
  if (typeof ing.limite_min !== "undefined" && ing.limite_min !== null && ing.limite_min !== 0) {
    limiteMin = ing.limite_min;
  }
  if (typeof ing.limite_max !== "undefined" && ing.limite_max !== null && ing.limite_max !== 100) {
    limiteMax = ing.limite_max;
  }

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
      <td><input type="number" class="form-control form-control-sm" name="min_${index}" value="${limiteMin}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="max_${index}" value="${limiteMax}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${index}" value="${formatearPeso ? formatearPeso(pesoBachada, false) : pesoBachada.toFixed(2)}" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${index}" value="${formatearPrecio ? formatearPrecio(precioIngrediente, false) : precioIngrediente.toFixed(2)}" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="valor_${index}" value="${formatearPrecio ? formatearPrecio(valorTotal, false) : valorTotal.toFixed(2)}" readonly></td>
      <td>
          <button type="button" class="btn btn-sm btn-danger" onclick="eliminarFila(this)">✖</button>
          <button type="button" class="btn btn-sm btn-info" onclick="mostrarInfo(this)">ℹ️</button>
      </td>
  `;

  tabla.appendChild(fila);
  
  console.log(`✅ Fila agregada con límites: ${ing.nombre || 'Ingrediente'} (min: ${limiteMin}, max: ${limiteMax})`);
}

// Función mejorada para precargar ingredientes CON LÍMITES
function precargarIngredientesConLimites() {
  if (typeof window.ingredientesPrecargados !== 'undefined' && Array.isArray(window.ingredientesPrecargados) && window.ingredientesPrecargados.length > 0) {
    console.log("🔄 Precargando ingredientes CON LÍMITES:", window.ingredientesPrecargados);
    
    // Limpiar tabla actual
    const tabla = document.getElementById('tabla-ingredientes');
    tabla.innerHTML = '';
    
    // Resetear contador si existe
    if (typeof contadorFilas !== 'undefined') {
      contadorFilas = 0;
    }
    
    // Agregar ingredientes precargados CON LÍMITES
    window.ingredientesPrecargados.forEach((ing, index) => {
      agregarFilaDesdeDatosConLimites(ing, index);
      if (typeof contadorFilas !== 'undefined') {
        contadorFilas++;
      }
    });
    
    // Agregar una fila vacía al final
    if (typeof agregarFilaVacia === 'function') {
      agregarFilaVacia();
    } else {
      // Fallback: agregar fila vacía básica
      agregarFilaVaciaBasica();
    }
    
    // Recalcular todos los valores después de cargar
    setTimeout(() => {
      if (typeof actualizarValoresBachada === 'function') actualizarValoresBachada();
      if (typeof calcularMinerales === 'function') calcularMinerales();
      if (typeof calcularSumaInclusion === 'function') calcularSumaInclusion();
      if (typeof calcularSumaTotal === 'function') calcularSumaTotal();
    }, 300);
    
    console.log("✅ Ingredientes precargados con límites completado");
  } else {
    console.log("ℹ️ No hay ingredientes precargados o no tienen límites");
  }
}

// Función auxiliar para agregar fila vacía
function agregarFilaVaciaBasica() {
  const tabla = document.getElementById('tabla-ingredientes');
  const fila = document.createElement('tr');
  const index = typeof contadorFilas !== 'undefined' ? contadorFilas : tabla.rows.length;
  
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
          <select class="form-select form-select-sm select-ingrediente" name="ingrediente_${index}" onchange="agregarFila(this)">
              ${opcionesSelect}
          </select>
      </td>
      <td><input type="number" class="form-control form-control-sm" name="inclusion_${index}" min="0" max="100" step="0.1" oninput="actualizarValores(this)"></td>
      <td><input type="number" class="form-control form-control-sm" name="min_${index}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="max_${index}" step="0.0001"></td>
      <td><input type="number" class="form-control form-control-sm" name="peso_bachada_${index}" step="0.01" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="costo_ingrediente_${index}" step="0.01" readonly></td>
      <td><input type="number" class="form-control form-control-sm" name="valor_${index}" step="0.01" readonly></td>
      <td>
          <button type="button" class="btn btn-sm btn-danger" onclick="eliminarFila(this)">✖</button>
          <button type="button" class="btn btn-sm btn-info" onclick="mostrarInfo(this)">ℹ️</button>
      </td>
  `;
  
  tabla.appendChild(fila);
  
  if (typeof contadorFilas !== 'undefined') {
    contadorFilas++;
  }
}

// Función mejorada para recopilar ingredientes CON LÍMITES (para guardado)
function recopilarIngredientesConLimites() {
  const ingredientes = [];
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
    const inclusion = parseFloat(inclusionInput?.value || 0);
    const limiteMinInput = fila.querySelector('input[name^="min_"]');
    const limiteMaxInput = fila.querySelector('input[name^="max_"]');
    
    // CORREGIDO: Solo incluir límites si tienen valores específicos (no vacíos)
    const limiteMinValue = limiteMinInput?.value;
    const limiteMaxValue = limiteMaxInput?.value;
    
    let limiteMin = null;
    let limiteMax = null;
    
    // Solo asignar si hay un valor específico diferente de vacío
    if (limiteMinValue && limiteMinValue !== "" && !isNaN(parseFloat(limiteMinValue))) {
      limiteMin = parseFloat(limiteMinValue);
    }
    if (limiteMaxValue && limiteMaxValue !== "" && !isNaN(parseFloat(limiteMaxValue))) {
      limiteMax = parseFloat(limiteMaxValue);
    }

    if (select && select.value && inclusion > 0) {
      const ingrediente = {
        ingrediente_id: parseInt(select.value),
        inclusion: inclusion
      };
      
      // Solo agregar límites si tienen valores específicos
      if (limiteMin !== null) {
        ingrediente.limite_min = limiteMin;
      }
      if (limiteMax !== null) {
        ingrediente.limite_max = limiteMax;
      }
      
      ingredientes.push(ingrediente);
    }
  });
  
  console.log("📊 Ingredientes recopilados con límites:", ingredientes);
  return ingredientes;
}

// Sobrescribir función de precarga si existe
if (typeof precargarIngredientes === 'function') {
  // Guardar función original como respaldo
  window.precargarIngredientesOriginal = precargarIngredientes;
  // Sobrescribir con la nueva función
  window.precargarIngredientes = precargarIngredientesConLimites;
  console.log("🔄 Función precargarIngredientes sobrescrita con soporte para límites");
}

// Inicialización cuando se carga este script
document.addEventListener('DOMContentLoaded', function() {
  console.log("🚀 Patch de límites cargado correctamente");
  
  // Si ya hay ingredientes precargados, aplicar la nueva función
  if (typeof window.ingredientesPrecargados !== 'undefined' && window.ingredientesPrecargados.length > 0) {
    console.log("🔄 Aplicando patch a ingredientes ya precargados");
    setTimeout(() => {
      precargarIngredientesConLimites();
    }, 500);
  }
});

console.log("✅ Formulador Límites Patch v1.0 cargado");
