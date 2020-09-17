# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/5/19.
新版签到，分为3个转盘，记录连续登陆天数解锁后2个转盘。
"""


import time
import random

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import gamedata
from hall.entity import hallvip
from poker.protocol import router
from newfish.entity import config, weakdata, module_tip, util
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.chest import chest_system


def _isCheckin(userId, ts=None):
    """
    判断今日是否已签到
    """
    ts = ts or int(time.time())
    # 当日签到后时间戳会设置为第二天的0点
    continuousCheckinDayTS = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.continuousCheckinDayTS)
    isCheckin = 1 if continuousCheckinDayTS == util.getDayStartTimestamp(ts) + 86400 else 0
    return isCheckin


def _isCheckContinuousBreak(userId, ts=None):
    """
    检查是否需要中断连续签到
    """
    ts = ts or int(time.time())
    dayStartTS = util.getDayStartTimestamp(int(ts))
    gamedata.setnxGameAttr(userId, FISH_GAMEID, GameData.breakContinuousCheckinTS, dayStartTS)
    gamedata.setnxGameAttr(userId, FISH_GAMEID, GameData.continuousCheckinDayTS, dayStartTS)
    # 未连续签到时要中断.
    continuousCheckinDayTS = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.continuousCheckinDayTS)
    if continuousCheckinDayTS + 86400 <= dayStartTS:
        breakContinuousCheckinTS = dayStartTS
        continuousCheckinDayTS = dayStartTS
        gamedata.setGameAttrs(userId, FISH_GAMEID,
                              [GameData.breakContinuousCheckinTS, GameData.continuousCheckinDayTS],
                              [breakContinuousCheckinTS, continuousCheckinDayTS])
        ftlog.debug("checkin, break, userId =", userId)
    # vip小于配置时，每周按照配置日期中断连续签到数据.
    st = time.localtime(dayStartTS)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    conf = config.getCheckinConf("resetInfo")
    resetVip = conf.get("vip", 0)
    resetWeekDay = conf.get("resetWeekDay", 0)
    if vipLevel <= resetVip and st.tm_wday == resetWeekDay:
        breakContinuousCheckinTS = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.breakContinuousCheckinTS)
        if breakContinuousCheckinTS < dayStartTS:
            breakContinuousCheckinTS = dayStartTS
            continuousCheckinDayTS = dayStartTS
            gamedata.setGameAttrs(userId, FISH_GAMEID, [GameData.breakContinuousCheckinTS, GameData.continuousCheckinDayTS],
                                  [breakContinuousCheckinTS, continuousCheckinDayTS])
            ftlog.debug("checkin, reset, userId =", userId, "resetTS =", dayStartTS)


def _getCheckinDay(userId):
    """
    获取已经签到了的天数
    """
    _isCheckContinuousBreak(userId)
    breakContinuousCheckinTS = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.breakContinuousCheckinTS)
    continuousCheckinDayTS = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.continuousCheckinDayTS)
    checkinDay = (continuousCheckinDayTS - breakContinuousCheckinTS) / 86400
    return checkinDay


def _getMsgRewardsDict(userId):
    """
    返回所有签到的奖励配置
    """
    msgDict = {}
    conf = config.getCheckinConf("checkinData")
    for k, v in conf.iteritems():
        msgDict[k] = [item["rewards"] for item in v.get("datas", [])]
    return msgDict


def sendFishCheckinInfo(userId, continueWindow=0):
    """
    发送签到详情
    :param continueWindow: 0:用户点击签到请求 1:客户端登录时自动请求
    """
    _isCheckContinuousBreak(userId)

    checkinDay = _getCheckinDay(userId)
    isCheckin = _isCheckin(userId)
    code = 1
    if (continueWindow and isCheckin):
        code = 2
    elif util.isFinishAllNewbieTask(userId):
        code = 0
        if not isCheckin:
            module_tip.addModuleTipEvent(userId, "checkin", checkinDay)
    mo = MsgPack()
    mo.setCmd("fishCheckin")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    # 签到日
    day = checkinDay if isCheckin else checkinDay + 1
    mo.setResult("loginDays", day)
    mo.setResult("day", day)
    mo.setResult("checkin", isCheckin)
    msgRewardsDict = _getMsgRewardsDict(userId)
    for k, v in msgRewardsDict.iteritems():
        mo.setResult(k, v)
    mo.setResult("continueWindow", continueWindow)
    mo.setResult("code", code)
    enableItems = []
    for k, v in config.getCheckinConf("checkinData").iteritems():
        if v["unlockdays"] <= day:
            enableItems.append(k)
    mo.setResult("enableItems", enableItems)
    router.sendToUser(mo, userId)
    ftlog.debug("checkin, userId =", userId, checkinDay, mo)


def sendFishCheckinRewardInfo(userId, day):
    """
    领取签到奖励
    """
    mo = MsgPack()
    mo.setCmd("fishCheckinReward")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    ts = int(time.time())
    code = 1
    if util.isFinishAllNewbieTask(userId):
        # kindId, rewards, checkinDay = getTodayCheckinRewards(userId)
        # if kindId and rewards :
        #     code = util.addRewards(userId, rewards, "BI_NFISH_CHECKIN_REWARDS")
        #     if code == 0:
        #         finishCheckin(userId, rewards, checkinDay)
        #         mo.setResult("kindId", kindId)
        #         mo.setResult("rewards", rewards)
        checkinDay, totalRewards, rd = getTodayCheckinRewards(userId)
        if totalRewards:
            code = util.addRewards(userId, totalRewards, "BI_NFISH_CHECKIN_REWARDS")
            finishCheckin(userId, totalRewards, checkinDay, ts=ts)
            for k, v in rd.iteritems():
                mo.setResult(k, v)
            mo.setResult("totalRewards", totalRewards)
            if code != 0:
                ftlog.error("checkin, userId =", userId, "day =", day, "checkinday =", checkinDay, "rd =", rd)
    mo.setResult("day", day)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)


def getTodayCheckinRewards(userId, isShare=False):
    """
    当天未签到时，获得签到奖励详情
    """
    # kindId, rewards = None, None
    # checkinDay = getCheckinDay(userId)
    # if checkinDay:
    #     rewardConf = config.getCheckinConf(checkinDay)
    #     reward = rewardConf["normalReward"]
    #     if isShare:
    #         reward = rewardConf["shareReward"]
    #     kindId = reward["name"]
    #     if util.isChestRewardId(kindId):
    #         rewards = chest_system.getChestRewards(userId, kindId)
    #     else:
    #         rewards = [reward]
    # return kindId, rewards, checkinDay
    rewardsDict = {}
    totalRewards = []
    totalRewardsDict = {}
    checkinDay = getCheckinDay(userId)
    multiple = 1
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    if checkinDay:
        for k, v in config.getCheckinConf("checkinData").iteritems():
            if v["unlockdays"] > checkinDay:
                if k == "rewards":
                    rewardsDict.update({"kindId": 0, "rewards": []})
                elif k == "rewards2":
                    rewardsDict.update({"kindId2": 0, "rewards2": []})
            else:
                idx = util.selectIdxByWeight([item["rate"] for item in v["datas"]])
                item = v["datas"][idx]
                if k == "multiple":
                    multiple = item["rewards"]
                else:
                    reward = item["rewards"]
                    kindId = reward["name"]
                    if util.isChestRewardId(kindId):
                        rewards = chest_system.getChestRewards(userId, kindId)
                    else:
                        rewards = [reward]
                    totalRewards.extend(rewards)
                    if k == "rewards":
                        rewardsDict.update({"kindId": kindId, "rewards": rewards})
                    else:
                        rewardsDict.update({"kindId2": kindId, "rewards2": rewards})
    rewardsDict.update({"multiple": multiple})
    ftlog.debug("checkin, userId =", userId, "totalRewards =", totalRewards, "multiple =", multiple, "isShare =", isShare)
    for item in totalRewards:
        itemCount = item["count"] * multiple * (2 if vipLevel >= 1 else 1)
        totalRewardsDict[item["name"]] = totalRewardsDict.get(item["name"], 0) + itemCount
    totalRewards = []
    for k, v in totalRewardsDict.iteritems():
        totalRewards.append({"name": k, "count": v})
    return checkinDay, totalRewards, rewardsDict


def getCheckinDay(userId):
    """
    当天未签到时，获取是第几天签到
    """
    # isCheckin = weakdata.getDayFishData(userId, "isCheckin", 0)
    isCheckin = _isCheckin(userId)
    if not isCheckin:
        checkinDay = _getCheckinDay(userId)
        checkinDay += 1
        return checkinDay
    return 0


def finishCheckin(userId, rewards=None, checkinDay=None, ts=None):
    """
    完成签到
    """
    # if not rewards or not checkinDay:
    #     kindId, rewards, checkinDay = getTodayCheckinRewards(userId)
    # if checkinDay:
    #     gamedata.setGameAttr(userId, FISH_GAMEID, GameData.checkinDay, checkinDay)
    #     weakdata.setDayFishData(userId, "isCheckin", 1)
    #     module_tip.resetModuleTipEvent(userId, "checkin")
    #     from newfish.game import TGFish
    #     from newfish.entity.event import CheckinEvent
    #     event = CheckinEvent(userId, FISH_GAMEID, checkinDay, rewards)
    #     TGFish.getEventBus().publishEvent(event)
    ts = ts or int(time.time())
    if not rewards or not checkinDay:
        checkinDay, rewards, _ = getTodayCheckinRewards(userId)
    if checkinDay:
        _isCheckContinuousBreak(userId, ts)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.continuousCheckinDayTS, util.getDayStartTimestamp(int(ts)) + 86400)
        weakdata.setDayFishData(userId, "isCheckin", 1)
        module_tip.resetModuleTipEvent(userId, "checkin")
        vipLevel = util.getVipRealLevel(userId)
        # 注册当天签到不增加充值奖池.
        registTime = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.registTime)
        if util.getDayStartTimestamp(int(time.time())) > util.getDayStartTimestamp(registTime):
            util.increaseExtraRechargeBonus(userId, config.getVipConf(vipLevel).get("checkinRechargeBonus", 0))
        from newfish.game import TGFish
        from newfish.entity.event import CheckinEvent
        event = CheckinEvent(userId, FISH_GAMEID, checkinDay, rewards)
        TGFish.getEventBus().publishEvent(event)


def _triggerNewbieTaskCompleteEvent(event):
    """
    新手任务完成
    """
    userId = event.userId
    checkinDay = getCheckinDay(userId)
    if checkinDay:
        module_tip.addModuleTipEvent(userId, "checkin", checkinDay)


_inited = False


def initialize():
    ftlog.info("newfish checkin initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.game import TGFish
        from newfish.entity.event import NewbieTaskCompleteEvent
        TGFish.getEventBus().subscribe(NewbieTaskCompleteEvent, _triggerNewbieTaskCompleteEvent)  # 新手任务完成事件
    ftlog.info("newfish checkin initialize end")