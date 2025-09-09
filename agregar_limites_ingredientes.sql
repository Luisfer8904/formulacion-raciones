-- Script para agregar columnas de límites a la tabla ingredientes
-- Fecha: 2024
-- Propósito: Permitir que los ingredientes tengan límites mínimos y máximos para optimización

USE formulacion_nutricional;

-- Verificar si las columnas ya existen antes de agregarlas
SET @exist_limite_min = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'ingredientes' 
    AND COLUMN_NAME = 'limite_min'
);

SET @exist_limite_max = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'ingredientes' 
    AND COLUMN_NAME = 'limite_max'
);

-- Agregar columna limite_min si no existe
SET @sql_min = IF(@exist_limite_min = 0, 
    'ALTER TABLE ingredientes ADD COLUMN limite_min DECIMAL(5,2) DEFAULT 0.00 COMMENT "Límite mínimo de inclusión (%)"',
    'SELECT "La columna limite_min ya existe" as mensaje'
);

PREPARE stmt_min FROM @sql_min;
EXECUTE stmt_min;
DEALLOCATE PREPARE stmt_min;

-- Agregar columna limite_max si no existe
SET @sql_max = IF(@exist_limite_max = 0, 
    'ALTER TABLE ingredientes ADD COLUMN limite_max DECIMAL(5,2) DEFAULT 100.00 COMMENT "Límite máximo de inclusión (%)"',
    'SELECT "La columna limite_max ya existe" as mensaje'
);

PREPARE stmt_max FROM @sql_max;
EXECUTE stmt_max;
DEALLOCATE PREPARE stmt_max;

-- Mostrar estructura actualizada de la tabla
DESCRIBE ingredientes;

-- Mostrar mensaje de confirmación
SELECT 
    'Migración completada exitosamente' as estado,
    'Se agregaron columnas limite_min y limite_max a la tabla ingredientes' as descripcion,
    NOW() as fecha_ejecucion;
