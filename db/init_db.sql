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

-- Deportes
INSERT INTO deportes (id, nombre) VALUES
    (1, 'Fútbol'),
    (2, 'Tenis'),
    (3, 'Pádel')
    ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- Canchas
INSERT INTO canchas (id, nombre, id_deporte, precio_hora, techada, activa) VALUES
    (1, 'Cancha Fútbol 5 Synthetica', 1, 15000, TRUE, TRUE),   -- Con reservas (para probar 409 al borrar)
    (2, 'Cancha Fútbol 7 Césped',    1, 20000, FALSE, TRUE),  -- Con reservas (para probar 409 al borrar)
    (3, 'Cancha Tenis Ladrillo',     2, 10000, FALSE, TRUE),  -- Sin reservas (para probar 204 borrado exitoso)
    (4, 'Cancha Pádel Panorámica',   3, 12000, TRUE, TRUE),   -- Sin reservas (para probar 204 borrado exitoso)
    (5, 'Cancha Fútbol Auxiliar',    1, 8000,  FALSE, FALSE)  -- Inactiva
    ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- Socios
INSERT INTO socios (id, nombre, email, activo) VALUES
    (1, 'Juan Pérez', 'juan.perez@email.com', TRUE),
    (2, 'María Gómez', 'maria.gomez@email.com', TRUE),
    (3, 'Carlos Rodríguez', 'carlos.rodriguez@email.com', TRUE)
    ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- Reservas (asociadas a las canchas 1 y 2)
INSERT INTO reservas (id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) VALUES
    (1, 1, 1, '2026-10-01 18:00:00.000000', '2026-10-01 19:00:00.000000', 'confirmada', 15000, 15000),
    (2, 2, 2, '2026-10-02 20:00:00.000000', '2026-10-02 21:00:00.000000', 'confirmada', 20000, 20000)
    ON DUPLICATE KEY UPDATE estado=VALUES(estado);