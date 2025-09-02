// Variables globales para la calculadora de aportes
let ingredientesDisponibles = [];
let nutrientesDisponibles = [];

function abrirCalculadoraAportes() {
    // Crear modal dinámico para calculadora de aportes
    const modalHtml = `
        <div class="modal fade" id="calculadoraAportesModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-calculator me-2"></i>Calculadora de Aportes Nutricionales</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Información de la Fórmula</h6>
                                <div class="mb-3">
                                    <label class="form-label">Cargar Fórmula Existente (Opcional)</label>
                                    <select class="form-select" id="formulaExistente" onchange="cargarFormulaSeleccionada()">
                                        <option value="">-- Seleccionar fórmula existente --</option>
                                    </select>
                                    <small class="form-text text-muted">O crear una nueva fórmula abajo</small>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Nombre de la Fórmula</label>
                                    <input type="text" class="form-control" id="nombreFormula" placeholder="Ej: Alimento para Bovinos">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Consumo por Animal (kg/día)</label>
                                    <input type="number" class="form-control" id="consumoAnimal" step="0.1" min="0.1" placeholder="Ej: 3.0">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Materia Seca de la Dieta (%)</label>
                                    <input type="number" class="form-control" id="materiaSecaDieta" step="0.1" min="0" max="100" value="88" placeholder="Ej: 88">
                                    <small class="form-text text-muted">Porcentaje de materia seca de la dieta completa</small>
                                </div>
                                
                                <h6 class="mt-4">Ingredientes de la Fórmula</h6>
