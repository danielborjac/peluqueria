-- BD: DPELOS
create database DPELOS;

-- Tabla: USUARIO
CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  telefono VARCHAR(20),
  direccion VARCHAR(255),
  rol ENUM('cliente', 'admin') NOT NULL,
  contraseña VARCHAR(255)
);

-- Tabla: ESPECIALISTA
CREATE TABLE especialista (
  id_especialista INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  especialidad VARCHAR(100),
  foto_url VARCHAR(255),
  descripcion TEXT
);

-- Tabla: SERVICIO
CREATE TABLE servicio (
  id_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  precio DECIMAL(10,2) NOT NULL,
  duracion_estimada INT NOT NULL, -- en minutos
  imagen_url VARCHAR(255)
);

-- Tabla intermedia: ESPECIALISTA_SERVICIO
CREATE TABLE especialista_servicio (
  id_especialista INT,
  id_servicio INT,
  PRIMARY KEY (id_especialista, id_servicio),
  FOREIGN KEY (id_especialista) REFERENCES especialista(id_especialista) ON DELETE CASCADE,
  FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio) ON DELETE CASCADE
);

-- Tabla: RESERVA
CREATE TABLE reserva (
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT,
  id_servicio INT,
  id_especialista INT,
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  estado VARCHAR(50) NOT NULL,
  codigo_reserva VARCHAR(7) NOT NULL,
  FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL,
  FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio) ON DELETE SET NULL,
  FOREIGN KEY (id_especialista) REFERENCES especialista(id_especialista) ON DELETE SET NULL
);