# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import time
import json
import random
import string

from freetime.util import log as ftlog
from hall.entity import hallvip
from poker.entity.configure import gdata
from poker.util import strutil
from poker.entity.dao import gamedata, userchip, userdata
from newfish.entity import config, util, weakdata, mail_system
from newfish.entity.gift import gift_system, newbie_7days_gift
from newfish.entity.config import FISH_GAMEID, SERVER_VERSION
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.data import FishData


def getInitDataKeys():
    """
    gamedata的key
    """
    return FishData.getGameDataKeys()


def getInitDataValues():
    """
    gamedata的value
    """
    return FishData.getGameDataValues()


def getGameInfo(userId, clientId):
    """
    获取玩家的游戏数据
    """
    from newfish.entity import user_system
    ukeys = getInitDataKeys()
    uvals = gamedata.getGameAttrs(userId, FISH_GAMEID, ukeys)
    uvals = list(uvals)
    values = getInitDataValues()
    for x in xrange(len(uvals)):
        if uvals[x] is None:
            uvals[x] = values[x]
    gdata = dict(zip(ukeys, uvals))
    gdata["name"] = util.getNickname(userId)
    gdata["userGuideStep"] = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.userGuideStep, [])
    redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
    gdata["redState"] = redState
    gdata["giftState"] = newbie_7days_gift.checkNewbie7DaysGiftState(userId, redState)
    # 是否可以领取启航礼包（1：是 0：否）
    # gdata["sailGiftState"] = 1 if gift_system.SailGift(userId, clientId).getGiftInfo() else 0
    gdata["surpriseGift"] = weakdata.getDayFishData(userId, GameData.surpriseGift, 0)
    gdata["exchangeCount"] = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.exchangeCount)
    gdata["nowServerTime"] = time.time()
    gdata["isAdult"] = user_system.isAdult(userId)

    # 是否为v2版本老玩家（1：是 0：否）
    isOldPlayerV2 = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.isOldPlayerV2)
    if isOldPlayerV2 is None:
        isOldPlayerV2 = 1 if redState else 0
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.isOldPlayerV2, isOldPlayerV2)
    gdata["isOldPlayerV2"] = isOldPlayerV2

    # 当前技能页面显示的模式，老玩家默认为经典模式（0：经典 1：千炮）
    skillMode = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.skillMode)
    if skillMode is None:
        skillMode = config.CLASSIC_MODE if isOldPlayerV2 else config.MULTIPLE_MODE
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.skillMode, skillMode)
    gdata["skillMode"] = skillMode

    # 当前炮台页显示的模式，老玩家默认为经典模式（0：经典 1：千炮）
    gunMode = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.gunMode)
    if gunMode is None:
        gunMode = config.CLASSIC_MODE if isOldPlayerV2 else config.MULTIPLE_MODE
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.gunMode, gunMode)
    gdata["gunMode"] = gunMode

    exp, level = gamedata.getGameAttrs(userId, FISH_GAMEID, [GameData.exp, GameData.level])
    level = max(1, level)
    userLevelConf = config.getUserLevelConf()
    lvUpExp = userLevelConf[level - 1]["exp"] if level <= len(userLevelConf) else userLevelConf[-1]["exp"]
    gdata["level"] = level
    gdata["expPct"] = min(100, max(0, int(exp * 100. / lvUpExp)))
    return gdata


def createGameData(userId, gameId):
    """
    创建玩家的游戏数据
    """
    ftlog.debug("createGameData->userId =", userId, gameId)
    gdkeys = getInitDataKeys()
    gvals = getInitDataValues()
    gamedata.setGameAttrs(userId, FISH_GAMEID, gdkeys, gvals)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.registTime, int(time.time()))
    modifyUserName(userId)
    provideRenameItem(userId)
    sendWelcomeMail(userId)
    setNewbie7Day(userId)
    return gdkeys, gvals


def setNewbie7Day(userId):
    """
    设置新手8日礼包数据
    """
    ts = int(time.time())
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.newbie7DayGiftData, strutil.dumps([util.getDayStartTimestamp(ts), []]))


