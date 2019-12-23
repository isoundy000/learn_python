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
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buddy_chat_text_messages`
--

LOCK TABLES `buddy_chat_text_messages` WRITE;
/*!40000 ALTER TABLE `buddy_chat_text_messages` DISABLE KEYS */;
INSERT INTO `buddy_chat_text_messages` VALUES (28,19,'1000000001_6','1000000005_6','我们已经称为好友了,可以开始聊天了！',1575012201889),(29,19,'1000000001_6','1000000005_6','走开',1575012213771),(30,19,'1000000001_6','1000000005_6','[:emo_xytc]',1575012219616),(31,19,'1000000005_6','1000000001_6','大风刮过和',1575012409277),(32,19,'1000000005_6','1000000001_6','[:emo_gc]',1575012423392),(33,19,'1000000072_1','1000000062_1','我们已经称为好友了,可以开始聊天了！',1575268262129),(34,19,'1000000027_6','1000000028_6','我们已经称为好友了,可以开始聊天了！',1575279593449),(35,19,'1000000043_6','1000000039_6','我们已经称为好友了,可以开始聊天了！',1575350290924),(36,19,'1000000039_6','1000000043_6','[:emo_gc]',1575350304554),(37,19,'1000000039_6','1000000043_6','[:emo_hj]',1575350308159),(38,19,'1000000000_1','1000000005_1','我们已经称为好友了,可以开始聊天了！',1575427178134);
/*!40000 ALTER TABLE `buddy_chat_text_messages` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_banquet_messages`
--

