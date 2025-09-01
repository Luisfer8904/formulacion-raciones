-- =====================================================
-- TABLAS PARA PLANIFICADOR DE PRODUCCIÓN
-- =====================================================

USE railway;

-- Tabla bachadas (programación de producción)
CREATE TABLE IF NOT EXISTS bachadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    mezcla_id INT,
    formula_nombre VARCHAR(255) NOT NULL,
    cantidad_programada DECIMAL(10,2) NOT NULL,
    cantidad_producida DECIMAL(10,2) DEFAULT 0,
    unidad VARCHAR(20) DEFAULT 'kg',
    fecha_programada DATETIME NOT NULL,
    fecha_inicio DATETIME NULL,
    fecha_completada DATETIME NULL,
    estado ENUM('Programada', 'En Proceso', 'Completada', 'Cancelada', 'Pausada') DEFAULT 'Programada',
    prioridad ENUM('Baja', 'Normal', 'Alta', 'Urgente') DEFAULT 'Normal',
    observaciones TEXT,
    observaciones_finales TEXT,
    tiempo_estimado DECIMAL(5,2), -- horas
    tiempo_real DECIMAL(5,2), -- horas
    eficiencia DECIMAL(5,2), -- porcentaje
    costo_estimado DECIMAL(10,2),
    costo_real DECIMAL(10,2),
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (mezcla_id) REFERENCES mezclas(id) ON DELETE SET NULL,
    INDEX idx_estado (estado),
    INDEX idx_fecha_programada (fecha_programada),
    INDEX idx_usuario (usuario_id)
);

-- Tabla inventario_ingredientes (control de stock)
CREATE TABLE IF NOT EXISTS inventario_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingrediente_id INT NOT NULL,
    stock_actual DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_maximo DECIMAL(10,2) NOT NULL DEFAULT 0,
    unidad VARCHAR(20) DEFAULT 'kg',
    ubicacion VARCHAR(100),
    lote VARCHAR(50),
    fecha_vencimiento DATE,
    precio_ultima_compra DECIMAL(10,2),
    proveedor_principal VARCHAR(255),
    fecha_ultima_entrada DATETIME,
    fecha_ultima_salida DATETIME,
    estado ENUM('Disponible', 'Agotado', 'Bajo Stock', 'Vencido', 'Bloqueado') DEFAULT 'Disponible',
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_ingrediente (ingrediente_id),
    INDEX idx_estado (estado),
    INDEX idx_stock_minimo (stock_actual, stock_minimo)
);

-- Tabla movimientos_inventario (registro de entradas y salidas)
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inventario_id INT NOT NULL,
    tipo_movimiento ENUM('Entrada', 'Salida', 'Ajuste', 'Transferencia') NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    stock_anterior DECIMAL(10,2) NOT NULL,
    stock_nuevo DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(255),
    referencia VARCHAR(100), -- número de bachada, orden de compra, etc.
    bachada_id INT NULL,
    usuario_id INT NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventario_id) REFERENCES inventario_ingredientes(id) ON DELETE CASCADE,
    FOREIGN KEY (bachada_id) REFERENCES bachadas(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_inventario (inventario_id),
    INDEX idx_tipo (tipo_movimiento),
    INDEX idx_fecha (fecha_movimiento)
);

-- Tabla ordenes_produccion (órdenes de trabajo detalladas)
CREATE TABLE IF NOT EXISTS ordenes_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_orden VARCHAR(50) UNIQUE NOT NULL,
    bachada_id INT NOT NULL,
    linea_produccion VARCHAR(50),
    operador_asignado VARCHAR(100),
    supervisor VARCHAR(100),
    turno ENUM('Mañana', 'Tarde', 'Noche') DEFAULT 'Mañana',
    fecha_asignacion DATETIME NOT NULL,
    fecha_inicio_real DATETIME,
    fecha_fin_real DATETIME,
    estado ENUM('Asignada', 'En Proceso', 'Completada', 'Pausada', 'Cancelada') DEFAULT 'Asignada',
    notas_operador TEXT,
    notas_supervisor TEXT,
    calidad_aprobada BOOLEAN DEFAULT FALSE,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bachada_id) REFERENCES bachadas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_bachada (bachada_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_asignacion (fecha_asignacion)
);

-- Tabla recursos_produccion (personal y equipos)
CREATE TABLE IF NOT EXISTS recursos_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_recurso ENUM('Personal', 'Equipo', 'Linea') NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) UNIQUE,
    descripcion TEXT,
    capacidad_maxima DECIMAL(10,2), -- kg/hora para equipos, horas/día para personal
    unidad_capacidad VARCHAR(20),
    estado ENUM('Disponible', 'Ocupado', 'Mantenimiento', 'Fuera de Servicio') DEFAULT 'Disponible',
    ubicacion VARCHAR(100),
    fecha_ultimo_mantenimiento DATE,
    fecha_proximo_mantenimiento DATE,
    costo_hora DECIMAL(8,2),
    observaciones TEXT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_tipo (tipo_recurso),
    INDEX idx_estado (estado)
);

