-- MySQL dump 10.13  Distrib 5.7.26, for Linux (x86_64)
--
-- Host: localhost    Database: sfs_db
-- ------------------------------------------------------
-- Server version	5.7.26

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
-- Table structure for table `buddy_chat_text_messages`
--

DROP TABLE IF EXISTS `buddy_chat_text_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `buddy_chat_text_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `sender` varchar(22) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1967 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buddy_chat_text_messages`
--

LOCK TABLES `buddy_chat_text_messages` WRITE;
/*!40000 ALTER TABLE `buddy_chat_text_messages` DISABLE KEYS */;
INSERT INTO `buddy_chat_text_messages` VALUES (1961,19,'s6.100003_6','s6.100000_6','我们已经称为好友了,可以开始聊天了！',1583411790633),(1962,19,'s6.100002_6','s6.100000_6','我们已经称为好友了,可以开始聊天了！',1583411804984),(1963,19,'s6.100000_6','s6.100002_6','个梵蒂冈',1583415515219),(1964,19,'s6.100000_6','s6.100002_6','[:emo_swy]',1583415520351),(1965,19,'s6.100000_6','s6.100003_6','[:emo_azgc]',1583415525330),(1966,19,'s6.100000_6','s6.100003_6','热挖人啊',1583415530211);
/*!40000 ALTER TABLE `buddy_chat_text_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `online_times`
--

