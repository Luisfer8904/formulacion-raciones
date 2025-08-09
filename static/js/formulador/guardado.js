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
