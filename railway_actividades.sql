-- Script SQL para crear tabla actividades en Railway
-- Ejecutar este código en el panel de Railway > MySQL > Data > Query

-- Crear tabla de actividades por usuario
CREATE TABLE IF NOT EXISTS `actividades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `tipo_actividad` varchar(50) NOT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_usuario_fecha` (`usuario_id`, `fecha`),
  CONSTRAINT `fk_actividades_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar actividades de ejemplo para usuarios existentes
INSERT IGNORE INTO `actividades` (`usuario_id`, `descripcion`, `tipo_actividad`, `fecha`) VALUES
(3, 'Creó el ingrediente: Carbonato de calcio fino', 'ingrediente', '2024-01-15 10:30:00'),
(3, 'Creó el ingrediente: Urea', 'ingrediente', '2024-01-15 11:45:00'),
(3, 'Creó el ingrediente: Fosfato Monocalcico', 'ingrediente', '2024-01-16 09:20:00'),
(3, 'Guardó una nueva formulación', 'formulacion', '2024-01-16 14:30:00'),
(3, 'Editó el ingrediente: Availa 4', 'ingrediente', '2024-01-17 08:15:00'),
(4, 'Creó el ingrediente: Maiz amarillo', 'ingrediente', '2024-01-18 09:00:00'),
(4, 'Creó el ingrediente: Harina de soya', 'ingrediente', '2024-01-18 09:30:00'),
(4, 'Creó el ingrediente: Melaza de Caña', 'ingrediente', '2024-01-18 10:00:00');

-- Verificar que la tabla se creó correctamente
SELECT 'Tabla actividades creada exitosamente' as resultado;
SELECT COUNT(*) as total_actividades FROM actividades;
