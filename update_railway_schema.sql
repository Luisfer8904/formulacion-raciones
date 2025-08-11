-- Script para actualizar la base de datos de Railway con requerimientos completos
-- Ejecutar este script directamente en Railway MySQL

USE railway;

-- Asegurar que existe el usuario con ID 3
INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, fecha_creacion) 
VALUES (3, 'Usuario Formulador', 'formulador@test.com', 'pass123', 'user', NOW());

-- Limpiar datos existentes para evitar duplicados
DELETE FROM conjuntos_requerimientos;
DELETE FROM requerimientos WHERE id > 6;

-- Insertar requerimientos adicionales
INSERT IGNORE INTO requerimientos (id, nombre, especie, categoria, descripcion, usuario_id, fecha_creacion) VALUES
(7, 'Cerdo Iniciador', 'Cerdo', 'Iniciador', 'Requerimientos para cerdos en etapa de iniciación', 3, NOW()),
(8, 'Cerdo Crecimiento', 'Cerdo', 'Crecimiento', 'Requerimientos para cerdos en crecimiento', 3, NOW()),
(9, 'Cerdo Finalización', 'Cerdo', 'Finalización', 'Requerimientos para cerdos en finalización', 3, NOW()),
(10, 'Pollo Iniciador', 'Aves', 'Iniciador', 'Requerimientos para pollos en etapa de iniciación', 3, NOW()),
(11, 'Pollo Crecimiento', 'Aves', 'Crecimiento', 'Requerimientos para pollos en crecimiento', 3, NOW()),
(12, 'Pollo Finalización', 'Aves', 'Finalización', 'Requerimientos para pollos en finalización', 3, NOW()),
(13, 'Gallina Ponedora', 'Aves', 'Postura', 'Requerimientos para gallinas ponedoras', 3, NOW()),
(14, 'Bovino Lechero', 'Bovino', 'Producción', 'Requerimientos para vacas lecheras', 3, NOW()),
(15, 'Bovino Engorde', 'Bovino', 'Engorde', 'Requerimientos para bovinos de engorde', 3, NOW());

-- Insertar conjuntos de requerimientos (valores nutricionales)
INSERT IGNORE INTO conjuntos_requerimientos (requerimiento_id, nutriente_id, valor_sugerido) VALUES
-- Bovino Adulto (id=4)
(4, 11, 0.4),   -- Calcio mínimo
(4, 12, 0.25),  -- Fósforo mínimo
(4, 15, 0.15),  -- Azufre
(4, 28, 8.0),   -- Proteína Equivalente
(4, 30, 2200),  -- Energía Digestible

-- Bovino Crecimiento (id=6)
(6, 11, 0.6),   -- Calcio
(6, 12, 0.35),  -- Fósforo
(6, 15, 0.2),   -- Azufre
(6, 28, 12.0),  -- Proteína Equivalente
(6, 30, 2800),  -- Energía Digestible

-- Cerdo Iniciador (id=7)
(7, 1, 20.0),   -- Proteína Bruta
(7, 2, 0.8),    -- Calcio
(7, 3, 0.65),   -- Fósforo

-- Cerdo Crecimiento (id=8)
(8, 1, 16.0),   -- Proteína Bruta
(8, 2, 0.7),    -- Calcio
(8, 3, 0.55),   -- Fósforo

-- Cerdo Finalización (id=9)
(9, 1, 14.0),   -- Proteína Bruta
(9, 2, 0.6),    -- Calcio
(9, 3, 0.5),    -- Fósforo

-- Pollo Iniciador (id=10)
(10, 18, 23.0), -- Proteína Bruta
(10, 19, 3000), -- Energía Metabolizable

-- Pollo Crecimiento (id=11)
(11, 18, 20.0), -- Proteína Bruta
(11, 19, 3100), -- Energía Metabolizable

-- Pollo Finalización (id=12)
(12, 18, 18.0), -- Proteína Bruta
(12, 19, 3200), -- Energía Metabolizable

-- Gallina Ponedora (id=13)
(13, 18, 16.0), -- Proteína Bruta
(13, 19, 2750), -- Energía Metabolizable

-- Bovino Lechero (id=14)
(14, 11, 0.7),  -- Calcio
(14, 12, 0.4),  -- Fósforo
(14, 28, 16.0), -- Proteína Equivalente
(14, 30, 2600), -- Energía Digestible

-- Bovino Engorde (id=15)
(15, 11, 0.5),  -- Calcio
(15, 12, 0.3),  -- Fósforo
(15, 28, 13.0), -- Proteína Equivalente
(15, 30, 2800); -- Energía Digestible

-- Verificar resultados
SELECT 'Requerimientos totales:' as info, COUNT(*) as cantidad FROM requerimientos
UNION ALL
SELECT 'Conjuntos de requerimientos:' as info, COUNT(*) as cantidad FROM conjuntos_requerimientos;

-- Mostrar requerimientos por especie
SELECT especie, COUNT(*) as cantidad 
FROM requerimientos 
GROUP BY especie 
ORDER BY especie;
