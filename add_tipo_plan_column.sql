-- Script para agregar columna tipo_plan a la tabla usuarios
-- Ejecutar este script en la base de datos

USE formulacion_nutricional;

-- Agregar columna tipo_plan si no existe
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS tipo_plan ENUM('basico', 'personal', 'profesional') DEFAULT 'basico' 
AFTER tema;

-- Verificar que la columna se agregó correctamente
DESCRIBE usuarios;

-- Actualizar usuarios existentes para que tengan un plan básico por defecto
UPDATE usuarios 
SET tipo_plan = 'basico' 
WHERE tipo_plan IS NULL;

-- Mostrar resultado
SELECT id, nombre, email, tipo_plan FROM usuarios;
