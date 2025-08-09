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
