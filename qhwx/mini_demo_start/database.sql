-- MySQL dump 10.14  Distrib 5.5.60-MariaDB, for Linux (x86_64)
--
-- Host: 10.66.168.81    Database: jpzmgtest
-- ------------------------------------------------------
-- Server version	5.6.28-cdb2016-log

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
-- Table structure for table `account_users_0`
--

DROP TABLE IF EXISTS `account_users_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_users_0` (
  `openid` varchar(32) NOT NULL,
  `user_info` mediumblob NOT NULL,
  PRIMARY KEY (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `accounts_0`
--

DROP TABLE IF EXISTS `accounts_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_0` (
  `account_number` varchar(32) NOT NULL COMMENT '账号名',
  `account_pwd` varchar(32) NOT NULL COMMENT '密码',
  `add_time` int(11) NOT NULL,
  `login_time` int(11) NOT NULL,
  `openid` varchar(32) NOT NULL,
  PRIMARY KEY (`account_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `accounts_mapping_0`
--

DROP TABLE IF EXISTS `accounts_mapping_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_mapping_0` (
  `openid` varchar(32) NOT NULL,
  `account_number` varchar(32) NOT NULL COMMENT '账号名',
  `openkey` varchar(72) NOT NULL,
  PRIMARY KEY (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `achv_stage_box_0`
--

DROP TABLE IF EXISTS `achv_stage_box_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `achv_stage_box_0` (
  `uid` varchar(20) NOT NULL,
  `asb_id` varchar(64) DEFAULT NULL,
  `integral` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `act_exchange_0`
--

DROP TABLE IF EXISTS `act_exchange_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `act_exchange_0` (
  `aid` varchar(32) NOT NULL,
  `prize` mediumblob,
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `act_giftbag_0`
--

DROP TABLE IF EXISTS `act_giftbag_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `act_giftbag_0` (
  `aid` varchar(32) NOT NULL,
  `prize` mediumblob,
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `act_rank_0`
--

DROP TABLE IF EXISTS `act_rank_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `act_rank_0` (
  `aid` varchar(32) NOT NULL,
  `is_prize` int(11) NOT NULL,
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `act_recharge_0`
--

DROP TABLE IF EXISTS `act_recharge_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `act_recharge_0` (
  `aid` varchar(32) NOT NULL,
  `prize` mediumblob,
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `act_timelimit_0`
--

DROP TABLE IF EXISTS `act_timelimit_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `act_timelimit_0` (
  `aid` varchar(32) NOT NULL,
  `prize` mediumblob,
  `add_time` int(12) NOT NULL,
  `parameter` int(14) NOT NULL,
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_exchange_0`
--

DROP TABLE IF EXISTS `activity_exchange_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_exchange_0` (
  `uid` varchar(32) NOT NULL,
  `act_ids` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_giftbag_0`
--

DROP TABLE IF EXISTS `activity_giftbag_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_giftbag_0` (
  `uid` varchar(32) NOT NULL,
  `act_ids` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_recharge_0`
--

DROP TABLE IF EXISTS `activity_recharge_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_recharge_0` (
  `uid` varchar(32) NOT NULL,
  `act_ids` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_timelimit_0`
--

DROP TABLE IF EXISTS `activity_timelimit_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_timelimit_0` (
  `uid` varchar(32) NOT NULL,
  `act_ids` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_turntable_0`
--

DROP TABLE IF EXISTS `activity_turntable_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_turntable_0` (
  `uid` varchar(20) NOT NULL,
  `new_turninfo` mediumblob,
  `old_turninfo` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admin_moderators`
--

DROP TABLE IF EXISTS `admin_moderators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_moderators` (
  `mid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL,
  `last_login` int(11) NOT NULL,
  `last_ip` varchar(30) DEFAULT NULL,
  `is_staff` int(11) NOT NULL,
  `permissions` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assistant_officer_0`
--

DROP TABLE IF EXISTS `assistant_officer_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assistant_officer_0` (
  `uid` varchar(20) NOT NULL,
  `pos_list` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `banquet_hall_0`
--

DROP TABLE IF EXISTS `banquet_hall_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `banquet_hall_0` (
  `uid` varchar(32) NOT NULL,
  `points` int(10) NOT NULL,
  `attend_times` int(10) NOT NULL,
  `attend_info` mediumblob,
  `last_attend_time` double NOT NULL,
  `is_first` tinyint(4) NOT NULL,
  `last_refresh_time` double NOT NULL,
  `had_attend_id` mediumblob,
  `banquet` mediumblob,
  `is_first_hold` tinyint(4) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `beacon_tower_0`
--

DROP TABLE IF EXISTS `beacon_tower_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `beacon_tower_0` (
  `uid` varchar(32) NOT NULL,
  `points` int(10) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card_0`
--

DROP TABLE IF EXISTS `card_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_0` (
  `cid` varchar(40) NOT NULL,
  `lv` int(11) NOT NULL,
  `exp` bigint(20) NOT NULL,
  `step_lv` int(11) NOT NULL,
  `break_lv` int(11) NOT NULL,
  `kp_lv` int(11) NOT NULL,
  `kp_exp` bigint(20) NOT NULL,
  `kp_number` int(11) NOT NULL,
  `gov_obj` mediumblob NOT NULL,
  `wit_obj` mediumblob NOT NULL,
  `pol_obj` mediumblob NOT NULL,
  `cha_obj` mediumblob NOT NULL,
  `card_total` bigint(15) NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card_biography_0`
--

DROP TABLE IF EXISTS `card_biography_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_biography_0` (
  `card_id` varchar(40) NOT NULL,
  `card_story` mediumblob,
  PRIMARY KEY (`card_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card_light_0`
--

DROP TABLE IF EXISTS `card_light_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_light_0` (
  `no` varchar(50) NOT NULL,
  `effects` mediumblob,
  `last_add_cno` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card_package_0`
--

DROP TABLE IF EXISTS `card_package_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_package_0` (
  `uid` varchar(20) NOT NULL,
  `cards` mediumblob,
  `total_gov` bigint(15) NOT NULL,
  `total_pol` bigint(15) NOT NULL,
  `total_cha` bigint(15) NOT NULL,
  `total_wit` bigint(15) NOT NULL,
  `total` bigint(20) NOT NULL,
  `loyalty_value` mediumblob NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card_story_0`
--

DROP TABLE IF EXISTS `card_story_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_story_0` (
  `story_id` varchar(32) NOT NULL,
  `is_finish` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`story_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cdkey_0`
--

DROP TABLE IF EXISTS `cdkey_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdkey_0` (
  `uid` varchar(20) NOT NULL,
  `use_cd_key` mediumblob,
  `card_ids` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cg_plot_0`
--

DROP TABLE IF EXISTS `cg_plot_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cg_plot_0` (
  `plot_no` varchar(32) NOT NULL,
  `plots` mediumblob,
  PRIMARY KEY (`plot_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `channel_lock`
--

DROP TABLE IF EXISTS `channel_lock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `channel_lock` (
  `cl_id` varchar(50) NOT NULL,
  `status` tinyint(4) DEFAULT NULL,
  `context` tinytext,
  PRIMARY KEY (`cl_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `child_abstract_0`
--

DROP TABLE IF EXISTS `child_abstract_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `child_abstract_0` (
  `cid` varchar(40) NOT NULL,
  `name` varchar(10) NOT NULL,
  `username` varchar(10) NOT NULL,
  `sex` int(11) NOT NULL,
  `title` int(11) NOT NULL,
  `own_character` int(11) NOT NULL,
  `like_character` int(11) NOT NULL,
  `head_no` mediumblob NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `children_garden_0`
--

DROP TABLE IF EXISTS `children_garden_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `children_garden_0` (
  `uid` varchar(20) NOT NULL,
  `seat_num` int(11) NOT NULL,
  `seq_id` int(11) NOT NULL,
  `is_first` tinyint(4) NOT NULL,
  `children` mediumblob NOT NULL,
  `child_attribute` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `climbing_tower_0`
--

DROP TABLE IF EXISTS `climbing_tower_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `climbing_tower_0` (
  `uid` varchar(20) NOT NULL,
  `tower_layer` int(10) DEFAULT NULL,
  `mop_up_time` int(15) DEFAULT NULL,
  `mop_up_count` int(10) DEFAULT NULL,
  `tower_reward` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `colleague_0`
--

DROP TABLE IF EXISTS `colleague_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `colleague_0` (
  `colleague_id` varchar(32) NOT NULL,
  `intimacy` varchar(32) DEFAULT NULL,
  `intersection_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`colleague_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `colleague_package_0`
--

DROP TABLE IF EXISTS `colleague_package_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `colleague_package_0` (
  `uid` varchar(32) NOT NULL,
  `invited_colleagues` mediumblob,
  `visit_reward` mediumblob,
  `visit_uid` mediumblob,
  `colleague_time` varchar(32) DEFAULT NULL,
  `colleagues` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `combat_gift_0`
--

DROP TABLE IF EXISTS `combat_gift_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `combat_gift_0` (
  `uid` varchar(20) NOT NULL,
  `fund_buy` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `confidant_0`
--

DROP TABLE IF EXISTS `confidant_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `confidant_0` (
  `cid` varchar(32) NOT NULL,
  `skill_exp` int(11) NOT NULL,
  `intimacy_lv` int(11) NOT NULL,
  `intimacy_exp` int(11) NOT NULL,
  `skills` mediumblob,
  `last_time` double NOT NULL,
  `make_times` int(11) NOT NULL,
  `quality` int(11) NOT NULL,
  `schedule` int(11) NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `confidant_biography_0`
--

DROP TABLE IF EXISTS `confidant_biography_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `confidant_biography_0` (
  `confidant_id` varchar(40) NOT NULL,
  `confidant_story` mediumblob,
  PRIMARY KEY (`confidant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `confidant_position_0`
--

DROP TABLE IF EXISTS `confidant_position_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `confidant_position_0` (
  `uid` varchar(20) NOT NULL,
  `main_room` mediumblob,
  `up_room` mediumblob,
  `middle_room` mediumblob,
  `down_room` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `confidant_story_0`
--

DROP TABLE IF EXISTS `confidant_story_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `confidant_story_0` (
  `story_id` varchar(32) NOT NULL,
  `is_finish` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`story_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `configs`
--

DROP TABLE IF EXISTS `configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `configs` (
  `config_name` varchar(50) NOT NULL,
  `config_value` mediumblob,
  PRIMARY KEY (`config_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `daily_tasks_0`
--

DROP TABLE IF EXISTS `daily_tasks_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daily_tasks_0` (
  `uid` varchar(32) NOT NULL,
  `daily_task` mediumblob,
  `schedule` int(8) NOT NULL,
  `daily_task_time` varchar(32) DEFAULT NULL,
  `complete_task_ids` mediumblob,
  `daily_task_box` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `debate_battle_0`
--

DROP TABLE IF EXISTS `debate_battle_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `debate_battle_0` (
  `debate_key` varchar(20) NOT NULL,
  `enemy_id` varchar(32) DEFAULT NULL,
  `own_card_obj` mediumblob,
  `enemy_card_obj` mediumblob,
  `enemy_cards` mediumblob,
  `kill_card_ids` mediumblob,
  `attribute_bias` varchar(32) DEFAULT NULL,
  `random_enemy_card` mediumblob,
  `random_skill` mediumblob,
  `debate_skill` mediumblob,
  `win_count` varchar(32) DEFAULT NULL,
  `position_index` int(5) NOT NULL,
  PRIMARY KEY (`debate_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `direct_purchase_0`
--

DROP TABLE IF EXISTS `direct_purchase_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `direct_purchase_0` (
  `uid` varchar(20) NOT NULL,
  `new_data` mediumblob,
  `old_data` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `direct_purchase_fund_0`
--

DROP TABLE IF EXISTS `direct_purchase_fund_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `direct_purchase_fund_0` (
  `uid` varchar(20) NOT NULL,
  `new_dpfinfo` mediumblob,
  `old_dpfinfo` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_child_0`
--

DROP TABLE IF EXISTS `exam_child_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exam_child_0` (
  `cid` varchar(40) NOT NULL,
  `status` int(11) NOT NULL,
  `start_time` int(11) NOT NULL,
  `designate_uid` varchar(40) NOT NULL,
  `designate_name` varchar(10) NOT NULL,
  `child_attribute` mediumblob,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fortune_0`
--

DROP TABLE IF EXISTS `fortune_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fortune_0` (
  `uid` varchar(32) NOT NULL,
  `fortune_info` mediumblob,
  `fortune_flush_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game_ext_0`
--

DROP TABLE IF EXISTS `game_ext_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_ext_0` (
  `uid` varchar(20) NOT NULL,
  `ext_info` mediumblob,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game_info_0`
--

DROP TABLE IF EXISTS `game_info_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_info_0` (
  `uid` varchar(20) NOT NULL,
  `gold` bigint(20) NOT NULL,
  `pct` int(11) NOT NULL,
  `windmill` bigint(20) NOT NULL,
  `flower` bigint(20) NOT NULL,
  `soldiers` bigint(20) NOT NULL,
  `wp` bigint(20) NOT NULL,
  `week_wp` int(11) NOT NULL,
  `week_update_time` bigint(20) NOT NULL,
  `strategy_val` int(8) DEFAULT NULL,
  `game_info_time` varchar(32) DEFAULT NULL,
  `league_contribution` bigint(20) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game_wgzz_icons_0`
--

DROP TABLE IF EXISTS `game_wgzz_icons_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_wgzz_icons_0` (
  `uid` varchar(32) NOT NULL,
  `icons` varchar(64) DEFAULT NULL,
  `user_name` varchar(128) DEFAULT NULL,
  `expire_time` int(15) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gov_hall_0`
--

DROP TABLE IF EXISTS `gov_hall_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gov_hall_0` (
  `uid` varchar(20) NOT NULL,
  `integral` int(10) NOT NULL,
  `box_level` int(10) NOT NULL,
  `affair_last_time` int(11) NOT NULL,
  `card_last_time` int(11) NOT NULL,
  `refresh_times` int(10) NOT NULL,
  `affair_columns` mediumblob,
  `card_ids` mediumblob,
  `affairs` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gov_hall_new_0`
--

DROP TABLE IF EXISTS `gov_hall_new_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gov_hall_new_0` (
  `uid` varchar(32) NOT NULL,
  `affairs` mediumblob,
  `today_cards` mediumblob,
  `last_refresh_time` int(15) NOT NULL,
  `refresh_common_time` int(15) NOT NULL,
  `refresh_vip_time` int(15) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guide_0`
--

DROP TABLE IF EXISTS `guide_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guide_0` (
  `uid` varchar(32) NOT NULL,
  `status` int(8) NOT NULL,
  `guide_id` int(8) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `harvests_0`
--

DROP TABLE IF EXISTS `harvests_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `harvests_0` (
  `uid` varchar(20) NOT NULL,
  `harvest_time` int(11) NOT NULL,
  `tmp_have_time` int(11) NOT NULL,
  `gains` mediumblob NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `item_package_0`
--

DROP TABLE IF EXISTS `item_package_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item_package_0` (
  `uid` varchar(20) NOT NULL,
  `items` mediumblob NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_0`
--

DROP TABLE IF EXISTS `league_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_0` (
  `league_id` varchar(32) NOT NULL,
  `league_name` varchar(48) DEFAULT NULL,
  `league_flags_id` varchar(4) DEFAULT NULL,
  `league_time` varchar(8) DEFAULT NULL,
  `login_replace_state` varchar(15) DEFAULT NULL,
  `league_tech_effect` mediumblob,
  PRIMARY KEY (`league_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_battle_global_info_0`
--

DROP TABLE IF EXISTS `league_battle_global_info_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_battle_global_info_0` (
  `league_id` varchar(64) NOT NULL,
  `enter_war_state` int(6) NOT NULL,
  PRIMARY KEY (`league_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_battle_reward_0`
--

DROP TABLE IF EXISTS `league_battle_reward_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_battle_reward_0` (
  `uid` varchar(16) NOT NULL,
  `session` int(8) NOT NULL,
  `periods` int(8) NOT NULL,
  `reward_info` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_inner_0`
--

DROP TABLE IF EXISTS `league_inner_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_inner_0` (
  `league_id` varchar(32) NOT NULL,
  `text` text,
  PRIMARY KEY (`league_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_leader_0`
--

DROP TABLE IF EXISTS `league_leader_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_leader_0` (
  `league_id` varchar(32) NOT NULL,
  `management_id` varchar(32) DEFAULT NULL,
  `vice_management` mediumblob,
  PRIMARY KEY (`league_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_name_mapping_0`
--

DROP TABLE IF EXISTS `league_name_mapping_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_name_mapping_0` (
  `league_name_md5` varchar(32) NOT NULL,
  `league_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`league_name_md5`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `league_outer_0`
--

DROP TABLE IF EXISTS `league_outer_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `league_outer_0` (
  `league_id` varchar(32) NOT NULL,
  `text` text,
  PRIMARY KEY (`league_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mail_0`
--

DROP TABLE IF EXISTS `mail_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_0` (
  `mail_id` varchar(32) NOT NULL,
  `title` varchar(32) DEFAULT NULL,
  `mail_type` varchar(6) DEFAULT NULL,
  `text` text,
  `enclosure` text,
  `send_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`mail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mail_package_0`
--

DROP TABLE IF EXISTS `mail_package_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_package_0` (
  `uid` varchar(32) NOT NULL,
  `mail_type_count` mediumblob,
  `mail_flush_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `main_task_0`
--

DROP TABLE IF EXISTS `main_task_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_task_0` (
  `task_id` varchar(32) NOT NULL,
  `task_args` mediumblob,
  `task_state` int(4) NOT NULL,
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mansion_0`
--

DROP TABLE IF EXISTS `mansion_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mansion_0` (
  `mid` varchar(32) NOT NULL,
  `rank_user` varchar(32) DEFAULT NULL,
  `get_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mansion_hall_0`
--

DROP TABLE IF EXISTS `mansion_hall_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mansion_hall_0` (
  `uid` varchar(32) NOT NULL,
  `last_ask_time` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mansion_info_0`
--

DROP TABLE IF EXISTS `mansion_info_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mansion_info_0` (
  `serverId` int(15) NOT NULL,
  `last_phase` mediumblob,
  `today_ask_list` mediumblob,
  `last_ask_time` int(15) DEFAULT NULL,
  PRIMARY KEY (`serverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `market_0`
--

DROP TABLE IF EXISTS `market_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `market_0` (
  `uid` varchar(20) NOT NULL,
  `power` int(11) NOT NULL,
  `last_time` int(11) NOT NULL,
  `plv` int(11) NOT NULL,
  `pexp` int(11) NOT NULL,
  `times` int(11) NOT NULL,
  `times_event` int(11) NOT NULL,
  `award_wp` int(11) NOT NULL,
  `award_time` int(11) NOT NULL,
  `curr_pos` int(11) NOT NULL,
  `event_no` int(11) NOT NULL,
  `buildings` mediumblob NOT NULL,
  `cards` mediumblob NOT NULL,
  `confidants` mediumblob NOT NULL,
  `strangers` mediumblob NOT NULL,
  `way` int(11) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marriage_room_0`
--

DROP TABLE IF EXISTS `marriage_room_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marriage_room_0` (
  `uid` varchar(20) NOT NULL,
  `un_marry` mediumblob,
  `wait_marry` mediumblob,
  `married` mediumblob,
  `married_attr` mediumblob,
  `statistics` mediumblob,
  `child_attribute` mediumblob,
  `issue_times` int(11) DEFAULT NULL,
  `issue_time` int(11) DEFAULT NULL,
  `is_first` tinyint(4) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marriaged_child_0`
--

DROP TABLE IF EXISTS `marriaged_child_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marriaged_child_0` (
  `cid` varchar(40) NOT NULL,
  `inlaws_cid` varchar(40) NOT NULL,
  `child_attribute` mediumblob,
  `inlaws_attribute` mediumblob,
  `marriaged_addition` mediumblob,
  `marriaged_time` int(11) NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `officer_right_0`
--

DROP TABLE IF EXISTS `officer_right_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `officer_right_0` (
  `uid` varchar(32) NOT NULL,
  `subordinates` mediumblob,
  `intercourse` mediumblob,
  `decree_reward` mediumblob,
  `soldiers_deal` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `official_struggle_game_0`
--

DROP TABLE IF EXISTS `official_struggle_game_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `official_struggle_game_0` (
  `uid` varchar(32) NOT NULL,
  `game_model` mediumblob,
  `official_struggle_time` int(10) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `online_duration`
--

DROP TABLE IF EXISTS `online_duration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `online_duration` (
  `duration_key` varchar(64) NOT NULL,
  `duration_num` int(11) NOT NULL,
  PRIMARY KEY (`duration_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `open_modules_0`
--

DROP TABLE IF EXISTS `open_modules_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `open_modules_0` (
  `uid` varchar(32) NOT NULL,
  `modules` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `operate_act_user_0`
--

DROP TABLE IF EXISTS `operate_act_user_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `operate_act_user_0` (
  `uid` varchar(20) NOT NULL,
  `theme_info` mediumblob,
  `league_ranking_reward_id` int(15) DEFAULT NULL,
  `user_ranking_reward_id` int(15) DEFAULT NULL,
  `activity_start_time` int(15) DEFAULT NULL,
  `integral_201` int(15) DEFAULT NULL,
  `integral_202` int(15) DEFAULT NULL,
  `integral_203` int(15) DEFAULT NULL,
  `integral_204` int(15) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `own_league_global_info_0`
--

DROP TABLE IF EXISTS `own_league_global_info_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `own_league_global_info_0` (
  `uid` varchar(32) NOT NULL,
  `league_id` varchar(64) DEFAULT NULL,
  `league_droit_tips_id` int(8) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `own_league_info_0`
--

DROP TABLE IF EXISTS `own_league_info_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `own_league_info_0` (
  `uid` varchar(32) NOT NULL,
  `build_count` int(12) DEFAULT NULL,
  `build_id` int(8) DEFAULT NULL,
  `build_league_id` varchar(32) DEFAULT NULL,
  `donate_wealth` int(8) DEFAULT NULL,
  `activity_box` mediumblob,
  `league_info_time` varchar(32) DEFAULT NULL,
  `day_task_box` mediumblob,
  `week_update_time` int(12) DEFAULT NULL,
  `day_task_reward` int(4) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `passive_marry_0`
--

DROP TABLE IF EXISTS `passive_marry_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `passive_marry_0` (
  `u_cno` varchar(40) NOT NULL,
  `in_laws_u_cno` varchar(40) NOT NULL,
  `married_time` int(11) NOT NULL,
  PRIMARY KEY (`u_cno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `personal_information_fashion_0`
--

DROP TABLE IF EXISTS `personal_information_fashion_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `personal_information_fashion_0` (
  `uid` varchar(32) NOT NULL,
  `title_id` int(10) DEFAULT NULL,
  `fashion_id` int(10) DEFAULT NULL,
  `background_id` int(10) DEFAULT NULL,
  `default_fashion_id` int(10) DEFAULT NULL,
  `title_package` mediumblob,
  `fashion_package` mediumblob,
  `background_package` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pray_palace_0`
--

DROP TABLE IF EXISTS `pray_palace_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pray_palace_0` (
  `uid` varchar(20) NOT NULL,
  `free_count` int(10) DEFAULT NULL,
  `pay_count` int(10) DEFAULT NULL,
  `pray_count` int(10) DEFAULT NULL,
  `max_pay_count` int(15) DEFAULT NULL,
  `pray_palace_flush_time` int(15) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prison_0`
--

DROP TABLE IF EXISTS `prison_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prison_0` (
  `uid` varchar(20) NOT NULL,
  `hearing` mediumblob NOT NULL,
  `prisons_time` int(15) NOT NULL,
  `prisoners` mediumblob NOT NULL,
  `event_no` int(11) NOT NULL,
  `prisons_index_increment` int(5) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `promote_hall_0`
--

DROP TABLE IF EXISTS `promote_hall_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `promote_hall_0` (
  `uid` varchar(32) NOT NULL,
  `jade` int(10) NOT NULL,
  `in_war` int(11) NOT NULL,
  `debate_cards` mediumblob,
  `enemy_id` varchar(32) DEFAULT NULL,
  `count_integral` int(7) DEFAULT NULL,
  `stage` int(10) DEFAULT NULL,
  `up_count` int(10) DEFAULT NULL,
  `in_war_count` int(6) DEFAULT NULL,
  `up_flush_time` int(14) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `random_plot_0`
--

DROP TABLE IF EXISTS `random_plot_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `random_plot_0` (
  `plot_no` varchar(32) NOT NULL,
  `reward_times` int(10) DEFAULT NULL,
  `plots` mediumblob,
  `last_reward_time` int(15) DEFAULT NULL,
  PRIMARY KEY (`plot_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ranking_operation_0`
--

DROP TABLE IF EXISTS `ranking_operation_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ranking_operation_0` (
  `uid` varchar(20) NOT NULL,
  `worship` mediumblob,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recharge_0`
--

DROP TABLE IF EXISTS `recharge_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recharge_0` (
  `uid` varchar(32) NOT NULL,
  `vip_first_double` mediumblob,
  `refresh_time` int(11) NOT NULL,
  `first_flag` tinyint(4) NOT NULL,
  `second_flag` tinyint(4) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recharge_order`
--

DROP TABLE IF EXISTS `recharge_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recharge_order` (
  `order_id` varchar(32) NOT NULL,
  `uid` varchar(20) NOT NULL,
  `shop_no` int(11) NOT NULL,
  `itemcount` int(11) NOT NULL,
  `add_time` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `openid` varchar(64) NOT NULL,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `red_packages_0`
--

DROP TABLE IF EXISTS `red_packages_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `red_packages_0` (
  `redId` varchar(32) NOT NULL,
  `sender` varchar(32) NOT NULL,
  `pctInfo` mediumblob,
  `userInfo` mediumblob,
  PRIMARY KEY (`redId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `school_field_0`
--

DROP TABLE IF EXISTS `school_field_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `school_field_0` (
  `uid` varchar(20) NOT NULL,
  `free_flush_count` varchar(32) DEFAULT NULL,
  `pay_flush_count` varchar(32) DEFAULT NULL,
  `debate_start_time` varchar(32) DEFAULT NULL,
  `envoy_ready_time` varchar(32) DEFAULT NULL,
  `record_time` varchar(32) DEFAULT NULL,
  `debate_battle_card` varchar(32) DEFAULT NULL,
  `enemy_id` varchar(32) DEFAULT NULL,
  `enemy_name` varchar(32) DEFAULT NULL,
  `debate_card` mediumblob,
  `revenge_card` mediumblob,
  `envoy_count` varchar(32) DEFAULT NULL,
  `envoy_state` varchar(32) DEFAULT NULL,
  `debate_state` varchar(32) DEFAULT NULL,
  `usr_envoy_count` varchar(32) DEFAULT NULL,
  `lost_integral` int(5) DEFAULT NULL,
  `battle_type` int(5) DEFAULT NULL,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scripture_library_0`
--

DROP TABLE IF EXISTS `scripture_library_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scripture_library_0` (
  `uid` varchar(20) NOT NULL,
  `last_time` double NOT NULL,
  `last_bonus_type` int(11) NOT NULL,
  `seats` mediumblob NOT NULL,
  `card_effects` mediumblob NOT NULL,
  `buy_times` int(11) NOT NULL,
  `seat_event` mediumblob NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sequence`
--

DROP TABLE IF EXISTS `sequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sequence` (
  `id` bigint(20) unsigned NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seven_days_0`
--

DROP TABLE IF EXISTS `seven_days_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seven_days_0` (
  `uid` varchar(32) NOT NULL,
  `data` varchar(100) NOT NULL,
  `collect_time` int(11) NOT NULL,
  `seven_times` int(11) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sign_in_0`
--

DROP TABLE IF EXISTS `sign_in_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sign_in_0` (
  `uid` varchar(20) NOT NULL,
  `sign_count` int(5) NOT NULL,
  `sign_time` int(16) NOT NULL,
  `use_group` int(5) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sites_dress_up_0`
--

DROP TABLE IF EXISTS `sites_dress_up_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sites_dress_up_0` (
  `uid` varchar(20) NOT NULL,
  `sites` mediumblob,
  `attrs` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `skill_effect_0`
--

DROP TABLE IF EXISTS `skill_effect_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `skill_effect_0` (
  `no` varchar(50) NOT NULL,
  `effects` mediumblob,
  PRIMARY KEY (`no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `squads_0`
--

DROP TABLE IF EXISTS `squads_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `squads_0` (
  `uid` varchar(20) NOT NULL,
  `lineup` int(11) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stage_0`
--

DROP TABLE IF EXISTS `stage_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stage_0` (
  `uid` varchar(20) NOT NULL,
  `chapter` int(11) NOT NULL,
  `sno_index` int(3) NOT NULL,
  `monster_index` int(3) NOT NULL,
  `receive_chapter_reward` int(11) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stage_plot_0`
--

DROP TABLE IF EXISTS `stage_plot_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stage_plot_0` (
  `plot_no` varchar(32) NOT NULL,
  `plots` mediumblob,
  PRIMARY KEY (`plot_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stores_0`
--

DROP TABLE IF EXISTS `stores_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stores_0` (
  `uid` varchar(20) NOT NULL,
  `stores` mediumblob,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subrecord`
--

DROP TABLE IF EXISTS `subrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subrecord` (
  `order_id` varchar(32) NOT NULL,
  `orderno` varchar(64) NOT NULL,
  `uid` varchar(20) NOT NULL,
  `shop_no` int(11) NOT NULL,
  `itemcount` int(11) NOT NULL,
  `add_time` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `state` int(11) NOT NULL,
  `openid` varchar(64) NOT NULL,
  `award_state` int(11) NOT NULL,
  `is_real` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suppress_bandits_0`
--

DROP TABLE IF EXISTS `suppress_bandits_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suppress_bandits_0` (
  `uid` varchar(32) NOT NULL,
  `start_time` int(15) DEFAULT NULL,
  `bandits_id` int(10) DEFAULT NULL,
  `bandits_hp` int(10) DEFAULT NULL,
  `kill_count` int(32) DEFAULT NULL,
  `add_integral` int(32) DEFAULT NULL,
  `reward_state` int(32) DEFAULT NULL,
  `used_card` mediumblob,
  `recovery_card` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tasks_0`
--

DROP TABLE IF EXISTS `tasks_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tasks_0` (
  `uid` varchar(32) NOT NULL,
  `counting_task` mediumblob,
  `main_task` int(12) DEFAULT NULL,
  `complete_task_ids` mediumblob,
  `task_update_sign` varchar(128) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uname_mapping_0`
--

DROP TABLE IF EXISTS `uname_mapping_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uname_mapping_0` (
  `uname_md` varchar(32) NOT NULL,
  `uid` varchar(32) NOT NULL,
  PRIMARY KEY (`uname_md`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_boss_0`
--

DROP TABLE IF EXISTS `user_boss_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_boss_0` (
  `uid` varchar(20) NOT NULL,
  `boss_id` varchar(64) DEFAULT NULL,
  `boss_lost_hp` varchar(32) DEFAULT NULL,
  `card_ids` mediumblob,
  `recommend_attribute` varchar(46) DEFAULT NULL,
  `wait_for_use_card` mediumblob,
  `boss_token` varchar(64) DEFAULT NULL,
  `first_combat` int(11) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_character_0`
--

DROP TABLE IF EXISTS `user_character_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_character_0` (
  `uid` varchar(20) NOT NULL,
  `enthusiasm` int(10) NOT NULL,
  `goodness` int(10) NOT NULL,
  `abdominal_black` int(10) NOT NULL,
  `apathy` int(10) NOT NULL,
  `evil` int(10) NOT NULL,
  `pure` int(10) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_device_0`
--

DROP TABLE IF EXISTS `user_device_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_device_0` (
  `uid` varchar(20) NOT NULL,
  `device_id` int(16) NOT NULL,
  `etime` int(10) NOT NULL,
  `idfa` varchar(64) NOT NULL,
  `imei` varchar(64) NOT NULL,
  `mac` varchar(64) NOT NULL,
  `sn` varchar(64) NOT NULL,
  `umid` varchar(64) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_lv_manage_0`
--

DROP TABLE IF EXISTS `user_lv_manage_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_lv_manage_0` (
  `uid` varchar(32) NOT NULL,
  `ulv` int(15) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_state_0`
--

DROP TABLE IF EXISTS `user_state_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_state_0` (
  `uid` varchar(20) NOT NULL,
  `state` int(15) NOT NULL,
  `banned_time` bigint(25) DEFAULT NULL,
  `banned_reason` varchar(255) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_0`
--

DROP TABLE IF EXISTS `users_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_0` (
  `uid` varchar(20) NOT NULL,
  `add_time` int(11) NOT NULL,
  `login_time` int(11) NOT NULL,
  `channel_id` int(12) NOT NULL,
  `age` int(12) NOT NULL,
  `is_check` int(12) NOT NULL,
  `is_tourists` int(12) NOT NULL,
  `openid` varchar(64) DEFAULT NULL,
  `username` varchar(32) DEFAULT NULL,
  `login_ip` varchar(32) DEFAULT NULL,
  `icons` int(11) DEFAULT NULL,
  `session_key` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_mapping_0`
--

DROP TABLE IF EXISTS `users_mapping_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_mapping_0` (
  `openid` varchar(64) NOT NULL,
  `openkey` varchar(96) NOT NULL,
  `uid` varchar(20) NOT NULL,
  PRIMARY KEY (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vip_0`
--

DROP TABLE IF EXISTS `vip_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vip_0` (
  `uid` varchar(32) NOT NULL,
  `lv` int(11) DEFAULT NULL,
  `exp` int(15) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vip_card_0`
--

DROP TABLE IF EXISTS `vip_card_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vip_card_0` (
  `uid` varchar(32) NOT NULL,
  `vcinfo` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vipstore_0`
--

DROP TABLE IF EXISTS `vipstore_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vipstore_0` (
  `uid` varchar(20) NOT NULL,
  `data` varchar(128) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wing_room_0`
--

DROP TABLE IF EXISTS `wing_room_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wing_room_0` (
  `uid` varchar(20) NOT NULL,
  `confidants` mediumblob,
  `halo` mediumblob,
  `factions` mediumblob,
  `intimacy_all` int(11) NOT NULL,
  `confidants_nothing` mediumblob,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `world_boss_0`
--

DROP TABLE IF EXISTS `world_boss_0`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `world_boss_0` (
  `uid` varchar(32) NOT NULL,
  `points` int(10) NOT NULL,
  `gold_times` int(10) NOT NULL,
  `pct_times` int(10) NOT NULL,
  `battled_card` mediumblob,
  `recover_card` mediumblob,
  `last_refresh_time` varchar(32) NOT NULL,
  `last_fight_key` varchar(64) NOT NULL,
  `is_reward` int(8) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-16 15:08:09
