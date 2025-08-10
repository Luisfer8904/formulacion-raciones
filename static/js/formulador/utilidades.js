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

// ===== GESTIÓN DE REQUERIMIENTOS =====

function mostrarSelectorRequerimientos() {
  const modal = new bootstrap.Modal(document.getElementById('selectorRequerimientosModal'));
  
  // Mostrar loading
  document.getElementById('loading-requerimientos').style.display = 'block';
  document.getElementById('lista-requerimientos').innerHTML = '';
  document.getElementById('preview-nutrientes').style.display = 'none';
  document.getElementById('aplicar-requerimientos').disabled = true;
  
  // Cargar requerimientos del usuario
  fetch('/api/requerimientos_usuario')
    .then(response => response.json())
    .then(data => {
      document.getElementById('loading-requerimientos').style.display = 'none';
      
      if (data.error) {
        document.getElementById('lista-requerimientos').innerHTML = `
          <div class="alert alert-warning">
            <strong>No hay requerimientos disponibles</strong><br>
            ${data.error}
          </div>`;
      } else if (Array.isArray(data) && data.length > 0) {
        let html = '<div class="list-group">';
        data.forEach(req => {
          html += `
            <button type="button" class="list-group-item list-group-item-action" onclick="seleccionarRequerimiento(${req.id}, '${req.nombre.replace(/'/g, "\\'")}')">
              <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${req.nombre}</h6>
                <small class="text-muted">${req.tipo_especie || 'Sin especificar'}</small>
              </div>
              <p class="mb-1">${req.comentario || 'Sin comentarios'}</p>
            </button>`;
        });
        html += '</div>';
        document.getElementById('lista-requerimientos').innerHTML = html;
      } else {
        document.getElementById('lista-requerimientos').innerHTML = `
          <div class="alert alert-info">
            <strong>No hay requerimientos disponibles</strong><br>
            Crea primero algunos requerimientos en la sección de Requerimientos.
          </div>`;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('loading-requerimientos').style.display = 'none';
      document.getElementById('lista-requerimientos').innerHTML = `
        <div class="alert alert-danger">Error al cargar requerimientos</div>`;
    });
  
  modal.show();
}

let requerimientoSeleccionado = null;

function seleccionarRequerimiento(id, nombre) {
  requerimientoSeleccionado = { id, nombre };
  
  // Mostrar preview
  fetch(`/api/requerimiento/${id}/nutrientes`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        document.getElementById('preview-nutrientes').style.display = 'none';
        alert('Error al cargar nutrientes del requerimiento: ' + data.error);
        return;
      }
      
      if (!Array.isArray(data) || data.length === 0) {
        document.getElementById('preview-nutrientes-body').innerHTML = `
          <tr>
            <td colspan="3" class="text-center text-muted">Este requerimiento no tiene nutrientes configurados</td>
          </tr>`;
        document.getElementById('preview-nutrientes').style.display = 'block';
        document.getElementById('aplicar-requerimientos').disabled = true;
      } else {
        let html = '';
        data.forEach(nutriente => {
          html += `
            <tr>
              <td>${nutriente.nombre}</td>
              <td>${nutriente.unidad || 'N/A'}</td>
              <td>${nutriente.valor_sugerido || 'N/A'}</td>
            </tr>`;
        });
        
        document.getElementById('preview-nutrientes-body').innerHTML = html;
        document.getElementById('preview-nutrientes').style.display = 'block';
        document.getElementById('aplicar-requerimientos').disabled = false;
      }
      
      // Highlight selected requirement
      document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
      });
      
      // Buscar el elemento que fue clickeado usando el event
      const clickedElement = document.querySelector(`[onclick="seleccionarRequerimiento(${id}, '${nombre.replace(/'/g, "\\'")}')"]`);
      if (clickedElement) {
        clickedElement.classList.add('active');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al cargar los nutrientes');
      document.getElementById('preview-nutrientes').style.display = 'none';
      document.getElementById('aplicar-requerimientos').disabled = true;
    });
}

function aplicarRequerimientosSeleccionados() {
  if (!requerimientoSeleccionado) {
    alert('Selecciona un requerimiento primero');
    return;
  }
  
  // Cargar nutrientes del requerimiento seleccionado
  fetch(`/api/requerimiento/${requerimientoSeleccionado.id}/nutrientes`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert('Error al cargar nutrientes: ' + data.error);
        return;
      }
      
      if (!Array.isArray(data) || data.length === 0) {
        alert('Este requerimiento no tiene nutrientes configurados');
        return;
      }
      
      // Limpiar tabla actual
      const tabla = document.getElementById('tabla-nutrientes');
      tabla.innerHTML = '';
      contadorNutrientes = 0;
      
      // Agregar nutrientes del requerimiento
      data.forEach(nutriente => {
        agregarFilaNutriente();
        const ultimaFila = tabla.lastElementChild;
        const select = ultimaFila.querySelector('select');
        const sugeridoInput = ultimaFila.querySelector(`input[name="sugerido_${contadorNutrientes-1}"]`);
        
        // Seleccionar el nutriente
        select.value = nutriente.nutriente_id;
        
        // Actualizar la unidad y sugerido
        actualizarUnidadSugerido(select, contadorNutrientes-1);
        
        // Sobrescribir el valor sugerido con el del requerimiento
        if (sugeridoInput && nutriente.valor_sugerido) {
          sugeridoInput.value = nutriente.valor_sugerido;
        }
      });
      
      // Agregar una fila vacía al final
      agregarFilaNutriente();
      
      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('selectorRequerimientosModal'));
      modal.hide();
      
      // Recalcular
      if (typeof calcularMinerales === 'function') {
        calcularMinerales();
      }
      
      alert(`✅ Requerimientos "${requerimientoSeleccionado.nombre}" aplicados correctamente`);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al aplicar requerimientos');
    });
}
