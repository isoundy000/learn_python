#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3
import time
import json
import random
import hashlib
from datetime import datetime

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.util import strutil, webpage
from poker.protocol import router
from poker.entity.biz import bireport
from poker.entity.dao import userdata, gamedata, daobase
from poker.entity.configure import gdata
from poker.entity.game.rooms import roominfo
from poker.entity.events import hall51event
from poker.entity.configure import configure
import poker.util.timestamp as pktimestamp
from poker.entity.dao import sessiondata, userchip, onlinedata
from poker.util.constants import CLIENT_SYS_ANDROID, CLIENT_SYS_IOS
from hall.entity import hallitem, hallvip, datachangenotify
from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
from newfish.entity import config, weakdata, keywords
from newfish.entity.redis_keys import GameData, WeakData, UserData, ABTestData
from newfish.entity.config import FISH_GAMEID, \
    CHIP_KINDID, COUPON_KINDID, STARFISH_KINDID, SILVER_BULLET_KINDID, \
    GOLD_BULLET_KINDID, BRONZE_BULLET_KINDID, DIAMOND_KINDID
from newfish.entity.event import BulletChangeEvent,\
    StarfishChangeEvent, AddGunSkinEvent, NewSkillEvent, ItemMonitorEvent, \
    ItemChangeEvent, SkillItemCountChangeEvent, GunItemCountChangeEvent
from newfish.entity import module_tip
from newfish.servers.util.rpc import user_rpc


_CHATLOGER = None


def getClientId(userId):
    """
    获得客户端标识
    """
    if userId < 10000:
        clientId = config.CLIENTID_ROBOT
    else:
        clientId = sessiondata.getClientId(userId)
    return clientId


def getLanguage(userId, clientId=None):
    """
    获取玩家手机语言
    """
    clientId = clientId or getClientId(userId)
    if clientId and config.getPublic("multipleLangClientIds", []):
        lang = userdata.getAttr(userId, "lang")
        if lang and not str(lang).startswith("zh"):
            return "en"
    return "zh"


def verifyPhoneNumber(phoneNumber):
    """
    验证手机号是否合法
    """
    import re
    pattern = re.compile(r"^[1]([3-9])[0-9]{9}$")
    if pattern.search(str(phoneNumber)):
        return True
    return False


def getGunX(wpId, mode):
    """
    获取炮台的倍数(经典模式为1:千炮为炮台倍数)
    """
    gunX = 1 if mode != config.MULTIPLE_MODE else config.getGunLevelConf(wpId, mode).get("levelValue", 1)
    return gunX


def isFinishAllRedTask(userId):
    """
    获得所有已完成的引导
    """
    userGuideStep = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.userGuideStep, [])
    return userGuideStep


