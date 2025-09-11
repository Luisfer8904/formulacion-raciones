-- Script para completar la implementación de límites en formulacion_ingredientes
-- Solo agrega las columnas faltantes

USE formulacion_nutricional;

-- Verificar si las columnas ya existen antes de agregarlas
SET @sql = '';

-- Verificar y agregar limite_min a formulacion_ingredientes
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.columns 
WHERE table_schema = 'formulacion_nutricional' 
AND table_name = 'formulacion_ingredientes' 
AND column_name = 'limite_min';

SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE formulacion_ingredientes ADD COLUMN limite_min DECIMAL(10,4) DEFAULT 0 COMMENT "Límite mínimo de inclusión del ingrediente (%)";',
    'SELECT "Columna limite_min ya existe en formulacion_ingredientes" as mensaje;'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verificar y agregar limite_max a formulacion_ingredientes
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.columns 
WHERE table_schema = 'formulacion_nutricional' 
AND table_name = 'formulacion_ingredientes' 
AND column_name = 'limite_max';

SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE formulacion_ingredientes ADD COLUMN limite_max DECIMAL(10,4) DEFAULT 100 COMMENT "Límite máximo de inclusión del ingrediente (%)";',
    'SELECT "Columna limite_max ya existe en formulacion_ingredientes" as mensaje;'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verificar el resultado
SELECT 'Verificando columnas agregadas a formulacion_ingredientes:' as mensaje;
DESCRIBE formulacion_ingredientes;

SELECT 'Implementación de límites completada exitosamente.' as resultado;
