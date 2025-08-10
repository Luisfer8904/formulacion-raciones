-- Schema bundle for Railway MySQL
-- Generated: 2025-08-10T06:53:31.592634Z

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- Create a dedicated schema (database) to keep things tidy inside Railway
CREATE DATABASE IF NOT EXISTS `formulacion_nutricional`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `formulacion_nutricional`;


-- ===== Begin: formulacion_nutricional_especies.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `especies`
--

DROP TABLE IF EXISTS `especies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `especies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especies`
--

LOCK TABLES `especies` WRITE;
/*!40000 ALTER TABLE `especies` DISABLE KEYS */;
INSERT INTO `especies` VALUES (1,'Bovinos'),(2,'Aves'),(3,'Cerdos'),(4,'Perros');
/*!40000 ALTER TABLE `especies` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_especies.sql =====

-- ===== Begin: formulacion_nutricional_ingredientes.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ingredientes`
--

DROP TABLE IF EXISTS `ingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `comentario` varchar(200) DEFAULT NULL,
  `es_global` tinyint(1) DEFAULT '0',
  `precio` decimal(10,2) DEFAULT NULL,
  `ms` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ingredientes_usuarios` (`usuario_id`),
  CONSTRAINT `fk_ingredientes_usuarios` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ingredientes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredientes`
--

LOCK TABLES `ingredientes` WRITE;
/*!40000 ALTER TABLE `ingredientes` DISABLE KEYS */;
INSERT INTO `ingredientes` VALUES (1,NULL,'Harina de soya','Proteína','None',0,6.30,NULL),(2,NULL,'Carbonato de calcio','Mineral','corregido',0,1.20,NULL),(3,2,'Maiz','Energía','3.00',0,2.00,NULL),(4,2,'Soja','Proteína','6.20',0,6.00,NULL),(5,2,'melaza','Energía','2.00',0,12.00,NULL),(9,2,'salvado','Fibra','prueba 3',0,4.00,NULL),(17,3,'Carbonato de calcio fino','Mineral','',0,1.30,98.00),(18,3,'Urea','Proteína','Se debe tener cuidado inclusion en bovinos',0,8.20,90.00),(19,3,'Fosfato Monocalcico','Mineral','Allta disponibilidad en cerdos y aves',0,17.45,98.65),(20,3,'Fosfato Monodicalcico','Mineral','Disagro',0,14.00,98.00),(21,3,'Availa 4','Mineral','Zinpro Fuente de Zinc, Cobre, Cobalto y Manganeso',0,81.81,98.25),(22,3,'Availa Se','Mineral','Zinpro Fuente de Selenio ',0,134.54,98.75),(23,3,'Phor 18%','Mineral','Harina de hueso Calcinada',0,8.00,98.00),(24,4,'Maiz amarillo','Energía','',0,4.30,86.40),(25,4,'Harina de soya','Proteína','',0,6.70,88.00),(26,4,'Melaza de Caña','Energía','',0,1.97,73.70),(27,3,'Azufre Micronizado','Mineral','',0,18.00,98.50),(28,3,'Cloruro de sodio','Mineral','Sal comun',0,1.40,94.00),(29,3,'PVM Trouw Nutrition','Vitamina','Premezcla Cerdo Trouw',0,54.00,98.00),(32,3,'prueba','Mineral','',0,12.00,88.00);
/*!40000 ALTER TABLE `ingredientes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_ingredientes.sql =====

-- ===== Begin: formulacion_nutricional_ingredientes_nutrientes.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ingredientes_nutrientes`
--

DROP TABLE IF EXISTS `ingredientes_nutrientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredientes_nutrientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ingrediente_id` int DEFAULT NULL,
  `nutriente_id` int DEFAULT NULL,
  `valor` decimal(10,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  KEY `nutriente_id` (`nutriente_id`),
  CONSTRAINT `ingredientes_nutrientes_ibfk_1` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ingredientes_nutrientes_ibfk_2` FOREIGN KEY (`nutriente_id`) REFERENCES `nutrientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=433 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredientes_nutrientes`
--