DROP TABLE IF EXISTS `online_times`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `online_times` (
  `openIdYMD` varchar(128) NOT NULL,
  `durationNum` bigint(11) NOT NULL,
  PRIMARY KEY (`openIdYMD`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `online_times`
--

LOCK TABLES `online_times` WRITE;
/*!40000 ALTER TABLE `online_times` DISABLE KEYS */;
INSERT INTO `online_times` VALUES ('384305665f5511eaaaa9000c290e82ac_2020-03-06',0),('412752e25ed611ea80eb000c290e82ac_2020-03-05',4884786),('412752e25ed611ea80eb000c290e82ac_2020-03-06',296739),('482b589e5edc11ea920d000c290e82ac_2020-03-05',3439082),('482b589e5edc11ea920d000c290e82ac_2020-03-06',4507686),('55a9fb205f4e11ea97b9000c290e82ac_2020-03-06',5349),('a5a42cbe5f5211eab641000c290e82ac_2020-03-06',0),('afb724605edd11eabcf5000c290e82ac_2020-03-05',572431),('afb724605edd11eabcf5000c290e82ac_2020-03-06',47373463),('bd815b3c5ed911eaa688000c290e82ac_2020-03-05',2836926),('bd815b3c5ed911eaa688000c290e82ac_2020-03-06',47775956),('c7f834625edb11ea9bbc000c290e82ac_2020-03-05',902798),('ccd7333a5ed511ea931c000c290e82ac_2020-03-05',7350350),('ccd7333a5ed511ea931c000c290e82ac_2020-03-06',4697437),('e9b281f25ed611ea8c49000c290e82ac_2020-03-05',6565740),('e9b281f25ed611ea8c49000c290e82ac_2020-03-06',3950241),('ec1591e25ed511ea8c49000c290e82ac_2020-03-05',7474624),('ec1591e25ed511ea8c49000c290e82ac_2020-03-06',1383413);
/*!40000 ALTER TABLE `online_times` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_banquet_messages`
--

DROP TABLE IF EXISTS `public_banquet_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_banquet_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  `sender` varchar(22) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `roomName` varchar(50) NOT NULL,
  `banquetUserId` varchar(22) NOT NULL,
  `banquetUserORank` int(10) NOT NULL,
  `banquetUserName` varchar(20) NOT NULL,
  `banquetType` int(10) NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4414 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_banquet_messages`
--

LOCK TABLES `public_banquet_messages` WRITE;
/*!40000 ALTER TABLE `public_banquet_messages` DISABLE KEYS */;
INSERT INTO `public_banquet_messages` VALUES (4405,4,'public banquet message',1583409948539,'s6.100000_6','all','prp_s6','s6.100000',4,'山若琳',1),(4406,4,'public banquet message',1583410200938,'s6.100003_6','all','prp_s6','s6.100003',4,'卞恨玉',1),(4407,4,'public banquet message',1583411753621,'s6.100004_6','all','prp_s6','s6.100004',4,'尤碧凡',1),(4408,4,'public banquet message',1583412412226,'s6.100002_6','all','prp_s6','s6.100002',5,'容幼丝',1),(4409,4,'public banquet message',1583412524202,'s6.100001_6','all','prp_s6','s6.100001',4,'慎冷卉',1),(4410,4,'public banquet message',1583412765294,'s6.100007_6','all','prp_s6','s6.100007',1,'何小丽',1),(4411,4,'public banquet message',1583415464937,'s6.100006_6','all','prp_s6','s6.100006',5,'桑怜翠',1),(4412,4,'public banquet message',1583460690194,'s6.100003_6','all','prp_s6','s6.100003',9,'卞恨玉',1),(4413,4,'public banquet message',1583462791522,'s6.100000_6','all','prp_s6','s6.100000',10,'山若琳',1);
/*!40000 ALTER TABLE `public_banquet_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_recruit_marry_messages`
--

DROP TABLE IF EXISTS `public_recruit_marry_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_recruit_marry_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  `sender` varchar(22) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `roomName` varchar(50) NOT NULL,
  `recruitChildId` varchar(22) NOT NULL,
  `recruitChildSex` int(10) NOT NULL,
  `recruitChildName` varchar(20) NOT NULL,
  `recruitChildTitle` int(10) NOT NULL,
  `recruitUserName` varchar(20) NOT NULL,
  `recruitChildDp` int(10) NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9049 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_recruit_marry_messages`
--

LOCK TABLES `public_recruit_marry_messages` WRITE;
/*!40000 ALTER TABLE `public_recruit_marry_messages` DISABLE KEYS */;
INSERT INTO `public_recruit_marry_messages` VALUES (9041,5,'recruit marry message',1583409564470,'s6.100000_6','all','prp_s6','s6.100000_1',2,'千金仕辞',2,'山若琳',4),(9042,5,'recruit marry message',1583410579082,'s6.100000_6','all','prp_s6','s6.100000_2',1,'公子骏升',1,'山若琳',7),(9043,5,'recruit marry message',1583412471805,'s6.100003_6','all','prp_s6','s6.100003_2',2,'千金辞泽',1,'卞恨玉',4),(9044,5,'recruit marry message',1583413504067,'s6.100004_6','all','prp_s6','s6.100004_1',2,'千金骏诚',1,'尤碧凡',8),(9045,5,'recruit marry message',1583461719712,'s6.100003_6','all','prp_s6','s6.100003_3',1,'公子逸烁',3,'卞恨玉',5),(9046,5,'recruit marry message',1583461723032,'s6.100003_6','all','prp_s6','s6.100003_1',1,'公子震振',3,'卞恨玉',2),(9047,5,'recruit marry message',1583462504975,'s6.100001_6','all','prp_s6','s6.100001_2',2,'千金然然',2,'慎冷卉',3),(9048,5,'recruit marry message',1583462614742,'s6.100001_6','all','prp_s6','s6.100001_3',1,'公子辰然',2,'慎冷卉',4);
/*!40000 ALTER TABLE `public_recruit_marry_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_red_messages`
--

DROP TABLE IF EXISTS `public_red_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_red_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  `sender` varchar(22) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `roomName` varchar(50) NOT NULL,
  `redId` varchar(32) NOT NULL,
  `redItemNo` int(10) NOT NULL,
  `carveUsers` text NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=288 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_red_messages`
--

LOCK TABLES `public_red_messages` WRITE;
/*!40000 ALTER TABLE `public_red_messages` DISABLE KEYS */;
INSERT INTO `public_red_messages` VALUES (281,2,'red package message',1583411881564,'s6.100000_6','all','prp_s6','26d3169e5ede11ea9588000c290e82ac',600014,'s6.100007,s6.100000'),(282,2,'red package message',1583411884829,'s6.100000_6','all','prp_s6','28c563265ede11eaaa78000c290e82ac',600012,'s6.100000'),(283,2,'red package message',1583411886984,'s6.100000_6','all','prp_s6','2a0ddaa65ede11ea9588000c290e82ac',600011,'s6.100000'),(284,2,'red package message',1583411888344,'s6.100000_6','all','prp_s6','2ade45f65ede11eabcf5000c290e82ac',600013,'s6.100000'),(285,2,'red package message',1583411889817,'s6.100000_6','all','prp_s6','2bbeb7d05ede11eab15d000c290e82ac',600011,''),(286,2,'red package message',1583411891288,'s6.100000_6','all','prp_s6','2c9f40485ede11eab15d000c290e82ac',600011,''),(287,2,'red package message',1583411893587,'s6.100000_6','all','prp_s6','2dfe47405ede11eabcf5000c290e82ac',600011,'s6.100000');
/*!40000 ALTER TABLE `public_red_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_system_league_messages`
--

DROP TABLE IF EXISTS `public_system_league_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_system_league_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  `sender` varchar(50) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `roomName` varchar(50) NOT NULL,
  `paramA` varchar(20) NOT NULL,
  `paramB` varchar(20) NOT NULL,
  `paramC` varchar(20) NOT NULL,
  `paramD` varchar(20) NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4142 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_system_league_messages`
--

LOCK TABLES `public_system_league_messages` WRITE;
/*!40000 ALTER TABLE `public_system_league_messages` DISABLE KEYS */;
INSERT INTO `public_system_league_messages` VALUES (4135,21,'beacon tower pre ',1583409421117,'npc','all','prp_s6','','','',''),(4136,12,'create league',1583410102624,'npc','all','prp_s6','山若琳','两千块大佬','',''),(4137,12,'create league',1583410588657,'npc','all','prp_s6','卞恨玉','唉唉唉唉','',''),(4138,6,'send launch league message',1583411947391,'npc','all','0272818a5eda11eab75c000c290e82ac','尤碧凡','','',''),(4139,6,'send launch league message',1583413545300,'npc','all','0272818a5eda11eab75c000c290e82ac','容幼丝','','',''),(4140,6,'send launch league message',1583416035969,'npc','all','0272818a5eda11eab75c000c290e82ac','桑怜翠','','',''),(4141,20,'beacon tower pre ',1583463420522,'npc','all','prp_s6','','','','');
/*!40000 ALTER TABLE `public_system_league_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `public_text_messages`
--

DROP TABLE IF EXISTS `public_text_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `public_text_messages` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `messageType` int(10) NOT NULL,
  `text` text NOT NULL,
  `sendTime` bigint(11) NOT NULL,
  `sender` varchar(22) NOT NULL,
  `receiver` varchar(22) DEFAULT NULL,
  `roomName` varchar(50) NOT NULL,
  PRIMARY KEY (`messageId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2535 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_text_messages`
--

LOCK TABLES `public_text_messages` WRITE;
/*!40000 ALTER TABLE `public_text_messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `public_text_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `loginName` varchar(50) NOT NULL,
  `lastLoginTime` bigint(11) NOT NULL,
  `lastOffTime` bigint(11) NOT NULL,
  `userId` varchar(11) NOT NULL,
  `userName` varchar(50) NOT NULL,
  `userLevel` int(11) NOT NULL,
  `serverId` int(11) NOT NULL,
  `vipLevel` int(11) NOT NULL,
  `icons` varchar(50) NOT NULL,
  `titleId` varchar(50) NOT NULL,
  `leagueId` varchar(50) NOT NULL,
  `platformId` varchar(11) DEFAULT NULL,
  `channelId` varchar(11) DEFAULT NULL,
  `deviceId` varchar(11) DEFAULT NULL,
  `openId` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`loginName`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('npc',0,0,'-1','npc',-1,-1,-1,'-1','-1','-1','-1','-1','-1',NULL),('s6.100000_6',1583463860848,1583463860848,'s6.100000','山若琳',10,6,7,'40001_0_1583463258','0_0','0272818a5eda11eab75c000c290e82ac','1','607','1','ccd7333a5ed511ea931c000c290e82ac'),('s6.100001_6',1583462367761,1583462650496,'s6.100001','慎冷卉',5,6,0,'40001_0_1583413051','0_0','','1','607','1','ec1591e25ed511ea8c49000c290e82ac'),('s6.100002_6',1583461324293,1583461324293,'s6.100002','容幼丝',6,6,4,'40003_0_0','0_0','0272818a5eda11eab75c000c290e82ac','1','607','1','412752e25ed611ea80eb000c290e82ac'),('s6.100003_6',1583461375262,1583463038561,'s6.100003','卞恨玉',9,6,6,'40001_0_0','0_0','242624665edb11eaa688000c290e82ac','1','607','1','e9b281f25ed611ea8c49000c290e82ac'),('s6.100004_6',1583461345267,1583461345267,'s6.100004','尤碧凡',8,6,0,'40003_0_0','0_0','0272818a5eda11eab75c000c290e82ac','1','607','1','bd815b3c5ed911eaa688000c290e82ac'),('s6.100005_6',1583411008740,1583411911538,'s6.100005','粱修洁',1,6,3,'40001_0_0','0_0','','1','607','1','c7f834625edb11ea9bbc000c290e82ac'),('s6.100006_6',1583463944641,1583463944641,'s6.100006','桑怜翠',6,6,0,'40001_0_1583414166','0_0','0272818a5eda11eab75c000c290e82ac','1','607','1','482b589e5edc11ea920d000c290e82ac'),('s6.100007_6',1583412730428,1583460103891,'s6.100007','何小丽',1,6,0,'40001_50003_1583414177','0_0','','1','607','1','afb724605edd11eabcf5000c290e82ac'),('s6.100008_6',1583460209403,1583460214752,'s6.100008','吉翊君',1,6,0,'40001_0_0','0_0','','1','607','1','55a9fb205f4e11ea97b9000c290e82ac'),('s6.100009_6',1583462124771,1583462124771,'s6.100009','谢之槐',2,6,0,'40001_0_0','0_0','','1','607','1','a5a42cbe5f5211eab641000c290e82ac'),('s6.100011_6',1583463223745,1583463223745,'s6.100011','裴绿海',3,6,0,'40001_0_0','0_0','','1','607','1','384305665f5511eaaaa9000c290e82ac');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-13  0:36:33
