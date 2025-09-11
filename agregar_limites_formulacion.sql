-- Script para agregar columnas de límites a las tablas de formulación
-- Ejecutar este script para implementar el guardado de límites de ingredientes

USE formulacion_nutricional;

-- 1. Agregar columnas de límites a la tabla formulacion_ingredientes
ALTER TABLE formulacion_ingredientes 
ADD COLUMN limite_min DECIMAL(10,4) DEFAULT 0 COMMENT 'Límite mínimo de inclusión del ingrediente (%)',
ADD COLUMN limite_max DECIMAL(10,4) DEFAULT 100 COMMENT 'Límite máximo de inclusión del ingrediente (%)';

-- 2. Agregar columnas de límites a la tabla mezcla_ingredientes
ALTER TABLE mezcla_ingredientes 
ADD COLUMN limite_min DECIMAL(10,4) DEFAULT 0 COMMENT 'Límite mínimo de inclusión del ingrediente (%)',
ADD COLUMN limite_max DECIMAL(10,4) DEFAULT 100 COMMENT 'Límite máximo de inclusión del ingrediente (%)';

-- 3. Crear tabla opcional para histórico detallado de límites de nutrientes
-- (Los límites de nutrientes ya se guardan en formulacion_requerimientos, 
--  pero esta tabla permite un histórico más detallado)
CREATE TABLE IF NOT EXISTS formulacion_limites_nutrientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    formulacion_id INT NOT NULL,
    nutriente_id INT NOT NULL,
    limite_min DECIMAL(10,4) DEFAULT NULL COMMENT 'Límite mínimo del nutriente',
    limite_max DECIMAL(10,4) DEFAULT NULL COMMENT 'Límite máximo del nutriente',
    valor_obtenido DECIMAL(10,4) DEFAULT NULL COMMENT 'Valor obtenido en la optimización',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (formulacion_id) REFERENCES formulaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id) ON DELETE CASCADE,
    INDEX idx_formulacion_nutriente (formulacion_id, nutriente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4. Verificar las modificaciones
SELECT 'Verificando columnas agregadas a formulacion_ingredientes:' as mensaje;
DESCRIBE formulacion_ingredientes;

SELECT 'Verificando columnas agregadas a mezcla_ingredientes:' as mensaje;
DESCRIBE mezcla_ingredientes;

SELECT 'Verificando tabla formulacion_limites_nutrientes creada:' as mensaje;
DESCRIBE formulacion_limites_nutrientes;

-- 5. Actualizar registros existentes con valores por defecto (opcional)
-- UPDATE formulacion_ingredientes SET limite_min = 0, limite_max = 100 WHERE limite_min IS NULL;
-- UPDATE mezcla_ingredientes SET limite_min = 0, limite_max = 100 WHERE limite_min IS NULL;

SELECT 'Script ejecutado exitosamente. Las tablas han sido modificadas para soportar límites de ingredientes.' as resultado;
