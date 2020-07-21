#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30

import random
import math

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
import poker.util.timestamp as pktimestamp
from poker.entity.biz import bireport
from poker.entity.dao import userchip, gamedata
from hall.entity import hallitem
from hall.entity.hallitem import TYOpenItemEvent
from hall.entity.hallitem import TYChestItem
from newfish.entity import config, util, module_tip
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData
from newfish.entity.skill import skill_system
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, \
     CHIP_KINDID, COUPON_KINDID, STARFISH_KINDID, SKILLCD_KINDID, \
    BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, RUBY_KINDID


# 宝箱栏最大数量
CHEST_NUMBER_LIMIT = 4


# 宝箱开启倒计时延时
CHEST_OPEN_DELAY_TIME = 0


# 宝箱ID前缀与大厅道具ID对应表
chestKindIdMap = {
    31: 1138,
    32: 1139,
    33: 1140,
    34: 1141,
    35: 1142,
    36: 1143,
    37: 1144
}


class ItemType:
    """
    宝箱物品类型
    """
    Skill = 1                       # 技能卡
    Star = 2                        # 升星卡
    GunSkin = 3                     # 皮肤炮
    Crystal = 4                     # (黄/紫)水晶


class ChestState:
    """
    宝箱状态
    """
    WaitOpen = 0                    # 等待开启
    Opening = 1                     # 开启倒计时中
    Opened = 2                      # 可以开启


class ChestAction:
    """
    宝箱执行行为
    """
    NormalOpen = 0  # 普通开启
    AtOnceOpen = 1  # 立即开启
    Discard = 2     # 丢弃


class ChestFromType:
    # 宝箱来源
    Share_Chest_Fish = 0            # 分享宝箱鱼
    Fly_Pig_Chest = 1               # 飞猪宝箱
    Cmptt_Ncmptt_Bonus_Task = 2     # 渔场比赛获得
    Daily_Quest_Week_Chest = 3      # 每日任务周宝箱
    Daily_Quest_Daily_Chest = 4     # 每日任务每日宝箱


def newChestItem(userId, chestId, eventId, intEventParam=0):
    """
    生成一个宝箱
    """
    idleOrder = getChestIdleOrder(userId)
    if idleOrder < 0:
        ftlog.debug("newChestItem-> not idle order", userId)
        return False
    kindId = chestKindIdMap.get(chestId // 1000, 0)
    if not kindId:
        ftlog.error("newChestItem-> chestId error", chestId, userId)
        return False
    pass
    return True



def getChestIdleOrder(userId):
    """
    得到空闲的宝箱栏位置
    """




    return -1


def getChestRewards(userId, chestId):
    """
    获取宝箱物品
    """
    rewards = []
    return rewards



def initialize():
    pass