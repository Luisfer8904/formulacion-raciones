// ===== OPTIMIZACIÓN =====

function optimizarMezcla() {
  // Obtener el tipo de optimización seleccionado
  const tipoOptimizacion = document.querySelector('input[name="tipoOptimizacion"]:checked')?.value || 'base_humeda';
  console.log("🎯 Tipo de optimización seleccionado:", tipoOptimizacion);

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
    const ms = parseFloat(selectedOption.getAttribute("data-ms")) || 100; // Obtener materia seca
    
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
      ms: ms, // Agregar materia seca al objeto
      aporte: aporte
    });
  });

  // Recopilar requerimientos desde la tabla de nutrientes
  const requerimientos = [];
  document.querySelectorAll("#tabla-nutrientes tr").forEach(fila => {
    const select = fila.querySelector("select");
    if (!select || !select.value || select.value === "") return;
    
    const selectedOption = select.options[select.selectedIndex];
    const nombre = selectedOption.textContent.trim();
    
    // Filtrar opciones "-- Seleccionar --" o nombres vacíos
    if (nombre === "-- Seleccionar --" || nombre === "" || !nombre) return;
    
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
  const data = { 
    ingredientes, 
    requerimientos, 
    tipo_optimizacion: tipoOptimizacion 
  };
  console.log("🟢 Datos enviados a backend (optimizarMezcla):", data);

  // Mostrar indicador de carga
  const btnOptimizar = document.querySelector('button[onclick="optimizarMezcla()"]');
  const textoOriginal = btnOptimizar ? btnOptimizar.textContent : '';
  if (btnOptimizar) {
    btnOptimizar.disabled = true;
    btnOptimizar.textContent = '⏳ Optimizando...';
  }

  fetch("/optimizar_formulacion", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    console.log("🔍 Respuesta del backend:", data);
    
    // Restaurar botón
    if (btnOptimizar) {
      btnOptimizar.disabled = false;
      btnOptimizar.textContent = textoOriginal;
    }
    
    // Procesar respuesta con el nuevo sistema de notificaciones
    if (typeof notificaciones !== 'undefined') {
      notificaciones.procesarRespuestaOptimizacion(data);
    }
    
    // Si hay resultado exitoso, actualizar la tabla
    if (data.resultado && data.exito) {
      const inclusiones = data.resultado;
      filas.forEach((fila, i) => {
        if (!fila.querySelector("select").value) return;
        fila.querySelector('input[name^="inclusion_"]').value = formatearInclusion(inclusiones[i].inclusion);
        actualizarValores(fila.querySelector('input[name^="inclusion_"]'));
      });
      calcularMinerales();
    } else if (data.validacion) {
      // Mostrar validación específica
      if (typeof notificaciones !== 'undefined') {
        notificaciones.mostrarValidacion(data.validacion);
      } else {
        // Fallback para navegadores sin el sistema de notificaciones
        alert(data.error || "No se pudo optimizar la mezcla.");
      }
    } else if (!data.resultado) {
      // Fallback para errores sin validación
      if (typeof notificaciones !== 'undefined') {
        notificaciones.mostrarToast(
          '❌ Error',
          data.error || "No se pudo optimizar la mezcla.",
          'error'
        );
      } else {
        alert(data.error || "No se pudo optimizar la mezcla.");
      }
    }
  })
  .catch(error => {
    console.error('Error en optimizarMezcla:', error);
    
    // Restaurar botón
    if (btnOptimizar) {
      btnOptimizar.disabled = false;
      btnOptimizar.textContent = textoOriginal;
    }
    
    // Mostrar error de conexión
    if (typeof notificaciones !== 'undefined') {
      notificaciones.mostrarToast(
        '🔌 Error de Conexión',
        'No se pudo conectar con el servidor. Verifique su conexión a internet.',
        'error',
        7000
      );
    } else {
      alert('No se pudo optimizar la mezcla. Error de conexión.');
    }
  });
}
