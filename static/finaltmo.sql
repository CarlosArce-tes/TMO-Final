-- MariaDB dump 10.19-11.2.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: logistica
-- ------------------------------------------------------
-- Server version	11.2.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Clientes`
--

DROP TABLE IF EXISTS `Clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Clientes` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NOMBRE` varchar(255) DEFAULT NULL,
  `RFC` varchar(50) DEFAULT NULL,
  `DIRECCION` text DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Clientes`
--

LOCK TABLES `Clientes` WRITE;
/*!40000 ALTER TABLE `Clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `Clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Ordenes`
--

DROP TABLE IF EXISTS `Ordenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Ordenes` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `CLIENTE_ID` int(11) DEFAULT NULL,
  `FECHA_SOLICITADA` date DEFAULT NULL,
  `FECHA_DE_ENTREGA` date DEFAULT NULL,
  `MATERIAL_A` varchar(255) DEFAULT NULL,
  `FOLIO` varchar(50) DEFAULT NULL,
  `COMENTARIOS` text DEFAULT NULL,
  `CANTIDAD` int(11) DEFAULT NULL,
  `OBRA` varchar(255) DEFAULT NULL,
  `ESTATUS` varchar(20) DEFAULT NULL,
  `ENTREGADA` int(11) DEFAULT NULL,
  `RESTANTE` int(11) DEFAULT NULL,
  `REMISION` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `CLIENTE_ID` (`CLIENTE_ID`),
  CONSTRAINT `Ordenes_ibfk_1` FOREIGN KEY (`CLIENTE_ID`) REFERENCES `Clientes` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Ordenes`
--

LOCK TABLES `Ordenes` WRITE;
/*!40000 ALTER TABLE `Ordenes` DISABLE KEYS */;
/*!40000 ALTER TABLE `Ordenes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Productos`
--

DROP TABLE IF EXISTS `Productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Productos` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NOMBRE` varchar(255) DEFAULT NULL,
  `DESCRIPCION` text DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Productos`
--

LOCK TABLES `Productos` WRITE;
/*!40000 ALTER TABLE `Productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `Productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Recolecciones`
--

DROP TABLE IF EXISTS `Recolecciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Recolecciones` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `REMISION_ID` int(11) DEFAULT NULL,
  `PRODUCTO_ID` int(11) DEFAULT NULL,
  `CANTIDAD` int(11) DEFAULT NULL,
  `PESO` decimal(10,2) DEFAULT NULL,
  `COSTO` decimal(10,2) DEFAULT NULL,
  `ESTATUS` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `REMISION_ID` (`REMISION_ID`),
  KEY `PRODUCTO_ID` (`PRODUCTO_ID`),
  CONSTRAINT `Recolecciones_ibfk_1` FOREIGN KEY (`REMISION_ID`) REFERENCES `Remisiones` (`ID`),
  CONSTRAINT `Recolecciones_ibfk_2` FOREIGN KEY (`PRODUCTO_ID`) REFERENCES `Productos` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Recolecciones`
--

LOCK TABLES `Recolecciones` WRITE;
/*!40000 ALTER TABLE `Recolecciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `Recolecciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Remisiones`
--

DROP TABLE IF EXISTS `Remisiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Remisiones` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FECHA` date DEFAULT NULL,
  `ORDEN_DE_T` varchar(50) DEFAULT NULL,
  `FACTURA` varchar(50) DEFAULT NULL,
  `FOLIO` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Remisiones`
--

LOCK TABLES `Remisiones` WRITE;
/*!40000 ALTER TABLE `Remisiones` DISABLE KEYS */;
/*!40000 ALTER TABLE `Remisiones` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-10 11:35:57
