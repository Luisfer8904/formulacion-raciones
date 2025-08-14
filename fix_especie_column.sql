-- Script para arreglar la columna 'especie' en la tabla requerimientos
-- Ejecutar este script en Railway MySQL

USE railway;

-- Verificar estructura actual
DESCRIBE requerimientos;

-- Agregar la columna 'especie' con valor por defecto
ALTER TABLE requerimientos 
ADD COLUMN especie VARCHAR(50) DEFAULT 'General' AFTER nombre;

-- Actualizar registros existentes para que tengan un valor en 'especie'
UPDATE requerimientos 
SET especie = CASE 
    WHEN tipo_especie LIKE '%Pollo%' OR tipo_especie LIKE '%pollo%' THEN 'Pollo'
    WHEN tipo_especie LIKE '%Cerdo%' OR tipo_especie LIKE '%cerdo%' THEN 'Cerdo'
    WHEN tipo_especie LIKE '%Bovino%' OR tipo_especie LIKE '%bovino%' OR tipo_especie LIKE '%Bovinos%' THEN 'Bovino'
    WHEN tipo_especie LIKE '%Ovino%' OR tipo_especie LIKE '%ovino%' THEN 'Ovino'
    WHEN tipo_especie LIKE '%Caprino%' OR tipo_especie LIKE '%caprino%' THEN 'Caprino'
    ELSE 'General'
END;

-- Verificar que los cambios se aplicaron correctamente
SELECT id, nombre, especie, tipo_especie, comentario FROM requerimientos;

-- Mostrar estructura final
DESCRIBE requerimientos;
