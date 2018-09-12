# -*- encoding: utf-8 -*-
'''
Created on 2018年9月7日

@author: houguangdong
'''

# hot_blood/source999999/SanguoGame/Source/DataBase/Table/t_daoguan.py
# hot_blood/source999999/SanguoGame/Source/DataBase/Table/t_daoguan_record.py
# hot_blood/source999999/SanguoGame/Source/DataBase/Table/t_daoguan_user.py
# hot_blood/source999999/SanguoGame/Source/DataBase/Table/t_protagonist.py
# hot_blood/source999999/SanguoGame/Source/GameConfig/GameConfigManager2.py
# hot_blood/source999999/SanguoGame/Source/GameData/DaoGuan.py
# hot_blood/source999999/SanguoGame/Source/GameData/GameData.py
# hot_blood/source999999/SanguoGame/Source/GameData/GameDataManager.py
# hot_blood/source999999/SanguoGame/Source/GameData/global_kv.py
# hot_blood/source999999/SanguoGame/Source/GameData/global_kv_opt.py
# hot_blood/source999999/SanguoGame/Source/GameData/i18n.py
# hot_blood/source999999/SanguoGame/Source/GameOperation/Battle25/Position.py
# hot_blood/source999999/SanguoGame/Source/GameOperation/Battle25/FighterInOut.py
# hot_blood/source999999/SanguoGame/Source/GameOperation/Battle25/PetInOut.py
# hot_blood/source999999/SanguoGame/Source/GameOperation/Battle25/PositionInOut.py
# hot_blood/source999999/SanguoGame/Source/GameOperation/General/GeneralFosterPreview2.py
# hot_blood/source999999/SanguoGame/Source/Timer/Config/Config.py
# hot_blood/source999999/SanguoGame/Source/Timer/Exact/Daoguan.py
# hot_blood/source999999/SanguoGame/Source/UserData/UserDataConfig.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/Config.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/UserBuyStamina.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/UserDaoGuan.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/UserGeneralFosterFree.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/UserProtagonist.py
# hot_blood/source999999/SanguoGame/Source/WorkPool/Functions/UserShowWing.py
# hot_blood/source999999/SanguoGame/Source/WSGI/Test/DaoGuanDayClear.py
# hot_blood/source999999/SanguoGame/Source/WSGI/Test/RechargeReturnTest.py
#
# hot_blood/source999999/SanguoGameExt/Source/GameOperation/Battle25/FighterInOut.py
# hot_blood/source999999/SanguoGameExt/Source/GameOperation/Battle25/PetInOut.py
# hot_blood/source999999/SanguoGameExt/Source/GameOperation/Battle25/Position.py
# hot_blood/source999999/SanguoGameExt/Source/GameOperation/Battle25/PositionInOut.py
#