-- Tabla asignacion_recursos (asignación de recursos a bachadas)
CREATE TABLE IF NOT EXISTS asignacion_recursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bachada_id INT NOT NULL,
    recurso_id INT NOT NULL,
    fecha_asignacion DATETIME NOT NULL,
    fecha_liberacion DATETIME,
    horas_asignadas DECIMAL(5,2),
    horas_utilizadas DECIMAL(5,2),
    costo_total DECIMAL(10,2),
    estado ENUM('Asignado', 'En Uso', 'Liberado', 'Cancelado') DEFAULT 'Asignado',
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bachada_id) REFERENCES bachadas(id) ON DELETE CASCADE,
    FOREIGN KEY (recurso_id) REFERENCES recursos_produccion(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_bachada (bachada_id),
    INDEX idx_recurso (recurso_id),
    INDEX idx_estado (estado)
);

-- Tabla actividades_produccion (registro detallado de actividades)
CREATE TABLE IF NOT EXISTS actividades_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bachada_id INT NOT NULL,
    orden_id INT,
    tipo_actividad ENUM('Preparacion', 'Mezclado', 'Control Calidad', 'Empaque', 'Limpieza', 'Mantenimiento', 'Pausa') NOT NULL,
    descripcion TEXT,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    duracion_minutos INT,
    operador VARCHAR(100),
    observaciones TEXT,
    parametros_calidad JSON, -- para almacenar datos de control de calidad
    estado ENUM('En Proceso', 'Completada', 'Pausada', 'Cancelada') DEFAULT 'En Proceso',
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bachada_id) REFERENCES bachadas(id) ON DELETE CASCADE,
    FOREIGN KEY (orden_id) REFERENCES ordenes_produccion(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_bachada (bachada_id),
    INDEX idx_tipo (tipo_actividad),
    INDEX idx_fecha_inicio (fecha_inicio)
);

-- Tabla alertas_inventario (sistema de alertas)
CREATE TABLE IF NOT EXISTS alertas_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inventario_id INT NOT NULL,
    tipo_alerta ENUM('Stock Bajo', 'Agotado', 'Vencimiento Proximo', 'Vencido', 'Reposicion Programada') NOT NULL,
    nivel_prioridad ENUM('Baja', 'Media', 'Alta', 'Critica') DEFAULT 'Media',
    mensaje TEXT NOT NULL,
    fecha_alerta DATETIME NOT NULL,
    fecha_vencimiento DATETIME, -- para alertas de vencimiento
    cantidad_sugerida DECIMAL(10,2), -- cantidad sugerida para reposición
    estado ENUM('Activa', 'Leida', 'Resuelta', 'Ignorada') DEFAULT 'Activa',
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP NULL,
    FOREIGN KEY (inventario_id) REFERENCES inventario_ingredientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_inventario (inventario_id),
    INDEX idx_tipo (tipo_alerta),
    INDEX idx_estado (estado),
    INDEX idx_prioridad (nivel_prioridad)
);

-- Tabla reportes_produccion (reportes generados)
CREATE TABLE IF NOT EXISTS reportes_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_reporte VARCHAR(50) UNIQUE NOT NULL,
    tipo_reporte ENUM('Diario', 'Semanal', 'Mensual', 'Personalizado', 'Eficiencia', 'Costos') NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    parametros JSON, -- parámetros del reporte
    datos_reporte JSON, -- datos calculados del reporte
    archivo_generado VARCHAR(255), -- ruta del archivo si se guarda
    estado ENUM('Generando', 'Completado', 'Error') DEFAULT 'Generando',
    usuario_id INT NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_tipo (tipo_reporte),
    INDEX idx_usuario (usuario_id),
    INDEX idx_fecha_generacion (fecha_generacion)
);

-- =====================================================
-- DATOS DE EJEMPLO PARA TESTING
-- =====================================================