def sendWelcomeMail(userId):
    """
    发送欢迎邮件
    """
    message = None
    welcomeMailConfs = config.getCommonValueByKey("ignoreConf")
    clientId = util.getClientId(userId)
    ftlog.debug("sendWelcomeMail", userId, "clientId = ", clientId)
    lang = util.getLanguage(userId)
    rewards = config.getCommonValueByKey("welcomeMailRewards")
    for welcomeMailConf in welcomeMailConfs:
        if clientId in welcomeMailConf.get("clientIds", []):
            # message = welcomeMailConf.get("messageNotAllow", None)
            message = config.getMultiLangTextConf("ID_CONFIG_BAN_ENTITY_WELCOME_MSG", lang=lang)
        else:
            message = config.getMultiLangTextConf("ID_CONFIG_ALLOW_ENTITY_WELCOME_MSG", lang=lang)
            #message = welcomeMailConf.get("messageAllowEntity", None)
    if message:
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message=message,
                                   title=config.getMultiLangTextConf("ID_MAIL_TITLE_HOT_WELCOME", lang=lang))


def createNewbieMode(userId):
    """
    新玩家ab测试
    """
    # 新手ABC测试.
    newbiewABCTestMode = config.getABTestConf("abcTest").get("mode")
    if newbiewABCTestMode is None:
       modes = ["a", "b", "c"]
       newbiewABCTestMode = modes[userId % len(modes)]
    gamedata.setGameAttr(userId, FISH_GAMEID, ABTestData.newbiewABCTestMode, newbiewABCTestMode)


def modifyUserName(userId):
    """
    iOS下游客登录及苹果登录用户修改昵称为g_xxxx
    """
    clientIdNum = util.getClientIdNum(userId)
    if clientIdNum in config.getCommonValueByKey("randomNickNameClientIds", []):
        snsId = userdata.getAttr(userId, "snsId")
        if not snsId or str(snsId).startswith("ios"):
            nickName = "g_" + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))
            userdata.setAttr(userId, "name", nickName)


def provideRenameItem(userId):
    """
    新注册用户发放改名卡道具
    """
    rewards = [{"name": config.RENAME_KINDID, "count": 1}]
    util.addRewards(userId, rewards, "BI_NFISH_NEW_USER_REWARDS")


def sendVipSpringFestivalRewards(userId):
    """
    vip玩家2019年春节礼包
    """
    vip_springfestival_rewards = {
        1: {"name": 101, "count": 10000}, 2: {"name": 101, "count": 30000},
        3: {"name": 101, "count": 60000}, 4: {"name": 101, "count": 100000},
        5: {"name": 101, "count": 200000}, 6: {"name": 101, "count": 300000},
        7: {"name": 101, "count": 500000}, 8: {"name": 101, "count": 1000000},
        9: {"name": 101, "count": 1600000}, 10: {"name": 101, "count": 3000000},
        11: {"name": 101, "count": 6000000}, 12: {"name": 101, "count": 10000000}
    }
    lang = util.getLanguage(userId)
    vip_springfestival_message = config.getMultiLangTextConf("ID_VIP_SPRING_FESTIVAL_MESSAGE", lang=lang)

    springFestival_time = {
        "start": "2019-01-31 00:00:00",
        "end": "2019-02-05 23:59:59"
    }
    if util.isTimeEffective(springFestival_time) is False:
        return
    if gamedata.getGameAttrInt(userId, FISH_GAMEID, "vip2019SpringFestivalRewards") == 0:  # vip2019NewYearRewards
        vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
        rewards = vip_springfestival_rewards.get(vipLevel, None)
        if rewards is not None:
            gamedata.setGameAttr(userId, FISH_GAMEID, "vip2019SpringFestivalRewards", 1)  # vip2019NewYearRewards
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, [rewards], vip_springfestival_message)


def vipAutoSupplyPerDay(userId):
    """
    vip每日自动补足
    """
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    key = GameData.autoSupplyKey % config.CHIP_KINDID
    autoSupplyCount = config.getVipConf(vipLevel).get(key, 0)
    chips = userchip.getUserChipAll(userId)
    if autoSupplyCount >= 10000 and chips < autoSupplyCount and weakdata.getDayFishData(userId, key, 0) == 0:
        weakdata.incrDayFishData(userId, key, 1)
        lang = util.getLanguage(userId)
        rewards = [{"name": config.CHIP_KINDID, "count": (autoSupplyCount - chips)}]
        message = config.getMultiLangTextConf("ID_VIP_AUTO_SUPPLY_PER_DAY", lang=lang) % (autoSupplyCount / 10000)
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message)
    ftlog.debug("vipAutoSupplyPerDay", userId, vipLevel, autoSupplyCount, chips, key, autoSupplyCount - chips)


