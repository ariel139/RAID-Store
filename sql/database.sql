-- MySQL dump 10.13  Distrib 5.7.42, for Linux (x86_64)
--
-- Host: localhost    Database: RAID
-- ------------------------------------------------------
-- Server version	5.7.42-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Computers`
--

DROP TABLE IF EXISTS `Computers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Computers` (
  `MAC` varchar(14) NOT NULL,
  `size` bigint(20) NOT NULL,
  `geo_location` int(11) NOT NULL,
  PRIMARY KEY (`MAC`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Computers`
--

LOCK TABLES `Computers` WRITE;
/*!40000 ALTER TABLE `Computers` DISABLE KEYS */;
/*!40000 ALTER TABLE `Computers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Data`
--

DROP TABLE IF EXISTS `Data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Data` (
  `hash` varchar(250) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `size` binary(1) NOT NULL,
  `path` varchar(255) NOT NULL,
  `relation` varchar(50) NOT NULL,
  `location` binary(1) NOT NULL,
  `parity` tinyint(1) NOT NULL DEFAULT '0',
  `Segment` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Data`
--

LOCK TABLES `Data` WRITE;
/*!40000 ALTER TABLE `Data` DISABLE KEYS */;
/*!40000 ALTER TABLE `Data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `computer_users`
--

DROP TABLE IF EXISTS `computer_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `computer_users` (
  `full_name` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `comouter` binary(1) NOT NULL,
  `salt` int(11) NOT NULL,
  PRIMARY KEY (`user_name`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `comouter` (`comouter`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `computer_users`
--

LOCK TABLES `computer_users` WRITE;
/*!40000 ALTER TABLE `computer_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `computer_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_users`
--

DROP TABLE IF EXISTS `data_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_users` (
  `user_id` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(64) NOT NULL,
  `AES_Key` varchar(256) NOT NULL,
  `salt` int(11) unsigned zerofill NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `AES_Key` (`AES_Key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_users`
--

LOCK TABLES `data_users` WRITE;
/*!40000 ALTER TABLE `data_users` DISABLE KEYS */;
INSERT INTO `data_users` VALUES ('ariel cohen','1212','6dfb725ef36958d2b68ef1ef1542556bdcb80c79f7fc67b6e5e9cb67a66a1e26','63f442d97278ea7259619983a830580380087b80554167b7c8570250283807dc56ea2c93a3611ea0d753faa2aa536d013cdda941d5edcb08281beed94b5e8a6ce7b46887e74803fdcdb932f57b1dde35a5c649ab502e342c2fe2314620e1eb78bd9ceec59375a06797583b347cea09f6d3bf1fdfa6ac3635382a70f11683d02b',00066560748),('ariel0','ariel cohen','2f694c605dbdb6ebf164bb2fd3f7385b938f388fff6419f13243c65c64082158','8600253fa300b4ddef8eb75a72d3347dee473e537922fba6f0dcc39b51045281b30835af665fc8b36f4f0032e464ace72a73d73d7f6e130aa137118ac0f5f6064c3beecd197bf44b39794d9286414b7905a613031c768943f82025477c6b3f8dd04e829f0086d6041fb7ca0a96ca5b757d7bd9925516102a357632afe00d7a17',00082390219),('ariel1d2dd4','ariel cohen','6e1fee8478a2e2549a6959813073ba237117ebad120aa365aa35ecb7582fc21c','5548ee276dd51fbeb02ac7ff5f421370ddb8addf28b42cbd684c7dc609c43d9d8671cd32750de19c249d5379f5f5fc6ad7c9bc45b48b59704a065e1cee363d2eb334325dca30c25be697a78df67328c92825a37690f027d9ce7559c8ab4d1214a2f3d504ccf5d68118df1a02d8c71b1bd54909b48fe86f3d03d1d5c7a50e7dec',01075058805);
/*!40000 ALTER TABLE `data_users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-04 13:15:42
