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
    <td class="text-center">
        <div class="btn-action-container">
            <button type="button" class="btn-action btn-action-danger" onclick="eliminarFilaNutriente(this); calcularMinerales();" title="Eliminar nutriente">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </td>
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
