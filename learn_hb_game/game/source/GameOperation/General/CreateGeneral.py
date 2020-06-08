#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.DataBase.Table.t_general4 import t_general4
from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.UserData.UserDataManager import UserDataManager
from Source.Log.Write import Log
import traceback


def CreateGeneral(roleid, generalcid, general, roledata):
    '''
    武将的出生
    :param roleid:
    :param generalcid:
    :param general:
    :param roledata:
    :return:
    '''
    general.cid = generalcid
    general.rid = roleid
    general.level1 = 1
    general.level2 = 0
    general.level3 = 0
    general.level4 = 0
    general.exp = 0
    general.hp_foster = 0
    general.atk_foster = 0
    general.def_foster = 0
    general.Init()
    generalConfig = general.config
    general.bhp = generalConfig["hp"]
    general.batk = generalConfig["atk"]
    general.bdef = generalConfig["def"]
    general.bspeed = generalConfig["speed"]
    general.bcritical = generalConfig["critical"]
    general.bdodge = generalConfig["dodge"]
    general.bparry = generalConfig["parry"]

    general_train = GameConfigManager.Data()["general_train"]
    tag = "train" + str(generalConfig["basic"])
    if tag in general_train["1"]:
        general.potential = general_train["1"][tag]
    else:
        general.potential = 0
    general.skillexp = 0
    general.skilllevel = 0

    # general.Init()

    try:
        general.role_obj = roledata["role"]
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())
    general.ComputeAttr()