# 越南更新
# set names utf8;
# alter table t_protagonist add column `wing_show` tinyint(1) unsigned NOT NULL DEFAULT '1';
#
#  CREATE TABLE `t_daoguan_record` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `daoguanId` int(11) NOT NULL DEFAULT '0',
#   `index` int(11) NOT NULL DEFAULT '0',
#   `rid1` int(11) NOT NULL,
#   `name1` varchar(32) DEFAULT NULL,
#   `rid2` int(11) NOT NULL,
#   `name2` varchar(32) DEFAULT NULL,
#   `rs` int(11) NOT NULL DEFAULT '0',
#   `time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
#   `content` varchar(128) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `daoguanId` (`daoguanId`),
#   KEY `rid1` (`rid1`),
#   KEY `rid2` (`rid2`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# CREATE TABLE `t_daoguan_user` (
#   `rid` int(11) NOT NULL,
#   `times` int(11) NOT NULL DEFAULT '0',
#   `recoverTime` timestamp NULL DEFAULT NULL,
#   `daoguanId` int(11) NOT NULL DEFAULT '0',
#   `index` int(11) NOT NULL DEFAULT '0',
#   `award` int(11) NOT NULL DEFAULT '0',
#   `hz1` int(11) NOT NULL DEFAULT '0',
#   `hz2` int(11) NOT NULL DEFAULT '0',
#   `hz3` int(11) NOT NULL DEFAULT '0',
#   `sta` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
#
# CREATE TABLE `t_daoguan` (
#   `id` int(11) NOT NULL,
#   `index` int(11) NOT NULL,
#   `rid` int(11) NOT NULL,
#   `name` varchar(32) DEFAULT NULL,
#   `power` int(11) NOT NULL DEFAULT '0',
#   `profile` int(11) NOT NULL DEFAULT '0',
#   `wing_level1` int(11) NOT NULL DEFAULT '0',
#   `wing_color` int(11) NOT NULL DEFAULT '0',
#   `gang_id` int(11) NOT NULL DEFAULT '0',
#   `gang_name` varchar(32) DEFAULT NULL,
#   `position` text,
#   `hp1` int(11) NOT NULL DEFAULT '100',
#   `hp2` int(11) NOT NULL DEFAULT '100',
#   `hp3` int(11) NOT NULL DEFAULT '100',
#   `hp4` int(11) NOT NULL DEFAULT '100',
#   `hp5` int(11) NOT NULL DEFAULT '100',
#   `hp6` int(11) NOT NULL DEFAULT '100',
#   `hp7` int(11) NOT NULL DEFAULT '100',
#   PRIMARY KEY (`id`,`index`),
#   KEY `rid` (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
# alter table t_role_groundhog add column `box6` enum('no','yes','get') NOT NULL DEFAULT 'no';
#
# CREATE TABLE `t_god_general` (
#   `rid` int(11) NOT NULL,
#   `point` int(11) NOT NULL DEFAULT '0',
#   `p1` int(11) NOT NULL DEFAULT '0',
#   `p2` int(11) NOT NULL DEFAULT '0',
#   `p3` int(11) NOT NULL DEFAULT '0',
#   `p4` int(11) NOT NULL DEFAULT '0',
#   `p5` int(11) NOT NULL DEFAULT '0',
#   `p6` int(11) NOT NULL DEFAULT '0',
#   `p7` int(11) NOT NULL DEFAULT '0',
#   `p8` int(11) NOT NULL DEFAULT '0',
#   `p9` int(11) NOT NULL DEFAULT '0',
#   `p10` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
# CREATE TABLE `t_legendary` (
#   `rid` int(11) NOT NULL,
#   `count` int(11) NOT NULL DEFAULT '0',
#   `k1` int(11) NOT NULL DEFAULT '0',
#   `i1` int(11) NOT NULL DEFAULT '0',
#   `k2` int(11) NOT NULL DEFAULT '0',
#   `i2` int(11) NOT NULL DEFAULT '0',
#   `k3` int(11) NOT NULL DEFAULT '0',
#   `i3` int(11) NOT NULL DEFAULT '0',
#   `k4` int(11) NOT NULL DEFAULT '0',
#   `i4` int(11) NOT NULL DEFAULT '0',
#   `k5` int(11) NOT NULL DEFAULT '0',
#   `i5` int(11) NOT NULL DEFAULT '0',
#   `k6` int(11) NOT NULL DEFAULT '0',
#   `i6` int(11) NOT NULL DEFAULT '0',
#   `k7` int(11) NOT NULL DEFAULT '0',
#   `i7` int(11) NOT NULL DEFAULT '0',
#   `k8` int(11) NOT NULL DEFAULT '0',
#   `i8` int(11) NOT NULL DEFAULT '0',
#   `k9` int(11) NOT NULL DEFAULT '0',
#   `i9` int(11) NOT NULL DEFAULT '0',
#   `k10` int(11) NOT NULL DEFAULT '0',
#   `i10` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`rid`)
# ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
#
# CREATE TABLE `t_reward_record` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `bid` int(11) NOT NULL,
#   `mid` int(11) NOT NULL DEFAULT '1',
#   `name` varchar(128) NOT NULL,
#   `cid` int(11) NOT NULL DEFAULT '0',
#   `num` int(11) NOT NULL DEFAULT '0',
#   `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   `c1` int(11) NOT NULL DEFAULT '0',
#   `c2` int(11) NOT NULL DEFAULT '0',
#   `c3` int(11) NOT NULL DEFAULT '0',
#   `c4` int(11) NOT NULL DEFAULT '0',
#   `c5` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`id`,`bid`,`mid`)
# ) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
#
# CREATE TABLE `t_turntable_record` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `rid` int(11) NOT NULL,
#   `name` varchar(128) NOT NULL,
#   `gold` int(11) NOT NULL DEFAULT '0',
#   `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   `c1` int(11) NOT NULL DEFAULT '0',
#   `c2` int(11) NOT NULL DEFAULT '0',
#   `c3` int(11) NOT NULL DEFAULT '0',
#   `c4` int(11) NOT NULL DEFAULT '0',
#   `c5` int(11) NOT NULL DEFAULT '0',
#   `c6` int(11) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`id`)
# ) ENGINE=MyISAM  DEFAULT CHARSET=utf8;