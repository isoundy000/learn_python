#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30

import time
import datetime
import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.dao import daobase, gamedata
from poker.protocol import router
from newfish.entity.config import FISH_GAMEID, STARFISH_KINDID, PEARL_KINDID
from newfish.entity import util, config, weakdata, module_tip, drop_system
from newfish.entity.chest import chest_system
from newfish.entity.redis_keys import GameData, WeakData, UserData


class QuestTaskState:
    Normal = 1                      # 未完成
    Complete = 2                    # 已完成
    Received = 3                    # 已领取


class TaskType():
    FishNum = 10001                 # 累计捕获鱼数
    MultipleFishNum = 10002         # 累计捕获倍率鱼数
    CoinNum = 10003                 # 累计捕鱼获得金币数
    SkillUseNum = 10004             # 累计技能使用数
    BossFishNum = 10005             # 累计捕获Boss鱼数
    PlayTime = 10006                # 累计游戏时长
    TableTaskNum = 10007            # 累计完成渔场任务数
    TableTimeTaskNum = 10008        # 累计完成渔场限时任务数
    StoreBuyNum = 10009             # 在商店购买任意物品数
    ShareFinishNum = 10010          # 分享完成次数
    GetFreeCoinNum = 10011          # 在金币商城领取免费金币次数

    CheckIn = 10012                 # 每日签到
    EelFishNum = 10013              # 捕获电鳗数量
    BombFishNum = 10014             # 捕获炸弹鱼数量
    DrillFishNum = 10015            # 捕获钻头鱼数量
    EnterMatchTimes = 10016         # 参加比赛次数
    StarfishNum = 10017             # 捕鱼获得海星数
    UseCoolDownNum = 10018          # 使用冷却次数
    FireNum = 10019                 # 累计开火次数
    PearlNum = 10020                # 捕鱼获得珍珠次数
    GoldenTurttleNum = 10021        # 捕获黄金龟次数
    GoldenJellyNum = 10022          # 捕获黄金水母次数
    GoldenCrab = 10023              # 捕获黄金蟹次数
    TurttleNum = 10024              # 捕获海龟次数
    JellyNum = 10025                # 捕获水母次数
    BlowFishNum = 10026             # 捕获河豚次数
    CrabNum = 10027                 # 捕获螃蟹次数
    LanternFishNum = 10028          # 捕获灯笼鱼次数
    DoradoFishNum = 10029           # 捕获剑鱼次数
    WinTask = 10030                 # 渔场比赛冠军(夺宝赛，奖金赛)
    TodayRechargeCount = 10031      # 当日充值数量
    EnterFishPool = 10032           # 进入渔场的次数


def refreshDailyQuestData(userId):
    """
    重置每日任务存档
    """
    # 刷新每日任务分组难度等级
    checkGroupLv(userId, True)
    refreshDailyQuestGroupLv(userId)
    key = _getUserDailyQuestKey(userId)
    daobase.executeUserCmd(userId, "DEL", key)
    key = _getUserDailyQuestRewardKey(userId)
    daobase.executeUserCmd(userId, "DEL", key)
    gamedata.delGameAttr(userId, FISH_GAMEID, _getUserDailyQuestInfoKey(userId))
    gamedata.delGameAttr(userId, FISH_GAMEID, GameData.refreshDailyQuestTimes)
    module_tip.resetModuleTipEvent(userId, "task")


def checkGroupLv(userId, refresh):
    """检查分组等级"""
    # 2019-06-07 0:0:0
    if int(time.time()) >= 1559836800:
        return
    key = "resetDailyQuestGroupLv:%d:%d" % (FISH_GAMEID, userId)
    if daobase.executeUserCmd(userId, "GET", key):
        return
    daobase.executeUserCmd(userId, "SET", key, 1)
    daobase.executeUserCmd(userId, "EXPIREAT", key, 1559836800)

    questInfo = getUserQuestInfoData(userId)
    key = _getUserDailyQuestGroupLvKey(userId)
    groupLvData = gamedata.getGameAttrJson(userId, FISH_GAMEID, key, {})
    dailyQuestConf = config.getDailyQuestConf()
    _newQuestInfo = {}
    update = False
    for taskId, val in questInfo.iteritems():
        process = val[0]
        _quest = dailyQuestConf.get(str(taskId))
        if _quest:
            oldTargetNum = _quest.get("targetsNum")
            groupId = _quest.get("groupId", 0)
            # 未完成任务难度降至1级.
            lvData = groupLvData.get(str(groupId), [1, 0, 0])
            if groupId and lvData and lvData[0] > 1:
                if val[1] == QuestTaskState.Normal and (refresh or lvData[1] != 1):
                    update = True
                    taskId, _lv = getQuestTaskId(groupId, 1, util.getDailyQuestCheckLevel(userId), userId)
                    groupLvData[str(groupId)] = [_lv, 0, lvData[2]]
                    _quest = dailyQuestConf.get(str(taskId))
                    if _quest and oldTargetNum:
                        process = int(process * 1. / oldTargetNum * _quest.get("targetsNum"))
        _newQuestInfo[str(taskId)] = [process, val[1]]
    if update:
        setUserQuestInfoData(userId, _newQuestInfo)
        gamedata.setGameAttr(userId, FISH_GAMEID, key, json.dumps(groupLvData))


