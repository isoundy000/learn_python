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
#
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