def timestampToStr(timestamp, formatTime="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转字符串
    """
    return time.strftime(formatTime, time.localtime(timestamp))


def getDayStartTimestamp(timestamp):
    """
    获取0点时间戳
    """
    ts = int(timestamp - time.timezone) / 86400 * 86400 + time.timezone
    # dayStr = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    # t = time.strptime(dayStr, "%Y-%m-%d")
    # t1 = int(time.mktime(t))
    # if t1 != ts:
    #     ftlog.debug("getDayStartTimestamp", timestamp, t1, ts)
    return ts


def getHourStartTimestamp(timestamp):
    """
    获取整点时间戳
    """
    dt = datetime.fromtimestamp(timestamp).replace(minute=0, second=0, microsecond=0)
    return int(time.mktime(dt.timetuple()))


def getTodayTimestampFromStr(strTime, formatTime="%Y-%m-%d %H:%M"):
    """
    获取当天任意时间点时间戳(strTime格式"%H:%M:%S")
    """
    dayStr = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    strTime = dayStr + " " + strTime
    timeArray = time.strptime(strTime, formatTime)
    return int(time.mktime(timeArray))


def getTimeDescStrFromStr(timeStr, formatTime="%Y年%m月%d日"):
    """
    获取时间的文本描述形式
    :param timeStr:2018-09-29 00:00:00
    """
    intTime = getTimestampFromStr(timeStr)
    return timestampToStr(intTime, formatTime)


def timeStrToInt(strTime):
    """
    "xx:xx"转成对应秒数
    """
    sendTimeArr = strTime.split(":")
    intTime = int(sendTimeArr[0]) * 3600 + int(sendTimeArr[1]) * 60
    return intTime


def formatScore(score, lang="zh"):
    """
    格式化数字
    """
    if lang == "zh":
        l = [
            (100000000, "亿", 2),
            (10000, "万", 2)
        ]
        condition = score >= 100000
    else:
        l = [
            (100000000, "B", 2),
            (1000000, "M", 2),
            (1000, "K", 2)
        ]
        condition = score >= 10000
    if condition:
        for divisor, units, ndigits in l:
            if score >= divisor:
                unitsScore = round(score / float(divisor), ndigits)
                fmt = "%d%s" if unitsScore == int(unitsScore) else "%%.%sf%%s" % (ndigits)
                return fmt % (unitsScore, units)
    return str(score)


def getNickname(userId):
    """
    获取玩家昵称
    """
    nickname = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.nickname)
    if not nickname:
        nickname = userdata.getAttr(userId, "name")
    nickname = str(nickname) if nickname else ""
    return keywords.replace(nickname)


def isVipShow(userId):
    """
    判断是否显示VIP
    """
    vipShow = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.vipShow)
    return vipShow


def getVipShowLevel(userId):
    """
    获得VIP显示等级
    """
    if isVipShow(userId) == 0:
        return 0
    return hallvip.userVipSystem.getUserVip(userId).vipLevel.level


def getWeaponType(wpId):
    """
    获得武器类型
    """
    if isinstance(wpId, int):
        if wpId // 100 == 21:
            return config.GUN_WEAPON_TYPE
        elif wpId // 100 == 22: # 技能
            return config.SKILL_WEAPON_TYPE
        elif wpId == 2301:      # 机器人开火
            return config.RB_FIRE_WEAPON_TYPE
        elif wpId == 2302:      # 机器人爆炸
            return config.RB_BOMB_WEAPON_TYPE
        elif wpId // 100 == 24: # 炸弹鱼爆炸
            return config.BOMB_WEAPON_TYPE
        elif wpId // 100 == 25: # 招财模式火炮
            return config.ROBBERY_WEAPON_TYPE
        elif wpId // 100 == 27: # 电鳗死亡
            return config.NUMB_WEAPON_TYPE
        elif wpId // 100 == 28: # 钻头鱼死亡
            return config.DRILL_WEAPON_TYPE
        elif wpId // 100 == 29: # 超级boss:宝箱怪,龙女王,大冰龙
            return config.SUPERBOSS_WEAPON_TYPE
    return 0


def getSeedRandom(seed, min=1, max=10000):
    """
    获得前后端统一随机数种子
    """
    seed = (int(seed) * 9301 + 49297) % 233280
    rand = seed / 233279.0
    return int(min + rand * (max - min))


def balanceItem(userId, kindId):
    """
    获得道具数量
    """
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(kindId), pktimestamp.getCurrentTimestamp())
    return surplusCount


def consumeItems(userId, items, eventId, intEventParam=0, param01=0, param02=0):
    """
    消耗多个道具
    :param userId:
    :param items: 需要消耗的道具列表
    :param eventId: BI事件ID
    :param intEventParam: BI事件参数（必须为int型）
    :param param01: BI事件扩展参数（任意可序列化类型）
    :param param02: BI事件扩展参数（任意可序列化类型）
    """
    assert isinstance(items, list)
    ret = []
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    for item in items:
        kindId = item["name"]
        count = item["count"]
        assetKind, consumeCount, final = userAssets.consumeAsset(FISH_GAMEID, "item:" + str(kindId), count,
                                 pktimestamp.getCurrentTimestamp(), str(eventId),
                                 intEventParam, param01=param01, param02=param02)
        if consumeCount == item["count"]:
            ret.append((assetKind, consumeCount, final))

    isUpSkillItem = False
    isUpGunItem = False
    changedItems = []
    from newfish.game import TGFish
    for assetKind, consumeCount, final in ret:
        changedItems.append({"name": assetKind.kindId, "count": final, "delta": -abs(consumeCount)})
        if assetKind.kindId in config.upgradeSkillKindIds:
            isUpSkillItem = True
        if assetKind.kindId in config.upgradeGunKindIds:
            isUpGunItem = True
    
    if isUpSkillItem:       # 存在技能升级所需物品
        event = SkillItemCountChangeEvent(userId, FISH_GAMEID)
        TGFish.getEventBus().publishEvent(event)
    if isUpGunItem:     # 存在普通炮升级所需物品
        event = GunItemCountChangeEvent(userId, FISH_GAMEID)
        TGFish.getEventBus().publishEvent(event)
    if changedItems:
        changed = {"items": changedItems}
        event = ItemMonitorEvent(userId, FISH_GAMEID, changed, eventId)
        TGFish.getEventBus().publishEvent(event)
    if ret:
        datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["chip", "item"])
    return ret


def addItems(userId, gain, eventId, intEventParam=0, roomId=0, tableId=0, clientId=None,
             type=0, param01=0, param02=0, changeNotify=False):
    """
    添加物品通用方法
    :param userId:
    :param gain: 需要改变的物品列表
    :param eventId: BI事件ID
    :param intEventParam: BI事件参数（必须为int型）
    :param roomId:
    :param tableId:
    :param clientId:
    :param type: 0：渔场外 1：渔场内
    :param param01: BI事件扩展参数（任意可序列化类型）
    :param param02: BI事件扩展参数（任意可序列化类型）
    :param changeNotify: 是否立即通知客户端刷新玩家资产数据
    :return: 改变内容
    """
    ud = []     # 用户获得
    gd = []     # 游戏获得
    return {}


def addRewards(userId, rewards, eventId, intEventParam=0, param01=0, param02=0, tableId=0, roomId=0):
    """
    添加奖励并立即刷新数据
    """

    return 0
        

def getAssetKindId(kindId):
    """
    通过kindId获得assetKindId
    """
    return config.customKindIdMap.get(kindId) or "item:%d" % kindId


def getGunLevel(userId, mode):
    """
    获取火炮等级索引(21xx)
    """
    gunLevelKey = GameData.gunLevel if mode == config.CLASSIC_MODE else GameData.gunLevel_m
    gunLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, gunLevelKey)
    return gunLevel


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getGunLevelVal(userId, mode):
    """
    获取火炮等级/倍率
    """
    gunLevel = getGunLevel(userId, mode)
    return config.getGunLevelConf(gunLevel, mode).get("levelValue", 1)


def isInFishTable(userId):
    """
    判断用户是否在渔场中
    """
    isIn = False
    roomId, tableId, seatId = 0, 0, 0
    locList = onlinedata.getOnlineLocList(userId)
    for roomId, tableId, seatId in locList:
        try:
            roomGameId = strutil.getGameIdFromInstanceRoomId(roomId)
            if (roomGameId == FISH_GAMEID and tableId != 0 and seatId != 0):
                isIn = True
                break
        except:
            pass
    return isIn, roomId, tableId, seatId