LOCK TABLES `public_banquet_messages` WRITE;
/*!40000 ALTER TABLE `public_banquet_messages` DISABLE KEYS */;
INSERT INTO `public_banquet_messages` VALUES (135,4,'public banquet message',1575001595425,'1000000000_6','all','prp_s6','1000000000',5,'喻摇伽',1),(136,4,'public banquet message',1575001637425,'1000000001_6','all','prp_s6','1000000001',5,'康轩宇',1),(137,4,'public banquet message',1575006196700,'1000000005_6','all','prp_s6','1000000005',4,'凌静蕾',1),(138,4,'public banquet message',1575011492690,'1000000010_6','all','prp_s6','1000000010',4,'从南珍',1),(139,4,'public banquet message',1575017080586,'1000000009_6','all','prp_s6','1000000009',4,'步语蓉',1),(140,4,'public banquet message',1575254531129,'1000000069_1','all','prp_s1','1000000069',5,'查冬莲',1),(141,4,'public banquet message',1575254675871,'1000000068_1','all','prp_s1','1000000068',4,'国君浩',1),(142,4,'public banquet message',1575256617570,'1000000015_6','all','prp_s6','1000000015',5,'祁槑槑',1),(143,4,'public banquet message',1575276796709,'1000000029_6','all','prp_s6','1000000029',4,'蓝寒梦',1),(144,4,'public banquet message',1575277496464,'1000000028_6','all','prp_s6','1000000028',5,'容尔阳',1),(145,4,'public banquet message',1575281176149,'1000000031_6','all','prp_s6','1000000031',5,'巩海亦',1),(146,4,'public banquet message',1575338694086,'1000000027_6','all','prp_s6','1000000027',5,'余慕山',1),(147,4,'public banquet message',1575339686735,'1000000013_1','all','prp_s1','1000000013',5,'凌思山',1),(148,4,'public banquet message',1575340712171,'1000000036_6','all','prp_s6','1000000036',4,'华不斜',1),(149,4,'public banquet message',1575341378029,'1000000038_6','all','prp_s6','1000000038',5,'仇平彤',1),(150,4,'public banquet message',1575343516680,'1000000009_1','all','prp_s1','1000000009',5,'仇初翠',1),(151,4,'public banquet message',1575344346527,'1000000039_6','all','prp_s6','1000000039',5,'褚从雪',1),(152,4,'public banquet message',1575344837123,'1000000042_6','all','prp_s6','1000000042',5,'吉夜蓉',1),(153,4,'public banquet message',1575346288177,'1000000043_6','all','prp_s6','1000000043',1,'平依秋',1),(154,4,'public banquet message',1575346331346,'1000000045_6','all','prp_s6','1000000045',21,'焦秋歌',1),(155,4,'public banquet message',1575346999930,'1000000046_6','all','prp_s6','1000000046',1,'蒲寻南',1),(156,4,'public banquet message',1575348050228,'1000000048_6','all','prp_s6','1000000048',1,'姜思远',1),(157,4,'public banquet message',1575348375281,'1000000049_6','all','prp_s6','1000000049',1,'谈冬灵',1),(158,4,'public banquet message',1575348686038,'1000000050_6','all','prp_s6','1000000050',1,'卓依霜',1),(159,4,'public banquet message',1575348849934,'1000000051_6','all','prp_s6','1000000051',1,'孙曼文',1),(160,4,'public banquet message',1575349003668,'1000000047_6','all','prp_s6','1000000047',23,'诸葛青烟',1),(161,4,'public banquet message',1575359412533,'1000000026_6','all','prp_s6','1000000026',5,'沃满天',1),(162,4,'public banquet message',1575377230716,'1000000000_1','all','prp_s1','1000000000',5,'花之桃',1),(163,4,'public banquet message',1575378067570,'1000000002_1','all','prp_s1','1000000002',5,'牧凤妖',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_recruit_marry_messages`
--

LOCK TABLES `public_recruit_marry_messages` WRITE;
/*!40000 ALTER TABLE `public_recruit_marry_messages` DISABLE KEYS */;
INSERT INTO `public_recruit_marry_messages` VALUES (142,5,'recruit marry message',1575005891475,'1000000001_6','all','prp_s6','1000000001_1',1,'公子振振',1,'康轩宇',2),(143,5,'recruit marry message',1575006114168,'1000000047_1','all','prp_s1','1000000047_1',2,'千金年胤',1,'竺夜白',1),(144,5,'recruit marry message',1575006356026,'1000000005_6','all','prp_s6','1000000005_1',1,'公子杰振',1,'凌静蕾',7),(145,5,'recruit marry message',1575012098794,'1000000005_6','all','prp_s6','1000000005_2',2,'千金晨龙',7,'凌静蕾',3),(146,5,'recruit marry message',1575017008653,'1000000054_1','all','prp_s1','1000000054_1',2,'千金凯宇',1,'严仁杰',2),(147,5,'recruit marry message',1575018174995,'1000000013_6','all','prp_s6','1000000013_1',2,'千金远骞',2,'翟问柳',1),(148,5,'recruit marry message',1575251318564,'1000000052_1','all','prp_s1','1000000052_2',2,'千金仕佑',1,'卓静丹',8),(149,5,'recruit marry message',1575276916682,'1000000029_6','all','prp_s6','1000000029_1',2,'千金然颜',1,'蓝寒梦',5),(150,5,'recruit marry message',1575277592781,'1000000010_1','all','prp_s1','1000000010_2',2,'千金平楷',1,'晁冰双',3),(151,5,'recruit marry message',1575277663015,'1000000010_1','all','prp_s1','1000000010_1',1,'公子骞然',1,'晁冰双',3),(152,5,'recruit marry message',1575277664644,'1000000010_1','all','prp_s1','1000000010_3',2,'千金延运',1,'晁冰双',3),(153,5,'recruit marry message',1575277715038,'1000000010_1','all','prp_s1','1000000010_4',2,'千金暄骏',1,'晁冰双',5),(154,5,'recruit marry message',1575287372796,'1000000031_6','all','prp_s6','1000000031_2',1,'公子震振',1,'巩海亦',8),(155,5,'recruit marry message',1575287706820,'1000000010_1','all','prp_s1','1000000010_7',1,'公子铭运',1,'晁冰双',4),(156,5,'recruit marry message',1575287709101,'1000000010_1','all','prp_s1','1000000010_5',2,'千金鸿杞',1,'晁冰双',3),(157,5,'recruit marry message',1575287805331,'1000000010_1','all','prp_s1','1000000010_6',1,'公子海浩',2,'晁冰双',8),(158,5,'recruit marry message',1575287857096,'1000000010_1','all','prp_s1','1000000010_9',1,'公子晨驰',1,'晁冰双',1),(159,5,'recruit marry message',1575287973586,'1000000010_1','all','prp_s1','1000000010_7',1,'公子铭运',1,'晁冰双',4),(160,5,'recruit marry message',1575290094269,'1000000028_6','all','prp_s6','1000000028_1',2,'千金晨翰',1,'容尔阳',5),(161,5,'recruit marry message',1575339792777,'1000000027_6','all','prp_s6','1000000027_1',2,'千金运星',1,'余慕山',7),(162,5,'recruit marry message',1575344610027,'1000000039_6','all','prp_s6','1000000039_1',1,'公子柏泽',1,'褚从雪',7),(163,5,'recruit marry message',1575344994904,'1000000042_6','all','prp_s6','1000000042_1',1,'公子俊辰',1,'吉夜蓉',4),(164,5,'recruit marry message',1575368484818,'1000000032_6','all','prp_s6','1000000032_1',2,'千金俊辰',1,'闵尔冬',1),(165,5,'recruit marry message',1575376876603,'1000000000_1','all','prp_s1','1000000000_1',1,'公子晨龙',1,'花之桃',8),(166,5,'recruit marry message',1575426384564,'1000000002_1','all','prp_s1','1000000002_1',1,'公子谷祯',1,'牧凤妖',2),(167,5,'recruit marry message',1575440105495,'1000000004_1','all','prp_s1','1000000004_2',1,'公子晨骞',1,'骆阑悦',4),(168,5,'recruit marry message',1575441371546,'1000000000_1','all','prp_s1','1000000000_1',1,'公子晨龙',1,'花之桃',8),(169,5,'recruit marry message',1575441376975,'1000000000_1','all','prp_s1','1000000000_1',1,'公子晨龙',1,'花之桃',8),(170,5,'recruit marry message',1575453494443,'1000000000_1','all','prp_s1','1000000000_1',1,'公子晨龙',1,'花之桃',8),(171,5,'recruit marry message',1575453511012,'1000000000_1','all','prp_s1','1000000000_1',1,'公子晨龙',1,'花之桃',8);
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
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_red_messages`
--

LOCK TABLES `public_red_messages` WRITE;
/*!40000 ALTER TABLE `public_red_messages` DISABLE KEYS */;
INSERT INTO `public_red_messages` VALUES (32,2,'red package message',1575008285301,'1000000001_6','all','prp_s6','011f91da127011eaa01c000c290e82ac',600014,'1000000004'),(33,2,'red package message',1575008288549,'1000000001_6','all','prp_s6','030f70e6127011eaae6f000c290e82ac',600013,''),(34,2,'red package message',1575008290801,'1000000001_6','all','prp_s6','0466bb84127011eabdc9000c290e82ac',600012,''),(35,2,'red package message',1575008294009,'1000000001_6','all','prp_s6','06506e72127011eaa3c9000c290e82ac',600011,'1000000004,1000000005'),(36,2,'red package message',1575008324752,'1000000001_6','all','24b542d0126a11eaa0fa000c290e82ac','18a35760127011eabdc9000c290e82ac',600021,''),(37,2,'red package message',1575008327057,'1000000001_6','all','24b542d0126a11eaa0fa000c290e82ac','1a03220c127011eaacb1000c290e82ac',600022,''),(38,2,'red package message',1575008334132,'1000000001_6','all','24b542d0126a11eaa0fa000c290e82ac','1e3a94a4127011eab68b000c290e82ac',600023,''),(39,2,'red package message',1575008336135,'1000000001_6','all','24b542d0126a11eaa0fa000c290e82ac','1f6bb16e127011eabdc9000c290e82ac',600024,''),(40,2,'red package message',1575012114633,'1000000005_6','all','09e35e86126c11eaa3c9000c290e82ac','eb955a44127811ea9570000c290e82ac',600023,'1000000005'),(41,2,'red package message',1575020946743,'1000000001_6','all','prp_s6','7bee7f4e128d11ea8ced000c290e82ac',600013,'1000000013'),(42,2,'red package message',1575020965828,'1000000001_6','all','822f2d90128d11eab5a1000c290e82ac','874d91ea128d11ea8822000c290e82ac',600023,'1000000001'),(43,2,'red package message',1575253123692,'1000000067_1','all','prp_s1','102dcdb814aa11eab7a3000c29a82b41',600011,'1000000062'),(44,2,'red package message',1575288982694,'1000000031_6','all','prp_s6','8dcf28ea14fd11ea9807000c290e82ac',600014,'1000000031'),(45,2,'red package message',1575288992718,'1000000031_6','all','prp_s6','93c8e52414fd11eaae4b000c290e82ac',600014,'1000000031'),(46,2,'red package message',1575288999267,'1000000031_6','all','prp_s6','97aff54214fd11eabea2000c290e82ac',600014,'1000000031'),(47,2,'red package message',1575289040631,'1000000031_6','all','prp_s6','b0542ab414fd11eaae4b000c290e82ac',600014,'1000000031'),(48,2,'red package message',1575289079574,'1000000027_6','all','prp_s6','c78daf1614fd11eabda1000c290e82ac',600014,'1000000027,1000000031'),(49,2,'red package message',1575289086508,'1000000027_6','all','prp_s6','cbb03fdc14fd11eaa28c000c290e82ac',600013,'1000000027,1000000031'),(50,2,'red package message',1575289330259,'1000000031_6','all','prp_s6','5cf97cba14fe11eabda1000c290e82ac',600014,'1000000031'),(51,2,'red package message',1575289348596,'1000000031_6','all','prp_s6','67e78a4a14fe11eaa28c000c290e82ac',600013,'1000000031'),(52,2,'red package message',1575289387067,'1000000031_6','all','prp_s6','7ed1b69014fe11eaaacb000c290e82ac',600014,'1000000031'),(53,2,'red package message',1575289411805,'1000000031_6','all','prp_s6','8d94807c14fe11eabea2000c290e82ac',600014,'1000000031'),(54,2,'red package message',1575289919008,'1000000027_6','all','prp_s6','bbe54fbe14ff11eabea2000c290e82ac',600013,''),(55,2,'red package message',1575290102409,'1000000027_6','all','230ac9f8150011eaa28c000c290e82ac','29360d74150011eabea2000c290e82ac',600023,''),(56,2,'red package message',1575290106938,'1000000027_6','all','230ac9f8150011eaa28c000c290e82ac','2be90bac150011eabea2000c290e82ac',600024,''),(57,2,'red package message',1575290362177,'1000000027_6','all','prp_s6','c40b863a150011ea8d88000c290e82ac',600012,'1000000027'),(58,2,'red package message',1575290364322,'1000000027_6','all','prp_s6','c5532890150011eaa001000c290e82ac',600011,'1000000027'),(59,2,'red package message',1575290392761,'1000000027_6','all','prp_s6','d64541d8150011ea8d88000c290e82ac',600014,'1000000027'),(60,2,'red package message',1575341604409,'1000000039_6','all','prp_s6','12cb38de157811ea8d88000c290e82ac',600011,''),(61,2,'red package message',1575350652217,'1000000039_6','all','prp_s6','23b610a0158d11eaa7f6000c290e82ac',600013,'1000000050,1000000026,1000000039'),(62,2,'red package message',1575353534391,'1000000050_6','all','prp_s6','d99e4a30159311eabc39000c290e82ac',600012,'1000000050,1000000026'),(63,2,'red package message',1575363788254,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac','b9655dfe15ab11eaa930000c290e82ac',600024,''),(64,2,'red package message',1575426158210,'1000000005_1','all','62f11e82175d11eaaa52000c29a82b41','29dcd230182a11ea8d64000c29a82b41',600024,''),(65,2,'red package message',1575426167856,'1000000005_1','all','62f11e82175d11eaaa52000c29a82b41','2f222c86182a11ea883e000c29a82b41',600023,'1000000005');
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
) ENGINE=InnoDB AUTO_INCREMENT=711 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_system_league_messages`
--

LOCK TABLES `public_system_league_messages` WRITE;
/*!40000 ALTER TABLE `public_system_league_messages` DISABLE KEYS */;
INSERT INTO `public_system_league_messages` VALUES (594,6,'send launch league message',1575000013931,'npc','all','ecd685ca10bd11ea970c000c29a82b41','白傻','','',''),(595,12,'create league',1575005768054,'npc','all','prp_s6','康轩宇','没元宝了','',''),(596,6,'send launch league message',1575006119146,'npc','all','24b542d0126a11eaa0fa000c290e82ac','喻摇伽','','',''),(597,12,'create league',1575006582049,'npc','all','prp_s6','凌静蕾','木有钱啊','',''),(598,11,'upgrade league tech message',1575009007913,'npc','all','24b542d0126a11eaa0fa000c290e82ac','1','1','',''),(599,11,'upgrade league tech message',1575009008441,'npc','all','24b542d0126a11eaa0fa000c290e82ac','1','2','',''),(600,11,'upgrade league tech message',1575009011202,'npc','all','24b542d0126a11eaa0fa000c290e82ac','2','1','',''),(601,11,'upgrade league tech message',1575009011700,'npc','all','24b542d0126a11eaa0fa000c290e82ac','2','2','',''),(602,11,'upgrade league tech message',1575009012370,'npc','all','24b542d0126a11eaa0fa000c290e82ac','2','3','',''),(603,11,'upgrade league tech message',1575009015470,'npc','all','24b542d0126a11eaa0fa000c290e82ac','3','1','',''),(604,18,'update league user power',1575009102266,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','喻摇伽','0','1'),(605,18,'update league user power',1575009107638,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','喻摇伽','1','0'),(606,17,'update league recruit state',1575009116478,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','0','',''),(607,16,'change league name',1575009134986,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','热特权','',''),(608,9,'send launch league message',1575009140937,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','','',''),(609,13,'tran**er league leader',1575009534759,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','喻摇伽','',''),(610,15,'expulsion user from league',1575009570731,'npc','all','24b542d0126a11eaa0fa000c290e82ac','康轩宇','喻摇伽','',''),(611,6,'send launch league message',1575010441637,'npc','all','24b542d0126a11eaa0fa000c290e82ac','常从菡','','',''),(612,15,'expulsion user from league',1575010491204,'npc','all','24b542d0126a11eaa0fa000c290e82ac','常从菡','喻摇伽','',''),(613,12,'create league',1575012045469,'npc','all','prp_s1','居文龙','点点滴滴','',''),(614,6,'send launch league message',1575012211605,'npc','all','c255ac2e127811eab1ec000c29a82b41','姜秋实','','',''),(615,15,'expulsion user from league',1575012220213,'npc','all','c255ac2e127811eab1ec000c29a82b41','姜秋实','居文龙','',''),(616,12,'create league',1575015590882,'npc','all','prp_s1','何初翠','呦呦呦右右右','',''),(617,6,'send launch league message',1575015595890,'npc','all','03925c66128111ea94ed000c29a82b41','水小钰','','',''),(618,15,'expulsion user from league',1575015611647,'npc','all','03925c66128111ea94ed000c29a82b41','水小钰','何初翠','',''),(619,6,'send launch league message',1575016138785,'npc','all','c255ac2e127811eab1ec000c29a82b41','牧恶天','','',''),(620,15,'expulsion user from league',1575016156747,'npc','all','c255ac2e127811eab1ec000c29a82b41','牧恶天','居文龙','',''),(621,6,'send launch league message',1575016201120,'npc','all','03925c66128111ea94ed000c29a82b41','陈书航','','',''),(622,15,'expulsion user from league',1575016458789,'npc','all','03925c66128111ea94ed000c29a82b41','陈书航','何初翠','',''),(623,6,'send launch league message',1575016687043,'npc','all','03925c66128111ea94ed000c29a82b41','邓三颜','','',''),(624,15,'expulsion user from league',1575016697119,'npc','all','03925c66128111ea94ed000c29a82b41','邓三颜','何初翠','',''),(625,6,'send launch league message',1575017539380,'npc','all','03925c66128111ea94ed000c29a82b41','池惜筠','','',''),(626,15,'expulsion user from league',1575017546415,'npc','all','03925c66128111ea94ed000c29a82b41','池惜筠','何初翠','',''),(627,6,'send launch league message',1575019340801,'npc','all','09e35e86126c11eaa3c9000c290e82ac','步语蓉','','',''),(628,12,'create league',1575020957272,'npc','all','prp_s6','康轩宇','谽家咯看见了','',''),(629,21,'beacon tower pre ',1575028620091,'npc','all','prp_s1','','','',''),(630,21,'beacon tower pre ',1575028620191,'npc','all','prp_s6','','','',''),(631,21,'beacon tower pre ',1575028620212,'npc','all','prp_s6','','','',''),(632,21,'beacon tower pre ',1575028620663,'npc','all','prp_s6','','','',''),(633,20,'beacon tower pre ',1575082620062,'npc','all','prp_s6','','','',''),(634,20,'beacon tower pre ',1575082620139,'npc','all','prp_s6','','','',''),(635,20,'beacon tower pre ',1575082620188,'npc','all','prp_s1','','','',''),(636,21,'beacon tower pre ',1575115020079,'npc','all','prp_s6','','','',''),(637,21,'beacon tower pre ',1575115020174,'npc','all','prp_s6','','','',''),(638,21,'beacon tower pre ',1575115020211,'npc','all','prp_s1','','','',''),(639,20,'beacon tower pre ',1575169020097,'npc','all','prp_s6','','','',''),(640,20,'beacon tower pre ',1575169020167,'npc','all','prp_s6','','','',''),(641,20,'beacon tower pre ',1575169020157,'npc','all','prp_s1','','','',''),(642,21,'beacon tower pre ',1575201420143,'npc','all','prp_s6','','','',''),(643,21,'beacon tower pre ',1575201420188,'npc','all','prp_s1','','','',''),(644,21,'beacon tower pre ',1575201420171,'npc','all','prp_s6','','','',''),(645,6,'send launch league message',1575254109569,'npc','all','03925c66128111ea94ed000c29a82b41','池惜筠','','',''),(646,15,'expulsion user from league',1575254117871,'npc','all','03925c66128111ea94ed000c29a82b41','池惜筠','何初翠','',''),(647,6,'send launch league message',1575254523183,'npc','all','03925c66128111ea94ed000c29a82b41','弘冬莲','','',''),(648,15,'expulsion user from league',1575254543221,'npc','all','03925c66128111ea94ed000c29a82b41','弘冬莲','何初翠','',''),(649,6,'send launch league message',1575255284678,'npc','all','03925c66128111ea94ed000c29a82b41','习依波','','',''),(650,15,'expulsion user from league',1575255320719,'npc','all','03925c66128111ea94ed000c29a82b41','习依波','何初翠','',''),(651,20,'beacon tower pre ',1575255420139,'npc','all','prp_s6','','','',''),(652,20,'beacon tower pre ',1575255420121,'npc','all','prp_s1','','','',''),(653,20,'beacon tower pre ',1575255420161,'npc','all','prp_s6','','','',''),(654,12,'create league',1575256721800,'npc','all','prp_s6','祁槑槑','图二三月','',''),(655,10,'send launch league message',1575258002852,'npc','all','ecd685ca10bd11ea970c000c29a82b41','白傻','','',''),(656,12,'create league',1575258023329,'npc','all','prp_s1','白傻','撒旦法我','',''),(657,6,'send launch league message',1575258027855,'npc','all','7891f68a14b511ea846e000c29a82b41','袁黎昕','','',''),(658,15,'expulsion user from league',1575258037130,'npc','all','7891f68a14b511ea846e000c29a82b41','袁黎昕','白傻','',''),(659,6,'send launch league message',1575259285882,'npc','all','c255ac2e127811eab1ec000c29a82b41','国君浩','','',''),(660,12,'create league',1575274457493,'npc','all','prp_s1','双傲薇','萨达按时啊啊','',''),(661,6,'send launch league message',1575275808365,'npc','all','bc18b1d414db11eab470000c29a82b41','班友瑶','','',''),(662,6,'send launch league message',1575277128903,'npc','all','09e35e86126c11eaa3c9000c290e82ac','蓝寒梦','','',''),(663,6,'send launch league message',1575281305260,'npc','all','09e35e86126c11eaa3c9000c290e82ac','巩海亦','','',''),(664,21,'beacon tower pre ',1575287820086,'npc','all','prp_s6','','','',''),(665,21,'beacon tower pre ',1575287820181,'npc','all','prp_s6','','','',''),(666,21,'beacon tower pre ',1575287820329,'npc','all','prp_s1','','','',''),(667,6,'send launch league message',1575289673517,'npc','all','09e35e86126c11eaa3c9000c290e82ac','容尔阳','','',''),(668,12,'create league',1575290092099,'npc','all','prp_s6','余慕山','的阿萨啊都是','',''),(669,10,'send launch league message',1575290177800,'npc','all','09e35e86126c11eaa3c9000c290e82ac','巩海亦','','',''),(670,6,'send launch league message',1575339986477,'npc','all','bc18b1d414db11eab470000c29a82b41','凌思山','','',''),(671,6,'send launch league message',1575341605809,'npc','all','09e35e86126c11eaa3c9000c290e82ac','华不斜','','',''),(672,20,'beacon tower pre ',1575341820094,'npc','all','prp_s6','','','',''),(673,20,'beacon tower pre ',1575341820113,'npc','all','prp_s1','','','',''),(674,20,'beacon tower pre ',1575341820155,'npc','all','prp_s6','','','',''),(675,6,'send launch league message',1575343341424,'npc','all','230ac9f8150011eaa28c000c290e82ac','褚从雪','','',''),(676,20,'beacon tower pre ',1575345733559,'npc','all','prp_s1','','','',''),(677,21,'beacon tower pre ',1575345733660,'npc','all','prp_s1','','','',''),(678,20,'beacon tower pre ',1575345733738,'npc','all','prp_s1','','','',''),(679,21,'beacon tower pre ',1575345733819,'npc','all','prp_s1','','','',''),(680,20,'beacon tower pre ',1575345733907,'npc','all','prp_s1','','','',''),(681,21,'beacon tower pre ',1575345733954,'npc','all','prp_s1','','','',''),(682,20,'beacon tower pre ',1575345734098,'npc','all','prp_s1','','','',''),(683,21,'beacon tower pre ',1575345734179,'npc','all','prp_s1','','','',''),(684,12,'create league',1575350141735,'npc','all','prp_s6','诸葛青烟','打但是','',''),(685,6,'send launch league message',1575359644103,'npc','all','09e35e86126c11eaa3c9000c290e82ac','沃满天','','',''),(686,12,'create league',1575362872037,'npc','all','prp_s6','荣浩然','发送到发送到','',''),(687,12,'create league',1575362877904,'npc','all','prp_s6','孙曼文','浮点数发萨达','',''),(688,6,'send launch league message',1575362904279,'npc','all','9ac40f4615a911ea8114000c290e82ac','宰天荷','','',''),(689,10,'send launch league message',1575369377682,'npc','all','9ac40f4615a911ea8114000c290e82ac','宰天荷','','',''),(690,12,'create league',1575369407316,'npc','all','prp_s6','宰天荷','小夏夏是啊啊','',''),(691,21,'beacon tower pre ',1575374220125,'npc','all','prp_s6','','','',''),(692,21,'beacon tower pre ',1575374220143,'npc','all','prp_s6','','','',''),(693,12,'create league',1575376969628,'npc','all','prp_s1','骆阑悦','唯我独尊啊啊','',''),(694,12,'create league',1575377157442,'npc','all','prp_s1','骆阑悦','萨达啊按时啊','',''),(695,6,'send launch league message',1575377787114,'npc','all','61599f8c16f811eaa9f7000c29a82b41','花之桃','','',''),(696,6,'send launch league message',1575378408690,'npc','all','61599f8c16f811eaa9f7000c29a82b41','牧凤妖','','',''),(697,20,'beacon tower pre ',1575385838527,'npc','all','prp_s1','','','',''),(698,21,'beacon tower pre ',1575421184069,'npc','all','prp_s1','','','',''),(699,12,'create league',1575424483079,'npc','all','prp_s1','古浩阑','打的','',''),(700,6,'send launch league message',1575424579822,'npc','all','9743610a15a911ea98d9000c290e82ac','平依秋','','',''),(701,20,'beacon tower pre ',1575428520800,'npc','all','prp_s6','','','',''),(702,20,'beacon tower pre ',1575428520783,'npc','all','prp_s6','','','',''),(703,20,'beacon tower pre ',1575428522189,'npc','all','prp_s6','','','',''),(704,20,'beacon tower pre ',1575428522233,'npc','all','prp_s6','','','',''),(705,21,'beacon tower pre ',1575463866236,'npc','all','prp_s6','','','',''),(706,21,'beacon tower pre ',1575463866286,'npc','all','prp_s6','','','',''),(707,21,'beacon tower pre ',1575463867681,'npc','all','prp_s6','','','',''),(708,21,'beacon tower pre ',1575463867702,'npc','all','prp_s6','','','',''),(709,20,'beacon tower pre ',1575480058634,'npc','all','prp_s1','','','',''),(710,21,'beacon tower pre ',1575515404129,'npc','all','prp_s1','','','','');
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
) ENGINE=InnoDB AUTO_INCREMENT=444 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `public_text_messages`
--

LOCK TABLES `public_text_messages` WRITE;
/*!40000 ALTER TABLE `public_text_messages` DISABLE KEYS */;
INSERT INTO `public_text_messages` VALUES (356,1,'[:emo_ts]',1575008305330,'1000000001_6','all','prp_s6'),(357,1,'[:emo_swy]',1575011090757,'1000000004_6','all','prp_s6'),(358,1,'[:emo_zxdhb]',1575011096675,'1000000004_6','all','prp_s6'),(359,1,'[:emo_swy]',1575011100302,'1000000004_6','all','prp_s6'),(360,1,'[:emo_jz]',1575252558456,'1000000067_1','all','prp_s1'),(361,1,'[:emo_gc]',1575254038771,'1000000069_1','all','prp_s1'),(362,1,'1232132131',1575268160640,'1000000062_1','all','prp_s1'),(363,1,'21412321',1575268197147,'1000000062_1','all','prp_s1'),(364,1,'[:emo_ax]',1575268214263,'1000000062_1','all','prp_s1'),(365,1,'1',1575274361441,'1000000002_1','all','prp_s1'),(366,1,'12312',1575275033837,'1000000004_1','all','prp_s1'),(367,1,'4t3ewrfdscxz',1575275419818,'1000000004_1','all','prp_s1'),(368,1,'[:emo_azgc]',1575275424658,'1000000004_1','all','prp_s1'),(369,1,'213213',1575275445390,'1000000002_1','all','prp_s1'),(370,1,'21321312',1575275763413,'1000000002_1','all','bc18b1d414db11eab470000c29a82b41'),(371,1,'1212',1575275838403,'1000000004_1','all','bc18b1d414db11eab470000c29a82b41'),(372,1,'[:emo_jz]',1575275845888,'1000000004_1','all','bc18b1d414db11eab470000c29a82b41'),(373,1,'88888',1575278936789,'1000000027_6','all','prp_s6'),(374,1,'[:emo_hs]',1575278973334,'1000000027_6','all','prp_s6'),(375,1,'[:emo_hj]',1575279198835,'1000000027_6','all','prp_s6'),(376,1,'[:emo_jz]',1575279203785,'1000000027_6','all','prp_s6'),(377,1,'[:emo_gc]',1575279231488,'1000000027_6','all','prp_s6'),(378,1,'[:emo_swy]',1575279521984,'1000000020_6','all','prp_s6'),(379,1,'[:emo_zl]',1575279526449,'1000000027_6','all','prp_s6'),(380,1,'[:emo_hj]',1575279555447,'1000000027_6','all','prp_s6'),(381,1,'[:emo_ts]',1575279559160,'1000000027_6','all','prp_s6'),(382,1,'[:emo_zl]',1575279608657,'1000000027_6','all','prp_s6'),(383,1,'[:emo_ax]',1575279618437,'1000000027_6','all','prp_s6'),(384,1,'[:emo_sq]',1575279623058,'1000000027_6','all','prp_s6'),(385,1,'[:emo_zl]',1575279630659,'1000000020_6','all','prp_s6'),(386,1,'[:emo_tsn]',1575279634961,'1000000020_6','all','prp_s6'),(387,1,'[:emo_ts]',1575279640784,'1000000027_6','all','prp_s6'),(388,1,'[:emo_hh]',1575279644911,'1000000027_6','all','prp_s6'),(389,1,'[:emo_hg]',1575281378758,'1000000031_6','all','prp_s6'),(390,1,'[:emo_swy]',1575281385177,'1000000031_6','all','prp_s6'),(391,1,'[:emo_ax]',1575281390183,'1000000031_6','all','prp_s6'),(392,1,'[:emo_hj]',1575281393377,'1000000031_6','all','prp_s6'),(393,1,'[:emo_gc]',1575281398739,'1000000031_6','all','prp_s6'),(394,1,'[:emo_sq]',1575281404446,'1000000031_6','all','prp_s6'),(395,1,'[:emo_hh]',1575288009368,'1000000010_1','all','prp_s1'),(396,1,'123',1575288971379,'1000000031_6','all','prp_s6'),(397,1,'[:emo_hj]',1575343677169,'1000000009_1','all','prp_s1'),(398,1,'[:emo_sq]',1575343685227,'1000000038_6','all','prp_s6'),(399,1,'[:emo_xytc]',1575343852778,'1000000012_1','all','prp_s1'),(400,1,'[:emo_sq]',1575344944873,'1000000042_6','all','prp_s6'),(401,1,'[:emo_ax]',1575359717617,'1000000026_6','all','09e35e86126c11eaa3c9000c290e82ac'),(402,1,'[:emo_zl]',1575362882730,'1000000036_6','all','prp_s6'),(403,1,'[:emo_hj]',1575362996130,'1000000026_6','all','prp_s6'),(404,1,'[:emo_ax]',1575363049941,'1000000051_6','all','prp_s6'),(405,1,'[:emo_hj]',1575363162492,'1000000051_6','all','prp_s6'),(406,1,'1112',1575363247979,'1000000051_6','all','prp_s6'),(407,1,'412321',1575363378827,'1000000051_6','all','prp_s6'),(408,1,'[:emo_hj]',1575363383105,'1000000051_6','all','prp_s6'),(409,1,'1321',1575363478422,'1000000051_6','all','prp_s6'),(410,1,'[:emo_gc]',1575363482119,'1000000051_6','all','9ac40f4615a911ea8114000c290e82ac'),(411,1,'[:emo_jz]',1575363487190,'1000000051_6','all','9ac40f4615a911ea8114000c290e82ac'),(412,1,'[:emo_azgc]',1575363490351,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(413,1,'[:emo_ax]',1575363495451,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(414,1,'[:emo_gc]',1575363527967,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(415,1,'[:emo_jz]',1575363531755,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(416,1,'[:emo_bs]',1575363543276,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(417,1,'[:emo_ax]',1575363623621,'1000000051_6','all','prp_s6'),(418,1,'[:emo_bs]',1575363633218,'1000000056_6','all','prp_s6'),(419,1,'[:emo_jz]',1575363703258,'1000000056_6','all','prp_s6'),(420,1,'[:emo_ax]',1575363713678,'1000000056_6','all','prp_s6'),(421,1,'[:emo_jz]',1575363726205,'1000000051_6','all','prp_s6'),(422,1,'[:emo_zl]',1575363733990,'1000000056_6','all','9ac40f4615a911ea8114000c290e82ac'),(423,1,'[:emo_azgc]',1575363741115,'1000000056_6','all','prp_s6'),(424,1,'[:emo_azgc]',1575365120649,'1000000051_6','all','9ac40f4615a911ea8114000c290e82ac'),(425,1,'[:emo_hj]',1575368169949,'1000000026_6','all','09e35e86126c11eaa3c9000c290e82ac'),(426,1,'mlgb',1575375252840,'1000000055_6','all','9743610a15a911ea98d9000c290e82ac'),(427,1,'啥啥啥啥啥啥所所',1575375298185,'1000000055_6','all','prp_s6'),(428,1,'[:emo_hj]',1575376615670,'1000000056_6','all','ce9a2f9415b811ea804e000c290e82ac'),(429,1,'[:emo_bs]',1575376619858,'1000000056_6','all','ce9a2f9415b811ea804e000c290e82ac'),(430,1,'[:emo_ax]',1575376623461,'1000000056_6','all','ce9a2f9415b811ea804e000c290e82ac'),(431,1,'[:emo_hj]',1575377017497,'1000000004_1','all','faba48f816f711eabf3c000c29a82b41'),(432,1,'[:emo_ax]',1575377021212,'1000000004_1','all','faba48f816f711eabf3c000c29a82b41'),(433,1,'[:emo_jz]',1575377033959,'1000000004_1','all','faba48f816f711eabf3c000c29a82b41'),(434,1,'[:emo_azgc]',1575377171225,'1000000004_1','all','61599f8c16f811eaa9f7000c29a82b41'),(435,1,'[:emo_jz]',1575377180293,'1000000004_1','all','61599f8c16f811eaa9f7000c29a82b41'),(436,1,'[:emo_gc]',1575377191757,'1000000004_1','all','prp_s1'),(437,1,'[:emo_azgc]',1575377813178,'1000000000_1','all','61599f8c16f811eaa9f7000c29a82b41'),(438,1,'[:emo_hs]',1575377828717,'1000000000_1','all','61599f8c16f811eaa9f7000c29a82b41'),(439,1,'[:emo_azgc]',1575377868583,'1000000000_1','all','prp_s1'),(440,1,'[:emo_hs]',1575424370292,'1000000001_1','all','prp_s1'),(441,1,'123',1575426183047,'1000000002_1','all','prp_s1'),(442,1,'sheisheis',1575445811733,'1000000000_1','all','prp_s1'),(443,1,'[:emo_bs]',1575449638306,'1000000001_1','all','prp_s1');
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
  PRIMARY KEY (`loginName`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('1000000000_1',1575271860768,1575271860768,'1000000000','花之桃',10,1,2,'40001_0_0','0_0','61599f8c16f811eaa9f7000c29a82b41','1','607','1'),('1000000000_6',1575000151361,1575000151361,'1000000000','喻摇伽',7,6,0,'40002_0_0','0_0','24b542d0126a11eaa0fa000c290e82ac','1','607','1'),('1000000001_1',1575271569664,1575271569664,'1000000001','丰听露',4,1,2,'40001_0_0','0_0','','1','607','1'),('1000000001_6',1575000108257,1575000108257,'1000000001','康轩宇',8,6,1,'40001_0_0','0_0','822f2d90128d11eab5a1000c290e82ac','1','607','1'),('1000000002_1',1575271869339,1575271869339,'1000000002','牧凤妖',7,1,0,'40003_0_0','0_0','61599f8c16f811eaa9f7000c29a82b41','1','607','1'),('1000000002_6',1575000264823,1575000264823,'1000000002','习鹏笑',3,6,0,'40003_0_0','0_0','','1','607','1'),('1000000003_1',1575346679766,1575346679766,'1000000003','宁语梦',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000003_6',1575000303087,1575000303087,'1000000003','又双叒叕',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000004_1',1575272171512,1575272171512,'1000000004','骆阑悦',2,1,3,'40001_0_0','0_0','61599f8c16f811eaa9f7000c29a82b41','1','607','1'),('1000000004_6',1575000649020,1575000649020,'1000000004','耿冰夏',3,6,0,'40001_50002_1575012517','0_0','','1','607','1'),('1000000005_1',1575272790863,1575272790863,'1000000005','古浩阑',23,1,0,'40001_0_0','0_0','62f11e82175d11eaaa52000c29a82b41','1','607','1'),('1000000005_6',1575001145416,1575001145416,'1000000005','凌静蕾',24,6,5,'40001_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000006_1',1575272657916,1575272657916,'1000000006','桑春雨',1,1,0,'40001_50002_1575748939','0_0','','1','607','1'),('1000000006_6',1575001222074,1575001222074,'1000000006','乐一曲',3,6,0,'40001_0_0','0_0','','1','607','1'),('1000000007_1',1575273866864,1575273866864,'1000000007','甄冰安',1,1,0,'40003_0_0','0_0','','1','607','1'),('1000000007_6',1575006357904,1575006357904,'1000000007','常从菡',3,6,0,'40001_0_0','0_0','','1','607','1'),('1000000008_1',1575274190551,1575274190551,'1000000008','浦士晋',2,1,0,'40001_0_1575748988','0_0','','1','607','1'),('1000000008_6',1575009573228,1575009573228,'1000000008','水世立',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000009_1',1575286885452,1575286885452,'1000000009','仇初翠',6,1,0,'40001_0_0','0_0','','1','607','1'),('1000000009_6',1575011427289,1575011427289,'1000000009','步语蓉',5,6,0,'40001_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000010_1',1575014590223,1575014590223,'1000000010','倪又莲',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000010_6',1575010561925,1575010561925,'1000000010','从南珍',4,6,3,'40001_50002_1575346141','0_0','','1','607','1'),('1000000011_1',1575368524055,1575368524055,'1000000011','寇绿海',3,1,0,'40003_0_0','0_0','','1','607','1'),('1000000012_1',1575291498464,1575291498464,'1000000012','霍聪健',3,1,0,'40001_0_0','0_0','','1','607','1'),('1000000012_6',1575015788827,1575015788827,'1000000012','慕水云',3,6,6,'40003_0_0','0_0','','1','607','1'),('1000000013_1',1575337861009,1575337861009,'1000000013','凌思山',8,1,0,'40003_0_0','0_0','bc18b1d414db11eab470000c29a82b41','1','607','1'),('1000000013_6',1575017687588,1575017687588,'1000000013','翟问柳',6,6,6,'40003_0_0','0_0','','1','607','1'),('1000000014_1',1575338501399,1575338501399,'1000000014','席昊焱',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000014_6',1575252674338,1575252674338,'1000000014','郑不可',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000015_6',1575254584820,1575254584820,'1000000015','祁槑槑',6,6,0,'40001_0_0','0_0','70cc35ee14b211ea8822000c290e82ac','1','607','1'),('1000000016_6',1575260865499,1575260865499,'1000000016','冀铁树',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000018_6',1575257219311,1575257219311,'1000000018','阎君浩',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000019_6',1575259630477,1575259630477,'1000000019','夏侯明杰',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000020_6',1575258411839,1575258411839,'1000000020','储博涛',4,6,0,'40001_0_0','0_0','','1','607','1'),('1000000021_6',1575258426085,1575258426085,'1000000021','印香芦',1,6,6,'40001_0_0','0_0','','1','607','1'),('1000000022_6',1575258618261,1575258618261,'1000000022','邬含烟',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000023_6',1575260979951,1575260979951,'1000000023','苏修雅',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000024_6',1575259957099,1575259957099,'1000000024','童雁桃',4,6,6,'40001_0_0','0_0','','1','607','1'),('1000000025_1',1574999878233,1574999878233,'1000000025','居文龙',12,1,8,'40001_0_0','0_0','c255ac2e127811eab1ec000c29a82b41','1','607','1'),('1000000026_6',1575346529040,1575346529040,'1000000026','沃满天',7,6,0,'40001_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000027_6',1575276080481,1575276080481,'1000000027','余慕山',5,6,0,'40001_0_0','0_0','230ac9f8150011eaa28c000c290e82ac','1','607','1'),('1000000028_6',1575276196860,1575276196860,'1000000028','容尔阳',7,6,4,'40002_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000029_6',1575276033432,1575276033432,'1000000029','蓝寒梦',6,6,0,'40001_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000030_6',1575277200214,1575277200214,'1000000030','花蓓妍',2,6,0,'40003_0_0','0_0','','1','607','1'),('1000000031_6',1575278579206,1575278579206,'1000000031','巩海亦',8,6,2,'40003_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000032_6',1575281403290,1575281403290,'1000000032','闵尔冬',4,6,0,'40001_0_0','0_0','','1','607','1'),('1000000034_6',1575292431092,1575292431092,'1000000034','毋巧凡',1,6,0,'40003_0_0','0_0','','1','607','1'),('1000000035_6',1575339924440,1575339924440,'1000000035','蒙道天',3,6,0,'40001_0_0','0_0','','1','607','1'),('1000000036_6',1575338750374,1575338750374,'1000000036','华不斜',9,6,4,'40002_0_0','0_0','09e35e86126c11eaa3c9000c290e82ac','1','607','1'),('1000000037_6',1575339671693,1575339671693,'1000000037','周凌文',1,6,0,'40004_0_0','0_0','','1','607','1'),('1000000038_6',1575339991953,1575339991953,'1000000038','仇平彤',5,6,0,'40001_0_0','0_0','','1','607','1'),('1000000039_6',1575340257014,1575340257014,'1000000039','褚从雪',7,6,5,'40001_0_1575346232','0_0','230ac9f8150011eaa28c000c290e82ac','1','607','1'),('1000000040_6',1575342274322,1575342274322,'1000000040','扶尔琴',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000041_1',1575006707420,1575006707420,'1000000041','星期四',4,1,0,'40001_0_0','0_0','','1','607','1'),('1000000042_6',1575342987491,1575342987491,'1000000042','吉夜蓉',5,6,0,'40001_0_0','0_0','','1','607','1'),('1000000043_1',1575006714890,1575006714890,'1000000043','熊晓刚',3,1,0,'40006_0_0','0_0','','1','607','1'),('1000000043_6',1575346002884,1575346002884,'1000000043','平依秋',2,6,0,'40001_0_0','0_0','9743610a15a911ea98d9000c290e82ac','1','607','1'),('1000000045_6',1575346238109,1575346238109,'1000000045','焦秋歌',21,6,0,'40001_0_0','0_0','','1','607','1'),('1000000046_6',1575346865353,1575346865353,'1000000046','蒲寻南',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000047_1',1574999878201,1574999878201,'1000000047','竺夜白',7,1,0,'40001_0_0','0_0','ecd685ca10bd11ea970c000c29a82b41','1','607','1'),('1000000047_6',1575347433023,1575347433023,'1000000047','诸葛青烟',23,6,0,'40001_0_0','0_0','','1','607','1'),('1000000048_6',1575347484465,1575347484465,'1000000048','姜思远',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000049_6',1575348324445,1575348324445,'1000000049','谈冬灵',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000050_6',1575348625138,1575348625138,'1000000050','卓依霜',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000051_6',1575348807343,1575348807343,'1000000051','孙曼文',20,6,0,'40001_0_0','0_0','9ac40f4615a911ea8114000c290e82ac','1','607','1'),('1000000052_1',1574999878176,1574999878176,'1000000052','卓静丹',7,1,0,'40003_0_0','0_0','ecd685ca10bd11ea970c000c29a82b41','1','607','1'),('1000000052_6',1575357003454,1575357003454,'1000000052','应惜寒',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000053_1',1575267695941,1575267695941,'1000000053','蔚志锋',10,1,0,'40001_0_0','0_0','','1','607','1'),('1000000053_6',1575357162966,1575357162966,'1000000053','乐宫苴',2,6,0,'40001_0_0','0_0','','1','607','1'),('1000000054_1',1575016814766,1575016814766,'1000000054','严仁杰',5,1,0,'40003_0_0','0_0','','1','607','1'),('1000000054_6',1575362184712,1575362184712,'1000000054','那四娘',1,6,0,'40001_0_0','0_0','','1','607','1'),('1000000055_6',1575362226347,1575362226347,'1000000055','荣浩然',23,6,0,'40001_0_0','0_0','9743610a15a911ea98d9000c290e82ac','1','607','1'),('1000000056_6',1575362802385,1575362802385,'1000000056','宰天荷',18,6,0,'40001_0_0','0_0','ce9a2f9415b811ea804e000c290e82ac','1','607','1'),('1000000057_6',1575364670973,1575364670973,'1000000057','符剑封',5,6,0,'40003_0_0','0_0','','1','607','1'),('1000000058_1',1574999879003,1574999879003,'1000000058','白傻',6,1,0,'40001_0_0','0_0','7891f68a14b511ea846e000c29a82b41','1','607','1'),('1000000058_6',1575447323542,1575447323542,'1000000058','曹嫣娆',3,6,0,'40001_0_0','0_0','','1','607','1'),('1000000060_1',1575012148688,1575012148688,'1000000060','姜秋实',1,1,0,'40001_0_0','0_0','','1','607','1'),('1000000061_1',1575012420422,1575012420422,'1000000061','牧恶天',1,1,0,'40001_0_0','0_0','','1','607','1'),('1000000062_1',1575015406457,1575015406457,'1000000062','何初翠',2,1,6,'40001_0_0','0_0','03925c66128111ea94ed000c29a82b41','1','607','1'),('1000000063_1',1575016099685,1575016099685,'1000000063','陈书航',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000065_1',1575016644127,1575016644127,'1000000065','薛夏岚',10,1,5,'40001_0_0','0_0','','1','607','1'),('1000000066_1',1575016604624,1575016604624,'1000000066','邓三颜',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000067_1',1575017382392,1575017382392,'1000000067','池惜筠',2,1,6,'40001_0_0','0_0','','1','607','1'),('1000000068_1',1575252165692,1575252165692,'1000000068','国君浩',6,1,0,'40003_0_0','0_0','','1','607','1'),('1000000069_1',1575252923726,1575252923726,'1000000069','查冬莲',5,1,0,'40001_0_0','0_0','','1','607','1'),('1000000070_1',1575254434256,1575254434256,'1000000070','弘冬莲',1,1,0,'40001_0_0','0_0','','1','607','1'),('1000000071_1',1575254870313,1575254870313,'1000000071','嵇小钰',4,1,0,'40001_0_0','0_0','','1','607','1'),('1000000072_1',1575254923300,1575254923300,'1000000072','习依波',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000074_1',1575257922654,1575257922654,'1000000074','袁黎昕',23,1,6,'40001_0_0','0_0','','1','607','1'),('1000000075_1',1575258890522,1575258890522,'1000000075','勾含灵',1,1,6,'40001_0_0','0_0','','1','607','1'),('1000000076_1',1575260169362,1575260169362,'1000000076','冯幼丝',4,1,0,'40003_0_0','0_0','','1','607','1'),('1000000077_1',1575265792246,1575265792246,'1000000077','白忆丹',2,1,0,'40001_0_0','0_0','','1','607','1'),('1000000078_1',1575266606809,1575266606809,'1000000078','房冰海',2,1,0,'40003_0_0','0_0','','1','607','1'),('1000000080_1',1575268052127,1575268052127,'1000000080','昌君芊',10,1,1,'40001_0_0','0_0','','1','607','1'),('1000000081_1',1575269235121,1575269235121,'1000000081','曹春雷',1,1,6,'40001_0_0','0_0','','1','607','1'),('npc',0,0,'-1','npc',-1,-1,-1,'-1','-1','-1','-1','-1','-1');
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

-- Dump completed on 2019-12-08 20:27:07
