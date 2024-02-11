DROP TABLE IF EXISTS `Computers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Computers` (
  `MAC` varchar(14) NOT NULL,
  `size` bigint(20) NOT NULL,
  `geo_location` int(11) NOT NULL,
  PRIMARY KEY (`MAC`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;