/**
 * Formulador Modular - Archivo Principal
 * Integra todos los módulos del formulador para una mejor organización y mantenimiento
 * 
 * Este archivo reemplaza gradualmente al formulador.js monolítico
 */

// Importar módulos
import { 
    inicializarConfiguracion, 
    obtenerConfigUsuario, 
    actualizarEtiquetasUI,
    formatearMoneda,
    formatearPeso
} from './modules/formulador-config.js';

import { 
    inicializarCalculos, 
    calcularConOptimizacion,
    actualizarTodosLosCalculos,
    validarSumaInclusiones
} from './modules/formulador-calculations.js';

import { 
    inicializarEventosUI,
    mostrarAlerta,
    agregarFila,
    eliminarFila,
    mostrarInfo
} from './modules/formulador-ui.js';

/**
 * Clase principal del Formulador Modular
 */
class FormuladorModular {
    constructor() {
        this.inicializado = false;
        this.version = '2.0.0';
        this.debug = window.location.hostname === 'localhost';
    }

    /**
     * Inicializa el formulador modular
     */
    async inicializar() {
        if (this.inicializado) {
            console.warn('⚠️ Formulador ya inicializado');
            return;
        }

        try {
            this.log('🚀 Iniciando Formulador Modular v' + this.version);

            // Verificar dependencias
            await this.verificarDependencias();

            // Inicializar módulos en orden
            inicializarConfiguracion();
            inicializarCalculos();
            inicializarEventosUI();

            // Configurar eventos globales
            this.configurarEventosGlobales();

            // Cargar datos iniciales
            await this.cargarDatosIniciales();

            // Realizar cálculo inicial
            calcularConOptimizacion();

            this.inicializado = true;
            this.log('✅ Formulador Modular inicializado correctamente');

            // Mostrar información de depuración si está en desarrollo
            if (this.debug) {
                this.mostrarInfoDebug();
            }

        } catch (error) {
            console.error('❌ Error al inicializar Formulador Modular:', error);
            mostrarAlerta('Error al inicializar el formulador. Recarga la página.', 'error');
        }
    }

    /**
     * Verifica que todas las dependencias estén disponibles
     */
    async verificarDependencias() {
        const dependencias = [
            { nombre: 'Bootstrap', objeto: 'bootstrap' },
            { nombre: 'jQuery', objeto: '$' },
        ];

        const faltantes = dependencias.filter(dep => typeof window[dep.objeto] === 'undefined');

        if (faltantes.length > 0) {
            throw new Error(`Dependencias faltantes: ${faltantes.map(d => d.nombre).join(', ')}`);
        }

        this.log('✅ Dependencias verificadas');
    }

    /**
     * Configura eventos globales del formulador
     */
    configurarEventosGlobales() {
        // Evento para optimización
        window.optimizarMezcla = () => this.optimizarMezcla();
        
        // Evento para guardar
        window.guardarMezcla = () => this.guardarMezcla();
        
        // Evento para guardar como
        window.guardarComo = () => this.guardarComo();
        
        // Evento para imprimir
        window.imprimirTabla = () => this.imprimirTabla();

        // Exponer funciones principales globalmente para compatibilidad
        window.calcularMinerales = calcularConOptimizacion;
        window.actualizarValores = calcularConOptimizacion;

        this.log('✅ Eventos globales configurados');
    }

    /**
     * Carga datos iniciales si están disponibles
     */
    async cargarDatosIniciales() {
        // Cargar ingredientes precargados si existen
        if (typeof window.ingredientesPrecargados !== 'undefined' && 
            Array.isArray(window.ingredientesPrecargados) && 
            window.ingredientesPrecargados.length > 0) {
            
            this.log('📦 Cargando ingredientes precargados:', window.ingredientesPrecargados.length);
            await this.cargarIngredientesPrecargados();
        }

        this.log('✅ Datos iniciales cargados');
    }

    /**
     * Carga ingredientes precargados en la tabla
     */
    async cargarIngredientesPrecargados() {
        // Esta funcionalidad se implementará cuando se migre completamente
        // Por ahora, mantener compatibilidad con el código existente
        this.log('⏳ Carga de ingredientes precargados pendiente de migración');
    }