LOCK TABLES `ingredientes_nutrientes` WRITE;
/*!40000 ALTER TABLE `ingredientes_nutrientes` DISABLE KEYS */;
INSERT INTO `ingredientes_nutrientes` VALUES (1,1,1,44.0000),(2,2,2,38.0000),(3,1,3,0.7000),(4,1,2,1.0000),(7,5,1,1.5000),(8,5,2,0.0000),(9,5,3,0.0000),(12,9,1,12.0000),(13,9,2,0.0000),(14,9,3,0.0000),(17,4,1,12.0000),(18,4,2,0.0000),(19,4,3,0.0000),(22,2,1,0.0000),(23,2,3,0.0000),(26,3,1,0.0000),(27,3,2,0.0000),(28,3,3,0.0000),(44,5,9,0.0000),(45,9,9,12.0000),(50,4,9,12.0000),(116,24,18,7.3000),(117,24,19,3420.0000),(118,25,18,47.0000),(119,25,19,3360.0000),(122,26,18,4.3000),(123,26,19,2275.0000),(172,27,11,0.0000),(173,27,12,0.0000),(174,27,14,0.0000),(175,27,15,99.0000),(176,27,16,0.0000),(177,27,21,0.0000),(178,27,22,0.0000),(179,27,23,0.0000),(180,27,24,0.0000),(181,27,25,0.0000),(182,27,26,0.0000),(183,27,27,0.0000),(248,17,11,38.6000),(249,17,12,0.0100),(250,17,14,0.3000),(251,17,15,0.0700),(252,17,16,620.0000),(253,17,21,0.0000),(254,17,22,12.0000),(255,17,23,0.0000),(256,17,24,0.0000),(257,17,25,0.0000),(258,17,26,0.0200),(259,17,27,0.0700),(260,17,28,0.0000),(300,18,11,0.0000),(301,18,12,0.0000),(302,18,14,0.0000),(303,18,15,0.0000),(304,18,16,0.0000),(305,18,21,0.0000),(306,18,22,0.0000),(307,18,23,0.0000),(308,18,24,0.0000),(309,18,25,0.0000),(310,18,26,0.0000),(311,18,27,0.0000),(312,18,28,287.0000),(326,19,11,17.2000),(327,19,12,22.7000),(328,19,14,0.6000),(329,19,15,0.6500),(330,19,16,4000.0000),(331,19,21,0.0000),(332,19,22,8.0000),(333,19,23,0.0000),(334,19,24,0.0000),(335,19,25,0.0000),(336,19,26,0.0000),(337,19,27,0.0000),(338,19,28,0.0000),(339,20,11,20.5000),(340,20,12,21.5000),(341,20,14,0.6500),(342,20,15,0.7000),(343,20,16,4000.0000),(344,20,21,0.0000),(345,20,22,9.0000),(346,20,23,0.0000),(347,20,24,0.0000),(348,20,25,0.0000),(349,20,26,0.3000),(350,20,27,0.1300),(351,20,28,0.0000),(352,23,11,35.0000),(353,23,12,18.0000),(354,23,14,1.0000),(355,23,15,1.9000),(356,23,16,610.0000),(357,23,21,15.0000),(358,23,22,8.0000),(359,23,23,5.7000),(360,23,24,128.0000),(361,23,25,0.0000),(362,23,26,0.0000),(363,23,27,0.0000),(364,23,28,0.0000),(365,28,11,0.0000),(366,28,12,0.0000),(367,28,14,0.0000),(368,28,15,0.0000),(369,28,16,0.0000),(370,28,21,0.0000),(371,28,22,0.0000),(372,28,23,0.0000),(373,28,24,0.0000),(374,28,25,0.0000),(375,28,26,57.8000),(376,28,27,38.5000),(377,28,28,0.0000),(378,22,11,0.0000),(379,22,12,0.0000),(380,22,14,0.0000),(381,22,15,0.0000),(382,22,16,0.0000),(383,22,21,0.0000),(384,22,22,0.0000),(385,22,23,0.0000),(386,22,24,0.0000),(387,22,25,1000.0000),(388,22,26,0.0000),(389,22,27,0.0000),(390,22,28,0.0000),(391,29,11,0.0000),(392,29,12,0.0000),(393,29,14,0.0000),(394,29,15,0.0000),(395,29,16,70000.0000),(396,29,21,0.0000),(397,29,22,5000.0000),(398,29,23,0.0000),(399,29,24,100000.0000),(400,29,25,300.0000),(401,29,26,0.0000),(402,29,27,0.0000),(403,29,28,0.0000),(404,21,11,0.0000),(405,21,12,0.0000),(406,21,14,0.0000),(407,21,15,0.0000),(408,21,16,0.0000),(409,21,21,28600.0000),(410,21,22,18000.0000),(411,21,23,1800.0000),(412,21,24,51500.0000),(413,21,25,0.0000),(414,21,26,0.0000),(415,21,27,0.0000),(416,21,28,0.0000),(417,21,29,12.0000),(418,32,11,99.0000),(419,32,12,0.0000),(420,32,14,0.0000),(421,32,15,0.0000),(422,32,16,0.0000),(423,32,21,0.0000),(424,32,22,0.0000),(425,32,23,0.0000),(426,32,24,0.0000),(427,32,25,0.0000),(428,32,26,0.0000),(429,32,27,0.0000),(430,32,28,0.0000),(431,32,29,0.0000),(432,32,30,0.0000);
/*!40000 ALTER TABLE `ingredientes_nutrientes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_ingredientes_nutrientes.sql =====

-- ===== Begin: formulacion_nutricional_ingrediente_especie.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ingrediente_especie`
--

DROP TABLE IF EXISTS `ingrediente_especie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingrediente_especie` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ingrediente_id` int NOT NULL,
  `especie_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  KEY `especie_id` (`especie_id`),
  CONSTRAINT `ingrediente_especie_ibfk_1` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ingrediente_especie_ibfk_2` FOREIGN KEY (`especie_id`) REFERENCES `especies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingrediente_especie`
--

LOCK TABLES `ingrediente_especie` WRITE;
/*!40000 ALTER TABLE `ingrediente_especie` DISABLE KEYS */;
/*!40000 ALTER TABLE `ingrediente_especie` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_ingrediente_especie.sql =====

-- ===== Begin: formulacion_nutricional_conjuntos_requerimientos.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `conjuntos_requerimientos`
--

DROP TABLE IF EXISTS `conjuntos_requerimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conjuntos_requerimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int DEFAULT NULL,
  `nutriente_id` int DEFAULT NULL,
  `valor_sugerido` decimal(10,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `requerimiento_id` (`requerimiento_id`),
  KEY `nutriente_id` (`nutriente_id`),
  CONSTRAINT `conjuntos_requerimientos_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimientos` (`id`),
  CONSTRAINT `conjuntos_requerimientos_ibfk_2` FOREIGN KEY (`nutriente_id`) REFERENCES `nutrientes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conjuntos_requerimientos`
--

LOCK TABLES `conjuntos_requerimientos` WRITE;
/*!40000 ALTER TABLE `conjuntos_requerimientos` DISABLE KEYS */;
INSERT INTO `conjuntos_requerimientos` VALUES (9,4,15,11.0000),(10,4,11,11.0000),(12,6,15,3.0000),(13,6,12,9.0000);
/*!40000 ALTER TABLE `conjuntos_requerimientos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_conjuntos_requerimientos.sql =====

-- ===== Begin: formulacion_nutricional_formulaciones.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `formulaciones`
--

DROP TABLE IF EXISTS `formulaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formulaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `tamano_bachada` decimal(10,2) DEFAULT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `formulaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formulaciones`
--

LOCK TABLES `formulaciones` WRITE;
/*!40000 ALTER TABLE `formulaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `formulaciones` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_formulaciones.sql =====

-- ===== Begin: formulacion_nutricional_formulacion_ingredientes.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `formulacion_ingredientes`
--

DROP TABLE IF EXISTS `formulacion_ingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formulacion_ingredientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `formulacion_id` int DEFAULT NULL,
  `ingrediente_id` int DEFAULT NULL,
  `inclusion` decimal(10,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `formulacion_id` (`formulacion_id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  CONSTRAINT `formulacion_ingredientes_ibfk_1` FOREIGN KEY (`formulacion_id`) REFERENCES `formulaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `formulacion_ingredientes_ibfk_2` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formulacion_ingredientes`
--

LOCK TABLES `formulacion_ingredientes` WRITE;
/*!40000 ALTER TABLE `formulacion_ingredientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `formulacion_ingredientes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_formulacion_ingredientes.sql =====

-- ===== Begin: formulacion_nutricional_formulacion_requerimientos.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `formulacion_requerimientos`
--

DROP TABLE IF EXISTS `formulacion_requerimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formulacion_requerimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `formulacion_id` int DEFAULT NULL,
  `nutriente_id` int DEFAULT NULL,
  `min_valor` decimal(10,4) DEFAULT NULL,
  `max_valor` decimal(10,4) DEFAULT NULL,
  `usar` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `formulacion_id` (`formulacion_id`),
  KEY `nutriente_id` (`nutriente_id`),
  CONSTRAINT `formulacion_requerimientos_ibfk_1` FOREIGN KEY (`formulacion_id`) REFERENCES `formulaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `formulacion_requerimientos_ibfk_2` FOREIGN KEY (`nutriente_id`) REFERENCES `nutrientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formulacion_requerimientos`
--

LOCK TABLES `formulacion_requerimientos` WRITE;
/*!40000 ALTER TABLE `formulacion_requerimientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `formulacion_requerimientos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_formulacion_requerimientos.sql =====

-- ===== Begin: formulacion_nutricional_mezcla_ingredientes.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mezcla_ingredientes`
--

DROP TABLE IF EXISTS `mezcla_ingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mezcla_ingredientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mezcla_id` int DEFAULT NULL,
  `ingrediente_id` int DEFAULT NULL,
  `inclusion` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mezcla_id` (`mezcla_id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  CONSTRAINT `mezcla_ingredientes_ibfk_1` FOREIGN KEY (`mezcla_id`) REFERENCES `mezclas` (`id`),
  CONSTRAINT `mezcla_ingredientes_ibfk_2` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=274 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mezcla_ingredientes`
--

LOCK TABLES `mezcla_ingredientes` WRITE;
/*!40000 ALTER TABLE `mezcla_ingredientes` DISABLE KEYS */;
INSERT INTO `mezcla_ingredientes` VALUES (28,18,24,70.00),(29,18,25,25.00),(30,18,26,5.00),(259,69,17,0.57),(260,69,18,99.43),(261,70,17,56.99),(262,70,18,2.00),(263,70,27,41.01),(267,73,20,55.79),(268,73,17,44.21),(269,74,19,52.84),(270,74,17,47.16),(271,75,18,3.00),(272,75,17,44.16),(273,75,19,52.84);
/*!40000 ALTER TABLE `mezcla_ingredientes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_mezcla_ingredientes.sql =====

-- ===== Begin: formulacion_nutricional_mezcla_ingredientes_nutrientes.sql =====
-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: formulacion_nutricional
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mezcla_ingredientes_nutrientes`
--

DROP TABLE IF EXISTS `mezcla_ingredientes_nutrientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mezcla_ingredientes_nutrientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mezcla_id` int NOT NULL,
  `nutriente_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `nutriente_id` (`nutriente_id`),
  KEY `fk_mezcla` (`mezcla_id`),
  CONSTRAINT `fk_mezcla` FOREIGN KEY (`mezcla_id`) REFERENCES `mezclas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mezcla_ingredientes_nutrientes_ibfk_3` FOREIGN KEY (`nutriente_id`) REFERENCES `nutrientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=217 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mezcla_ingredientes_nutrientes`
--

LOCK TABLES `mezcla_ingredientes_nutrientes` WRITE;
/*!40000 ALTER TABLE `mezcla_ingredientes_nutrientes` DISABLE KEYS */;
INSERT INTO `mezcla_ingredientes_nutrientes` VALUES (212,69,11),(213,70,11),(214,73,12),(215,74,12),(216,75,12);
/*!40000 ALTER TABLE `mezcla_ingredientes_nutrientes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-10  0:52:03

-- ===== End: formulacion_nutricional_mezcla_ingredientes_nutrientes.sql =====

SET FOREIGN_KEY_CHECKS=1;
-- End of bundle
