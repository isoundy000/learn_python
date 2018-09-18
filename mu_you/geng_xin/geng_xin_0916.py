# -*- encoding: utf-8 -*-
'''
Created on 2018年9月16日

@author: houguangdong
'''

# 开发版本
# set names utf8;
# alter table t_role add column `filteronline` int(11) DEFAULT '0';
#
# CREATE TABLE `t_world_boss_shop` (
#   `rid` int(11) NOT NULL,
#   `c1` int(11) NOT NULL DEFAULT '0',
#   `c2` int(11) NOT NULL DEFAULT '0',
#   `c3` int(11) NOT NULL DEFAULT '0',
#   `c4` int(11) NOT NULL DEFAULT '0',
#   `c5` int(11) NOT NULL DEFAULT '0',
#   `c6` int(11) NOT NULL DEFAULT '0',
#   `c7` int(11) NOT NULL DEFAULT '0',
#   `c8` int(11) NOT NULL DEFAULT '0',
#   `c9` int(11) NOT NULL DEFAULT '0',
#   `c10` int(11) NOT NULL DEFAULT '0',
#   `history_rank` int(11) NOT NULL DEFAULT '0',
#   `point` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# alter table t_general4 add column `level5` int(11) DEFAULT '0';
#
# alter table t_top_of_world_role_exchange add column `c301` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c302` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c303` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c304` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c305` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c306` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c307` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c308` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c309` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c310` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c311` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c312` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c313` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c314` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c315` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c316` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c317` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c318` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c319` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c320` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c321` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c322` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c323` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c324` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c325` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c326` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c327` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c328` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c329` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c330` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c331` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c332` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c333` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c334` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c335` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c336` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c337` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c338` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c339` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c340` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c341` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c342` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c343` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c344` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c345` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c346` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c347` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c348` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c349` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c350` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c351` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c352` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c353` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c354` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c355` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c356` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c357` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c358` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c359` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c360` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c361` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c362` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c363` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c364` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c365` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c366` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c367` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c368` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c369` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c370` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c371` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c372` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c373` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c374` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c375` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c376` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c377` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c378` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c379` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c380` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c381` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c382` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c383` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c384` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c385` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c386` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c387` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c388` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c389` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c390` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c391` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c392` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c393` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c394` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c395` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c396` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c397` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c398` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c399` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c400` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c401` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c402` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c403` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c404` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c405` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c406` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c407` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c408` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c409` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c410` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c411` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c412` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c413` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c414` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c415` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c416` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c417` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c418` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c419` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c420` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c421` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c422` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c423` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c424` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c425` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c426` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c427` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c428` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c429` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c430` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c431` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c432` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c433` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c434` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c435` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c436` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c437` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c438` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c439` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c440` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c441` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c442` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c443` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c444` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c445` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c446` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c447` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c448` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c449` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c450` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c451` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c452` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c453` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c454` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c455` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c456` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c457` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c458` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c459` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c460` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c461` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c462` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c463` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c464` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c465` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c466` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c467` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c468` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c469` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c470` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c471` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c472` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c473` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c474` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c475` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c476` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c477` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c478` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c479` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c480` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c481` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c482` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c483` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c484` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c485` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c486` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c487` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c488` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c489` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c490` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c491` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c492` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c493` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c494` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c495` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c496` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c497` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c498` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c499` int(11) DEFAULT '0';
# alter table t_top_of_world_role_exchange add column `c500` int(11) DEFAULT '0';
#
# CREATE TABLE `t_activity_consumegiftx3` (
#   `rid` int(11) NOT NULL,
#   `c1` int(11) NOT NULL DEFAULT '0',
#   `s1` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s2` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s3` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s4` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s5` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s6` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s7` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s8` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s9` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `s10` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r1` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r2` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r3` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r4` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r5` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r6` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r7` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r8` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r9` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   `r10` enum('yes','no','get') NOT NULL DEFAULT 'no',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# CREATE TABLE `t_heroboss` (
#   `bossId` int(11) NOT NULL,
#   `status` int(11) NOT NULL DEFAULT '0',
#   `hp` bigint(11) NOT NULL DEFAULT '0',
#   `hpMax` bigint(11) NOT NULL DEFAULT '0',
#   `rtime` timestamp NULL DEFAULT NULL,
#   `dtime` timestamp NULL DEFAULT NULL,
#   `num` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`bossId`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# CREATE TABLE `t_heroboss_award` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `bossId` int(11) NOT NULL DEFAULT '0',
#   `rid` int(11) NOT NULL DEFAULT '0',
#   `damage` bigint(11) NOT NULL DEFAULT '0',
#   `recordTime` timestamp NULL DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `bossId` (`bossId`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
#  CREATE TABLE `t_heroboss_rank` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `rid` int(11) NOT NULL,
#   `bossId` int(11) NOT NULL DEFAULT '0',
#   `damage` bigint(11) NOT NULL DEFAULT '0',
#   `num` int(11) NOT NULL DEFAULT '0',
#   `cheer` int(11) NOT NULL DEFAULT '0',
#   `time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
#   PRIMARY KEY (`id`),
#   KEY `bossId` (`bossId`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# CREATE TABLE `t_heroboss_user` (
#   `rid` int(11) NOT NULL,
#   `count` int(11) NOT NULL DEFAULT '0',
#   `rtime` timestamp NULL DEFAULT NULL,
#   `follow` int(11) NOT NULL DEFAULT '0',
#   `bossId` int(11) NOT NULL DEFAULT '0',
#   `damage` bigint(11) NOT NULL DEFAULT '0',
#   `num` int(11) NOT NULL DEFAULT '0',
#   `cheer` int(11) NOT NULL DEFAULT '0',
#   `double` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# game/Source/DataBase/Table/t_role.py
# game/Source/DataBase/Table/t_general4.py
# game/Source/DataBase/Table/t_world_boss_shop.py
# game/Source/GameConfig/GameConfigManager2.py
# game/Source/GameData/WorldBoss1.py
# game/Source/GameData/WorldBoss2.py
# game/Source/GameOperation/Consume/ConsumeCheck.py
# game/Source/GameOperation/Consume/ConsumeUse.py
# game/Source/GameOperation/General/CopyGeneralProto.py
# game/Source/GameOperation/General/CreateGeneral.py
# game/Source/GameOperation/General/InheritGeneralReset.py
# game/Source/GameOperation/Props/AddProps.py
# game/Source/GameOperation/Reward/GetRewards.py
# game/Source/Timer/Config/Config.py
# game/Source/Timer/DayHour/WorldBossShopDayClear.py
# game/Source/Timer/DayHour/AchievementLimitTimeX5DayClear.py
# game/Source/Timer/DayHour/AchievementLimitTimeX6DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX3DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX4DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX5DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX6DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX7DayClear.py
# game/Source/Timer/DayHour/ConsumegiftX8DayClear.py
# game/Source/Timer/DayHour/GodDownDayClear_x7.py
# game/Source/Timer/DayHour/GodDownDayClear_x8.py
# game/Source/Timer/DayHour/OldDriverDayClear_x6.py
# game/Source/Timer/DayHour/OldDriverDayClear_x7.py
# game/Source/Timer/DayHour/RechargeGiftDayClear_x6.py
# game/Source/Timer/DayHour/RechargeGiftDayClear_x7.py
# game/Source/Timer/DayHour/SingleRechargeGiftDayClear_x6.py
# game/Source/Timer/DayHour/SingleRechargeGiftDayClear_x7.py
# game/Source/Timer/DayHour/SpinampWinDayClear_x6.py
# game/Source/Timer/DayHour/SpinampWinDayClear_x7.py
# game/Source/UserData/UserDataConfig.py
# game/Source/WSGI/Test/GeneralAdvanced.py
# game/Source/WSGI/Test/TestManage.py
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserDragonWishingQuery.py
# game/Source/WorkPool/Functions/UserFriendFilterOnline.py
# game/Source/WorkPool/Functions/UserFriendRecommend.py
# game/Source/WorkPool/Functions/UserGeneralAdvanced5.py
# game/Source/WorkPool/Functions/UserGeneralReset.py
# game/Source/WorkPool/Functions/UserWorldBossShop.py
#
# game/Source/DataBase/Table/t_activity_consumegiftx3.py
# game/Source/DataBase/Table/t_begin28days_role_count.py
# game/Source/DataBase/Table/t_spinampwin.py
# game/Source/DataBase/Table/t_top_of_world.py
# game/Source/DataBase/Table/t_top_of_world_role.py
# game/Source/DataBase/Table/t_top_of_world_role_count.py
# game/Source/DataBase/Table/t_top_of_world_role_exchange.py
# game/Source/GameData/AchievementLimitTimeC.py
# game/Source/GameData/GameData.py
# game/Source/GameData/GameDataManager.py
# game/Source/GameData/TopOfWorld.py
# game/Source/GameOperation/Hint/Build463t468_leijixiaofei.py
# game/Source/GameOperation/Hint/build402t429_topofworld.py
# game/Source/GameOperation/Hint/config.py
# game/Source/GameOperation/Hint/HintCheckSystem.py
# game/Source/GameOperation/Intent/CheckIntent.py
# game/Source/GameOperation/Intent/CommonIntent.py
# game/Source/GameOperation/OldDriver/OldDriverTask.py
# game/Source/GameOperation/Recharge/RechargeComm.py
# game/Source/GameOperation/Role/RoleGetExp.py
# game/Source/GameOperation/Role/RoleUseGold.py
# game/Source/GameOperation/TopOfWorld/CheckTasks.py
# game/Source/GameOperation/TopOfWorld/DaysCompute.py
#
# game/Source/WorkPool/Functions/ActivityCopyModUp.py
# game/Source/WorkPool/Functions/UserAchievementLimitTime_x5.py
# game/Source/WorkPool/Functions/UserAchievementLimitTime_x6.py
# game/Source/WorkPool/Functions/UserActivityCoinCopy.py
# game/Source/WorkPool/Functions/UserActivityExpDanCopy.py
# game/Source/WorkPool/Functions/UserActivityForgeStoneCopy.py
# game/Source/WorkPool/Functions/UserAthleticsAttack.py
# game/Source/WorkPool/Functions/UserAthleticsAttack2.py
# game/Source/WorkPool/Functions/UserAthleticsBoss.py
# game/Source/WorkPool/Functions/UserConsumeGiftX3.py
# game/Source/WorkPool/Functions/UserConsumeGiftX4.py
# game/Source/WorkPool/Functions/UserConsumeGiftX5.py
# game/Source/WorkPool/Functions/UserConsumeGiftX6.py
# game/Source/WorkPool/Functions/UserConsumeGiftX7.py
# game/Source/WorkPool/Functions/UserConsumeGiftX8.py
# game/Source/WorkPool/Functions/UserCopyAttack22.py
# game/Source/WorkPool/Functions/UserCopyModUp2.py
# game/Source/WorkPool/Functions/UserDayDayGift_x6.py
# game/Source/WorkPool/Functions/UserDayDayGift_x7.py
# game/Source/WorkPool/Functions/UserFriendCopyAttack.py
# game/Source/WorkPool/Functions/UserGeneralCopyAttack.py
# game/Source/WorkPool/Functions/UserGodDownQuery_x7.py
# game/Source/WorkPool/Functions/UserGodDownQuery_x8.py
# game/Source/WorkPool/Functions/UserHint.py
# game/Source/WorkPool/Functions/UserKingManBattle.py
# game/Source/WorkPool/Functions/UserMieshendianReset.py
# game/Source/WorkPool/Functions/UserOldDriver_x6.py
# game/Source/WorkPool/Functions/UserOldDriver_x7.py
# game/Source/WorkPool/Functions/UserOverPassBattle.py
# game/Source/WorkPool/Functions/UserPenglai3Dice.py
# game/Source/WorkPool/Functions/UserRechargeGift_x6.py
# game/Source/WorkPool/Functions/UserRechargeGift_x7.py
# game/Source/WorkPool/Functions/UserRecruit2General.py
# game/Source/WorkPool/Functions/UserSingleRechargeGift_x6.py
# game/Source/WorkPool/Functions/UserSingleRechargeGift_x7.py
# game/Source/WorkPool/Functions/UserSoulHunt.py
# game/Source/WorkPool/Functions/UserSpinampWin_x6.py
# game/Source/WorkPool/Functions/UserSpinampWin_x7.py
# game/Source/WorkPool/Functions/UserTreasureFragmentRob.py
# game/Source/WorkPool/Functions/UserTrialBattle.py
# game/Source/GameConfig/GameConfigVars.py
# game/Source/GameOperation/TopOfWorld/CheckTOWTypeTask.py
# game/Source/WorkPool/Functions/UserTopOfWorldQuery.py           # 此文件需要找磊哥确认
# game/Source/WorkPool/Functions/UserTopOfWorldReward.py
# game/Source/WSGI/Test/TestActivity.py
# game/Source/WSGI/Test/TestManage.py
# game/Source/GameOperation/General/GeneralFosterPreview2.py
# game/Source/GameOperation/Props/CheckProps.py
# game/Source/WorkPool/Functions/UserGeneralFosterFree.py
#
#
# game/Source/GameOperation/Battle25/Battle.py
# game/Source/GameOperation/Battle25/Break/break_9000336.py
# game/Source/GameOperation/Battle25/Break/break_9000316.py
#
# # 扩展
# ext/Source/GameOperation/Battle25/Battle.py
# ext/Source/GameOperation/Battle25/Break/break_9000316.py
# ext/Source/GameOperation/Battle25/Break/break_9000336.py
# # 跨服
# worldwar/Source/GameOperation/Battle25/Battle.py
# worldwar/Source/GameOperation/Battle25/Break/break_9000316.py
# worldwar/Source/GameOperation/Battle25/Break/break_9000336.py