-- Insertar recursos de producción de ejemplo
INSERT IGNORE INTO recursos_produccion (tipo_recurso, nombre, codigo, descripcion, capacidad_maxima, unidad_capacidad, estado, ubicacion, costo_hora, usuario_id) VALUES
('Linea', 'Línea de Producción 1', 'LP-001', 'Línea principal de mezclado', 500.00, 'kg/hora', 'Disponible', 'Planta Principal - Sector A', 25.00, 1),
('Linea', 'Línea de Producción 2', 'LP-002', 'Línea secundaria de mezclado', 300.00, 'kg/hora', 'Disponible', 'Planta Principal - Sector B', 20.00, 1),
('Linea', 'Línea de Producción 3', 'LP-003', 'Línea de productos especiales', 200.00, 'kg/hora', 'Mantenimiento', 'Planta Principal - Sector C', 30.00, 1),
('Equipo', 'Mezcladora Industrial A', 'MZ-001', 'Mezcladora de alta capacidad', 1000.00, 'kg/batch', 'Disponible', 'Línea 1', 15.00, 1),
('Equipo', 'Mezcladora Industrial B', 'MZ-002', 'Mezcladora de capacidad media', 750.00, 'kg/batch', 'Disponible', 'Línea 2', 12.00, 1),
('Equipo', 'Empacadora Automática', 'EP-001', 'Empacadora de sacos automática', 100.00, 'sacos/hora', 'Ocupado', 'Área de Empaque', 8.00, 1),
('Personal', 'Juan Pérez', 'OP-001', 'Operador Senior Línea 1', 8.00, 'horas/día', 'Disponible', 'Línea 1', 12.50, 1),
('Personal', 'María González', 'OP-002', 'Operadora Línea 2', 8.00, 'horas/día', 'Disponible', 'Línea 2', 11.00, 1),
('Personal', 'Carlos Rodríguez', 'SV-001', 'Supervisor de Producción', 8.00, 'horas/día', 'Disponible', 'Supervisión', 18.00, 1),
('Personal', 'Ana Martínez', 'CC-001', 'Control de Calidad', 8.00, 'horas/día', 'Disponible', 'Laboratorio', 15.00, 1);

-- Insertar inventario de ingredientes de ejemplo (basado en ingredientes existentes)
INSERT IGNORE INTO inventario_ingredientes (ingrediente_id, stock_actual, stock_minimo, stock_maximo, unidad, ubicacion, estado, usuario_id) 
SELECT 
    i.id,
    CASE 
        WHEN i.nombre LIKE '%Maíz%' THEN 1500.00
        WHEN i.nombre LIKE '%Soya%' THEN 800.00
        WHEN i.nombre LIKE '%Harina%' THEN 200.00
        WHEN i.nombre LIKE '%Aceite%' THEN 150.00
        ELSE 500.00
    END as stock_actual,
    CASE 
        WHEN i.nombre LIKE '%Maíz%' THEN 500.00
        WHEN i.nombre LIKE '%Soya%' THEN 300.00
        WHEN i.nombre LIKE '%Harina%' THEN 100.00
        WHEN i.nombre LIKE '%Aceite%' THEN 50.00
        ELSE 100.00
    END as stock_minimo,
    CASE 
        WHEN i.nombre LIKE '%Maíz%' THEN 3000.00
        WHEN i.nombre LIKE '%Soya%' THEN 2000.00
        WHEN i.nombre LIKE '%Harina%' THEN 500.00
        WHEN i.nombre LIKE '%Aceite%' THEN 300.00
        ELSE 1000.00
    END as stock_maximo,
    'kg' as unidad,
    'Bodega Principal' as ubicacion,
    CASE 
        WHEN i.nombre LIKE '%Harina de Pescado%' THEN 'Agotado'
        WHEN i.nombre LIKE '%Maíz%' AND RAND() < 0.3 THEN 'Bajo Stock'
        ELSE 'Disponible'
    END as estado,
    1 as usuario_id
FROM ingredientes i 
WHERE i.usuario_id = 1
LIMIT 20;

-- Insertar bachadas de ejemplo
INSERT IGNORE INTO bachadas (codigo, nombre, formula_nombre, cantidad_programada, fecha_programada, estado, prioridad, observaciones, tiempo_estimado, costo_estimado, usuario_id) VALUES
('BCH-001', 'Pollo Engorde Inicial - Lote 001', 'Pollo Engorde Inicial', 500.00, DATE_ADD(NOW(), INTERVAL 2 HOUR), 'En Proceso', 'Alta', 'Bachada prioritaria para cliente especial', 4.5, 625.00, 1),
('BCH-002', 'Cerdo Crecimiento - Lote 002', 'Cerdo Crecimiento Premium', 750.00, DATE_ADD(NOW(), INTERVAL 1 DAY), 'Programada', 'Normal', 'Producción regular', 5.2, 1087.50, 1),
('BCH-003', 'Gallina Postura - Lote 003', 'Gallina Postura Comercial', 300.00, DATE_ADD(NOW(), INTERVAL 2 DAY), 'Programada', 'Normal', 'Pedido mensual', 3.8, 405.00, 1),
('BCH-004', 'Bovino Engorde - Lote 004', 'Bovino Engorde Intensivo', 1000.00, DATE_ADD(NOW(), INTERVAL 3 DAY), 'Programada', 'Baja', 'Producción de reserva', 6.5, 1550.00, 1),
('BCH-005', 'Pollo Finalizador - Lote 005', 'Pollo Finalizador', 600.00, DATE_ADD(NOW(), INTERVAL 4 DAY), 'Programada', 'Normal', 'Segundo lote del mes', 4.8, 780.00, 1);

