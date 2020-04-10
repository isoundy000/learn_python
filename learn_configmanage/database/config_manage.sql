/*
 Navicat Premium Data Transfer

 Source Server         : RyanWond
 Source Server Type    : MySQL
 Source Server Version : 50621
 Source Host           : localhost
 Source Database       : config_manage

 Target Server Type    : MySQL
 Target Server Version : 50621
 File Encoding         : utf-8

 Date: 07/06/2017 11:09:57 AM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `t_activity_monitor`
-- ----------------------------
DROP TABLE IF EXISTS `t_activity_monitor`;
CREATE TABLE `t_activity_monitor` (
  `id` int(11) NOT NULL,
  `gid` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `activity` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gid` (`gid`,`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_activity_validate`
-- ----------------------------
DROP TABLE IF EXISTS `t_activity_validate`;
CREATE TABLE `t_activity_validate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aid` int(11) NOT NULL,
  `gid` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `user` int(11) DEFAULT NULL,
  `process_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `aid` (`aid`,`gid`),
  KEY `gid` (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_alarm`
-- ----------------------------
DROP TABLE IF EXISTS `t_alarm`;
CREATE TABLE `t_alarm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform` varchar(255) DEFAULT '',
  `gid` int(11) NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '0',
  `type` enum('open','error','online','status','config') DEFAULT NULL,
  `level` enum('serious','normal','info') DEFAULT NULL,
  `status` int(11) DEFAULT '0',
  `otime` timestamp  NOT NULL DEFAULT '0000-00-00 00:00:00',
  `mess1` varchar(255) DEFAULT NULL,
  `mess2` mediumtext,
  `sendtime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `gid` (`gid`),
  KEY `status` (`status`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_alarm_process`
-- ----------------------------
DROP TABLE IF EXISTS `t_alarm_process`;
CREATE TABLE `t_alarm_process` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aid` int(11) NOT NULL,
  `user` int(11) NOT NULL,
  `otime` timestamp DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `aid` (`aid`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_broadcast2`
-- ----------------------------
DROP TABLE IF EXISTS `t_broadcast2`;
CREATE TABLE `t_broadcast2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person` varchar(64) NOT NULL,
  `content` varchar(128) NOT NULL,
  `type` enum('5M','10M','20M','30M','60M') NOT NULL,
  `server` int(11) NOT NULL,
  `count` int(11) DEFAULT NULL,
  `createtime` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `durationtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_closeaccount`
-- ----------------------------
DROP TABLE IF EXISTS `t_closeaccount`;
CREATE TABLE `t_closeaccount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` int(11) NOT NULL,
  `rid` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `createtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `endtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_command`
-- ----------------------------
DROP TABLE IF EXISTS `t_command`;
CREATE TABLE `t_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `command` varchar(255) DEFAULT NULL,
  `param` varchar(255) DEFAULT NULL,
  `server_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `server_id` (`server_id`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `t_command`
-- ----------------------------
BEGIN;
INSERT INTO `t_command` VALUES ('37', '王的男人', '/test/kingman', 'rid=628&boss=33009', '1'), ('25', '清空副本cache', '/gm/clearcopycache', '', '1'), ('26', 'test', 'id', '', '1'), ('27', '测试团战', '/test/mbattle', '', '1'), ('28', '帮派据点测试', '/test/gptest', 'state=0', '1'), ('29', 'GP注册开始', '/test/gptest', 'state=0', '1'), ('30', 'GP注册结束', '/test/gptest', 'state=1', '1'), ('31', 'GP战斗参与人生成', '/test/gptest', 'state=2', '1'), ('32', 'GP第一回合开始', '/test/gptest', 'state=3', '1'), ('33', 'GP第一回合结束', '/test/gptest', 'state=4', '1'), ('34', 'GP第二回合开始', '/test/gptest', 'state=5', '1'), ('35', 'GP第二回合结束', '/test/gptest', 'state=6', '1'), ('36', 'GP清理报名数据', '/test/gptest', 'state=7', '1'), ('38', 'test', 'id', '', '0'), ('39', '珍品折扣清零', '/gm/cleargemdiscount', '', '1'), ('40', '找回应用宝充值(个人)', '/gm/fixmsdkrecharge1', 'rid=68', '1'), ('41', '清除箱子缓存', '/gm/clearpropboxcache', '', '1'), ('42', '内存探测', '/gm/gccheckobj', '', '1'), ('43', '清空不在线response', '/gm/clearresponse', '', '1');
COMMIT;

-- ----------------------------
--  Table structure for `t_config`
-- ----------------------------
DROP TABLE IF EXISTS `t_config`;
CREATE TABLE `t_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL,
  `section` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `version` int(11) NOT NULL DEFAULT '1',
  `excelurl` varchar(255) NOT NULL,
  `who` int(11) DEFAULT NULL,
  `upload_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `desc` varchar(255) DEFAULT NULL,
  `tag` int(11) NOT NULL DEFAULT '0',
  `url1` varchar(255) DEFAULT NULL,
  `url2` varchar(255) DEFAULT NULL,
  `url3` varchar(255) DEFAULT NULL,
  `filepath` varchar(255) NOT NULL,
  `jsonname` varchar(255) DEFAULT NULL,
  `status` enum('invalid','effective','online') DEFAULT NULL,
  `eff_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `online_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `jsonpath` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `section` (`section`,`type`,`status`),
  KEY `type` (`type`),
  KEY `status` (`status`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_config_log`
-- ----------------------------
DROP TABLE IF EXISTS `t_config_log`;
CREATE TABLE `t_config_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL,
  `opt` enum('upload','effective','online') DEFAULT NULL,
  `ctype` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `opt_time` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_config_temp`
-- ----------------------------
DROP TABLE IF EXISTS `t_config_temp`;
CREATE TABLE `t_config_temp` (
  `cid` int(11) NOT NULL,
  `task` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_device`
-- ----------------------------
DROP TABLE IF EXISTS `t_device`;
CREATE TABLE `t_device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `deviceid` varchar(48) NOT NULL,
  `devicetype` varchar(32) DEFAULT NULL,
  `ostype` varchar(48) DEFAULT NULL,
  `osversion` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_downfile`
-- ----------------------------
DROP TABLE IF EXISTS `t_downfile`;
CREATE TABLE `t_downfile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `time` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `size` float DEFAULT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `t_exchange`
-- ----------------------------
DROP TABLE IF EXISTS `t_exchange`;
CREATE TABLE `t_exchange` (
  `key` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_func`
-- ----------------------------
DROP TABLE IF EXISTS `t_func`;
CREATE TABLE `t_func` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `stay_time` int(11) DEFAULT NULL,
  `out_time` int(11) DEFAULT NULL,
  `system` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`name`),
  KEY `system` (`system`)
) ENGINE=MyISAM AUTO_INCREMENT=176 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Records of `t_func`
-- ----------------------------
BEGIN;
INSERT INTO `t_func` VALUES ('11', 'UserOnlineRewardQuery', '2', '2', '1'), ('10', 'UserCombMessages', '5', '5', '1'), ('9', 'UserBraveCopyModUp', '10', '30', '3'), ('12', 'UserOnlineReward', '2', '2', '1'), ('13', 'UserHint', '2', '2', '1'), ('15', 'UserLivenessReward', '5', '5', '4'), ('16', 'UserTaskComplete', '5', '5', '4'), ('17', 'UserTaskQuery', '5', '5', '4'), ('19', 'UserLiveness', '5', '5', '4'), ('22', 'UserShopQuery', '5', '20', '5'), ('23', 'UserShopBuy', '10', '20', '5'), ('24', 'UserGiftBagQuery', '5', '20', '5'), ('25', 'UserGiftBagBuy', '10', '20', '5'), ('26', 'UserRecruitQuery', '5', '20', '5'), ('27', 'UserRecruitGeneral', '10', '20', '5'), ('28', 'UserFirstRechargeReward', '10', '10', '6'), ('29', 'UserGeneralChangePos', '15', '30', '7'), ('30', 'UserCheerPos', '15', '30', '7'), ('31', 'UserSlotChangeEquip', '15', '30', '7'), ('32', 'UserSlotChangeSoul', '15', '30', '7'), ('33', 'UserQuickEquip', '10', '30', '7'), ('34', 'UserUpgradeSkill', '15', '30', '7'), ('35', 'UserChangePosOnSlot', '15', '30', '7'), ('36', 'UserTreasureUp', '15', '30', '7'), ('37', 'UserGeneralInheritConfirm', '10', '30', '7'), ('38', 'UserGeneralFosterPreview', '15', '30', '7'), ('39', 'UserEquipStrengthen', '15', '30', '7'), ('40', 'UserEquipRefine', '15', '30', '7'), ('41', 'UserGeneralInheritPreview', '10', '30', '7'), ('42', 'UserEquipStrengthenEx', '10', '30', '7'), ('43', 'UserTreasureRefine', '15', '30', '7'), ('44', 'UserGeneralCompound', '15', '30', '7'), ('45', 'UserGeneralCompound', '15', '30', '8'), ('46', 'UserGeneralExchange', '15', '30', '8'), ('47', 'UserDevilUp', '10', '30', '9'), ('48', 'UserProtagonistAddAttr', '10', '30', '9'), ('49', 'UserProtagonistGrowUp', '10', '30', '9'), ('50', 'UserProtagonistRecoverTrain', '10', '30', '9'), ('51', 'UserDevilStatus', '10', '30', '9'), ('52', 'UserProtagonist', '5', '30', '9'), ('53', 'UserDevilExchangeFragment', '15', '30', '9'), ('54', 'UserSoulUpgrade', '15', '30', '7'), ('55', 'UserSoulHuntQuery', '5', '30', '10'), ('56', 'UserSoulHunt', '10', '30', '10'), ('57', 'UserSoulExchange', '15', '30', '10'), ('58', 'UserSoulHunt41', '10', '30', '10'), ('59', 'UserSoulResolve', '15', '30', '10'), ('60', 'UserFriendQuery', '5', '30', '11'), ('61', 'UserFriendRecommend', '5', '30', '11'), ('62', 'UserFriendSearch', '15', '30', '11'), ('63', 'UserFriendReqQuery', '5', '30', '11'), ('64', 'UserFriendRep', '10', '30', '11'), ('65', 'UserLevelRankQuery', '10', '30', '12'), ('66', 'UserMailList', '5', '30', '13'), ('67', 'UserMailRead', '10', '30', '13'), ('68', 'UserMailDelete', '10', '30', '13'), ('69', 'UserMailSend', '15', '30', '13'), ('70', 'UserGeneralCollect', '30', '30', '14'), ('71', 'UserEquipCollect', '30', '30', '14'), ('72', 'UserCopyModUp', '10', '30', '3'), ('73', 'UserCopyAll3StarReward', '10', '30', '3'), ('74', 'UserCopyPrestigeReward', '10', '30', '3'), ('75', 'UserCopyRecoverKill', '10', '30', '3'), ('76', 'UserBraveCopyQuery', '5', '30', '3'), ('77', 'UserBraveCopyAttack', '80', '300', '3'), ('78', 'UserBraveCopyAll3StarReward', '10', '30', '3'), ('79', 'UserBraveCopyPrestigeReward', '10', '30', '3'), ('80', 'UserBraveCopyRecoverKill', '10', '30', '3'), ('83', 'UserCopyAttack', '60', '300', '3'), ('84', 'UserActivityQuery', '10', '30', '15'), ('85', 'UserActivityEatChickenQuery', '5', '30', '15'), ('86', 'UserActivityEatChicken', '5', '30', '15'), ('87', 'UserMysticalCave', '5', '30', '15'), ('88', 'UserMysticalCaveForecast', '10', '30', '15'), ('89', 'UserMysticalReversion', '10', '30', '15'), ('90', 'UserMysticalConfirm', '5', '30', '15'), ('91', 'UserMysticalReward', '10', '30', '15'), ('92', 'UserActivityMammonQuery', '5', '30', '15'), ('93', 'UserActivityMammon', '10', '30', '15'), ('94', 'UserActivityMammonTips', '5', '30', '15'), ('95', 'UserSignInStatus', '5', '30', '15'), ('96', 'UserConsumeGiftReward', '10', '30', '15'), ('97', 'UserConsumeGift', '5', '30', '15'), ('98', 'UserDayDayGift', '5', '30', '15'), ('99', 'UserDayDayGiftReward', '10', '30', '15'), ('100', 'UserSignIn', '10', '30', '15'), ('101', 'UserInviteCode', '5', '30', '15'), ('102', 'UserInviteCodeSet', '10', '30', '15'), ('103', 'UserInviteCodeReward', '10', '30', '15'), ('104', 'UserMonthCard', '5', '30', '15'), ('105', 'UserMonthCardGet', '10', '30', '15'), ('106', 'UserMonthCardReward', '5', '30', '15'), ('107', 'UserMonthCardRewardGet', '10', '30', '15'), ('108', 'UserGrowPlan', '5', '30', '15'), ('109', 'UserGrowPlanBuy', '15', '30', '15'), ('110', 'UserGrowPlanReward', '10', '30', '15'), ('111', 'UserActivityStartGiftQuery', '5', '30', '15'), ('112', 'UserActivityStartGift', '10', '30', '15'), ('113', 'UserChatQuery', '5', '60', '15'), ('114', 'UserContinue7Reward', '10', '30', '15'), ('115', 'UserHappinessPlace', '5', '30', '15'), ('116', 'UserHappinessPlaceSearch', '10', '30', '15'), ('117', 'UserHappinessPlaceRank', '10', '30', '15'), ('118', 'UserHappinessStoneExchange', '10', '30', '15'), ('119', 'UserHappinessServerTotoalReward', '10', '30', '15'), ('120', 'UserPropsList', '5', '30', '16'), ('121', 'UserUseProps', '10', '30', '16'), ('122', 'UserEquipResolve', '15', '30', '16'), ('123', 'UserEquipFragmentCompound', '15', '30', '16'), ('124', 'UserChatQuery', '20', '30', '17'), ('125', 'UserChat', '15', '30', '17'), ('126', 'UserGangChatQuery', '20', '30', '17'), ('127', 'UserGangChat', '15', '30', '17'), ('128', 'UserAthleticsList', '5', '30', '18'), ('129', 'UserAthleticsAttack', '35', '150', '18'), ('130', 'UserAthleticsOtherDetail', '25', '30', '18'), ('131', 'UserAthleticsRewardsQuery', '5', '30', '18'), ('132', 'UserAthleticsRewardsExchange', '10', '30', '18'), ('133', 'UserAthleticsChump', '30', '150', '18'), ('134', 'UserAthleticsBoss', '35', '150', '18'), ('135', 'UserTreasureFragmentRobQuery', '5', '30', '19'), ('136', 'UserTreasureFragmentRob', '35', '150', '19'), ('137', 'UserGeneralFragmentRobQuery', '5', '30', '19'), ('138', 'UserGeneralFragmentRob', '35', '150', '19'), ('139', 'UserPenglai', '5', '30', '20'), ('140', 'UserPenglaiSelectDifficulty', '5', '30', '20'), ('141', 'UserPenglaiSearch', '10', '30', '20'), ('142', 'UserPenglaiBattle', '70', '300', '20'), ('143', 'UserPenglaiRank', '10', '30', '20'), ('144', 'UserPenglaiTodayReward', '5', '30', '20'), ('145', 'UserPenglaiTotal', '10', '30', '20'), ('146', 'UserPenglaiTotalReward', '15', '30', '20'), ('147', 'UserPenglaiTask', '10', '30', '20'), ('148', 'UserPenglaiTaskReward', '15', '30', '20'), ('149', 'UserWorldBoss1Query', '5', '30', '21'), ('150', 'UserBloodQuery', '5', '30', '21'), ('151', 'UserWorldBoss1Rank', '10', '30', '21'), ('152', 'UserWorldBoss1PreRank', '10', '30', '21'), ('153', 'UserBloodQuery', '5', '30', '22'), ('154', 'UserBloodBattle', '35', '150', '22'), ('155', 'UserBlood3AttrBufQuery', '5', '30', '22'), ('156', 'UserBlood3AttrBuf', '5', '30', '22'), ('157', 'UserBloodModUpConfirm', '5', '30', '22'), ('158', 'UserBlood5Award', '5', '30', '22'), ('159', 'UserBloodRankQuery', '10', '30', '22'), ('160', 'UserBloodModUpContinue', '10', '30', '22'), ('161', 'UserBlood5AwardQuery', '5', '30', '22'), ('162', 'UserBloodModUp', '10', '30', '22'), ('163', 'UserCupStatus', '5', '30', '23'), ('164', 'UserCupJoinTomorrow', '5', '30', '23'), ('165', 'UserCupTop', '10', '30', '23'), ('166', 'UserCupBattlePlay', '60', '300', '23'), ('167', 'UserCupBattleReward', '10', '30', '23'), ('168', 'UserCupBattleBet', '10', '30', '23'), ('169', 'UserExpeditionQuery', '5', '30', '24'), ('170', 'UserExpeditionAttack', '35', '150', '24'), ('171', 'UserFriendSendGift', '10', '30', '11'), ('172', 'UserFriendChat', '15', '30', '11'), ('173', 'UserFriendChatQuery', '15', '30', '11'), ('174', 'UserFriendRecvGift', '10', '30', '11'), ('175', 'UserFriendDelete', '10', '30', '11');
COMMIT;

-- ----------------------------
--  Table structure for `t_gag`
-- ----------------------------
DROP TABLE IF EXISTS `t_gag`;
CREATE TABLE `t_gag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rid` int(11) NOT NULL,
  `gagnum` int(11) DEFAULT NULL,
  `type` enum('hour','day','forever') DEFAULT NULL,
  `server` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `server` (`server`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_game_log_status`
-- ----------------------------
DROP TABLE IF EXISTS `t_game_log_status`;
CREATE TABLE `t_game_log_status` (
  `gid` int(11) NOT NULL,
  `status_time` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `status` int(11) DEFAULT '0',
  PRIMARY KEY (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_gamebase`
-- ----------------------------
DROP TABLE IF EXISTS `t_gamebase`;
CREATE TABLE `t_gamebase` (
  `server` int(11) NOT NULL,
  `port` int(11) NOT NULL DEFAULT '3306',
  `database` varchar(64) NOT NULL,
  `user` varchar(64) NOT NULL,
  `password` varchar(64) DEFAULT NULL,
  `desc` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`server`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_gameerror`
-- ----------------------------
DROP TABLE IF EXISTS `t_gameerror`;
CREATE TABLE `t_gameerror` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform` enum('ios','android','ysdk','yue') DEFAULT NULL,
  `server` int(11) DEFAULT NULL,
  `tag` enum('game','ext', 'acc') DEFAULT NULL,
  `error_tag` enum('TraceBack','Critical') DEFAULT NULL,
  `message` mediumtext,
  `send` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `send` (`send`),
  KEY `server` (`server`,`otime`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_gameerror_filter`
-- ----------------------------
DROP TABLE IF EXISTS `t_gameerror_filter`;
CREATE TABLE `t_gameerror_filter` (
  `id` int(11) NOT NULL,
  `mess` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_gamelog_process`
-- ----------------------------
DROP TABLE IF EXISTS `t_gamelog_process`;
CREATE TABLE `t_gamelog_process` (
  `name` varchar(255) NOT NULL,
  `tag` int(11) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_gamestatus`
-- ----------------------------
DROP TABLE IF EXISTS `t_gamestatus`;
CREATE TABLE `t_gamestatus` (
  `gid` int(11) NOT NULL,
  `gates_status` int(11) DEFAULT '0',
  `game_status` int(11) DEFAULT '0',
  `ext_status` int(11) DEFAULT NULL,
  `total` int(11) DEFAULT '0',
  `online` int(11) DEFAULT '0',
  `open_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_log`
-- ----------------------------
DROP TABLE IF EXISTS `t_log`;
CREATE TABLE `t_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(64) NOT NULL,
  `op_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `user` varchar(64) DEFAULT NULL,
  `content` varchar(256) DEFAULT NULL,
  `ip` varchar(255) not null default '0.0.0.0',
  PRIMARY KEY (`id`),
  KEY `op_time` (`op_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_mail_approve`
-- ----------------------------
DROP TABLE IF EXISTS `t_mail_approve`;
CREATE TABLE `t_mail_approve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` int(11) DEFAULT NULL,
  `channel_list` varchar(64) DEFAULT NULL,
  `vip_grade` int(11) NOT NULL DEFAULT '0',
  `rid` int(11) DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  `reward` varchar(255) DEFAULT NULL,
  `reward_alias` varchar(255) DEFAULT NULL,
  `status` enum('yes','no','refuse') DEFAULT 'no',
  `itime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` varchar(255) DEFAULT NULL,
  `user2` varchar(255) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  `title` varchar(64) DEFAULT NULL,
  `mail_record_id` int(11) NOT NULL DEFAULT '0',
  `send_mail_way` char(2) NOT NULL COMMENT '发送邮件方式',
  `role_recharge` varchar(30) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_merge_info`
-- ----------------------------
DROP TABLE IF EXISTS `t_merge_info`;
CREATE TABLE `t_merge_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `method` int(11) DEFAULT NULL,
  `world_method` int(11) NOT NULL,
  `world_ip` varchar(64) DEFAULT NULL,
  `world_port` int(11) DEFAULT NULL,
  `create_instance` int(11) DEFAULT NULL,
  `mid` int(11) DEFAULT NULL,
  `oid_list` varchar(255) DEFAULT NULL,
  `base_port` int(11) DEFAULT NULL,
  `game_port` int(11) DEFAULT NULL,
  `mysql_version` int(11) DEFAULT '1',
  `listen_ip` varchar(255) DEFAULT NULL,
  `filter_level` int(11) DEFAULT NULL,
  `status` enum('prepare','execute','finish','empty') DEFAULT NULL,
  `sql_id` int(11) DEFAULT NULL,
  `merge_source` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_online_1h`
-- ----------------------------
DROP TABLE IF EXISTS `t_online_1h`;
CREATE TABLE `t_online_1h` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `game` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  `high` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `game` (`game`) USING BTREE,
  KEY `otime` (`otime`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_openserver`
-- ----------------------------
DROP TABLE IF EXISTS `t_openserver`;
CREATE TABLE `t_openserver` (
  `gid` int(11) NOT NULL,
  `opentime` timestamp DEFAULT '0000-00-00 00:00:00',
  `status` enum('prepare','execute') DEFAULT NULL,
  `executetime` timestamp DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `result` enum('success','fail') DEFAULT NULL,
  PRIMARY KEY (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_param`
-- ----------------------------
DROP TABLE IF EXISTS `t_param`;
CREATE TABLE `t_param` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `t_param`
-- ----------------------------
BEGIN;
INSERT INTO `t_param` VALUES ('2', '登录', '登录'), ('3', '在线', '在线时长');
COMMIT;

-- ----------------------------
--  Table structure for `t_param_data`
-- ----------------------------
DROP TABLE IF EXISTS `t_param_data`;
CREATE TABLE `t_param_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `t_param_data`
-- ----------------------------
BEGIN;
INSERT INTO `t_param_data` VALUES ('1', '2', '1', '10'), ('2', '2', '10', '20'), ('3', '2', '20', '30'), ('4', '3', '0', '5'), ('5', '3', '5', '10'), ('6', '3', '10', '15');
COMMIT;

-- ----------------------------
--  Table structure for `t_partner`
-- ----------------------------
DROP TABLE IF EXISTS `t_partner`;
CREATE TABLE `t_partner` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `alias` varchar(255) NOT NULL,
  `desc` varchar(255) DEFAULT NULL,
  `discount` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_platform_recharge`
-- ----------------------------
DROP TABLE IF EXISTS `t_platform_recharge`;
CREATE TABLE `t_platform_recharge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `percent` int(11) DEFAULT NULL,
  `tongdao` int(11) DEFAULT '0',
  `kuajing` int(11) DEFAULT '0',
  `month_total` int(11) DEFAULT NULL,
  `total_total` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`platform`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_process_time`
-- ----------------------------
DROP TABLE IF EXISTS `t_process_time`;
CREATE TABLE `t_process_time` (
  `process_time` timestamp NULL DEFAULT NULL,
  `status` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

insert into t_process_time values (now(), 1);

-- ----------------------------
--  Table structure for `t_recharge`
-- ----------------------------
DROP TABLE IF EXISTS `t_recharge`;
CREATE TABLE `t_recharge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL DEFAULT '0',
  `gid` int(11) NOT NULL,
  `cid` int(11) NOT NULL,
  `result` enum('yes','no') NOT NULL DEFAULT 'no',
  `notify` enum('yes','no') NOT NULL DEFAULT 'no',
  `cp` int(11) DEFAULT NULL,
  `createtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `recvtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `amount` float(11,2) DEFAULT NULL,
  `channel` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recvtime` (`recvtime`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_regist`
-- ----------------------------
DROP TABLE IF EXISTS `t_regist`;
CREATE TABLE `t_regist` (
  `uid` int(11) NOT NULL,
  `account` varchar(48) DEFAULT NULL,
  `channel` int(11) NOT NULL,
  `createtime` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`uid`),
  KEY `k_createtime` (`createtime`) USING BTREE,
  KEY `k_account` (`account`) USING BTREE,
  KEY `channel` (`channel`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_section`
-- ----------------------------
DROP TABLE IF EXISTS `t_section`;
CREATE TABLE `t_section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '',
  `desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`,`name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_section_config_version`
-- ----------------------------
DROP TABLE IF EXISTS `t_section_config_version`;
CREATE TABLE `t_section_config_version` (
  `section` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`section`,`version`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_section_log`
-- ----------------------------
DROP TABLE IF EXISTS `t_section_log`;
CREATE TABLE `t_section_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) DEFAULT NULL,
  `section` int(11) DEFAULT NULL,
  `type` enum('move','copy') DEFAULT NULL,
  `zipname` varchar(255) DEFAULT NULL,
  `zippath` varchar(255) DEFAULT NULL,
  `opt_time` timestamp NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `zipdata` mediumtext,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_section_log_details`
-- ----------------------------
DROP TABLE IF EXISTS `t_section_log_details`;
CREATE TABLE `t_section_log_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sid` int(11) NOT NULL DEFAULT '0',
  `type` varchar(255) DEFAULT NULL,
  `opt` enum('add','modify') DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `filepath` varchar(255) DEFAULT NULL,
  `jsonname` varchar(255) DEFAULT NULL,
  `jsonpath` varchar(255) DEFAULT NULL,
  `alias` varchar(255) DEFAULT NULL,
  `type_key` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_server`
-- ----------------------------
DROP TABLE IF EXISTS `t_server`;
CREATE TABLE `t_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gameid` int(11) NOT NULL,
  `ip` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `extport` int(11) NOT NULL,
  `path` varchar(128) NOT NULL,
  `extpath` varchar(128) NOT NULL,
  `gmport` int(11) NOT NULL,
  `extgmport` int(11) NOT NULL,
  `log_path` varchar(255) NOT NULL,
  `config_path` varchar(255) DEFAULT NULL,
  `section` int(11) NOT NULL,
  `extranet_ip` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `createtime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `mode` int(11) DEFAULT '1',
  `status` enum('online','offline','maintain','fault','inner') DEFAULT NULL,
  `tag1` enum('new','normal','old') NOT NULL,
  `tag2` enum('normal','hot','full') NOT NULL,
  `change` int(11) default 0 not null,
  PRIMARY KEY (`id`),
  KEY `gameid` (`gameid`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_simrecharge`
-- ----------------------------
DROP TABLE IF EXISTS `t_simrecharge`;
CREATE TABLE `t_simrecharge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gid` int(11) DEFAULT NULL,
  `rid` int(11) DEFAULT NULL,
  `cid` int(11) DEFAULT NULL,
  `rechargetime` timestamp NULL DEFAULT NULL,
  `desc` varchar(255) NOT NULL,
  `user` varchar(255) DEFAULT NULL,
  `type` enum('test','order','recharge') DEFAULT NULL,
  `amount` int(11) NOT NULL DEFAULT '0',
  `mode` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_systemparam`
-- ----------------------------
DROP TABLE IF EXISTS `t_systemparam`;
CREATE TABLE `t_systemparam` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `param` int(11) DEFAULT NULL,
  `tag` int(11) DEFAULT '0',
  `desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Records of `t_systemparam`
-- ----------------------------
BEGIN;
INSERT INTO `t_systemparam` VALUES ('1', '主页面', '2', '0', '主页面'), ('3', '副本', '2', '1', ''), ('4', '每日奖励', '2', '0', '每日任务，成就奖励'), ('5', '商城', '2', '0', ''), ('6', '首冲', '2', '0', '首次充值'), ('7', '阵容', '2', '1', '上阵人物详情'), ('8', '伙伴', '2', '0', '英雄详情'), ('9', '魔宫', '2', '0', ''), ('10', '猎命', '2', '1', ''), ('11', '好友', '2', '0', ''), ('12', '排行榜', '2', '0', ''), ('13', '邮件', '2', '0', ''), ('14', '图鉴', '2', '0', ''), ('15', '活动', '2', '1', ''), ('16', '背包', '2', '0', ''), ('17', '聊天', '2', '0', ''), ('18', '竞技场', '2', '0', ''), ('19', '夺宝', '2', '0', ''), ('20', '蓬莱仙岛', '2', '0', ''), ('21', '群仙屠龙', '2', '0', ''), ('22', '伏魔塔', '2', '0', ''), ('23', '杯赛', '2', '0', ''), ('24', '好友副本', '2', '0', '');
COMMIT;

-- ----------------------------
--  Table structure for `t_task`
-- ----------------------------
DROP TABLE IF EXISTS `t_task`;
CREATE TABLE `t_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `type` enum('config') DEFAULT NULL,
  `opt_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `auto_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `desc` varchar(255) DEFAULT NULL,
  `user` int(11) NOT NULL,
  `restart_game` int(11) DEFAULT '0',
  `restart_ext` int(11) DEFAULT '0',
  `status` enum('prepare','execute','success','fail') DEFAULT NULL,
  `ext` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_type`
-- ----------------------------
DROP TABLE IF EXISTS `t_type`;
CREATE TABLE `t_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `type_key` varchar(64) NOT NULL,
  `section` int(11) NOT NULL,
  `alias` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`) USING BTREE,
  KEY `section` (`section`,`name`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_users`
-- ----------------------------
DROP TABLE IF EXISTS `t_users`;
CREATE TABLE `t_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) not null default '',
  `username` varchar(64) NOT NULL COMMENT '用户名',
  `password` varchar(128) NOT NULL,
  `channel` int(11) NOT NULL DEFAULT '0',
  `role1` int(11) NOT NULL DEFAULT '0' COMMENT '管理系统权限',
  `role2` int(11) NOT NULL DEFAULT '0' COMMENT '策划系统权限',
  `role3` int(11) NOT NULL DEFAULT '0' COMMENT '统计系统权限',
  `role4` int(11) NOT NULL DEFAULT '0' COMMENT '运维系统权限',
  `role5` int(11) NOT NULL DEFAULT '0' COMMENT '运营系统权限',
  `game` varchar(255) DEFAULT NULL,
  `upload` int(11) DEFAULT '0',
  `start` varchar(255) DEFAULT NULL,
  `recharge` varchar(255) DEFAULT NULL,
  `custom` varchar(255) DEFAULT NULL,
  `approve` int(11) DEFAULT '0',
  `simulator` int(11) DEFAULT '0',
  `phone` varchar(255) DEFAULT '' COMMENT '电话',
  `email` varchar(255) DEFAULT '' COMMENT '电子邮件',
  PRIMARY KEY (`id`),
  KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `t_users`
-- ----------------------------
BEGIN;
INSERT INTO `t_users` VALUES ('1', '',
'administrator_muyou', '3e111be310fae9a1e2f5f651376d9225', '0', '1', '1', '1', '1', '1', '', '1', '', '', '', '0', '0', '', '');
COMMIT;


-- ----------------------------
--  Table structure for `world_drop_result`
-- ----------------------------
DROP TABLE IF EXISTS `world_drop_result`;
CREATE TABLE `world_drop_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_type` char(50) NOT NULL,
  `player_grade` int(11) NOT NULL,
  `stay_days` int(11) NOT NULL,
  `save_date` char(50) NOT NULL,
  `drop_result` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `player_grade` (`player_grade`) USING BTREE,
  KEY `save_date` (`save_date`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;

DROP TABLE IF EXISTS `t_restartserver`;
CREATE TABLE `t_restartserver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gid_list` varchar(255) DEFAULT NULL,
  `status` enum('prepare','execute') DEFAULT NULL,
  `restarttime` timestamp NULL DEFAULT NULL,
  `executetime` timestamp NULL DEFAULT NULL,
  `game` int(11) DEFAULT '0',
  `ext` int(11) DEFAULT '0',
  `result` enum('success','fail') DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_channel_force`;
CREATE TABLE `t_channel_force` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `cn_name` varchar(64) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `url` varchar(64) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_pick_in`;
CREATE TABLE `t_pick_in` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gid` int(11) DEFAULT NULL,
  `json_path` varchar(64) DEFAULT NULL,
  `new_rid` int(11) DEFAULT NULL,
  `to_rid` int(11) DEFAULT NULL,
  `result` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  `otime2` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gid` (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `t_pick_out`;
CREATE TABLE `t_pick_out` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gid` int(11) NOT NULL,
  `rid` int(11) DEFAULT NULL,
  `role_name` varchar(64) DEFAULT NULL,
  `json_path` varchar(64) DEFAULT NULL,
  `json_url` varchar(64) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gid` (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `check_ip_set`;
CREATE TABLE `check_ip_set` (
     `id` int(11) NOT NULL AUTO_INCREMENT,
   `ip`  varchar(15) NOT NULL COMMENT 'ip地址',
 `port` varchar(10) NOT NULL COMMENT '端口号',
 `status_cd` char(2) NOT NULL DEFAULT '00' COMMENT '状态',
  `protocol` varchar(10) NOT NULL COMMENT '协议',
  `req_path` varchar(50)  DEFAULT '' COMMENT '请求路径',
  `req_way` varchar(5)  DEFAULT '' COMMENT '请求类型',
  `req_param` varchar(50)  DEFAULT '' COMMENT '请求参数',
  `remark` varchar(50) DEFAULT '' COMMENT '其他',
 `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
 ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='检测的ip';

 DROP TABLE IF EXISTS `auto_cut_partition_record`;
 CREATE TABLE `auto_cut_partition_record` (
  `record_id` int(11) NOT NULL,
  `server_id` int(11) NOT NULL,
  `sour_partition` int(11) NOT NULL,
  `desc_partition` int(11) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT NULL,
  `up_day` int(11) DEFAULT NULL,
  `status` enum('ok','fail') NOT NULL,
  `info` varchar(120) DEFAULT NULL,
  KEY `record_id` (`record_id`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

  DROP TABLE IF EXISTS `t_common_conf`;
 CREATE TABLE `t_common_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conf_name` varchar(64) NOT NULL,
  `field_1` varchar(64) DEFAULT '',
  `field_2` varchar(64) DEFAULT '',
  `field_3` varchar(64) DEFAULT '',
  `field_4` varchar(64) DEFAULT '',
  `field_5` varchar(64) DEFAULT '',
  `field_6` varchar(512) DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('start','stop') NOT NULL DEFAULT 'start',
  PRIMARY KEY (`id`),
  KEY `conf_name` (`conf_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
 insert into t_common_conf (id,conf_name) values (1,'auto_cut_partition');

DROP TABLE IF EXISTS `mail_batch_role_rel`;
CREATE TABLE `mail_batch_role_rel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_time` char(8) NOT NULL COMMENT '发送邮件日期',
  `batch_id` int(11) NOT NULL COMMENT '批量ID',
  `server_id` int(11) NOT NULL COMMENT '区服',
  `channel_id` int(11) NOT NULL COMMENT '渠道',
  `rec_role_id` int(11) NOT NULL COMMENT '收件人',
  `mail_title` varchar(64) DEFAULT '' COMMENT '邮件标题',
  `mail_content` varchar(128) DEFAULT '' COMMENT '邮件内容',
  `mail_att` varchar(32) DEFAULT '' COMMENT '邮件附件',
  `mail_att_ch` varchar(32) DEFAULT '' COMMENT '附件转译',
  `s_time` datetime NOT NULL COMMENT '发邮件时间',
  `mail_status` char(2) NOT NULL COMMENT '邮件状态',
  `send_mail_way` char(2) NOT NULL COMMENT '发送邮件方式',
  `remark_con` varchar(64) DEFAULT '' COMMENT '备注字段',
  PRIMARY KEY (`id`),
  KEY `date_time` (`date_time`),
  KEY `batch_type` (`batch_id`,`send_mail_way`,`mail_status`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='批量邮件与角色的关系';

DROP TABLE IF EXISTS `t_batch_mail_record`;
CREATE TABLE `t_batch_mail_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_time` char(8) NOT NULL COMMENT '发送邮件日期',
  `op_user` int(11) NOT NULL COMMENT '发件人',
  `s_time` datetime NOT NULL COMMENT '发邮件时间',
  `att_name` varchar(64) NOT NULL COMMENT '附件名',
  `batch_status` char(2) NOT NULL COMMENT '邮件状态',
  `remark_con` varchar(64) DEFAULT NULL COMMENT '备注字段',
  PRIMARY KEY (`id`),
  KEY `date_time` (`date_time`),
  KEY `op_user` (`op_user`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='批量邮件记录';

DROP TABLE IF EXISTS `mail_send_record`;
CREATE TABLE `mail_send_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_time` char(8) NOT NULL COMMENT '发送邮件日期',
  `s_uid` int(11) NOT NULL COMMENT '发件人',
  `mail_type` char(2) NOT NULL COMMENT '邮件类型',
  `server_id` int(11) NOT NULL DEFAULT '0' COMMENT '区服',
  `channel_id` varchar(64) NOT NULL DEFAULT '' COMMENT '渠道',
  `vip_grade` int(11) NOT NULL DEFAULT '0',
  `r_rid` varchar(64) NOT NULL DEFAULT '0' COMMENT '收件人',
  `mail_title` varchar(64) DEFAULT '' COMMENT '邮件标题',
  `mail_content` varchar(512) DEFAULT '',
  `mail_att` varchar(512) DEFAULT '' COMMENT '邮件附件',
  `mail_att_ch` varchar(512) DEFAULT '' COMMENT '附件转译',
  `s_time` datetime NOT NULL COMMENT '发邮件时间',
  `u_time` datetime NOT NULL COMMENT '邮件状态变更时间',
  `mail_status` char(2) NOT NULL COMMENT '邮件状态',
  `remark_con` varchar(64) DEFAULT '' COMMENT '备注字段',
  `send_mail_way` char(2) NOT NULL COMMENT '发送邮件方式',
  `is_batch` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `date_time` (`date_time`),
  KEY `s_uid` (`s_uid`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='邮件发送记录';

DROP TABLE IF EXISTS `task_info`;
CREATE TABLE `task_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `op_user` varchar(40) NOT NULL,
  `task_name` varchar(40) NOT NULL,
  `schedule` varchar(40) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT NULL,
  `task_num` int(11) NOT NULL,
  `is_stop` char(1) DEFAULT '0',
  `is_new_task` char(1) DEFAULT '0',
  `task_src` varchar(45) DEFAULT NULL,
  `host_ip` varchar(20) DEFAULT NULL,
  `proc_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `op_user` (`op_user`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `task_sub_info`;
CREATE TABLE `task_sub_info` (
  `task_id` int(11) NOT NULL,
  `sub_id` int(11) NOT NULL,
  `task_name` varchar(40) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT NULL,
  `task_status` char(2) NOT NULL,
  KEY `task_id` (`task_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `t_ip_dict`;
CREATE TABLE `t_ip_dict` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `create_user` varchar(64) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_command_record`;
CREATE TABLE `t_command_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `command` varchar(255) DEFAULT NULL,
  `param` varchar(255) DEFAULT NULL,
  `server_id` int(11) DEFAULT NULL,
  `insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `op_user` varchar(20) NOT NULL,
  `response` varchar(128) NOT NULL,
  `status` varchar(8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `insert_time` (`insert_time`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mail_del_record`;
CREATE TABLE `mail_del_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `op_user` varchar(64) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `server_id` int(11) NOT NULL,
  `mail_id` int(11) NOT NULL,
  `mail_time` timestamp NOT NULL DEFAULT '1970-01-01 08:00:01',
  `del_reason` varchar(128) DEFAULT '',
  `role_id` int(11) NOT NULL,
  `mail_content` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `mail_time` (`mail_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_update`;
CREATE TABLE `t_update` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `location` varchar(128) DEFAULT NULL,
  `status` varchar(2) DEFAULT '0',
  `file_describe` varchar(254) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_update_push_record`;
CREATE TABLE `t_update_push_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `update_id` int(11) NOT NULL,
  `op_user` varchar(64) NOT NULL,
  `ip` varchar(16) DEFAULT NULL,
  `game_id` int(11) DEFAULT NULL,
  `desc_path` varchar(128) DEFAULT NULL,
  `status` varchar(2) DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_server_status`;
CREATE TABLE `t_server_status` (
  `gid` int(11) NOT NULL COMMENT '区服ID',
  `status` int(11) DEFAULT NULL,
  `total` int(11) DEFAULT NULL,
  `online` int(11) DEFAULT NULL,
  `gates` int(11) DEFAULT NULL,
  `game` int(11) DEFAULT NULL,
  `ext` int(11) DEFAULT NULL,
  PRIMARY KEY (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_setgame_B_command`
-- ----------------------------
DROP TABLE IF EXISTS `t_setgame_B_command`;
CREATE TABLE `t_setgame_B_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(128) DEFAULT NULL COMMENT '操作用户ID',
  `opt` int(11) DEFAULT NULL COMMENT '1.启动，2.',
  `info` varchar(255) DEFAULT NULL,
  `method` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_setgame_B_log`
-- ----------------------------
DROP TABLE IF EXISTS `t_setgame_B_log`;
CREATE TABLE `t_setgame_B_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `command_id` int(11) DEFAULT NULL COMMENT '命令ID',
  `gid` int(11) DEFAULT NULL COMMENT '区服ID',
  `ip` varchar(64) DEFAULT NULL COMMENT '区服IP地址',
  `opt` int(11) DEFAULT NULL,
  `method` int(11) DEFAULT NULL COMMENT '启动服务： 1：game 2：gates，3：game， 4：ext， 5：标准所有， 6：性能所有 ',
  `status` int(11) DEFAULT NULL COMMENT '1:执行中，2：成功，3：失败',
  `otime` timestamp NULL DEFAULT NULL,
  `err_info` varchar(255) DEFAULT NULL COMMENT '错误信息',
  PRIMARY KEY (`id`),
  KEY `cid` (`command_id`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `t_setgame_retry`;
CREATE TABLE `t_setgame_retry` (
  `id` int(11) not null,
  `command_id` int(11) DEFAULT NULL COMMENT '命令ID',
  `gid` int(11) DEFAULT NULL COMMENT '区服ID',
  `ip` varchar(64) DEFAULT NULL COMMENT '区服IP地址',
  `opt` int(11) DEFAULT NULL,
  `method` int(11) DEFAULT NULL COMMENT '启动服务： 1：game 2：gates，3：game， 4：ext， 5：标准所有， 6：性能所有 ',
  `status` int(11) DEFAULT NULL COMMENT '1:执行中，2：成功，3：失败',
  `otime` timestamp NULL DEFAULT NULL,
  `err_info` varchar(255) DEFAULT NULL COMMENT '错误信息',
  PRIMARY KEY (`id`),
  KEY `cid` (`command_id`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `t_setgame_command`
-- ----------------------------
DROP TABLE IF EXISTS `t_setgame_command`;
CREATE TABLE `t_setgame_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(128) DEFAULT NULL COMMENT '操作用户ID',
  `opt` int(11) NOT NULL,
  `info` varchar(255) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  `method` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `t_setgame_log`
-- ----------------------------
DROP TABLE IF EXISTS `t_setgame_log`;
CREATE TABLE `t_setgame_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) DEFAULT NULL,
  `gid` int(11) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `t_type` int(11) DEFAULT NULL,
  `opt` int(11) DEFAULT NULL,
  `method` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `otime` timestamp NULL DEFAULT NULL,
  `err_info` varchar(255) DEFAULT NULL,
  `retry_num` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `cid` (`cid`),
  KEY `tag` (`t_type`),
  KEY `status` (`status`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `t_gs_account`;
CREATE TABLE `t_gs_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(45) DEFAULT NULL,
  `checked` varchar(45) DEFAULT NULL,
  `checked_time` varchar(45) DEFAULT NULL,
  `c_user` varchar(45) NOT NULL,
  `u_user` varchar(45) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_gs_recharge_account`;
CREATE TABLE `t_gs_recharge_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `gid` int(11) DEFAULT NULL,
  `rid` int(11) DEFAULT NULL,
  `cid` int(11) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(255) NOT NULL,
  `op_user` varchar(255) DEFAULT NULL,
  `single_money` int(11) NOT NULL DEFAULT '0',
  `total_money` int(11) NOT NULL DEFAULT '0',
  `recharge_num` varchar(255) DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_guild_info`;
CREATE TABLE `t_guild_info` (
  `game_id` int(11) NOT NULL,
  `guild_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `level` int(11) NOT NULL DEFAULT '1',
  `rid` int(11) NOT NULL,
  `rid1` int(11) DEFAULT NULL,
  `rid2` int(11) DEFAULT NULL,
  `rid3` int(11) DEFAULT NULL,
  `content1` varchar(255) DEFAULT NULL,
  `content2` varchar(255) DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `game_id` (`game_id`),
  KEY `rid` (`rid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_guild_operate_num`;
CREATE TABLE `t_guild_operate_num` (
  `game_id` int(11) NOT NULL,
  `guild_id` int(11) NOT NULL,
  `num` int(11) NOT NULL DEFAULT '0',
  KEY `game_id` (`game_id`),
  KEY `guild_id` (`guild_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
