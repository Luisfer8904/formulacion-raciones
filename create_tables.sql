-- Crear base de datos y usar
USE railway;

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'user') DEFAULT 'user',
    pais VARCHAR(50),
    moneda VARCHAR(10),
    tipo_moneda VARCHAR(20),
    unidad_medida VARCHAR(20),
    idioma VARCHAR(10) DEFAULT 'es',
    tema VARCHAR(20) DEFAULT 'claro',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla especies
CREATE TABLE IF NOT EXISTS especies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla nutrientes
CREATE TABLE IF NOT EXISTS nutrientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    tipo VARCHAR(50),
    usuario_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla ingredientes
CREATE TABLE IF NOT EXISTS ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    comentario TEXT,
    tipo VARCHAR(100),
    precio DECIMAL(10,2),
    ms DECIMAL(8,4),
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla ingredientes_nutrientes
CREATE TABLE IF NOT EXISTS ingredientes_nutrientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingrediente_id INT NOT NULL,
    nutriente_id INT NOT NULL,
    valor DECIMAL(10,4),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
    FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_ingrediente_nutriente (ingrediente_id, nutriente_id)
);

-- Tabla ingrediente_especie
CREATE TABLE IF NOT EXISTS ingrediente_especie (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingrediente_id INT NOT NULL,
    especie_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
    FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE CASCADE,
    UNIQUE KEY unique_ingrediente_especie (ingrediente_id, especie_id)
);

-- Tabla requerimientos
CREATE TABLE IF NOT EXISTS requerimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla conjuntos_requerimientos
CREATE TABLE IF NOT EXISTS conjuntos_requerimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requerimiento_id INT NOT NULL,
    nutriente_id INT NOT NULL,
    valor_sugerido DECIMAL(10,4),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requerimiento_id) REFERENCES requerimientos(id) ON DELETE CASCADE,
    FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id) ON DELETE CASCADE
);

-- Tabla mezclas
CREATE TABLE IF NOT EXISTS mezclas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    especie VARCHAR(50),
    categoria VARCHAR(100),
    costo_total DECIMAL(10,2),
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla mezcla_ingredientes
CREATE TABLE IF NOT EXISTS mezcla_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mezcla_id INT NOT NULL,
    ingrediente_id INT NOT NULL,
    porcentaje DECIMAL(8,4) NOT NULL,
    cantidad_kg DECIMAL(10,4),
    costo DECIMAL(10,2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mezcla_id) REFERENCES mezclas(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE
);

-- Tabla mezcla_ingredientes_nutrientes
CREATE TABLE IF NOT EXISTS mezcla_ingredientes_nutrientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mezcla_id INT NOT NULL,
    nutriente_id INT NOT NULL,
    valor_total DECIMAL(10,4),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mezcla_id) REFERENCES mezclas(id) ON DELETE CASCADE,
    FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id) ON DELETE CASCADE
);

-- Tabla formulaciones
CREATE TABLE IF NOT EXISTS formulaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla formulacion_ingredientes
CREATE TABLE IF NOT EXISTS formulacion_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    formulacion_id INT NOT NULL,
    ingrediente_id INT NOT NULL,
    porcentaje DECIMAL(8,4),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (formulacion_id) REFERENCES formulaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE
);

-- Tabla formulacion_requerimientos
CREATE TABLE IF NOT EXISTS formulacion_requerimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    formulacion_id INT NOT NULL,
    requerimiento_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (formulacion_id) REFERENCES formulaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (requerimiento_id) REFERENCES requerimientos(id) ON DELETE CASCADE
);

-- Insertar usuario admin por defecto
INSERT IGNORE INTO usuarios (nombre, email, password, rol) 
VALUES ('Administrador', 'admin@formulacion.com', 'admin123', 'admin');

-- Insertar especies básicas
INSERT IGNORE INTO especies (nombre, descripcion) VALUES
('Pollo', 'Pollos de engorde'),
('Cerdo', 'Cerdos de engorde'),
('Bovino', 'Ganado bovino'),
('Ovino', 'Ganado ovino'),
('Caprino', 'Ganado caprino'),
('Peces', 'Acuicultura'),
('Conejos', 'Cunicultura');

-- Insertar nutrientes básicos (asociados al usuario admin)
INSERT IGNORE INTO nutrientes (nombre, unidad, tipo, usuario_id) VALUES
('Proteína Bruta', '%', 'Macronutriente', 1),
('Energía Metabolizable', 'Kcal/kg', 'Energía', 1),
('Fibra Bruta', '%', 'Macronutriente', 1),
('Grasa Bruta', '%', 'Macronutriente', 1),
('Cenizas', '%', 'Macronutriente', 1),
('Materia Seca', '%', 'Composición', 1),
('Calcio', '%', 'Mineral', 1),
('Fósforo', '%', 'Mineral', 1),
('Sodio', '%', 'Mineral', 1),
('Potasio', '%', 'Mineral', 1),
('Magnesio', '%', 'Mineral', 1),
('Lisina', '%', 'Aminoácido', 1),
('Metionina', '%', 'Aminoácido', 1),
('Treonina', '%', 'Aminoácido', 1),
('Triptófano', '%', 'Aminoácido', 1),
('Arginina', '%', 'Aminoácido', 1);