-- Insertar alertas de inventario de ejemplo
INSERT IGNORE INTO alertas_inventario (inventario_id, tipo_alerta, nivel_prioridad, mensaje, fecha_alerta, estado, usuario_id)
SELECT 
    ii.id,
    CASE 
        WHEN ii.stock_actual = 0 THEN 'Agotado'
        WHEN ii.stock_actual <= ii.stock_minimo THEN 'Stock Bajo'
        ELSE 'Reposicion Programada'
    END as tipo_alerta,
    CASE 
        WHEN ii.stock_actual = 0 THEN 'Critica'
        WHEN ii.stock_actual <= ii.stock_minimo THEN 'Alta'
        ELSE 'Media'
    END as nivel_prioridad,
    CASE 
        WHEN ii.stock_actual = 0 THEN CONCAT('URGENTE: ', i.nombre, ' está agotado. Reposición inmediata requerida.')
        WHEN ii.stock_actual <= ii.stock_minimo THEN CONCAT('ALERTA: ', i.nombre, ' tiene stock bajo (', ii.stock_actual, ' kg restantes)')
        ELSE CONCAT('INFO: Programar reposición de ', i.nombre)
    END as mensaje,
    NOW() as fecha_alerta,
    'Activa' as estado,
    1 as usuario_id
FROM inventario_ingredientes ii
JOIN ingredientes i ON ii.ingrediente_id = i.id
WHERE ii.stock_actual <= ii.stock_minimo OR ii.estado = 'Agotado'
LIMIT 10;

-- Crear índices adicionales para optimización
CREATE INDEX idx_bachadas_fecha_estado ON bachadas(fecha_programada, estado);
CREATE INDEX idx_inventario_stock_estado ON inventario_ingredientes(stock_actual, estado);
CREATE INDEX idx_alertas_fecha_prioridad ON alertas_inventario(fecha_alerta, nivel_prioridad);

-- =====================================================
-- VISTAS ÚTILES PARA REPORTES
-- =====================================================

-- Vista resumen de bachadas
CREATE OR REPLACE VIEW vista_resumen_bachadas AS
SELECT 
    b.id,
    b.codigo,
    b.nombre,
    b.formula_nombre,
    b.cantidad_programada,
    b.cantidad_producida,
    b.fecha_programada,
    b.fecha_completada,
    b.estado,
    b.prioridad,
    b.eficiencia,
    CASE 
        WHEN b.fecha_completada IS NOT NULL THEN 
            TIMESTAMPDIFF(HOUR, b.fecha_inicio, b.fecha_completada)
        ELSE NULL 
    END as horas_produccion,
    b.costo_estimado,
    b.costo_real,
    u.nombre as usuario_nombre
FROM bachadas b
JOIN usuarios u ON b.usuario_id = u.id;

-- Vista alertas críticas
CREATE OR REPLACE VIEW vista_alertas_criticas AS
SELECT 
    a.id,
    i.nombre as ingrediente,
    ii.stock_actual,
    ii.stock_minimo,
    a.tipo_alerta,
    a.nivel_prioridad,
    a.mensaje,
    a.fecha_alerta,
    a.estado
FROM alertas_inventario a
JOIN inventario_ingredientes ii ON a.inventario_id = ii.id
JOIN ingredientes i ON ii.ingrediente_id = i.id
WHERE a.estado = 'Activa' AND a.nivel_prioridad IN ('Alta', 'Critica')
ORDER BY a.nivel_prioridad DESC, a.fecha_alerta ASC;

-- Vista eficiencia de producción
CREATE OR REPLACE VIEW vista_eficiencia_produccion AS
SELECT 
    DATE(b.fecha_programada) as fecha,
    COUNT(*) as total_bachadas,
    SUM(CASE WHEN b.estado = 'Completada' THEN 1 ELSE 0 END) as completadas,
    SUM(b.cantidad_programada) as cantidad_programada_total,
    SUM(b.cantidad_producida) as cantidad_producida_total,
    AVG(b.eficiencia) as eficiencia_promedio,
    SUM(b.tiempo_estimado) as tiempo_estimado_total,
    SUM(b.tiempo_real) as tiempo_real_total
FROM bachadas b
WHERE b.fecha_programada >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(b.fecha_programada)
ORDER BY fecha DESC;

COMMIT;

-- Mensaje de confirmación
SELECT 'Tablas del Planificador de Producción creadas exitosamente' as mensaje;
