-- Script para arreglar la columna 'especie' con flexibilidad para errores de ortografía
-- Ejecutar este script desde terminal MySQL

USE railway;

-- Verificar estructura actual
DESCRIBE requerimientos;

-- Agregar la columna 'especie' con valor por defecto (permite NULL para flexibilidad)
ALTER TABLE requerimientos 
ADD COLUMN especie VARCHAR(50) DEFAULT NULL AFTER nombre;

-- Actualizar registros existentes con lógica flexible para errores de ortografía
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
    -- Si no coincide con nada, usar el valor original o 'General'
    ELSE COALESCE(tipo_especie, 'General')
END;

-- Verificar que los cambios se aplicaron correctamente
SELECT id, nombre, especie, tipo_especie, comentario FROM requerimientos;

-- Mostrar estructura final
DESCRIBE requerimientos;

-- Mostrar estadísticas de especies
SELECT especie, COUNT(*) as cantidad FROM requerimientos GROUP BY especie;
