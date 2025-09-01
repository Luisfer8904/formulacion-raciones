-- Agregar columna tipo_plan a la tabla usuarios
USE railway;

-- Agregar la columna tipo_plan si no existe
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS tipo_plan ENUM('basico', 'personal', 'profesional') DEFAULT 'basico' 
AFTER rol;

-- Actualizar usuarios existentes con planes por defecto
-- Admin tendrá plan profesional
UPDATE usuarios SET tipo_plan = 'profesional' WHERE rol = 'admin';

-- Usuarios regulares tendrán plan básico por defecto
UPDATE usuarios SET tipo_plan = 'basico' WHERE rol = 'user' AND tipo_plan IS NULL;

-- Crear algunos usuarios de ejemplo con diferentes planes para testing
INSERT IGNORE INTO usuarios (nombre, email, password, rol, tipo_plan) VALUES
('Usuario Básico', 'basico@test.com', 'test123', 'user', 'basico'),
('Usuario Personal', 'personal@test.com', 'test123', 'user', 'personal'),
('Usuario Profesional', 'profesional@test.com', 'test123', 'user', 'profesional');

-- Verificar la estructura actualizada
DESCRIBE usuarios;

-- Mostrar usuarios con sus planes
SELECT id, nombre, email, rol, tipo_plan FROM usuarios;

COMMIT;

-- Mensaje de confirmación
SELECT 'Columna tipo_plan agregada exitosamente a la tabla usuarios' as mensaje;