    /**
     * Optimiza la mezcla usando el algoritmo de optimización
     */
    async optimizarMezcla() {
        try {
            mostrarAlerta('Iniciando optimización...', 'info');
            
            // Validar antes de optimizar
            const validacion = validarSumaInclusiones();
            if (!validacion.valida && validacion.suma > 105) {
                mostrarAlerta('La suma de inclusiones es muy alta para optimizar. Ajusta los valores primero.', 'warning');
                return;
            }

            // Recopilar datos para optimización
            const datosOptimizacion = this.recopilarDatosOptimizacion();
            
            if (datosOptimizacion.ingredientes.length === 0) {
                mostrarAlerta('Agrega al menos un ingrediente para optimizar', 'warning');
                return;
            }

            // Llamar al endpoint de optimización
            const response = await fetch('/optimizar_mezcla', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datosOptimizacion)
            });

            const resultado = await response.json();

            if (resultado.success) {
                this.aplicarResultadoOptimizacion(resultado.data);
                mostrarAlerta('Optimización completada exitosamente', 'success');
            } else {
                mostrarAlerta(resultado.message || 'Error en la optimización', 'error');
            }

        } catch (error) {
            console.error('Error en optimización:', error);
            mostrarAlerta('Error al optimizar la mezcla', 'error');
        }
    }

    /**
     * Recopila datos necesarios para la optimización
     */
    recopilarDatosOptimizacion() {
        const ingredientes = [];
        const requerimientos = [];

        // Recopilar ingredientes
        const filasIngredientes = document.querySelectorAll('#tabla-ingredientes tbody tr');
        filasIngredientes.forEach(fila => {
            const select = fila.querySelector('select[name^="ingrediente_"]');
            const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
            const inputMin = fila.querySelector('input[name^="min_"]');
            const inputMax = fila.querySelector('input[name^="max_"]');

            if (select && select.value) {
                ingredientes.push({
                    id: parseInt(select.value),
                    inclusion: parseFloat(inputInclusion?.value || 0),
                    min: parseFloat(inputMin?.value || 0),
                    max: parseFloat(inputMax?.value || 100)
                });
            }
        });

        // Recopilar requerimientos
        const filasNutrientes = document.querySelectorAll('#tabla-nutrientes tbody tr');
        filasNutrientes.forEach(fila => {
            const select = fila.querySelector('select[name^="nutriente_"]');
            const inputMin = fila.querySelector('input[name^="min_"]');
            const inputMax = fila.querySelector('input[name^="max_"]');

            if (select && select.value && (inputMin?.value || inputMax?.value)) {
                requerimientos.push({
                    nutriente_id: parseInt(select.value),
                    min: parseFloat(inputMin?.value || 0),
                    max: parseFloat(inputMax?.value || 999999)
                });
            }
        });

        return { ingredientes, requerimientos };
    }

    /**
     * Aplica el resultado de la optimización a la interfaz
     */
    aplicarResultadoOptimizacion(resultado) {
        if (!resultado || !resultado.ingredientes) return;

        // Actualizar valores de inclusión
        resultado.ingredientes.forEach(ing => {
            const fila = document.querySelector(`select[value="${ing.id}"]`)?.closest('tr');
            if (fila) {
                const inputInclusion = fila.querySelector('input[name^="inclusion_"]');
                if (inputInclusion) {
                    inputInclusion.value = ing.inclusion.toFixed(4);
                }
            }
        });

        // Recalcular todos los valores
        calcularConOptimizacion();
    }

    /**
     * Guarda la mezcla actual
     */
    async guardarMezcla() {
        try {
            const datosMezcla = this.recopilarDatosMezcla();
            
            const response = await fetch('/guardar_mezcla', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datosMezcla)
            });

            const resultado = await response.json();

            if (resultado.success) {
                mostrarAlerta('Mezcla guardada exitosamente', 'success');
            } else {
                mostrarAlerta(resultado.message || 'Error al guardar la mezcla', 'error');
            }

        } catch (error) {
            console.error('Error al guardar:', error);
            mostrarAlerta('Error al guardar la mezcla', 'error');
        }
    }

    /**
     * Guarda la mezcla con un nuevo nombre
     */
    async guardarComo() {
        const modal = document.querySelector('#modalGuardarComo');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * Imprime la tabla actual
     */
    imprimirTabla() {
        const datosMezcla = this.recopilarDatosMezcla();
        const config = obtenerConfigUsuario();
        
        // Generar HTML para impresión
        const htmlImpresion = this.generarHTMLImpresion(datosMezcla, config);
        
        // Abrir ventana de impresión
        const ventana = window.open('', '_blank', 'width=1200,height=800');
        if (ventana) {
            ventana.document.write(htmlImpresion);
            ventana.document.close();
            ventana.focus();
            
            // Imprimir automáticamente después de cargar
            ventana.onload = () => {
                setTimeout(() => {
                    ventana.print();
                }, 500);
            };
        }
    }

    /**
     * Recopila todos los datos de la mezcla actual
     */
    recopilarDatosMezcla() {
        const config = obtenerConfigUsuario();
        
        return {
            nombre: document.querySelector('#nombre-mezcla')?.value || 'Mezcla sin nombre',
            tipo_animales: document.querySelector('#tipo-animales')?.value || '',
            etapa_produccion: document.querySelector('#etapa-produccion')?.value || '',
            observaciones: document.querySelector('#observaciones')?.value || '',
            tamano_bachada: parseFloat(document.querySelector('#tamano-bachada')?.value || 100),
            ingredientes: this.recopilarDatosOptimizacion().ingredientes,
            nutrientes: this.recopilarDatosOptimizacion().requerimientos,
            config_usuario: config
        };
    }

    /**
     * Genera HTML para impresión
     */
    generarHTMLImpresion(datos, config) {
        const fecha = new Date().toLocaleDateString();
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Formulación - ${datos.nombre}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .info { margin: 20px 0; }
                    @media print { body { margin: 0; } }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Formulación Nutricional</h1>
                    <h2>${datos.nombre}</h2>
                    <p>Generado el: ${fecha}</p>
                </div>
                
                <div class="info">
                    <p><strong>Tipo de Animales:</strong> ${datos.tipo_animales}</p>
                    <p><strong>Etapa de Producción:</strong> ${datos.etapa_produccion}</p>
                    <p><strong>Tamaño de Bachada:</strong> ${datos.tamano_bachada} ${config.unidad_medida}</p>
                    <p><strong>Observaciones:</strong> ${datos.observaciones}</p>
                </div>
                
                <!-- Aquí se agregarían las tablas de ingredientes y nutrientes -->
                
                <script>
                    window.onload = function() {
                        setTimeout(function() { window.print(); }, 500);
                    };
                </script>
            </body>
            </html>
        `;
    }

    /**
     * Muestra información de depuración
     */
    mostrarInfoDebug() {
        console.group('🔍 Formulador Modular - Info Debug');
        console.log('Versión:', this.version);
        console.log('Configuración Usuario:', obtenerConfigUsuario());
        console.log('Ingredientes Template:', window.mineralesTemplate?.length || 0);
        console.log('Nutrientes Template:', window.nutrientesTemplate?.length || 0);
        console.log('Ingredientes Precargados:', window.ingredientesPrecargados?.length || 0);
        console.groupEnd();
    }

    /**
     * Función de logging condicional
     */
    log(...args) {
        if (this.debug) {
            console.log(...args);
        }
    }

    /**
     * Destruye la instancia del formulador
     */
    destruir() {
        this.inicializado = false;
        this.log('🗑️ Formulador Modular destruido');
    }
}

// Crear instancia global
window.FormuladorModular = FormuladorModular;

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.formuladorModular = new FormuladorModular();
        window.formuladorModular.inicializar();
    });
} else {
    window.formuladorModular = new FormuladorModular();
    window.formuladorModular.inicializar();
}

// Exportar para uso como módulo
export default FormuladorModular;
