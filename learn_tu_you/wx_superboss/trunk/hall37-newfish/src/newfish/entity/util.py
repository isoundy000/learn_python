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
    return clientId.startswith(CLIENT_SYS_ANDROID.lower() or clientId.startswith(CLIENT_SYS_IOS.lower()))
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
    pass


def getReviewVersionList(userId):
    pass


def getFishPoolByBigRoomId(bigRoomId):
    """
    :param bigRoomId:
    :return:
    """
    if bigRoomId == 44499:
        return 44001
    elif 44405 >= bigRoomId >= 44401:
        return 44000 + bigRoomId % 44400
    else:
        return bigRoomId


def getBigRoomId(roomId):
    """获取大房间"""
    if not roomId:
        return 0, 0
    pass


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


def isFinishAllRedTask(userId):
    """
    获得所有已完成的引导
    """
    userGuideStep = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.userGuideStep, [])
    return userGuideStep


def isRedRoom(typeName):
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
    pass


def isVersionLimit(userId, clientVersion=None):
    """
    判断客户端版本是否属于提审版本
    """
    if isInWhiteList(userId):
        return False
    clientVersion = clientVersion or gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    if clientVersion in getReviewVersionList(userId):       # config.getPublic("reviewClientVersion", []):
        return True
    return False


# TODO.需要根据产品设计需求确定使用火炮等级还是玩家等级等等.
def getLevelByGunLevel(userId):
    """
    获取火炮等级对应的等级
    """
    # 需要注意游戏中已有的升级相关的等级含义.
    uLevel = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.level)
    return uLevel


def getRoomMinLevel(roomId, abcTestMode):
    """
    获取房间最小等级
    """
    bigRoomId, _ = getBigRoomId(roomId)
    fishPool = getFishPoolByBigRoomId(bigRoomId)
    abcTestConf = config.getABTestConf("abcTest").get("enterLimit", {}).get(str(fishPool), {}).get(abcTestMode)
    if abcTestConf and abcTestConf.get("minLevel"):
        return abcTestConf["minLevel"]
    roomConf = gdata.roomIdDefineMap()[roomId].configure
    return roomConf.get("minLevel", 0)


def getRoomMinCoin(roomId, abcTestMode):
    """
    获取房间最小金币
    """
    bigRoomId, _ = getBigRoomId(roomId)
    fishPool = getFishPoolByBigRoomId(bigRoomId)
    abcTestConf = config.getABTestConf("abcTest").get("enterLimit", {}).get(str(fishPool), {}).get(abcTestMode)
    if abcTestConf and abcTestConf.get("minCoin"):
        return abcTestConf["minCoin"]
    roomConf = gdata.roomIdDefineMap()[roomId].configure
    return roomConf.get("minCoin", 0)


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
    pass


def canSetVipShow(userId):
    """
    判断能否设置VIP可见性
    """
    vipLevel = hallvip.userVipSystem.getUserVip(userId).get("level", 0)
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


def getItemPresentTestMode(userId):
    """
    获取物品赠送测试模式
    """
    itemPresentTestMode = config.getPublic("itemPresentTestMode")
    return itemPresentTestMode or gamedata.getGameAttr(userId, FISH_GAMEID, ABTestData.itemPresentTestMode)


def selectIdxByWeight(weightList):
    """
    根据权重选择索引位置
    """
    try:
        totalWeight = sum(weightList)
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
    items = []
    # 竞赛积分，只用于处理addRewards逻辑以免返回错误占位使用!
    compPoints = []
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
        for item in items:
            if item["name"] in config.upgradeSkillKindIds:
                isUpSkillItem = True
            if item["name"] in config.upgradeGunKindIds:
                isUpGunItem = True
        if isUpSkillItem:   # 存在技能升级所需物品
            event = SkillItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        if isUpGunItem:     # 存在普通炮升级所需物品
            event = GunItemCountChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        # 道具监控
        event = ItemMonitorEvent(userId, FISH_GAMEID, changed, eventId)
        TGFish.getEventBus().publishEvent(event)

    # 资产/道具变化
    event = ItemChangeEvent(userId, FISH_GAMEID, gain, changed, type)
    TGFish.getEventBus().publishEvent(event)
    if compPoints:
        changed["comPoints"] = compPoints
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
        if kindId in config.skillCardKindIdMap:                                 # 技能提示和事件
            skillId = config.skillCardKindIdMap[kindId]
            skill = skill_system.getSkill(userId, skillId)
            if skill[skill_system.INDEX_ORIGINAL_LEVEL] == 0:
                # skill_system.setSkill(userId, skillId, [1, 1, 1, 0])
                module_tip.addModuleTipEvent(userId, "newskill", skillId)
                from newfish.game import TGFish
                event = NewSkillEvent(userId, FISH_GAMEID, skillId, eventId)
                TGFish.getEventBus().publishEvent(event)
        elif kindId in config.getAllGunIds(clientId, config.CLASSIC_MODE):      # 经典火炮的提示和事件
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
            event = AddGunSkinEvent(userId, FISH_GAMEID, kindId, int(item["count"]), intEventParam,
                                    config.MULTIPLE_MODE)
            TGFish.getEventBus().publishEvent(event)
            gunIds = gun_system.getGunIds(userId, config.MULTIPLE_MODE)
            if kindId not in gunIds:
                module_tip.addModuleTipEvent(userId, "gunskin", kindId)
        elif kindId in [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]:    # 青铜、白银、黄金招财珠
            from newfish.game import TGFish
            event = BulletChangeEvent(userId, FISH_GAMEID)
            TGFish.getEventBus().publishEvent(event)
        elif (kindId == STARFISH_KINDID and int(item["count"]) > 0 and eventId not in
            ["BI_NFISH_BUY_ITEM_GAIN", "BI_NFISH_ACTIVITY_REWARDS", "BI_NFISH_MAIL_REWARDS"]):  # 海星
            from newfish.game import TGFish
            event = StarfishChangeEvent(userId, FISH_GAMEID, int(item["count"]))
            TGFish.getEventBus().publishEvent(event)
        elif config.getTreasureConf(kindId):                                                # 获取宝藏配置
            from newfish.entity import treasure_system
            treasure_system.refreshTreasureState(userId, kindId)
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
        if roomConfig.get('isMatch', 0):
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
        if r["name"] == config.COUPON_KINDID:       # 红包券
            rewardId = "user:coupon"
            count *= config.COUPON_DISPLAY_RATE     # 红包券:奖券 比率
            count = "%.2f" % count
        elif r["name"] == config.CHIP_KINDID:       # 金币
            rewardId = "user:chip"
        elif r["name"] == config.DIAMOND_KINDID:    # 钻石
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
    pass

def getNewbieABCTestMode(userId):
    """
    获取玩家新手ABC测试模式
    """
    testMode = gamedata.getGameAttr(userId, FISH_GAMEID, ABTestData.newbiewABCTestMode)
    if testMode is None:
        return testMode
    # 苹果版本使用a模式.
    if getClientIdSys(userId) == CLIENT_SYS_IOS.lower():
        return "a"
    testMode = config.getABTestConf("abcTest").get("mode") or testMode
    return testMode


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