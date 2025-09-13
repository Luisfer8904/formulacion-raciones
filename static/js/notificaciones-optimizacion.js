/**
 * Sistema de Notificaciones para Optimización de Fórmulas
 * Maneja notificaciones modales y toast para mostrar resultados de optimización
 */

class NotificacionesOptimizacion {
    constructor() {
        this.initializeToastContainer();
    }

    /**
     * Inicializar contenedor de notificaciones toast
     */
    initializeToastContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
    }

    /**
     * Mostrar notificación modal detallada
     * @param {Object} notificacion - Datos de la notificación
     */
    mostrarModal(notificacion) {
        // Crear overlay si no existe
        let overlay = document.getElementById('notification-overlay');
        if (!overlay) {
            overlay = this.crearOverlay();
        }

        // Crear contenido del modal
        const modal = overlay.querySelector('.notification-modal');
        modal.innerHTML = this.generarContenidoModal(notificacion);

        // Mostrar modal
        overlay.classList.add('show');

        // Agregar event listeners
        this.agregarEventListeners(overlay);

        // Auto-cerrar después de 10 segundos si es éxito
        if (notificacion.tipo === 'exito') {
            setTimeout(() => {
                this.cerrarModal();
            }, 10000);
        }
    }

    /**
     * Crear overlay del modal
     */
    crearOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'notification-overlay';
        overlay.className = 'notification-overlay';
        overlay.innerHTML = `
            <div class="notification-modal">
                <!-- Contenido se genera dinámicamente -->
            </div>
        `;
        document.body.appendChild(overlay);
        return overlay;
    }

    /**
     * Generar contenido HTML del modal
     * @param {Object} notificacion - Datos de la notificación
     */
    generarContenidoModal(notificacion) {
        const tipoClass = `notification-${notificacion.tipo}`;
        
        let detallesHtml = '';
        if (notificacion.detalles) {
            detallesHtml = `
                <div class="notification-details">
                    <h4>📊 Detalles de la Optimización</h4>
                    ${Object.entries(notificacion.detalles).map(([key, value]) => `
                        <div class="detail-item">
                            <span class="detail-label">${this.formatearEtiqueta(key)}:</span>
                            <span class="detail-value">${this.formatearValor(key, value)}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        let sugerenciasHtml = '';
        if (notificacion.sugerencias && notificacion.sugerencias.length > 0) {
            sugerenciasHtml = `
                <div class="notification-suggestions">
                    <h4>💡 Información Adicional</h4>
                    <ul class="suggestion-list">
                        ${notificacion.sugerencias.map(sugerencia => `
                            <li class="suggestion-item">${sugerencia}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        return `
            <div class="notification-header ${tipoClass}">
                <h3 class="notification-title">${notificacion.titulo}</h3>
                <button class="notification-close" onclick="notificaciones.cerrarModal()">×</button>
            </div>
            <div class="notification-body">
                <div class="notification-message">${notificacion.mensaje}</div>
                ${detallesHtml}
                ${sugerenciasHtml}
            </div>
            <div class="notification-footer">
                <button class="notification-btn notification-btn-primary" onclick="notificaciones.cerrarModal()">
                    Entendido
                </button>
            </div>
        `;
    }

    /**
     * Mostrar notificación toast (esquina superior derecha)
     * @param {string} titulo - Título de la notificación
     * @param {string} mensaje - Mensaje de la notificación
     * @param {string} tipo - Tipo: 'exito', 'error', 'warning'
     * @param {number} duracion - Duración en ms (default: 5000)
     */
    mostrarToast(titulo, mensaje, tipo = 'exito', duracion = 5000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        const toastId = 'toast-' + Date.now();
        
        toast.id = toastId;
        toast.className = `toast-notification toast-${tipo}`;
        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-title">${titulo}</div>
                <button class="toast-close" onclick="notificaciones.cerrarToast('${toastId}')">×</button>
            </div>
            <div class="toast-message">${mensaje}</div>
        `;

        container.appendChild(toast);

        // Mostrar con animación
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // Auto-cerrar
        setTimeout(() => {
            this.cerrarToast(toastId);
        }, duracion);
    }

    /**
     * Cerrar modal
     */
    cerrarModal() {
        const overlay = document.getElementById('notification-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }

    /**
     * Cerrar toast específico
     * @param {string} toastId - ID del toast a cerrar
     */
    cerrarToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    /**
     * Agregar event listeners al modal
     * @param {HTMLElement} overlay - Elemento overlay
     */
    agregarEventListeners(overlay) {
        // Cerrar al hacer clic fuera del modal
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.cerrarModal();
            }
        });

        // Cerrar con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cerrarModal();
            }
        });
    }

    /**
     * Formatear etiquetas para mostrar
     * @param {string} key - Clave del detalle
     */
    formatearEtiqueta(key) {
        const etiquetas = {
            'metodo_usado': 'Método utilizado',
            'costo_total': 'Costo total',
            'ingredientes_usados': 'Ingredientes principales',
            'suma_verificada': 'Suma verificada',
            'restricciones_cumplidas': 'Restricciones aplicadas',
            'suma_actual': 'Suma actual',
            'suma_requerida': 'Suma requerida',
            'deficit': 'Déficit',
            'suma_maxima': 'Suma máxima',
            'exceso': 'Exceso'
        };
        return etiquetas[key] || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Formatear valores para mostrar
     * @param {string} key - Clave del detalle
     * @param {any} value - Valor a formatear
     */
    formatearValor(key, value) {
        if (key.includes('costo')) {
            return `$${parseFloat(value).toFixed(2)}`;
        }
        if (key.includes('suma') || key.includes('deficit') || key.includes('exceso')) {
            return `${parseFloat(value).toFixed(1)}%`;
        }
        if (key === 'ingredientes_usados') {
            return `${value} ingrediente${value !== 1 ? 's' : ''}`;
        }
        if (key === 'restricciones_cumplidas') {
            return `${value} restricción${value !== 1 ? 'es' : ''}`;
        }
        return value;
    }

    /**
     * Procesar respuesta de optimización y mostrar notificación apropiada
     * @param {Object} respuesta - Respuesta del backend
     */
    procesarRespuestaOptimizacion(respuesta) {
        if (respuesta.exito && respuesta.notificacion) {
            // Determinar tipo de toast basado en si es aproximada
            let tipoToast = 'exito';
            let tituloToast = '✅ Optimización Exitosa';
            
            if (respuesta.aproximada) {
                // Es una optimización aproximada
                if (respuesta.notificacion.tipo === 'aproximada_buena') {
                    tipoToast = 'warning';
                    tituloToast = '⚠️ Optimización Aproximada';
                } else if (respuesta.notificacion.tipo === 'aproximada_limitada') {
                    tipoToast = 'warning';
                    tituloToast = '⚠️ Aproximación Limitada';
                }
            }
            
            // Mostrar modal detallado
            this.mostrarModal(respuesta.notificacion);
            
            // También mostrar toast rápido
            this.mostrarToast(
                tituloToast,
                `Costo: $${respuesta.costo_total}${respuesta.aproximada ? ' (Aproximado)' : ''}`,
                tipoToast,
                respuesta.aproximada ? 5000 : 3000
            );
        } else if (respuesta.error) {
            // Mostrar notificación de error
            const notificacionError = {
                tipo: 'error',
                titulo: '❌ Error en Optimización',
                mensaje: respuesta.error,
                detalles: respuesta.validacion?.detalles || null,
                sugerencias: respuesta.validacion?.sugerencias || [
                    'Revise los datos ingresados',
                    'Verifique que todos los campos estén completos',
                    'Contacte soporte si el problema persiste'
                ]
            };
            
            this.mostrarModal(notificacionError);
            
            // Toast de error
            this.mostrarToast(
                '❌ Error',
                respuesta.validacion?.mensaje || respuesta.error,
                'error',
                7000
            );
        }
    }

    /**
     * Mostrar notificación de validación específica
     * @param {Object} validacion - Datos de validación del backend
     */
    mostrarValidacion(validacion) {
        const tiposIconos = {
            'datos_incompletos': '📝',
            'limites_maximos_insuficientes': '⚠️',
            'limites_minimos_excesivos': '🚫',
            'limites_inconsistentes': '⚖️',
            'optimizacion_fallida': '❌',
            'optimizacion_fallida_detallada': '🔬'
        };

        // Si es análisis detallado, usar modal especializado
        if (validacion.tipo === 'optimizacion_fallida_detallada') {
            this.mostrarAnalisisDetallado(validacion);
            return;
        }

        const notificacion = {
            tipo: 'error',
            titulo: `${tiposIconos[validacion.tipo] || '⚠️'} ${validacion.tipo.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
            mensaje: validacion.mensaje,
            detalles: validacion.detalles || null,
            sugerencias: validacion.sugerencias || []
        };

        this.mostrarModal(notificacion);
    }

    /**
     * Mostrar análisis detallado de falla en optimización
     * @param {Object} validacion - Datos de validación detallada
     */
    mostrarAnalisisDetallado(validacion) {
        console.log('🔬 Mostrando análisis detallado:', validacion);
        
        // Crear overlay si no existe
        let overlay = document.getElementById('notification-overlay');
        if (!overlay) {
            overlay = this.crearOverlay();
        }

        // Crear contenido especializado
        const modal = overlay.querySelector('.notification-modal');
        modal.innerHTML = this.generarAnalisisDetallado(validacion);

        // Mostrar modal
        overlay.classList.add('show');

        // Agregar event listeners específicos
        this.agregarEventListenersAnalisis(overlay);
    }

    /**
     * Generar HTML para análisis detallado
     * @param {Object} validacion - Datos de validación
     */
    generarAnalisisDetallado(validacion) {
        return `
            <div class="notification-header notification-error">
                <h3 class="notification-title">🔬 Análisis Detallado de Optimización</h3>
                <button class="notification-close" onclick="notificaciones.cerrarModal()">×</button>
            </div>
            <div class="notification-body analisis-detallado">
                <div class="analisis-tabs">
                    <button class="tab-btn active" data-tab="nutrientes">🧪 Nutrientes</button>
                    <button class="tab-btn" data-tab="aportes">📊 Aportes Actuales</button>
                    <button class="tab-btn" data-tab="sugerencias">💡 Sugerencias</button>
                </div>
                <div class="tab-content">
                    <div id="tab-nutrientes" class="tab-panel active">
                        ${this.generarTabNutrientes(validacion)}
                    </div>
                    <div id="tab-aportes" class="tab-panel">
                        ${this.generarTabAportes(validacion)}
                    </div>
                    <div id="tab-sugerencias" class="tab-panel">
                        ${this.generarTabSugerencias(validacion)}
                    </div>
                </div>
            </div>
            <div class="notification-footer">
                <button class="notification-btn notification-btn-primary" onclick="notificaciones.cerrarModal()">
                    Entendido
                </button>
            </div>
        `;
    }

    /**
     * Generar tab de nutrientes problemáticos
     */
    generarTabNutrientes(validacion) {
        let html = '<div class="nutrientes-analisis">';
        
        // Nutrientes sin aporte
        if (validacion.nutrientes_sin_aporte && validacion.nutrientes_sin_aporte.length > 0) {
            html += `
                <div class="seccion-critica">
                    <h4>🚨 Nutrientes Sin Aporte (${validacion.nutrientes_sin_aporte.length})</h4>
                    <p class="seccion-descripcion">Estos nutrientes no tienen ningún ingrediente que los aporte:</p>
                    <div class="nutrientes-lista">
            `;
            
            validacion.nutrientes_sin_aporte.forEach(nutriente => {
                html += `
                    <div class="nutriente-item critico">
                        <div class="nutriente-nombre">${nutriente.nutriente}</div>
                        <div class="nutriente-valores">
                            <span class="requerido">Requerido: ${nutriente.requerimiento.toFixed(4)}</span>
                            <span class="actual">Actual: ${nutriente.aporte_actual.toFixed(4)}</span>
                            <span class="deficit">Déficit: ${nutriente.deficit.toFixed(4)}</span>
                        </div>
                        <div class="nutriente-accion">
                            ❌ Ningún ingrediente aporta este nutriente
                        </div>
                    </div>
                `;
            });
            
            html += '</div></div>';
        }
        
        // Nutrientes deficientes
        if (validacion.nutrientes_deficientes && validacion.nutrientes_deficientes.length > 0) {
            html += `
                <div class="seccion-advertencia">
                    <h4>⚠️ Nutrientes Deficientes (${validacion.nutrientes_deficientes.length})</h4>
                    <p class="seccion-descripcion">Estos nutrientes tienen aportes insuficientes:</p>
                    <div class="nutrientes-lista">
            `;
            
            validacion.nutrientes_deficientes.forEach(nutriente => {
                const porcentaje_cumplimiento = (nutriente.aporte_actual / nutriente.requerimiento * 100).toFixed(1);
                html += `
                    <div class="nutriente-item deficiente">
                        <div class="nutriente-nombre">${nutriente.nutriente}</div>
                        <div class="nutriente-valores">
                            <span class="requerido">Requerido: ${nutriente.requerimiento.toFixed(4)}</span>
                            <span class="actual">Actual: ${nutriente.aporte_actual.toFixed(4)} (${porcentaje_cumplimiento}%)</span>
                            <span class="deficit">Déficit: ${nutriente.deficit.toFixed(4)}</span>
                        </div>
                        <div class="nutriente-accion">
                            ✅ ${nutriente.ingredientes_disponibles} ingrediente(s) disponible(s)
                        </div>
                    </div>
                `;
            });
            
            html += '</div></div>';
        }

        if ((!validacion.nutrientes_sin_aporte || validacion.nutrientes_sin_aporte.length === 0) && 
            (!validacion.nutrientes_deficientes || validacion.nutrientes_deficientes.length === 0)) {
            html += '<div class="sin-problemas">✅ No se detectaron problemas específicos con nutrientes</div>';
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Generar tab de aportes actuales
     */
    generarTabAportes(validacion) {
        let html = '<div class="aportes-analisis">';
        
        if (validacion.aportes_actuales) {
            html += '<h4>📊 Aportes Actuales por Nutriente</h4>';
            html += '<p class="seccion-descripcion">Análisis con distribución uniforme de ingredientes:</p>';
            
            Object.keys(validacion.aportes_actuales).forEach(nutriente => {
                const aporte = validacion.aportes_actuales[nutriente];
                const estado = aporte.deficit > 0 ? 'deficiente' : 'suficiente';
                
                html += `
                    <div class="aporte-nutriente ${estado}">
                        <div class="aporte-header">
                            <h5>${nutriente}</h5>
                            <span class="estado-badge ${estado}">${estado.toUpperCase()}</span>
                        </div>
                        <div class="aporte-valores">
                            <div class="valor-item">
                                <label>Aporte Total:</label>
                                <span>${aporte.aporte_total.toFixed(4)}</span>
                            </div>
                            ${aporte.requerimiento_min ? `
                                <div class="valor-item">
                                    <label>Requerimiento Mín:</label>
                                    <span>${aporte.requerimiento_min.toFixed(4)}</span>
                                </div>
                            ` : ''}
                            ${aporte.deficit > 0 ? `
                                <div class="valor-item deficit">
                                    <label>Déficit:</label>
                                    <span>${aporte.deficit.toFixed(4)}</span>
                                </div>
                            ` : ''}
                        </div>
                        ${aporte.ingredientes_que_aportan.length > 0 ? `
                            <div class="ingredientes-aporte">
                                <label>Ingredientes que aportan:</label>
                                <ul>
                                    ${aporte.ingredientes_que_aportan.slice(0, 5).map(ing => 
                                        `<li>${ing.nombre}: ${ing.valor_base.toFixed(2)} → ${ing.aporte.toFixed(4)}</li>`
                                    ).join('')}
                                    ${aporte.ingredientes_que_aportan.length > 5 ? 
                                        `<li><em>... y ${aporte.ingredientes_que_aportan.length - 5} más</em></li>` : ''}
                                </ul>
                            </div>
                        ` : '<div class="sin-ingredientes">❌ Ningún ingrediente aporta este nutriente</div>'}
                    </div>
                `;
            });
        } else {
            html += '<div class="sin-datos">No hay datos de aportes disponibles</div>';
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Generar tab de sugerencias
     */
    generarTabSugerencias(validacion) {
        let html = '<div class="sugerencias-analisis">';
        
        if (validacion.causas_principales && validacion.causas_principales.length > 0) {
            html += `
                <div class="causas-principales">
                    <h4>🎯 Causas Principales</h4>
                    <ul>
                        ${validacion.causas_principales.map(causa => `<li>${causa}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (validacion.sugerencias_especificas && validacion.sugerencias_especificas.length > 0) {
            html += `
                <div class="sugerencias-especificas">
                    <h4>💡 Sugerencias Específicas</h4>
                    <ul>
                        ${validacion.sugerencias_especificas.map(sugerencia => `<li>${sugerencia}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if ((!validacion.causas_principales || validacion.causas_principales.length === 0) && 
            (!validacion.sugerencias_especificas || validacion.sugerencias_especificas.length === 0)) {
            html += '<div class="sin-sugerencias">No hay sugerencias específicas disponibles</div>';
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Agregar event listeners específicos para análisis detallado
     */
    agregarEventListenersAnalisis(overlay) {
        // Event listeners básicos
        this.agregarEventListeners(overlay);

        // Event listeners para tabs
        overlay.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.cambiarTab(overlay, tabName);
            });
        });
    }

    /**
     * Cambiar tab activa
     */
    cambiarTab(container, tabName) {
        // Desactivar todas las tabs
        container.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        container.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        
        // Activar la tab seleccionada
        container.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        container.querySelector(`#tab-${tabName}`).classList.add('active');
    }
}

// Instancia global
const notificaciones = new NotificacionesOptimizacion();

// Exportar para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificacionesOptimizacion;
}
