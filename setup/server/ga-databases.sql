-- MySQL dump 10.17  Distrib 10.3.17-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: gasensors
-- ------------------------------------------------------
-- Server version	10.3.17-MariaDB-0+deb10u1

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
-- Current Database: `gasensors`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `gasensors` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `gasensors`;

--
-- Table structure for table `aht`
--

DROP TABLE IF EXISTS `aht`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aht` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DATE` date DEFAULT NULL,
  `TIME` time DEFAULT NULL,
  `CONTROLLER` char(5) DEFAULT NULL,
  `SENSOR` char(6) DEFAULT NULL,
  `TEMPERATURE` decimal(6,3) DEFAULT NULL,
  `HUMIDITY` decimal(6,3) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aht`
--

LOCK TABLES `aht` WRITE;
/*!40000 ALTER TABLE `aht` DISABLE KEYS */;
/*!40000 ALTER TABLE `aht` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eh`
--

DROP TABLE IF EXISTS `eh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eh` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DATE` date DEFAULT NULL,
  `TIME` time DEFAULT NULL,
  `CONTROLLER` char(5) DEFAULT NULL,
  `SENSOR` char(5) DEFAULT NULL,
  `HUMIDITY` decimal(4,0) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eh`
--

LOCK TABLES `eh` WRITE;
/*!40000 ALTER TABLE `eh` DISABLE KEYS */;
/*!40000 ALTER TABLE `eh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `gaactions`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `gaactions` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `gaactions`;

--
-- Table structure for table `psu`
--

DROP TABLE IF EXISTS `psu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `psu` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DATE` date DEFAULT NULL,
  `TIME` time DEFAULT NULL,
  `CONTROLLER` char(5) DEFAULT NULL,
  `ACTIONTAKEN` char(40) DEFAULT NULL,
  `OLUSAGE` char(10) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `psu`
--

LOCK TABLES `psu` WRITE;
/*!40000 ALTER TABLE `psu` DISABLE KEYS */;
/*!40000 ALTER TABLE `psu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pump`
--

DROP TABLE IF EXISTS `pump`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pump` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DATE` date DEFAULT NULL,
  `TIME` time DEFAULT NULL,
  `CONTROLLER` char(5) DEFAULT NULL,
  `ACTIONTAKEN` char(40) DEFAULT NULL,
  `ACTIONTIME` int(4) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pump`
--

LOCK TABLES `pump` WRITE;
/*!40000 ALTER TABLE `pump` DISABLE KEYS */;
/*!40000 ALTER TABLE `pump` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `win`
--

DROP TABLE IF EXISTS `win`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `win` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DATE` date DEFAULT NULL,
  `TIME` time DEFAULT NULL,
  `CONTROLLER` char(5) DEFAULT NULL,
  `ACTIONTAKEN` char(40) DEFAULT NULL,
  `ACTIONTIME` int(4) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `win`
--

LOCK TABLES `win` WRITE;
/*!40000 ALTER TABLE `win` DISABLE KEYS */;
/*!40000 ALTER TABLE `win` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-01-25 23:16:33
