-- ============================================
-- BEN AURA - Setup de base de datos MySQL/XAMPP
-- Ejecutar: mysql -u root -h localhost -P 3307 < setup_db.sql
-- (Si tu XAMPP usa el puerto 3306, cambia -P a 3306)
-- ============================================
CREATE DATABASE IF NOT EXISTS `benaura_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `benaura_db`;

CREATE TABLE IF NOT EXISTS `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `n_pedido` varchar(50) DEFAULT NULL,
  `cliente` varchar(100) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `producto` varchar(100) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `medio_pago` varchar(50) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `entrega` varchar(50) DEFAULT NULL,
  `ganancia` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `ventas` (`id`, `fecha`, `n_pedido`, `cliente`, `telefono`, `producto`, `cantidad`, `precio_unitario`, `total`, `medio_pago`, `estado`, `entrega`, `ganancia`) VALUES
(1, '2026-08-25', '1', '', '', 'Vela Mini Bubble / Margaritas', 1, '3000.00', '3000.00', 'Transferencia', 'Pendiente', 'Entregado', '2200.00'),
(2, '2026-08-25', '1', 'Benjamin', '2616943949', 'Vela Mini Bubble / Margaritas', 1, '3000.00', '3000.00', 'Transferencia', 'Pendiente', 'Entregado', '2200.00'),
(3, '2026-08-25', '1', 'Benjamin', '2616943949', 'Vela Mini Bubble / Margaritas', 1, '3000.00', '3000.00', 'Transferencia', 'Pendiente', 'Entregado', '2200.00'),
(4, '2026-08-25', '004', 'Lucas', '02616943949', 'Vela Mini Bubble / Margaritas', 1, '3000.00', '3000.00', 'Transferencia', 'Pendiente', 'Entregado', '2200.00'),
(5, '2026-08-25', '005', 'Sabrina', '2616943949', 'Vela Mini Bubble / Margaritas', 1, '3000.00', '3000.00', 'Transferencia', 'Pendiente', 'Entregado', '2200.00');

ALTER TABLE `ventas` AUTO_INCREMENT = 6;

-- ============================================
-- Tabla de productos (catálogo de velas/aromáticas)
-- ============================================
CREATE TABLE IF NOT EXISTS `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `stock` int(11) DEFAULT 0,
  `gramos_cera` decimal(10,2) DEFAULT 0.00,
  `gramos_esencia` decimal(10,2) DEFAULT 0.00,
  `gramos_colorante` decimal(10,2) DEFAULT 0.00,
  `cm_pabilo` decimal(10,2) DEFAULT 0.00,
  `precio_unitario` decimal(10,2) DEFAULT 0.00,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- Tabla de compras de insumos (precio real pagado)
-- ============================================
CREATE TABLE IF NOT EXISTS `compras_insumos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `insumo` varchar(50) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `precio_total` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================
-- Tabla de configuración de insumos (margen objetivo)
-- ============================================
CREATE TABLE IF NOT EXISTS `config_insumos` (
  `id` int(11) NOT NULL,
  `margen_objetivo` decimal(5,4) DEFAULT 0.5000,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT IGNORE INTO `config_insumos` (`id`, `margen_objetivo`) VALUES (1, 0.5000);