def getTodayQuest(userId):
    """
    获取当日所有每日任务配置
    """
    pass


def getDailyQuestData(userId):
    """
    获取玩家每日任务数据
    """
    level = util.getUnlockCheckLevel(userId)
    if level < config.getCommonValueByKey("dailyQuestOpenLevel"):
        return {}
    lang = util.getLanguage(userId)
    # 替换为新版任务时，重置玩家每日任务数据.
    key = _getUserDailyQuestGroupLvKey(userId)                              # 任务分组的当前难度等级数据
    groupLvData = gamedata.getGameAttrJson(userId, FISH_GAMEID, key, {})
    if len(groupLvData) == 0:
        refreshDailyQuestData(userId)
    groupIdList = config.getDailyQuestGroupOrder()
    dailyQuestData = {}
    todayQuest, activeLv = getTodayQuest(userId)
    # userData = _getUserQuestData(userId)
    finishedStar = 0
    key = _getUserDailyQuestWeeklyRewardKey(userId)
    ret = json.loads(weakdata.getWeekFishData(userId, key, "{}"))
    finishedWeekStar = ret.get("star", 0)
    questInfo = getUserQuestInfoData(userId)
    tasks = []
    update = False
    questList = sorted(todayQuest.items(), key=lambda val: groupIdList.index(val[1]["groupId"]))
    all = len(todayQuest) == len(groupIdList)
    # for k, v in todayQuest.iteritems():
    pass


def getUserQuestInfoData(userId):
    """
    获取每日任务完成状态
    """
    key = _getUserDailyQuestInfoKey(userId)
    questInfo = gamedata.getGameAttr(userId, FISH_GAMEID, key)
    if questInfo is None:
        questInfo = {}
    else:
        questInfo = json.loads(questInfo)
    return questInfo


def setUserQuestInfoData(userId, info):
    """
    存储每日任务完成状态
    """
    key = _getUserDailyQuestInfoKey(userId)
    gamedata.setGameAttr(userId, FISH_GAMEID, key, json.dumps(info))


def getInitQuestLv(userId):
    """
    计算玩家初始难度等级
    """
    return 1
    # level = util.getDailyQuestLevel(userId)
    # if level <= 14:
    #     return 1
    # elif level <= 24:
    #     return 2
    # elif level <= 29:
    #     return 5
    # else:
    #     return 8


def getQuestTaskId(groupId, lv, userLv, userId):
    """
    根据任务分组和难度等级选择任务id
    """
    dayOfWeek = datetime.datetime.now().weekday()
    lv = max(1, lv)
    taskId = 0
    groupLv = 1
    for k, v in config.getDailyQuestConf().iteritems():
        if v.get("groupId") == int(groupId) and (0 in v["showDay"] or (dayOfWeek + 1) in v["showDay"]):
            if v.get("lv") <= lv and v.get("unlockUserLv") <= userLv:
                taskId = v.get("taskId")
                groupLv = v.get("lv")
    groupLv = max(1, groupLv)
    return taskId, groupLv


def _getUserDailyQuestKey(userId):
    """
    每日任务类型的完成进度存档
    {type: progress}
    """
    return UserData.fishDailyQuest % (FISH_GAMEID, userId)


def _getUserDailyQuestRewardKey(userId):
    """
    每日任务星级奖励领取存档
    [star1, start2...]
    """
    return UserData.fishDailyQuestReward % (FISH_GAMEID, userId)






def _getUserDailyQuestInfoKey(userId):
    """
    每日任务完成状态存档
    {taskId: [target, state]}
    """
    return UserData.fishDailyQuestInfo % (FISH_GAMEID, userId)


def _getUserDailyQuestGroupLvKey(userId):
    """
    任务分组的当前难度等级数据
    {groupId: [lv, expChange, ts], expChange: +2升级;-2降级;未连读登录清0}
    """
    return UserData.fishDailyQuestGroupLv % (FISH_GAMEID, userId)





