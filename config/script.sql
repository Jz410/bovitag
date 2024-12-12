-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS bovitag1;

-- Usar la base de datos
USE bovitag1;

-- Crear la tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rango VARCHAR(50) NOT NULL,
    activo TiNYINT (1)
);

-- Crear la tabla registros
CREATE TABLE IF NOT EXISTS registros (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    nombre_imagen TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_nombre VARCHAR(255), 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
