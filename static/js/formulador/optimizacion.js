// ===== OPTIMIZACIÓN =====

/**
 * Muestra una notificación detallada (modal Bootstrap) con diagnósticos
 * @param {Object|Object[]} diagnosticos - Array de diagnósticos o un solo diagnóstico
 */
function mostrarNotificacionOptimizacion(diagnosticos) {
  const diags = Array.isArray(diagnosticos) ? diagnosticos : [diagnosticos];

  // Crear/reciclar modal contenedor
  let modal = document.getElementById('optimizacionNotificacionModal');
  if (!modal) {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <div class="modal fade" id="optimizacionNotificacionModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Diagnóstico de Optimización</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body">
              <div id="contenidoDiagnosticos"></div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
          </div>
        </div>
      </div>`;
    document.body.appendChild(wrapper.firstElementChild);
    modal = document.getElementById('optimizacionNotificacionModal');
  }

  // Construir el contenido
  const cont = modal.querySelector('#contenidoDiagnosticos');
  const items = diags.map(d => {
    const detalles = (d.detalles || []).map(it => `<li>${it}</li>`).join('');
    const badge = {
      limites_incompatibles: 'warning',
      limite_individual_invalido: 'warning',
      nutriente_insuficiente: 'danger',
      costos_faltantes: 'info',
      nutrientes_faltantes: 'info',
      optimizador_fallo: 'danger',
      datos_incompletos: 'secondary'
    }[d.tipo] || 'secondary';
    return `
      <div class="mb-3 p-3 border rounded">
        <div class="d-flex align-items-start justify-content-between">
          <h6 class="mb-2">${d.titulo || 'Aviso'}</h6>
          <span class="badge text-bg-${badge}">${d.tipo || ''}</span>
        </div>
        <p class="mb-2">${d.mensaje || ''}</p>
        ${d.solucion ? `<div class="alert alert-light border"><strong>Sugerencia:</strong> ${d.solucion}</div>` : ''}
        ${detalles ? `<ul class="mb-0">${detalles}</ul>` : ''}
      </div>`;
  }).join('');
  cont.innerHTML = items || '<div class="alert alert-info">No se proporcionaron detalles.</div>';

  // Mostrar modal
  const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
  bsModal.show();
}

// Recopila datos del formulario y llama al backend
function optimizarMezcla() {
  const tipoOptimizacion = document.querySelector('input[name="tipoOptimizacion"]:checked')?.value || 'base_humeda';

  // Ingredientes
  const filasIng = document.querySelectorAll('#tabla-ingredientes tr');
  const ingredientes = [];
  filasIng.forEach(fila => {
    const select = fila.querySelector('select');
    if (!select || !select.value) return;
    const opt = select.options[select.selectedIndex];
    const nombre = opt.textContent.trim();
    const limite_min = parseFloat(fila.querySelector('input[name^="min_"]')?.value || 0);
    const limite_max = parseFloat(fila.querySelector('input[name^="max_"]')?.value || 100);
    const costo = parseFloat(fila.querySelector('input[name^="costo_ingrediente_"]')?.value || 0);
    const ms = parseFloat(opt.getAttribute('data-ms')) || 100;
    
    let aporte = {};
    const nutrientesJson = opt.getAttribute('data-nutrientes');
    if (nutrientesJson) {
      try {
        const nutrientes = JSON.parse(nutrientesJson);
        if (Array.isArray(nutrientes)) {
          nutrientes.forEach(n => { aporte[n.nombre] = parseFloat(n.valor) || 0; });
        }
      } catch (e) {
        console.warn('⚠️ Error parseando nutrientes de', nombre, e);
      }
    }
    ingredientes.push({ nombre, limite_min, limite_max, costo, ms, aporte });
  });

  // Requerimientos
  const requerimientos = [];
  document.querySelectorAll('#tabla-nutrientes tr').forEach(fila => {
    const select = fila.querySelector('select');
    if (!select || !select.value) return;
    const opt = select.options[select.selectedIndex];
    const nombre = opt.textContent.trim();
    if (!nombre || nombre === '-- Seleccionar --') return;
    const min = fila.querySelector('input[name^="min_"]')?.value;
    const max = fila.querySelector('input[name^="max_"]')?.value;
    const unidad = fila.querySelector('input[name^="unidad_"]')?.value || '';
    requerimientos.push({ nombre, min: min !== '' ? parseFloat(min) : null, max: max !== '' ? parseFloat(max) : null, unidad });
  });

  const payload = { ingredientes, requerimientos, tipo_optimizacion: tipoOptimizacion };
  console.log('🟢 Enviando a backend /optimizar_formulacion:', payload);

  fetch('/optimizar_formulacion', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        // Mostrar diagnósticos si están disponibles
        if (data.diagnosticos) return mostrarNotificacionOptimizacion(data.diagnosticos);
        if (data.diagnostico) return mostrarNotificacionOptimizacion(data.diagnostico);
        return mostrarNotificacionOptimizacion({
          tipo: 'error',
          titulo: 'No se pudo optimizar',
          mensaje: data.error || 'Ocurrió un error durante la optimización.',
          solucion: 'Verifica límites y requerimientos. Intenta con valores menos restrictivos.'
        });
      }

      // Éxito
      console.log('🔍 Respuesta OK backend:', data);
      if (!data.resultado || !Array.isArray(data.resultado)) {
        return mostrarNotificacionOptimizacion({
          tipo: 'error',
          titulo: 'Respuesta inesperada',
          mensaje: 'No se encontraron resultados de inclusión.'
        });
      }

      const inclusiones = data.resultado;
      let idx = 0;
      document.querySelectorAll('#tabla-ingredientes tr').forEach(fila => {
        const select = fila.querySelector('select');
        if (!select || !select.value) return;
        const inclusionInput = fila.querySelector('input[name^="inclusion_"]');
        if (inclusionInput && inclusiones[idx]) {
          inclusionInput.value = formatearInclusion(inclusiones[idx].inclusion);
          actualizarValores(inclusionInput);
          idx++;
        }
      });
      if (typeof calcularMinerales === 'function') calcularMinerales();
    })
    .catch((err) => {
      console.error('❌ Error de red en optimizarMezcla:', err);
      mostrarNotificacionOptimizacion({
        tipo: 'network_error',
        titulo: 'Problema de conexión',
        mensaje: 'No se pudo contactar al servidor.',
        solucion: 'Revisa tu conexión e inténtalo de nuevo.'
      });
    });
}
