# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

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
    ItemChangeEvent, SkillItemCountChangeEvent, GunItemCountChangeEvent, TreasureItemCountChangeEvent, \
    ConsumeVoucherEvent
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


def getClientIdVer(userId):
    """
    获得客户端标识版本
    """
    if userId < 10000:
        clientIdVer = config.CLIENT_VERSION_ROBOT
    else:
        clientIdVer = sessiondata.getClientIdVer(userId)
    return clientIdVer


def getClientIdNum(userId, clientId=None):
    """
    获得客户端数字标识
    """
    clientId = clientId or getClientId(userId)
    return sessiondata.getClientIdNum(userId, clientId)[1]


def getClientIdSys(userId):
    """
    获得客户端运行系统
    """
    clientOs = sessiondata.getClientIdSys(userId)
    return clientOs.lower()


def isAppClient(userId):
    """
    判断是否为单包客户端
    """
    clientId = getClientId(userId).lower()
    return clientId.startswith(CLIENT_SYS_ANDROID.lower()) or clientId.startswith(CLIENT_SYS_IOS.lower())
    # return getClientIdSys(userId) in [CLIENT_SYS_ANDROID.lower(), CLIENT_SYS_IOS.lower()]


def isChannel(userId, channel):
    """
    客户端是否为指定渠道
    """
    return sessiondata.getClientIdMainChannel(getClientId(userId)) == channel


def isReviewLimitClient(userId):
    """
    是否为提审限制版本的客户端
    """
    intClientId = configure.clientIdToNumber(getClientId(userId))
    return intClientId in config.getCommonValueByKey("reviewLimitClientIds", [])


def getReviewVersionList(userId):
    """
    获取review版本号列表
    """
    reviewClientVersion = []
    # 单包和白名单用户不受提审版本限制.
    if isInWhiteList(userId) or (not isReviewLimitClient(userId)):
        return reviewClientVersion
    reviewClientVersion = config.getPublic("reviewClientVersion", [])
    return reviewClientVersion


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


def getFishPoolByBigRoomId(bigRoomId):
    """
    根据bigRoomId获取渔场id FishPool
    """
    if bigRoomId == 44499:
        return 44001
    elif 44405 >= bigRoomId >= 44401:       # [44001, 44002, ... 44005]
        return 44000 + bigRoomId % 44400
    else:
        return bigRoomId


def itemListTransfer(items):
    """把道具奖励转化一下"""
    ret = {}
    for item in items:
        if item["name"] == "tableChip":
            ret["tableChip"] = item["count"]
        else:
            ret[item["name"]] = item["count"]
    return ret


def hasChip(items):
    """道具中是否有金币奖励"""
    itemNames = [x["name"] for x in items]
    if "user:chip" in itemNames:
        return True
    return False


def getChip(items):
    """获取配置道具奖励中的金币数"""
    hasChip = False
    chipFinal = 0
    for item in items:
        if item["name"] == "user:chip":
            chipFinal = item["count"]
            hasChip = True
            break
    return hasChip, chipFinal


def getRoomTypeName(roomId):
    """获取房间名"""
    if not roomId:
        return ""
    bigRoomId = gdata.getBigRoomId(roomId)
    return gdata.getRoomConfigure(bigRoomId).get("typeName")


def getBigRoomId(roomId):
    """获取大房间和是否是比赛房间"""
    if not roomId:
        return 0, 0
    bigRoomId = gdata.getBigRoomId(roomId)
    typeName = gdata.getRoomConfigure(bigRoomId).get("typeName")
    isMatch = 0
    if typeName in [config.FISH_TIME_MATCH, config.FISH_TIME_POINT_MATCH]:
        isMatch = 1
    return bigRoomId, isMatch


def getWeek1DateStr(nowts):
    """
    获取周一时间戳
    """
    week = int(time.strftime("%w", time.localtime(nowts)))
    if week == 0:
        week = 7
    week1 = time.strftime("%Y-%m-%d", time.localtime(nowts - (int(week) - 1) * 3600 * 24))
    return week1


def getWeek7DateStr(nowts):
    """
    获取周日时间戳
    """
    week = int(time.strftime("%w", time.localtime(nowts)))
    if week == 0:
        week = 7
    week7 = time.strftime("%Y-%m-%d", time.localtime(nowts + (7 - int(week)) * 3600 * 24))
    return week7


def getWeekDay(nowts):
    """
    获取是周几
    """
    week = int(time.strftime("%w", time.localtime(nowts)))
    if week == 0:
        return 7
    return week


def isTimeEffective(timeMap, curTime=None):
    """
    判断当前时间是否处在有效期内
    :param curTime: "%Y-%m-%d %H:%M:%S"
    """
    if not timeMap or not isinstance(timeMap, dict):
        return True
    curTime = curTime or int(time.time())
    startTime = getTimestampFromStr(timeMap["start"])
    endTime = getTimestampFromStr(timeMap["end"])
    if startTime <= curTime <= endTime:
        return True
    return False


def getTimestampFromStr(strTime, formatTime="%Y-%m-%d %H:%M:%S"):
    """
    字符串转时间戳
    """
    isDefaultFormat = (formatTime == "%Y-%m-%d %H:%M:%S")
    global _timeStampFromStrCache
    if isDefaultFormat and strTime in _timeStampFromStrCache:
        return _timeStampFromStrCache[strTime]
    timeArray = time.strptime(strTime, formatTime)
    ts = int(time.mktime(timeArray))
    if isDefaultFormat:
        if len(_timeStampFromStrCache) > 200:
            _timeStampFromStrCache.clear()
        _timeStampFromStrCache[strTime] = ts
    return ts


