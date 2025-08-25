// ===== UTILIDADES =====

function imprimirTabla() {
  const nombre = document.getElementById("nombre-mezcla").value || 'Sin nombre';
  const tipo = document.getElementById("tipo-animales").value || 'No especificado';
  const etapa = document.getElementById("etapa-produccion").value || 'No especificado';
  const observaciones = document.getElementById("observaciones").value || 'Sin observaciones';
  const tamanoBachada = parseFloat(document.getElementById("tamano-bachada").value) || 100;
  const totalCosto = document.getElementById("suma-total").textContent || "0.00";
  const sumaInclusion = document.getElementById("suma-inclusion").textContent || "0";
  const materiaSecaTotal = document.getElementById("materia-seca-total").textContent || "0.00";

  // Recopilar ingredientes
  let ingredientes = [];
  document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombreIngrediente = select?.options[select.selectedIndex]?.text || '';
    const inclusion = parseFloat(fila.querySelector('input[name^="inclusion_"]')?.value || 0);
    const peso = parseFloat(fila.querySelector('input[name^="peso_bachada_"]')?.value || 0);
    const precio = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0);
    const total = parseFloat(fila.querySelector('input[name^="valor_"]')?.value || 0);
    
    if (select && select.value && inclusion > 0) {
      ingredientes.push({
        nombre: nombreIngrediente,
        inclusion: formatearInclusion(inclusion),
        peso: peso.toFixed(2),
        precio: precio.toFixed(2),
        valor_total: total.toFixed(2)
      });
    }
  });

  // Recopilar nutrientes
  let nutrientes = [];
  document.querySelectorAll('#tabla-nutrientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    const nombreNutriente = select?.options[select.selectedIndex]?.text || '';
    const unidad = fila.querySelector('input[name^="unidad_"]')?.value || '';
    const sugerido = fila.querySelector('input[name^="sugerido_"]')?.value || '';
    const minimo = fila.querySelector('input[name^="min_"]')?.value || '';
    const maximo = fila.querySelector('input[name^="max_"]')?.value || '';
    const resultadoTC = fila.querySelector('span[id^="resultado-tc-"]')?.textContent || '0.00';
    const resultadoBS = fila.querySelector('span[id^="resultado-bs-"]')?.textContent || '0.00';
    
    if (select && select.value && nombreNutriente.trim() !== '') {
      nutrientes.push({
        nombre: nombreNutriente,
        unidad: unidad,
        sugerido: sugerido || '',
        minimo: minimo || '',
        maximo: maximo || '',
        resultado_tc: resultadoTC,
        resultado_bs: resultadoBS
      });
    }
  });

  // Preparar datos para enviar
  const datosImpresion = {
    nombre_mezcla: nombre,
    tipo_animales: tipo,
    etapa_produccion: etapa,
    observaciones: observaciones,
    tamano_bachada: tamanoBachada,
    total_costo: totalCosto,
    suma_inclusion: sumaInclusion,
    materia_seca_total: materiaSecaTotal,
    ingredientes: ingredientes,
    nutrientes: nutrientes
  };

  // Usar fetch para enviar los datos y luego abrir la nueva ventana
  fetch('/hoja_impresion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosImpresion)
  })
  .then(response => {
    if (response.ok) {
      return response.text();
    }
    throw new Error('Error en la respuesta del servidor');
  })
  .then(html => {
    // Abrir nueva ventana y escribir el HTML
    const ventana = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    if (ventana) {
      ventana.document.write(html);
      ventana.document.close();
    } else {
      alert('No se pudo abrir la ventana de impresión. Verifica que no esté bloqueada por el navegador.');
    }
  })
  .catch(error => {
    console.error('Error al generar hoja de impresión:', error);
    alert('Error al generar la hoja de impresión. Inténtalo de nuevo.');
  });
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

function seleccionarRequerimiento(id, nombre) {
  if (typeof requerimientoSeleccionado === 'undefined') {
    window.requerimientoSeleccionado = null;
  }
  window.requerimientoSeleccionado = { id, nombre };
  
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
  if (!window.requerimientoSeleccionado) {
    alert('Selecciona un requerimiento primero');
    return;
  }
  
  // Cargar nutrientes del requerimiento seleccionado
  fetch(`/api/requerimiento/${window.requerimientoSeleccionado.id}/nutrientes`)
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
      
      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('selectorRequerimientosModal'));
      modal.hide();
      
      // Recalcular
      if (typeof calcularMinerales === 'function') {
        calcularMinerales();
      }
      
      alert(`✅ Requerimientos "${window.requerimientoSeleccionado.nombre}" aplicados correctamente`);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al aplicar requerimientos');
    });
}
