CREATE DATABASE IF NOT EXISTS club_deportivo;
USE club_deportivo;

CREATE TABLE IF NOT EXISTS deportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS canchas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL,
    techada BOOLEAN NOT NULL DEFAULT FALSE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id)
);

CREATE TABLE IF NOT EXISTS socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado ENUM('confirmada', 'cancelada', 'finalizada') NOT NULL DEFAULT 'confirmada',
    precio_hora INT NOT NULL,
    precio_total INT NOT NULL,
    FOREIGN KEY (id_socio) REFERENCES socios(id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
('Cancha 1', 1, 1000, FALSE, TRUE),
('Cancha 2', 1, 1000, FALSE, TRUE),
('Cancha 3', 2, 1500, TRUE, TRUE),
('Cancha 4', 2, 1500, TRUE, TRUE),
('Cancha 5', 3, 1200, FALSE, TRUE);


INSERT INTO deportes (id, nombre) VALUES 
(1, 'Fútbol'),
(2, 'Tenis'),
(3, 'Pádel');