def timestampToStr(timestamp, formatTime="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转字符串
    """
    return time.strftime(formatTime, time.localtime(timestamp))


def getDayStartTimestamp(timestamp=None):
    """
    获取0点时间戳
    """
    if timestamp is None:
        timestamp = time.time()
    ts = int(timestamp - time.timezone) / 86400 * 86400 + time.timezone
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


def getWeaponType(wpId):
    """
    获得武器类型
    """
    if isinstance(wpId, int):
        if wpId // 100 == 21:       # 火炮
            return config.GUN_WEAPON_TYPE
        elif wpId // 100 == 22:     # 技能
            return config.SKILL_WEAPON_TYPE
        elif wpId == 2301:          # 机器人开火
            return config.RB_FIRE_WEAPON_TYPE
        elif wpId == 2302:          # 机器人爆炸
            return config.RB_BOMB_WEAPON_TYPE
        elif wpId // 100 == 24:     # 炸弹鱼爆炸
            return config.BOMB_WEAPON_TYPE
        elif wpId // 100 == 25:     # 招财模式火炮
            return config.ROBBERY_WEAPON_TYPE
        elif wpId // 100 == 27:     # 电鳗死亡
            return config.NUMB_WEAPON_TYPE
        elif wpId // 100 == 28:     # 钻头鱼死亡
            return config.DRILL_WEAPON_TYPE
        elif wpId // 100 in [29, 30, 31]:   # 超级Boss（宝箱怪、龙女王、大冰龙）
            return config.SUPER_BOSS_WEAPON_TYPE
        elif wpId // 100 == 32:     # 能量宝珠
            return config.ENERGY_ORB
        elif wpId // 100 == 33:     # 三叉戟
            return config.TRIDENT
        elif wpId // 100 == 34:     # 金钱箱
            return config.MONEY_BOX
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
    try:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        for item in items:
            kindId = item["name"]
            count = item["count"]
            _, consumeCount, final = userAssets.consumeAsset(FISH_GAMEID, "item:" + str(kindId), count,
                                                             pktimestamp.getCurrentTimestamp(), str(eventId),
                                                             intEventParam, param01=param01, param02=param02)
            if consumeCount == item["count"]:
                ret.append((kindId, consumeCount, final))

        isUpSkillItem = False
        isUpGunItem = False
        isUpTreasure = False
        voucherCount = 0
        changedItems = []
        from newfish.game import TGFish
        for kindId, consumeCount, final in ret:
            changedItems.append({"name": kindId, "count": final, "delta": -abs(consumeCount)})
            if kindId in config.upgradeSkillKindIds:
                isUpSkillItem = True
            if kindId in config.upgradeGunKindIds:
                isUpGunItem = True
            if kindId in config.upgradeTreasureKindIds:
                isUpTreasure = True
            if kindId == config.VOUCHER_KINDID:
                voucherCount += consumeCount

        if isUpSkillItem:   # 存在技能升级所需物品
            event = SkillItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if isUpGunItem:     # 存在普通炮升级所需物品
            event = GunItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if isUpTreasure:    # 存在宝藏升级所需物品
            event = TreasureItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if voucherCount > 0:
            event = ConsumeVoucherEvent(userId, FISH_GAMEID, voucherCount)
            TGFish.getEventBus().publishEvent(event)
        if changedItems:
            changed = {"items": changedItems}
            event = ItemMonitorEvent(userId, FISH_GAMEID, changed, eventId)
            TGFish.getEventBus().publishEvent(event)
        if ret:
            datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["chip", "item"])
    except Exception as e:
        ftlog.error("consumeItems error", userId, items, eventId, intEventParam, param01, param02, e)
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
    items = []
    # 竞赛积分，只用于处理addRewards逻辑以免返回错误占位使用!
    compPoints = []
    try:
        if not clientId:
            clientId = getClientId(userId)
        for item in gain:
            count = item["count"]
            assetKindId = item["name"]
            if assetKindId == "tableChip" or assetKindId == "bulletChip" or assetKindId == CHIP_KINDID:
                if type == 0:
                    # 对用户的金币进行INCR操作
                    delta, finalChip = userchip.incrChip(userId, FISH_GAMEID, count, 0,
                                                         eventId, intEventParam, clientId, roomId=roomId,
                                                         tableId=tableId, param01=param01, param02=param02)
                    ud.append({"name": "chip", "count": finalChip, "delta": delta})
                else:
                    # 用户的tablechip进行INCR操作
                    delta, finalChip = userchip.incrTableChip(userId, FISH_GAMEID, count, 1,
                                                              eventId, intEventParam, clientId, tableId,
                                                              roomId=roomId, param01=param01, param02=param02)
                    ud.append({"name": "tableChip", "count": finalChip, "delta": delta})
                if delta != count:
                    ud = []
                    if type != 0:
                        ftlog.error("addItemsErrorLog add user chip error,", userId, eventId, count, delta)
            elif assetKindId == COUPON_KINDID:          # 增加奖券
                delta, finalCoupon = userchip.incrCoupon(userId, FISH_GAMEID, count, 0,
                                                         eventId, intEventParam, clientId, roomId=roomId,
                                                         tableId=tableId, param01=param01, param02=param02)
                if delta == count:
                    ud.append({"name": "coupon", "count": finalCoupon, "delta": delta})
                else:
                    ftlog.error("addItemsErrorLog add user coupon error,", userId, eventId, count, delta)
            elif assetKindId == DIAMOND_KINDID:         # 增加钻石
                delta, finalDiamond = userchip.incrDiamond(userId, FISH_GAMEID, count, 0,
                                                         eventId, intEventParam, clientId, roomId=roomId,
                                                         tableId=tableId, param01=param01, param02=param02)
                if delta == count:
                    ud.append({"name": "diamond", "count": finalDiamond, "delta": delta})
                else:
                    ftlog.error("addItemsErrorLog add user diamond error,", userId, eventId, count, delta)
            # 竞赛活动积分道具
            elif assetKindId in config.COMP_ACT_POINT_KINDID_LIST:  # 竞赛活动积分
                from newfish.entity.fishactivity import competition_activity
                teamId = competition_activity._getCompTeamId(userId)
                if teamId >= 0 and count > 0:
                    compPoints.append(count)
                    competition_activity._addCompTeamPoint(userId, teamId, count)
                else:
                    ftlog.error("addItemsErrorLog add user comp act point error,", userId, eventId, count, teamId)
            else:
                from hall.entity import hallitem
                userAssets = hallitem.itemSystem.loadUserAssets(userId)
                timestamp = pktimestamp.getCurrentTimestamp()
                if ":" not in str(assetKindId):
                    assetKindId = "item:" + str(assetKindId)
                if count == 0:
                    continue
                if count > 0:
                    assetTuple = userAssets.addAsset(FISH_GAMEID, assetKindId, abs(count), timestamp,
                                                     eventId, intEventParam, roomId=roomId, tableId=tableId,
                                                     param01=param01, param02=param02)
                else:
                    assetTuple = userAssets.consumeAsset(FISH_GAMEID, assetKindId, abs(count), timestamp,
                                                         eventId, intEventParam, roomId=roomId, tableId=tableId,
                                                         param01=param01, param02=param02)

                assetKindId = int(assetKindId.split(":")[1])
                delta = assetTuple[1]
                if delta == abs(count):
                    items.append({"name": assetKindId, "count": assetTuple[2], "delta": count})
                else:
                    ftlog.error("addItemsErrorLog add user item error,", assetKindId, userId, count, delta)
    except Exception as e:
        ftlog.error("addItems error", userId, gain, eventId, intEventParam, e)
    changed = {}
    from newfish.game import TGFish
    if ud:
        changed["ud"] = ud
    if gd:
        changed["gd"] = gd
    if items:
        changed["items"] = items
        isUpSkillItem = False
        isUpGunItem = False
        isUpTreasure = False
        for item in items:
            if item["name"] in config.upgradeSkillKindIds:
                isUpSkillItem = True
            if item["name"] in config.upgradeGunKindIds:
                isUpGunItem = True
            if item["name"] in config.upgradeTreasureKindIds:
                isUpTreasure = True
        if isUpSkillItem:   # 存在技能升级所需物品
            event = SkillItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if isUpGunItem:     # 存在普通炮升级所需物品
            event = GunItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if isUpTreasure:    # 存在宝藏升级所需物品
            event = TreasureItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        # 道具监控
        event = ItemMonitorEvent(userId, FISH_GAMEID, changed, eventId)
        TGFish.getEventBus().publishEvent(event)

    # 资产/道具变化
    event = ItemChangeEvent(userId, FISH_GAMEID, gain, changed, type)
    TGFish.getEventBus().publishEvent(event)
    if compPoints:
        changed["compPoints"] = compPoints
    if changeNotify:
        datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["chip", "item"])
    return changed


def addRewards(userId, rewards, eventId, intEventParam=0, param01=0, param02=0, tableId=0, roomId=0):
    """
    添加奖励并立即刷新数据
    """
    clientId = getClientId(userId)
    from newfish.entity.skill import skill_system
    if not rewards:
        ftlog.error("addReward->not rewards", userId, rewards)
        return 4
    changed = addItems(userId, rewards, eventId, intEventParam, param01=param01, param02=param02, tableId=tableId, roomId=roomId)
    if not changed:
        ftlog.error("addReward->not changed", userId, rewards)
        return 5
    for item in rewards:
        kindId = dict(item)["name"]
        # if kindId in config.skillCardKindIdMap:                                 # 技能提示和事件
        #     skillId = config.skillCardKindIdMap[kindId]
        #     skill = skill_system.getSkill(userId, skillId)
        #     if skill[skill_system.INDEX_ORIGINAL_LEVEL] == 0:
                # skill_system.setSkill(userId, skillId, [1, 1, 1, 0])
                # from newfish.game import TGFish
                # event = NewSkillEvent(userId, FISH_GAMEID, skillId, eventId)
                # TGFish.getEventBus().publishEvent(event)
        if kindId in config.getAllGunIds(clientId, config.CLASSIC_MODE):      # 经典火炮的提示和事件
            from newfish.game import TGFish
            from newfish.entity.gun import gun_system
            event = AddGunSkinEvent(userId, FISH_GAMEID, kindId, int(item["count"]), intEventParam, config.CLASSIC_MODE)
            TGFish.getEventBus().publishEvent(event)
            gunIds = gun_system.getGunIds(userId, config.CLASSIC_MODE)
            if kindId not in gunIds:
                module_tip.addModuleTipEvent(userId, "gunskin", kindId)
        elif kindId in config.getAllGunIds(clientId, config.MULTIPLE_MODE):     # 千炮火炮的提示和事件
            from newfish.game import TGFish
            from newfish.entity.gun import gun_system
            event = AddGunSkinEvent(userId, FISH_GAMEID, kindId, int(item["count"]), intEventParam, config.MULTIPLE_MODE)
            TGFish.getEventBus().publishEvent(event)
            gunIds = gun_system.getGunIds(userId, config.MULTIPLE_MODE)
            if kindId not in gunIds:
                module_tip.addModuleTipEvent(userId, "gunskin", kindId)
        elif kindId in [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]:    # 青铜、白银、黄金招财珠
            from newfish.game import TGFish
            event = BulletChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        elif (kindId == STARFISH_KINDID and int(item["count"]) > 0 and
              eventId not in ["BI_NFISH_BUY_ITEM_GAIN", "BI_NFISH_ACTIVITY_REWARDS",
                              "BI_NFISH_MAIL_REWARDS"]):									# 海星
            from newfish.game import TGFish
            event = StarfishChangeEvent(userId, FISH_GAMEID, int(item["count"]))
            TGFish.getEventBus().publishEvent(event)
        elif config.getTreasureConf(kindId):                                                # 获取宝藏配置
            from newfish.entity import treasure_system
            treasure_system.refreshTreasureState(userId, kindId)
        elif kindId == config.SOUVENIR_KIND_ID and item["count"] < 0:
            from newfish.game import TGFish
            event = ConsumeVoucherEvent(userId, FISH_GAMEID, abs(item["count"]))
            TGFish.getEventBus().publishEvent(event)
    datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["chip", "item"])
    return 0


def doSendFishNotice(userId):
    """
    请求最新消息
    """
    noticeUrl = config.getNoticeUrl()
    noticeVersion = config.getNoticeVersion()
    message = MsgPack()
    message.setCmd("fishNotice")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("noticeUrl", noticeUrl)
    message.setResult("noticeVersion", noticeVersion)
    router.sendToUser(message, userId)


def loadAllRoomInfo():
    """
    读取所有房间信息
    """
    ret = {}
    roomInfoMap = roominfo.loadAllRoomInfo(FISH_GAMEID)
    for roomId, roomInfo in roomInfoMap.iteritems():
        bigRoomId = gdata.getBigRoomId(roomId)
        if not bigRoomId:
            continue
        bigRoomInfo = ret.get(bigRoomId)
        if bigRoomInfo:
            bigRoomInfo.signinCount += max(0, roomInfo.signinCount)
            bigRoomInfo.playerCount += max(0, roomInfo.playerCount)
        else:
            roomInfo.roomId = bigRoomId
            ret[bigRoomId] = roomInfo
    return ret


def getFishMatchSigninInfo(userId):
    """
    获取比赛报名信息
    """
    from newfish.servers.room.rpc import room_remote
    # 44411 * 10000 + 1000
    ctrlRoomIds = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap()[FISH_GAMEID]]
    for ctrlRoomId in ctrlRoomIds:
        roomConfig = gdata.getRoomConfigure(ctrlRoomId)
        if roomConfig.get("isMatch", 0):
            startTime = room_remote.getUserMatchSignin(userId, ctrlRoomId)      # 获取比赛的开始时间
            if startTime > 0:
                return ctrlRoomId, startTime
    return None, None


def isChestRewardId(itemId):
    """
    判断道具ID是否为宝箱
    """
    chestType = int(itemId) // 1000
    if 31 <= chestType <= 38:
        return True
    return False


def isCrystalChest(itemId):
    """
    判断是否为水晶宝箱
    """
    chestType = int(itemId) // 1000
    return chestType == 38


def isSkillCardItemId(itemId):
    """
    是否为技能相关卡片(升级卡/升星卡)
    """
    cardType = int(itemId) // 1000
    if cardType == 47 or cardType == 49:
        return True
    else:
        return False


def convertToFishItems(hallItems):
    """
    把大厅的道具列表数据格式转换为捕鱼的道具列表数据格式
    """
    hallItems = hallItems if isinstance(hallItems, list) else [hallItems]
    fishItems = []
    for item in hallItems:
        name = item["itemId"]
        if name == "user:chip":
            name = CHIP_KINDID
        elif name == "user:coupon":
            name = COUPON_KINDID
        elif str(name).startswith("item:"):
            name = int(name.split(":")[1])
        if not isinstance(name, int):
            ftlog.error("convertToFishItems", hallItems)
        fishItems.append({"name": name, "count": item["count"]})
    return fishItems


def buildRewardsDesc(rewardList, lang):
    """
    构建奖励描述
    """
    if rewardList:
        moreStr = u""
        if len(rewardList) > 1:
            moreStr = config.getMultiLangTextConf("ID_MORE_REWARDS_DESC", lang=lang)
            # moreStr = u"等奖励"
        r = rewardList[0]
        count = r["count"]
        rewardId = "item:" + str(r["name"])
        if r["name"] == config.COUPON_KINDID:           # 红包券
            rewardId = "user:coupon"
            count *= config.COUPON_DISPLAY_RATE         # 红包券:奖券 比率
            count = "%.2f" % count
        elif r["name"] == config.CHIP_KINDID:           # 金币
            rewardId = "user:chip"
        elif r["name"] == config.DIAMOND_KINDID:        # 钻石
            rewardId = "user:diamond"
        if lang == "zh":
            assetKind = hallitem.itemSystem.findAssetKind(rewardId)
            return u"%sx%s%s%s" % (assetKind.displayName, count, assetKind.units, moreStr)
        else:
            displayName = config.getMultiLangTextConf("ID_CONFIG_KINDID_%s" % rewardId.upper(), lang=lang)
            return u"%s x%s%s" % (displayName, count, moreStr)
    return u""


def buildRewards(rewardList):
    """
    构建奖励列表
    :param rewardList:[{"name":xx, "count":xx},...]
    :return:
    """
    rewards = []
    for r in rewardList:
        count = r["count"]
        if count <= 0:
            continue
        rewardId = "item:" + str(r["name"])
        if r["name"] == config.COUPON_KINDID:           # 红包券
            rewardId = "user:coupon"
            count *= config.COUPON_DISPLAY_RATE         # 红包券:奖券 比率
            count = "%.2f" % count
        elif r["name"] == config.CHIP_KINDID:           # 金币
            rewardId = "user:chip"
        elif r["name"] == config.DIAMOND_KINDID:        # 钻石
            rewardId = "user:diamond"
        assetKind = hallitem.itemSystem.findAssetKind(rewardId)
        if assetKind:
            rewards.append({
                "name": assetKind.displayName,
                "kindId": assetKind.kindId,             # 道具ID
                "count": count,                         # 数量
                "unit": assetKind.units,
                "desc": u"%sx%s" % (assetKind.displayName, count),
                "img": assetKind.pic
            })
    ftlog.debug("_buildRewards", rewards)
    return rewards


def buildActivityRewards(rewardList):
    """
    构建活动奖励列表
    """
    rewards = []
    for r in rewardList:
        rewardId = "item:" + str(r["name"])
        if isChestRewardId(r["name"]):              # 判断道具ID是否为宝箱
            rewards.append({
                "name": r["name"],
                "count": r["count"],
                "desc": r.get("desc", "")
            })
            continue
        count = r["count"]
        if count <= 0:
            continue
        if r["name"] == config.COUPON_KINDID:
            rewardId = "user:coupon"
            count *= config.COUPON_DISPLAY_RATE
            count = "%.2f" % count
        elif r["name"] == config.CHIP_KINDID:
            rewardId = "user:chip"
        elif r["name"] == config.DIAMOND_KINDID:
            rewardId = "user:diamond"
        assetKind = hallitem.itemSystem.findAssetKind(rewardId)
        if assetKind:
            rewards.append({
                "name": r["name"],
                "count": r["count"],
                "desc": r.get("desc", ""),
                "img": assetKind.pic,
                "unit": assetKind.units,
                "title": "%sx%s" % (assetKind.displayName, count),
                "rare": r.get("rare", 0)
            })
    ftlog.debug("buildActivityRewards", rewards)
    return rewards


def sendToHall51GameOverEvent(userId, roomId, tableId, fishes):
    """
    hall5游戏结束事件
    """
    ftlog.info("sendToHall51GameOverEvent->", userId, roomId, tableId, fishes)
    if hall51event.ISHALL51:
        hall51event.sendToHall51GameOverEvent(userId, FISH_GAMEID, roomId, tableId, **fishes)


def sendToHall51MatchOverEvent(userId, roomId):
    """
    hall5比赛结束事件
    """
    ftlog.info("sendToHall51MatchOverEvent->", userId, roomId)
    if hall51event.ISHALL51:
        hall51event.sendToHall51MatchOverEvent(userId, FISH_GAMEID, roomId)


def getClientVersion(userId):
    """
    获取玩家客户端版本号
    """
    return gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)        # 获取用户单个域游戏属性


def addGuideStep(userId, step, clientId):
    """
    添加引导步骤
    """
    userGuideStep = getAllUserGuideStep(userId)
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    if step not in userGuideStep and step in config.getPublic("allGuideIds", []):
        userGuideStep.append(step)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.userGuideStep, json.dumps(userGuideStep))
        bireport.reportGameEvent("BI_NFISH_GE_GUIDE_STEP", userId, FISH_GAMEID, 0,
                                 0, int(step), 0, 0, 0, [], clientId)
        # 完成新手任务即可
        isGuideOver = isFinishAllNewbieTask(userId)
        from newfish.entity.event import GuideChangeEvent
        from newfish.game import TGFish
        event = GuideChangeEvent(userId, FISH_GAMEID, isGuideOver)
        TGFish.getEventBus().publishEvent(event)
    elif clientVersion in getReviewVersionList(userId):
        userGuideStep.append(step)
    return userGuideStep


def isFinishAllGuide(userId, userGuideStep=None):
    """
    判断是否完成所有引导
    """
    userGuideStep = userGuideStep or getAllUserGuideStep(userId)
    totalGuide = config.getPublic("allGuideIds", [])                    # config.ALL_GUIDE_IDS
    leftStep = list(set(totalGuide) - set(userGuideStep))
    return len(leftStep) <= 0 and isFinishAllNewbieTask(userId)


def getAllUserGuideStep(userId):
    """
    获得所有已完成的引导
    """
    userGuideStep = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.userGuideStep, [])
    return userGuideStep


def isFinishAllNewbieTask(userId):
    """
    判断是否完成所有新手任务
    """
    redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
    if not redState:
        return False
    return True


def isNewbieRoom(typeName):
    """
    是否为新手场
    """
    return typeName == config.FISH_NEWBIE


def isInWhiteList(userId):
    """
    判断是否属于白名单用户
    """
    return int(userId) in config.getPublic("whiteList", [])


def isLocationLimit(userId, location=None):
    """
    判断客户端版本是否存在地区限制
    """
    if isInWhiteList(userId):
        return False
    if location:
        requestUrl = "http://iploc.ywdier.com/api/iploc5/search/city"
        postData = {"ip": sessiondata.getClientIp(userId)}
        result = doHttpQuery(requestUrl, postData)
        if not result or set(location) & set(result.get("loc", [])):
            return True
        return False
    else:
        isLocationLimit = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.isLocationLimit)
        return isLocationLimit == 1


def isVersionLimit(userId, clientVersion=None):
    """
    判断客户端版本是否属于提审版本
    """
    if isInWhiteList(userId):
        return False
    clientVersion = clientVersion or gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    if clientVersion in getReviewVersionList(userId):
        return True
    return False


def isUsableClientVersion(userId):
    """
    判断客户端版本是否可用
    """
    from distutils.version import StrictVersion
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)   # 客户端当前版本号
    if clientVersion:
        disableClientVersion = config.getDisableClientVersion()                 # 获取客户端禁止使用版本号
        usableClientVersion = config.getUsableClientVersion()                   # 获取客户端可用版本号
        if clientVersion in disableClientVersion:
            return False
        minimumVersion = usableClientVersion.get("minimumVersion", "0.0.0")     # 最小版本
        specialVersion = usableClientVersion.get("specialVersion", [])
        if StrictVersion(str(clientVersion)) >= StrictVersion(str(minimumVersion)):
            return True
        elif clientVersion in specialVersion:
            return True
    return False


def isPurchaseLimit(userId):
    """
    判断客户端版本是否存在购买限制（iOS用户等级小于12级的用户）
    """
    if isInWhiteList(userId):
        return False
    # from poker.util.constants import CLIENT_SYS_IOS
    # platformOS = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.platformOS)
    # if platformOS == CLIENT_SYS_IOS.lower():
    #     level = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    #     if level < 12:
    #         return True
    return False


def isProtectionLimit(userId):
    """
    该玩家是否存在健康保护限制
    """
    protectionLimit = config.getCommonValueByKey("protectionLimit", {})
    if protectionLimit:
        isProtectionLimit = weakdata.getMonthFishData(userId, WeakData.isProtectionLimit, 0)
        if isProtectionLimit:
            return True
        dailyProfitCoin, monthlyProfitCoin = getRobberyProfitCoin(userId)
        if (dailyProfitCoin <= protectionLimit["dailyLoss"] or monthlyProfitCoin <= protectionLimit["monthlyLoss"]):
            weakdata.setMonthFishData(userId, WeakData.isProtectionLimit, 1)
            return True
    return False


def isTextCensorLimit(text):
    """
    文本内容是否违规
    """
    if keywords.isContains(text):
        return True
    requestUrl = "http://text-cansoring.tuyoo.com" + "/textcansoring/v1/spam/sync.json"
    postData = {
        "access_id": "15a8d9001040d1ae",
        "algorithm": "sha256",
        "secret_type": "forever",
        "ts": int(time.time()),
        "content": str(text)
    }
    argsStr = sorted([("%s=%s" % (key, str(postData[key]))) for key in postData.keys()])
    signStr = "&".join(argsStr) + ":6tgxG9VMLehtC6pZKniOw0KmSPOo6RtF"
    signStr = hashlib.sha256(signStr).hexdigest().lower()
    postData["sign"] = signStr
    try:
        result = doHttpQuery(requestUrl, postData)
        if result and result.get("result", {}).get("spam") == 1:
            return True
    except:
        ftlog.error("isTextCensorLimit error", text)
    return False


def getRobberyProfitCoin(userId):
    """
    获得玩家招财模式下每日、每月盈亏金币
    """
    dailyBulletProfitCoin = weakdata.getDayRobberyData(userId, WeakData.bulletProfitCoin, 0)
    monthlyBulletProfitCoin = weakdata.getMonthFishData(userId, WeakData.bulletProfitCoin, 0)
    return dailyBulletProfitCoin, monthlyBulletProfitCoin


def getPoseidonProfitCoin(userId):
    """
    获得玩家海皇来袭下每日、每月盈亏金币
    """
    dailyPoseidonProfitCoin = weakdata.getDayPoseidonData(userId, WeakData.poseidonProfitCoin, 0)
    monthlyPoseidonProfitCoin = weakdata.getMonthFishData(userId, WeakData.poseidonProfitCoin, 0)
    return dailyPoseidonProfitCoin, monthlyPoseidonProfitCoin


def getProtectionProftCoin(userId):
    """
    获取玩家归属于健康保护限制渔场（招财、海皇）下的每日、每月盈亏金币（暂时无用）
    """
    dailyBulletProfitCoin, dailyPoseidonProfitCoin = getRobberyProfitCoin(userId)
    monthlyBulletProfitCoin, monthlyPoseidonProfitCoin = getPoseidonProfitCoin(userId)
    dailyProfitCoin = dailyBulletProfitCoin + dailyPoseidonProfitCoin
    monthlyProfitCoin = monthlyBulletProfitCoin + monthlyPoseidonProfitCoin
    return dailyProfitCoin, monthlyProfitCoin


def sendTodoTaskMsg(userId, message):
    """
    发送todoTask消息给客户端
    """
    todoTask = TodoTaskShowInfo(message)
    TodoTaskHelper.sendTodoTask(FISH_GAMEID, userId, todoTask)


def doHttpQuery(requestUrl, data, timeout=1, method="GET"):
    """
    http请求接口
    """
    querys, postData, response, result = None, None, None, None
    requestTime = time.time()
    try:
        if method == "GET":
            querys = data
        else:
            postData = data
        response, _ = webpage.webget(requestUrl, querys=querys, postdata_=postData,
                                     method_=method, connect_timeout=timeout, timeout=timeout+1)
        if response:
            result = json.loads(response)
            ftlog.info(requestUrl, "data =", data, "result =", result, "runtime =", time.time() - requestTime)
    except:
        ftlog.error(requestUrl, "data =", data, "response =", response)
    return result


def getOneResultByWeight(_list, _key="weight"):
    """
    根据权重获得随机1次的结果
    """
    totalWeight = sum([dict(_conf)[_key] for _conf in _list if _conf])
    if totalWeight > 0:
        randInt = random.randint(1, totalWeight)
        for _, _conf in enumerate(_list):
            randInt -= _conf[_key]
            if randInt <= 0:
                return _conf
    return None


def getGameTimePoolKey():
    """
    在线奖池数据库key
    """
    return "gametimepool:%d:%s" % (FISH_GAMEID, config.getGameTimePoolIssue())


def incrGameTimePool(coin):
    """
    增减在线奖池
    """
    assert (isinstance(coin, int))
    daobase.executeMixCmd("INCRBY", getGameTimePoolKey(), coin)


def getEggsOneResultByConfig(keyName, userId):
    """
    扭蛋抽奖、免费游戏时长抽奖
    """
    bonusConfig = config.getBonusConf(keyName)
    _bonusInfo = getOneResultByWeight(bonusConfig)
    coinNum = 0
    if _bonusInfo:
        coinNum = random.randint(_bonusInfo["minCoin"], _bonusInfo["maxCoin"])
        totalPoolNum = daobase.executeMixCmd("GET", getGameTimePoolKey())
        isLucky, curLuckyNum = isEggsLuckyPlayer(coinNum)
        ftlog.debug("getEggsOneResultByConfig->userId =", userId, "keyName =", keyName, "coinNum =", coinNum,
                    "isLucky =", isLucky, "curLuckyNum =", curLuckyNum)
        if isLucky:  # 幸运玩家
            if totalPoolNum >= coinNum:
                # reducePoolNum = min(totalPoolNum, coinNum)   # 减池子的钱不能减成负
                incrGameTimePool(-abs(coinNum))  # 减池子的钱
        else:   # 非幸运玩家，奖池金币不够，则从奖池金币和最小扭蛋金币中取最大值，
            if totalPoolNum < coinNum:
                minCoinRange = config.getEggsMinCoinRangeConf(keyName)
                minCoin = random.randint(minCoinRange[0], minCoinRange[1])
                coinNum = max(totalPoolNum, minCoin)
            incrGameTimePool(-abs(coinNum))  # 减池子的钱
        _addEggsLuckyUser(coinNum, curLuckyNum)
    return int(coinNum)


def isEggsLuckyPlayer(coinNum):
    """
    判断今日是否存在幸运玩家
    """
    isLucky = False
    mixEggsKey = "eggsLucky:%d" % FISH_GAMEID
    curValue = daobase.executeMixCmd("GET", mixEggsKey)
    timeRange = config.getCommonValueByKey("eggsLuckyResetTime", ["00:00", "20:00"])
    startTime = getTodayTimestampFromStr(timeRange[0])
    endTime = getTodayTimestampFromStr(timeRange[1])
    luckyTime = random.randint(startTime, endTime)
    # 每天刷新指定幸运时间
    if not curValue or isinstance(curValue, int):
        curValue = [luckyTime, 0, 0, 0]
        daobase.executeMixCmd("SET", mixEggsKey, json.dumps(curValue))
    else:
        curValue = json.loads(curValue)
        lastStartTime = getDayStartTimestamp(curValue[0])
        todayStartTime = getDayStartTimestamp(int(time.time()))
        if lastStartTime != todayStartTime:
            curValue = [luckyTime, 0, 0, 0]
            daobase.executeMixCmd("SET", mixEggsKey, json.dumps(curValue))

    if int(time.time()) >= curValue[0]: # 从指定时间开始发放超级大奖
        index_ = 1
        # 各超级大奖限制个数
        luckyEggsSuperPrize = config.getCommonValueByKey("luckyEggsSuperPrize", {})
        for superPrizeNum in sorted(map(int, luckyEggsSuperPrize), reverse=True):
            if coinNum >= superPrizeNum:
                if curValue[index_] >= luckyEggsSuperPrize[str(superPrizeNum)]:
                    isLucky = False
                else:
                    isLucky = True
                break
            index_ += 1
    return isLucky, curValue


def _addEggsLuckyUser(coinNum, curLuckyNum):
    mixEggsKey = "eggsLucky:%d" % FISH_GAMEID
    index_ = 1
    isSave = False
    luckyEggsSuperPrize = config.getCommonValueByKey("luckyEggsSuperPrize", {})
    for superPrizeNum in sorted(map(int, luckyEggsSuperPrize), reverse=True):
        if coinNum >= superPrizeNum:
            if curLuckyNum[index_] < luckyEggsSuperPrize[str(superPrizeNum)]:
                curLuckyNum[index_] += 1
                isSave = True
            break
        index_ += 1
    if isSave:
        daobase.executeMixCmd("SET", mixEggsKey, json.dumps(curLuckyNum))


def getMainTaskId(userId, fishPool):
    """
    获得用户主线任务ID
    """
    keyName = GameData.tableTask % fishPool
    tableTaskData = gamedata.getGameAttrJson(userId, FISH_GAMEID, keyName, {})
    return int(tableTaskData.get("mainTask", {}).get("taskId", 0))


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


def getVipRealLevel(userId):
    """
    获取VIP真实等级
    """
    return hallvip.userVipSystem.getUserVip(userId).vipLevel.level


def modifyVipShow(userId, modify):
    """
    修改VIP可见性
    """
    vipShow = isVipShow(userId)
    modify = int(modify)
    if canSetVipShow(userId) == 0:
        code = -2                       # return None
    else:
        if modify not in [0, 1]:
            code = -1
        elif vipShow == modify:         # 相同，不修改
            code = 1
        else:
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.vipShow, modify)
            vipShow = modify
            code = 0
    return vipShow, code


def canSetVipShow(userId):
    """
    判断能否设置VIP可见性
    """
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    return config.getVipConf(vipLevel).get("setVipShow", 0)


def getNickname(userId):
    """
    获取玩家昵称
    """
    nickname = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.nickname)
    if not nickname:
        nickname = userdata.getAttr(userId, "name")
    nickname = str(nickname) if nickname else ""
    return keywords.replace(nickname)


def getLanguage(userId, clientId=None):
    """
    获取玩家手机语言
    """
    clientId = clientId or getClientId(userId)
    if clientId in config.getPublic("multipleLangClientIds", []):
        lang = userdata.getAttr(userId, "lang")
        if lang and not str(lang).startswith("zh"):
            return "en"
    return "zh"


def getAllLanguage():
    """
    获取服务器所有语言
    """
    return ["zh", "en"]


def sendUserLed(msg, userId):
    """
    发送只有此用户可见的LED
    """
    if msg.get("msg", ""):
        mo = MsgPack()
        mo.setCmd("led")
        mo.setResult("type", msg.get("type", ""))
        mo.setResult("msg", msg.get("msg", ""))
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("scope", str(FISH_GAMEID))
        router.sendToUser(mo, userId)
    ftlog.debug("sendUserLed", userId, msg)


def adjustPearlCount(userId):
    """
    旧版本升级，调整珍珠数量
    """
    from newfish.entity import mail_system
    pearlCount = balanceItem(userId, config.PEARL_KINDID)
    adjustCount = pearlCount // 1000
    if adjustCount > 0:
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        userAssets.consumeAsset(FISH_GAMEID, "item:" + str(config.PEARL_KINDID), pearlCount - adjustCount, pktimestamp.getCurrentTimestamp(), "ITEM_USE", 0)
        message = config.getMultiLangTextConf("ID_ADJUST_PEARL_COUNT_MESSAGE", lang=getLanguage(userId))
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, message=message)


def processRebootLed(event):
    """
    处理停服维护时的全服LED
    """
    global _processInterval, _prevProcessRebootLedTime
    if event.count % _processInterval:
        return
    ftlog.debug("processRebootLed", event.count)
    currTime = int(time.time())
    rebootLedConf = config.getPublic("rebootLedConf", {})
    if not rebootLedConf:
        return
    startTime = getTimestampFromStr(rebootLedConf["startTime"])
    endTime = getTimestampFromStr(rebootLedConf["endTime"])
    urgentTime = getTimestampFromStr(rebootLedConf.get("urgentTime") or rebootLedConf["endTime"])
    urgentInterval = rebootLedConf.get("urgentInterval") or rebootLedConf["interval"]               # 紧急的间隔
    interval = rebootLedConf["interval"] if currTime < urgentTime else urgentInterval
    duration = rebootLedConf["duration"]
    if not (startTime <= currTime <= endTime):
        return
    if not _prevProcessRebootLedTime or int(currTime - _prevProcessRebootLedTime) / _processInterval >= interval:
        ledStrId = rebootLedConf.get("led_str_id", "ID_LED_REBOOT")
        for lang in getAllLanguage():
            if lang != "zh":
                continue
            leftMinutes = (getTimestampFromStr(rebootLedConf["rebootTime"]) - currTime) // 60
            msg = config.getMultiLangTextConf(ledStrId, lang=lang) % (leftMinutes, duration)
            user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, id=ledStrId, lang=lang)
        _prevProcessRebootLedTime = currTime


def saveRankInfo(userId, score, rankingId, time_, expireTime=None, updateTime=None):
    """保存排行榜信息"""
    time_ = timestampToStr(time_, "%Y-%m-%d")
    expireTime = expireTime or 24 * 3600
    updateTime = updateTime or pktimestamp.getCurrentTimestamp()
    key_ = UserData.rankingInfo % (str(rankingId), time_, FISH_GAMEID, userId)
    daobase.executeUserCmd(userId, "SETEX", key_, expireTime, json.dumps({
        "score": score,
        "time": updateTime
    }))


def incrUserRechargeBonus(userId, bonus):
    # 增加充值奖池
    try:
        final = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.rechargeBonus)            # 充值奖池数据
        bonus = int(bonus)
        if bonus > 0:
            final = int(final + bonus)
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.rechargeBonus, final)
            isIn, roomId, tableId, seatId = isInFishTable(userId)
            if isIn:
                mo = MsgPack()
                mo.setCmd("table_call")
                mo.setParam("action", "recharge_notify")
                mo.setParam("gameId", FISH_GAMEID)
                mo.setParam("clientId", getClientId(userId))
                mo.setParam("userId", userId)
                mo.setParam("roomId", roomId)
                mo.setParam("tableId", tableId)
                mo.setParam("seatId", seatId)
                router.sendTableServer(mo, roomId)
        ftlog.info("incrUserRechargeBonus, userId =", userId, "bonus =", bonus, "final =", final)
        return final
    except Exception, e:
        ftlog.error("incrUserRechargeBonus, userId =", userId, "bonus =", bonus, "e =", e)
    return 0


def isNumber(str):
    try:
        float(str)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(str)
        return True
    except (TypeError, ValueError):
        pass

    return False


def selectIdxByWeight(weightList):
    """
    根据权重选择索引位置
    """
    try:
        totalWeight = sum(weightList)
        if totalWeight > 0:
            weight = random.randint(1, totalWeight)
            for i, w in enumerate(weightList):
                if weight > w:
                    weight -= w
                else:
                    return i
        return -1
    except:
        ftlog.error("selectIdxByWeight, weightList =", weightList)
        return -1


def mergeItemList(itemList, newItemList):
    """
    合并相同道具
    """
    ftlog.debug("_mergeItemList->", itemList, newItemList)
    if not newItemList:
        return itemList
    kindIdList = [item["name"] for item in itemList if item]
    newKindIdList = [item["name"] for item in newItemList if item]
    sameKindIdList = set(kindIdList) & set(newKindIdList)
    if sameKindIdList:
        for kindId in sameKindIdList:
            index = kindIdList.index(kindId)
            newIndex = newKindIdList.index(kindId)
            item = itemList[index]
            newItem = newItemList[newIndex]
            if item["name"] == newItem["name"]:
                item["count"] += newItem["count"]
    else:
        itemList.extend(newItemList)
    ftlog.debug("_mergeItemList->", itemList)
    return itemList


def httpParamsSign(params):
    """
    http参数GDSS加密（用于GDSS等请求加密校验）
    """
    keys = sorted(params.keys())
    checkstr = ""
    for k in keys:
        checkstr += str(k) + "=" + str(params[k]) + "&"
    checkstr = checkstr[:-1]
    apikey = "www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com"
    checkstr = checkstr + apikey
    return strutil.md5digest(checkstr)


def chatReport(*argList):
    """
    渔场内聊天日志记录
    """
    from freetime5._tyserver._entity import ftglobal
    global _CHATLOGER
    if _CHATLOGER is None:
        logFileFullpath = gdata.globalConfig()["log_path"]
        logFileFullpath = logFileFullpath + "/chat.log"
        _CHATLOGER = ftlog.openNormalLogfile(logFileFullpath)
    logData = [ftglobal.cloudId, bireport._generateRecordId()]
    logData.extend(list(argList))
    msg = "\t".join(map(bireport._getFBRecordField, logData))
    _CHATLOGER.info(msg)


def getAssetKindId(kindId):
    """
    通过kindId获得assetKindId
    """
    return config.customKindIdMap.get(kindId) or "item:%d" % kindId


def _triggerHeartBeatEvent(event):
    """
    服务器心跳事件
    """
    processRebootLed(event)


# 测试代码
def testEggsResult(userId, itemId, count):
    num = 0
    for _ in xrange(count):
        result = getEggsOneResultByConfig(str(itemId), userId)
        if result >= 10000000:
            num += 1
    ftlog.debug("test1000EggsResult", num)


def addProductBuyEvent(userId, productId, clientId, buyCount=1):
    """
    商品购买完成事件
    """
    ftlog.debug("addProductBuyEvent, userId =", userId, productId, clientId, buyCount)
    from newfish.game import TGFish
    from newfish.entity.event import ProductBuyEvent
    event = ProductBuyEvent(userId, FISH_GAMEID, productId, clientId, buyCount)
    TGFish.getEventBus().publishEvent(event)


def increaseExtraRechargeBonus(userId, bonus):
    """
    给玩家添加额外充值奖池
    """
    extraRechargePool = config.getPublic("extraRechargePool", 0)
    lastCount = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.extraRechargePool)
    if lastCount < extraRechargePool and bonus > 0:
        curCount = gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.extraRechargePool, min(bonus, extraRechargePool - lastCount))
        incrUserRechargeBonus(userId, curCount - lastCount)


def decreaseExtraceRechargeBonus(userId, count):
    """
    减少玩家额外充值奖池
    """
    lastCount = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.extraRechargePool)
    if count > 0 and lastCount > 0:
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.extraRechargePool, -abs(min(count, lastCount)))


def getNewbieABCTestMode(userId):
    """
    获取玩家新手ABC测试模式
    """
    testMode = gamedata.getGameAttr(userId, FISH_GAMEID, ABTestData.newbiewABCTestMode)
    if testMode is None:
        return testMode
    testMode = config.getABTestConf("abcTest").get("mode") or testMode
    return testMode


def getGiftAbcTestMode(userId):
    """
    获取玩家礼包cde测试模式
    """
    # if getClientIdSys(userId) == CLIENT_SYS_IOS.lower():
    #     return "c"
    # giftAbcTestConf = config.getGiftAbcTestConf(getClientId(userId))
    # if giftAbcTestConf.get("mode"):
    #     return giftAbcTestConf.get("mode")
    # mode = ["c", "d", "e"]
    # idx = int(userId) % len(mode) if giftAbcTestConf.get("enable") else 0
    # return mode[idx]
    return "d"


def getRoomMinLevel(roomId):
    """
    获取房间最小等级
    """
    roomConf = {}
    if gdata.roomIdDefineMap().get(roomId):
        roomConf = gdata.roomIdDefineMap()[roomId].configure
    return roomConf.get("minLevel", 1)


def getRoomMinCoin(roomId):
    """
    获取房间最小金币
    """
    roomConf = {}
    if gdata.roomIdDefineMap().get(roomId):
        roomConf = gdata.roomIdDefineMap()[roomId].configure
    return roomConf.get("minCoin", 0)


def sendSmsCode(userId, mobile):
    """
    发送短信验证码接口
    """
    clientId = getClientId(userId)
    deviceId = sessiondata.getDeviceId(userId)
    requestUrl = gdata.httpGame() + "/open/v5/user/sendSmsCode"
    postData = {
        "appId": 9999,
        "userId": userId,
        "clientId": clientId,
        "deviceId": deviceId,
        "mobile": mobile,
        "imei": "null"
    }
    result = doHttpQuery(requestUrl, postData)
    if result and result.get("result", {}).get("code") is 0:
        return True
    return False


def verifySmsCode(userId, mobile, vcode):
    """
    验证短信验证码接口
    """
    clientId = getClientId(userId)
    deviceId = sessiondata.getDeviceId(userId)
    requestUrl = gdata.httpGame() + "/open/v6/user/checkSmsCodeOnly"
    postData = {
        "appId": 9999,
        "userId": userId,
        "clientId": clientId,
        "deviceId": deviceId,
        "mobile": mobile,
        "vcode": vcode,
        "snsId": "mobile:%d" % mobile,
        "imei": "null"
    }
    result = doHttpQuery(requestUrl, postData)
    if result:
        if result.get("result", {}).get("code") is 0:
            return True
        return False
    return None


def verifyPhoneNumber(phoneNumber):
    """
    验证手机号是否合法
    """
    import re
    pattern = re.compile(r"^[1]([3-9])[0-9]{9}$")
    if pattern.search(str(phoneNumber)):
        return True
    return False


def getRoomGameMode(roomId):
    """
    获取roomId所属的游戏玩法
    """
    if gdata.roomIdDefineMap().get(roomId):
        roomConf = gdata.roomIdDefineMap()[roomId].configure
        typeName = roomConf.get("typeName")
        if typeName in config.CLASSIC_MODE_ROOM_TYPE:
            return config.CLASSIC_MODE
    return config.MULTIPLE_MODE


def isOldPlayerV2(userId):
    """
    是否为2.0版本老用户
    """
    return gamedata.getGameAttr(userId, FISH_GAMEID, GameData.isOldPlayerV2)


def getGunX(wpId, mode):
    """
    获取炮台的倍数(经典模式为1:千炮为炮台倍数)
    """
    gunX = 1 if mode != config.MULTIPLE_MODE else config.getGunLevelConf(wpId, mode).get("levelValue", 1)
    return gunX


def getGunLevel(userId, mode):
    """
    获取火炮等级索引(21xx)
    """
    gunLevelKey = GameData.gunLevel if mode == config.CLASSIC_MODE else GameData.gunLevel_m
    return gamedata.getGameAttrInt(userId, FISH_GAMEID, gunLevelKey)


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getGunLevelVal(userId, mode):
    """
    获取火炮等级/倍率
    """
    gunLevel = getGunLevel(userId, mode)
    return config.getGunLevelConf(gunLevel, mode).get("levelValue", 1)


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getStoreCheckLevel(userId):
    """
    获取玩家商城需要检测的等级
    """
    # 使用玩家等级.
    level = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    return level


def getUserLevel(userId):
    """
    获取玩家等级
    """
    return gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getActivityCheckLevel(userId):
    """
    获取活动需要检测的等级
    """
    # 需要注意游戏中已有的升级相关的等级含义.
    # 应使用千炮等级
    userLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    return userLevel


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getUserValidCheckLevel(userId):
    """
    获取检测玩家有效性需要检测的等级
    """
    # 需要注意游戏中已有的升级相关的等级含义.
    level = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    return level


_inited = False
_processInterval = 10
_prevProcessRebootLedTime = None
_timeStampFromStrCache = {}


def initialize(isCenter):
    ftlog.debug("newfish util initialize begin")
    global _inited
    if not _inited:
        _inited = True
        if isCenter:
            from poker.entity.events.tyeventbus import globalEventBus
            from poker.entity.events.tyevent import EventHeartBeat
            globalEventBus.subscribe(EventHeartBeat, _triggerHeartBeatEvent)
    ftlog.debug("newfish util initialize end")