def _incQuestValue(userId, taskType, incVlaue, resetTime=0, fishPool=0, fpMultiple=0):
    """
    更新每日任务进度并检测；任务是否完成
    """
    pass




def incrRecharge(userId, rmbs):
    """
    充值
    """
    _incQuestValue(userId, TaskType.TodayRechargeCount, rmbs)


def triggerCatchEvent(event):
    """捕获事件"""
    pass


def triggerGameTimeEvent(event):
    """
    游戏时长事件
    """
    fishPool = event.fishPool
    userId = event.userId
    gameTime = event.gameTime
    fpMultiple = event.fpMultiple if hasattr(event, "fpMultiple") else 0
    _incQuestValue(userId, TaskType.PlayTime, gameTime, fishPool=fishPool, fpMultiple=fpMultiple)


def triggerLevelUpEvent(event):
    """
    等级提升事件
    """
    userId = event.userId
    level = event.level


def triggerOpenChestEvent(event):
    """
    开启宝箱事件
    """
    userId = event.userId
    atOnce = event.atOnce


def triggerBuyChestEvent(event):
    """
    购买宝箱事件
    """
    userId = event.userId
    buyType = event.buyType


def triggerUseSkillEvent(event):
    """
    使用技能事件
    """
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    fpMultiple = event.fpMultiple if hasattr(event, "fpMultiple") else 0
    userId = event.userId
    skillId = event.skillId
    _incQuestValue(userId, TaskType.SkillUseNum, 1, fishPool=fishPool, fpMultiple=fpMultiple)


def triggerUseSmiliesEvent(event):
    """
    使用表情事件
    """
    userId = event.userId
    smilieId = event.smilieId


def triggerWinCmpttTaskEvent(event):
    """
    夺宝赛获奖事件
    """
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    userId = event.userId
    _incQuestValue(userId, TaskType.WinTask, 1, fishPool=fishPool)


def triggerWinNcmpttTaskEvent(event):
    """
    限时任务获奖事件
    """
    userId = event.userId


def triggerWinBonusTaskEvent(event):
    """
    奖金赛获奖事件
    """
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    userId = event.userId
    rank = event.rank
    _incQuestValue(userId, TaskType.WinTask, 1, fishPool=fishPool)


def triggerEnterTableEvent(event):
    """
    进入渔场事件(参加回馈赛)
    """
    if event.reconnect:
        return
    userId = event.userId
    bigRoomId, isMatch = util.getBigRoomId(event.roomId)
    if isMatch:
        _incQuestValue(userId, TaskType.EnterMatchTimes, 1)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    _incQuestValue(userId, TaskType.EnterFishPool, 1, fishPool=fishPool)


def triggerStoreBuyEvent(event):
    """
    商城购买事件
    """
    userId = event.userId
    _incQuestValue(userId, TaskType.StoreBuyNum, 1)


def triggerTableTaskEndEvent(event):
    """
    渔场任务结束事件
    """
    userId = event.userId
    if event.isComplete:
        _incQuestValue(userId, TaskType.TableTaskNum, 1)
        if event.isLimitTime:
            _incQuestValue(userId, TaskType.TableTimeTaskNum, 1)


def triggerShareFinishEvent(event):
    """
    分享完成事件
    """
    from newfish.entity import share_system
    userId = event.userId
    if event.shareMode != share_system.ShareMode.Advert:
        _incQuestValue(userId, TaskType.ShareFinishNum, 1)
    if event.typeId == share_system.CoinStore.TYPEID:
        _incQuestValue(userId, TaskType.GetFreeCoinNum, 1)


def triggerCheckinEvent(event):
    """
    签到事件
    """
    userId = event.userId
    _incQuestValue(userId, TaskType.CheckIn, 1)


def triggerUseCoolDownEvent(event):
    """
    使用冷却事件
    """
    userId = event.userId
    _incQuestValue(userId, TaskType.UseCoolDownNum, 1)


def triggerFireEvent(event):
    """
    开火事件
    """
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    fpMultiple = event.fpMultiple if hasattr(event, "fpMultiple") else 0
    userId = event.userId
    _incQuestValue(userId, TaskType.FireNum, 1, fishPool=fishPool, fpMultiple=fpMultiple)


_inited = False


def initialize():
    ftlog.info("newfish DailyQuest initialize begin")
    global _inited
    if not _inited:
        _inited = True
    ftlog.info("newfish DailyQuest initialize end")