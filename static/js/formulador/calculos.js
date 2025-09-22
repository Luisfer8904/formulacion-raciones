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
  document.getElementById("suma-inclusion").textContent = suma.toFixed(4);
  
  // Calcular materia seca total
  calcularMateriaSeca();
}

function calcularMateriaSeca() {
  let materiaSecaTotal = 0;
  
  const filas = document.querySelectorAll("#tabla-ingredientes tr");
  filas.forEach(fila => {
    const select = fila.querySelector("select");
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0);
    
    if (select?.value && inclusion > 0) {
      const selectedOption = select.options[select.selectedIndex];
      const ms = parseFloat(selectedOption.getAttribute("data-ms")) || 100;
      
      // Calcular aporte de materia seca: (inclusión % * materia seca %) / 100
      const aporteMS = (inclusion * ms) / 100;
      materiaSecaTotal += aporteMS;
    }
  });
  
  // Actualizar el elemento en la interfaz
  const elementoMS = document.getElementById("materia-seca-total");
  if (elementoMS) {
    elementoMS.textContent = materiaSecaTotal.toFixed(2);
  }
}