def loginGame(userId, gameId, clientId, iscreate, isdayfirst):
    """
    用户登录一个游戏, 游戏自己做一些其他的业务或数据处理
    """
    ftlog.debug("userId =", userId, "gameId =", gameId, "clientId =", clientId,
                "iscreate =", iscreate, "isdayfirst =", isdayfirst, gdata.name())
    gamedata.setnxGameAttr(userId, FISH_GAMEID, GameData.gunLevel_m, 2101)
    if isdayfirst:
        sendVipSpringFestivalRewards(userId)
    if isdayfirst:
        vipAutoSupplyPerDay(userId)
    if isdayfirst:
        from newfish.entity.quest import daily_quest
        from newfish.entity import weakdata
        resetTime = weakdata.getDayFishData(userId, "resetTime")
        if not resetTime:
            weakdata.setDayFishData(userId, "resetTime", int(time.time()))
            daily_quest.refreshDailyQuestData(userId)
        # FTLoopTimer(1, 0, util.doSendFishNotice, userId).start()
    gamedata.setnxGameAttr(userId, FISH_GAMEID, GameData.vipShow, 1)
    serverVersion = gamedata.getGameAttrInt(userId, gameId, GameData.serverVersion)
    if isdayfirst and gamedata.getGameAttr(userId, FISH_GAMEID, GameData.hasBoughtMonthCard) is None:
        from hall.entity import hallitem
        # _, itemId, _ = gift_system.MonthCardGift(userId, clientId).getGiftInfo()
        # userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        item = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID) or \
               userBag.getItemByKindId(config.MONTH_CARD_KINDID)
        bought = 1 if item else 0
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.hasBoughtMonthCard, json.dumps(bought))
    if serverVersion and serverVersion <= 20180907:
        # 珍珠数量调整
        util.adjustPearlCount(userId)
    if serverVersion and serverVersion <= 20180918:
        # 老玩家屏蔽10元话费卡兑换
        gamedata.setGameAttr(userId, gameId, GameData.exchangeCount, 1)
    if serverVersion and serverVersion <= 20180928:
        # 老玩家金猪出现次数数据迁移
        from newfish.entity import share_system
        from newfish.entity.share_system import FlyingPig
        shareClass = FlyingPig(userId)
        flyPigFinishCount = shareClass.shareData[share_system.INDEX_FINISH_COUNT]
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.flyPigFinishCount, flyPigFinishCount)
    # 清理金币购买记录,19/12/25日0点后开始检测
    if int(time.time()) >= util.getTimestampFromStr("2019-12-25 00:00:00") and \
            not gamedata.getGameAttrInt(userId, gameId, "resetBuyCoinCount"):
        gamedata.delGameAttr(userId, FISH_GAMEID, GameData.buyCoinCount)
        gamedata.setGameAttr(userId, gameId, "resetBuyCoinCount", 1)
    if not serverVersion or int(serverVersion) != SERVER_VERSION:
        gamedata.setGameAttr(userId, gameId, GameData.serverVersion, SERVER_VERSION)

    if not util.isFinishAllNewbieTask(userId):  # 没完成所有新手引导，不主动弹出每日签到和最新消息
        return

    # 未领取女王红包的老账号直接放弃女王红包.
    redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
    from newfish.entity.task.task_system_user import RedState
    if redState in [RedState.Complete, RedState.CanReceived]:
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.redState, RedState.GiveUp)

    # 限定玩家比赛幸运值.
    from newfish.entity.match_record import MatchRecord
    vip = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    for roomId in [44102]:
        key = "initLuckyValue:%d" % int(roomId)
        initVal = config.getVipConf(vip).get(key, 10000)
        record = MatchRecord.loadRecord(FISH_GAMEID, userId, roomId)
        record.luckyValue = min(record.luckyValue, initVal)
        MatchRecord.saveRecord(FISH_GAMEID, userId, roomId, record)
        # noticeVersion = gamedata.getGameAttr(userId, gameId, "noticeVersion")
    # if not noticeVersion or int(noticeVersion) != config.getNoticeVersion():
    #     from newfish.entity import module_tip
    #     module_tip.addModuleTipEvent(userId, "notice", config.getNoticeVersion())
    #     gamedata.setGameAttr(userId, gameId, "noticeVersion", config.getNoticeVersion())


def getDaShiFen(userId, clientId):
    """
    获取玩家大师分信息
    """
    exp, level = gamedata.getGameAttrs(userId, FISH_GAMEID, [GameData.exp, GameData.level])
    info = {}
    info["score"] = exp
    info["level"] = level
    info["pic"] = "http://ddz.dl.tuyoo.com/texas/res/icon/shark/texas_shark_icon_" + level + ".png"
    info["title"] = ""
    info["name"] = "捕鱼"
    info["des"] = "捕鱼积分"
    return info