-- Script final para agregar la columna 'especie' a la tabla requerimientos
-- Ejecutar este comando en Railway MySQL

USE railway;

-- Verificar estructura actual
DESCRIBE requerimientos;

-- Agregar la columna 'especie' si no existe
ALTER TABLE requerimientos 
ADD COLUMN IF NOT EXISTS especie VARCHAR(50) DEFAULT NULL AFTER nombre;

-- Actualizar registros existentes basándose en tipo_especie
UPDATE requerimientos 
SET especie = CASE 
    -- Pollo y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(pollo|gallina|ave|broiler|chicken)' THEN 'Pollo'
    -- Cerdo y variaciones  
    WHEN LOWER(tipo_especie) REGEXP '(cerdo|cochino|porcino|pig|swine)' THEN 'Cerdo'
    -- Bovino y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(bovino|vaca|toro|res|cattle|beef)' THEN 'Bovino'
    -- Ovino y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(ovino|oveja|carnero|sheep)' THEN 'Ovino'
    -- Caprino y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(caprino|cabra|chivo|goat)' THEN 'Caprino'
    -- Peces y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(pez|pescado|fish|tilapia|salmon|trucha)' THEN 'Peces'
    -- Conejo y variaciones
    WHEN LOWER(tipo_especie) REGEXP '(conejo|rabbit)' THEN 'Conejos'
    -- Si no coincide, usar 'General'
    ELSE 'General'
END
WHERE especie IS NULL;

-- Verificar resultados
SELECT id, nombre, especie, tipo_especie, comentario FROM requerimientos;

-- Mostrar estructura final
DESCRIBE requerimientos;

-- Mostrar estadísticas
SELECT especie, COUNT(*) as cantidad FROM requerimientos GROUP BY especie;
