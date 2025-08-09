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
