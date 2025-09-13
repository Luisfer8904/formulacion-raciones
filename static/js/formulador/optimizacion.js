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
        const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
        inputInclusion.value = formatearInclusion(inclusiones[i].inclusion);
        
        // Agregar indicador visual si es aproximada
        if (data.aproximada) {
          inputInclusion.style.backgroundColor = '#fff3cd';
          inputInclusion.style.borderColor = '#ffc107';
          inputInclusion.title = 'Resultado aproximado - Calidad: ' + 
            (data.metricas_aproximacion ? (data.metricas_aproximacion.calidad_general * 100).toFixed(1) + '%' : 'N/A');
        } else {
          // Limpiar estilos si es resultado exacto
          inputInclusion.style.backgroundColor = '';
          inputInclusion.style.borderColor = '';
          inputInclusion.title = '';
        }
        
        actualizarValores(inputInclusion);
      });
      
      // Agregar indicador visual en la tabla si es aproximada
      if (data.aproximada) {
        mostrarIndicadorAproximacion(data);
      } else {
        ocultarIndicadorAproximacion();
      }
      
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

// Funciones auxiliares para indicadores de aproximación
function mostrarIndicadorAproximacion(data) {
  // Remover indicador existente si existe
  ocultarIndicadorAproximacion();
  
  // Crear indicador de aproximación
  const indicador = document.createElement('div');
  indicador.id = 'indicador-aproximacion';
  indicador.className = 'alert alert-warning mt-3';
  indicador.style.cssText = `
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  `;
  
  const calidad = data.metricas_aproximacion ? data.metricas_aproximacion.calidad_general * 100 : 0;
  const nutrientesCumplidos = data.metricas_aproximacion ? data.metricas_aproximacion.nutrientes_cumplidos : 0;
  const nutrientesTotales = data.metricas_aproximacion ? data.metricas_aproximacion.nutrientes_totales : 0;
  
  let iconoCalidad = '⚠️';
  let textoCalidad = 'Aproximación Limitada';
  let colorBarra = '#ffc107';
  
  if (calidad >= 95) {
    iconoCalidad = '✅';
    textoCalidad = 'Excelente Aproximación';
    colorBarra = '#28a745';
  } else if (calidad >= 80) {
    iconoCalidad = '⚠️';
    textoCalidad = 'Buena Aproximación';
    colorBarra = '#17a2b8';
  }
  
  indicador.innerHTML = `
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
      <span style="font-size: 1.2em;">${iconoCalidad}</span>
      <strong style="color: #856404;">Resultado Aproximado - ${textoCalidad}</strong>
    </div>
    <div style="margin-bottom: 8px;">
      <small style="color: #856404;">Calidad de aproximación:</small>
      <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin: 5px 0;">
        <div style="background: ${colorBarra}; height: 100%; border-radius: 10px; width: ${calidad}%; transition: width 0.3s ease;"></div>
      </div>
      <small style="color: #856404;">${calidad.toFixed(1)}% - Nutrientes cumplidos: ${nutrientesCumplidos}/${nutrientesTotales}</small>
    </div>
    <small style="color: #856404;">
      💡 Este resultado es una aproximación. Algunos requerimientos nutricionales pueden no cumplirse exactamente.
      <a href="#" onclick="mostrarDetallesAproximacion(); return false;" style="color: #856404; text-decoration: underline;">Ver detalles</a>
    </small>
  `;
  
  // Insertar después de la tabla de ingredientes
  const tablaIngredientes = document.getElementById('tabla-ingredientes');
  if (tablaIngredientes && tablaIngredientes.parentNode) {
    tablaIngredientes.parentNode.insertBefore(indicador, tablaIngredientes.nextSibling);
  }
  
  // Guardar datos para mostrar detalles
  window.datosAproximacion = data;
}

function ocultarIndicadorAproximacion() {
  const indicadorExistente = document.getElementById('indicador-aproximacion');
  if (indicadorExistente) {
    indicadorExistente.remove();
  }
  
  // Limpiar estilos de inputs
  document.querySelectorAll('input[name^="inclusion_"]').forEach(input => {
    input.style.backgroundColor = '';
    input.style.borderColor = '';
    input.title = '';
  });
  
  // Limpiar datos guardados
  delete window.datosAproximacion;
}

function mostrarDetallesAproximacion() {
  if (window.datosAproximacion && typeof notificaciones !== 'undefined') {
    // Mostrar modal con detalles de aproximación
    notificaciones.mostrarModal(window.datosAproximacion.notificacion);
  }
}
