# -*- coding=utf-8 -*-
"""
Created by lichen on 17/2/6.
"""

import time
import datetime
import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.dao import daobase, gamedata
from poker.protocol import router
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util, config, weakdata, module_tip, drop_system
from newfish.entity.chest import chest_system
from newfish.entity.redis_keys import GameData, WeakData, UserData


class QuestTaskState:
    Normal = 1                      # 未完成
    Complete = 2                    # 已完成
    Received = 3                    # 已领取


class TaskType():

    TableTaskNum = 10007            # 累计完成渔场任务数
    TableTimeTaskNum = 10008        # 累计完成渔场限时任务数
    StoreBuyNum = 10009             # 在商店购买任意物品数
    ShareFinishNum = 10010          # 分享完成次数
    GetFreeCoinNum = 10011          # 在金币商城领取免费金币次数
    EelFishNum = 10013              # 捕获电鳗数量
    BombFishNum = 10014             # 捕获炸弹鱼数量
    DrillFishNum = 10015            # 捕获钻头鱼数量
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
    EnterFishPool = 10032           # 进入渔场的次数

    # 复用
    GunYFishNum = 10001             # 使用n倍炮以上捕获鱼数
    GunYMultipleFishNum = 10002     # 使用n倍炮以上捕获倍率鱼数
    CoinNum = 10003                 # 累计捕鱼获得金币数
    SkillUseNum = 10004             # 累计技能使用数
    GunYBossFishNum = 10005         # 使用n倍炮以上捕获Boss鱼数
    PlayTime = 10006                # 累计游戏时长
    CheckIn = 10012                 # 每日签到
    EnterMatchTimes = 10016         # 参加比赛次数    回馈赛次数
    TodayRechargeCount = 10031      # 当日充值数量
    # 新加
    FreeChest = 10033               # 在商城中领取{}次免费宝箱
    UseSkillLockItem = 10034        # 使用多少次锁定
    UseSkillFreezeItem = 10035      # 使用多沙次冰冻
    LevelPrizeWheel = 10036         # 转盘的转动
    JoinGrandPrix = 10037           # 参加大奖赛次数
    # 捕获鱼的任务
    GunYTerrorFishNum = 10038       # 使用n倍炮以上捕获特殊鱼
    FishNum = 10039                 # 捕获n条鱼
    TerrorFishNum = 10040           # 捕获n条特殊鱼


def refreshDailyQuestData(userId):
    """
    重置每日任务存档
    """
    # 刷新每日任务分组难度等级
    refreshDailyQuestGroupLv(userId)
    key = _getUserDailyQuestKey(userId)
    daobase.executeUserCmd(userId, "DEL", key)
    key = _getUserDailyQuestRewardKey(userId)
    daobase.executeUserCmd(userId, "DEL", key)
    gamedata.delGameAttr(userId, FISH_GAMEID, _getUserDailyQuestInfoKey(userId))
    gamedata.delGameAttr(userId, FISH_GAMEID, GameData.refreshDailyQuestTimes)
    module_tip.resetModuleTipEvent(userId, "task")


def getTodayQuest(userId):
    """
    获取当日所有每日任务配置
    """
    activeLv = 0
    groupIdList = config.getDailyQuestGroupOrder()
    gunLevel_m = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    todayQuest = {}
    dailyQuestConf = config.getDailyQuestConf()
    questInfo = getUserQuestInfoData(userId)
    if len(questInfo) == 0:
        key = _getUserDailyQuestGroupLvKey(userId)
        groupLvData = gamedata.getGameAttrJson(userId, FISH_GAMEID, key, {})
        update = False
        for groupId in groupIdList:
            groupId = str(groupId)
            lvData = groupLvData.get(groupId, [1, 0, 0])
            lv = lvData[0]
            if lvData[1] >= 2:
                lv += 1
            taskId, _lv = getQuestTaskId(groupId, lv, gunLevel_m, userId)
            if _lv != lvData[0]:
                update = True
                groupLvData[groupId] = [_lv, 0, lvData[2]]
            if taskId:
                questInfo[str(taskId)] = [0, QuestTaskState.Normal]
                todayQuest[int(taskId)] = dailyQuestConf.get(str(taskId))
                activeLv += dailyQuestConf.get(str(taskId)).get("activeLv", 0)
        setUserQuestInfoData(userId, questInfo)
        if update:
            gamedata.setGameAttr(userId, FISH_GAMEID, key, json.dumps(groupLvData))
    else:
        questInfo = getUserQuestInfoData(userId)
        for taskId, _ in questInfo.iteritems():
            taskId = int(taskId)
            _quest = dailyQuestConf.get(str(taskId))
            if _quest:
                todayQuest[taskId] = _quest
                activeLv += _quest.get("activeLv", 0)
    activeLv = int(activeLv)
    old = activeLv
    activeLvList = sorted([int(key) for key in config.getDailyQuestRewardConf().keys()])
    if activeLv <= activeLvList[0]:
        activeLv = activeLvList[0]
    elif activeLv >= activeLvList[-1]:
        activeLv = activeLvList[-1]
    else:
        for val in activeLvList:
            if old >= val:
                activeLv = val
    if ftlog.is_debug():
        ftlog.debug("daily_quest, userId =", userId, "questInfo =", questInfo, "activeLv =", activeLv, old, activeLvList)
    return todayQuest, activeLv


def getDailyQuestData(userId):
    """
    获取玩家每日任务数据
    """
    level = util.getUserLevel(userId)
    if level < config.getCommonValueByKey("dailyQuestOpenLevel"):
        return {}
    if not util.isFinishAllNewbieTask(userId):
        return {}
    lang = util.getLanguage(userId)
    # 替换为新版任务时，重置玩家每日任务数据.
    key = _getUserDailyQuestGroupLvKey(userId)
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
    for _val in questList:
        k, v = _val
        task = {}
        task["taskId"] = k
        task["taskLevel"] = v["taskLevel"]
        task["targetsNum"] = v["targetsNum"]
        # progress = userData.get(v["taskType"], 0)
        progress, state = questInfo.get(str(k), [0, QuestTaskState.Normal])
        if progress >= task["targetsNum"] or state >= QuestTaskState.Complete:
            progress = task["targetsNum"]
            # 已领取
            if state == QuestTaskState.Received:
                finishedStar += task["taskLevel"]
            elif state == QuestTaskState.Normal:
                state = QuestTaskState.Complete
                questInfo[str(k)] = [progress, state]
                update = True
        task["progress"] = progress
        task["taskState"] = state
        task["rewards"] = v["rewards"]
        task["chestRewards"] = []
        for val in v["rewards"]:
            itemId = val["name"]
            if util.isChestRewardId(itemId):
                task["chestRewards"].append({"chestId": itemId, "chestInfo": chest_system.getChestInfo(itemId)})
        # if v["taskType"] == TaskType.CoinNum and v["des"].find("%s") >= 0:
        #    task["des"] = v["des"] % util.formatScore(v["targetsNum"])
        # elif v["des"].find("%d") >= 0:
        #    task["des"] = v["des"] % v["targetsNum"]
        # else:
        #    task["des"] = v["des"]
        vDesId = v["des"]
        vDes = config.getMultiLangTextConf(str(vDesId), lang=lang)
        if v["taskType"] == TaskType.CoinNum and vDes.find("%s") >= 0:
            task["des"] = vDes % util.formatScore(v["targetsNum"], lang=lang)
        elif vDes.find("%d") >= 0:
            task["des"] = vDes % v["targetsNum"]
        elif vDes.count("{}") >= 2:
            task["des"] = vDes.format(v["gunX"], v["targetsNum"])
        else:
            task["des"] = vDes
        tasks.append(task)
    if update:
        setUserQuestInfoData(userId, questInfo)
    dailyQuestReward = config.getDailyQuestRewardConf(activeLv, all)
    gotReward = _getUserQuestRewardData(userId, "day")
    gotWeekReward = _getUserQuestRewardData(userId, "week")
    dailyQuestData["tasks"] = tasks
    rewardData = [dailyQuestReward[str(key)] for key in sorted(map(int, dailyQuestReward.keys()))]
    for v in rewardData:
        v["chestRewards"] = []
        for val in v["rewards"]:
            itemId = val["itemId"]
            if util.isChestRewardId(itemId):
                v["chestRewards"].append({"chestId": itemId, "chestInfo": chest_system.getChestInfo(itemId)})
    dailyQuestData["rewardData"] = rewardData
    dailyQuestData["finishedStar"] = finishedStar
    dailyQuestData["gotReward"] = gotReward
    dailyQuestData["finishedWeekStar"] = finishedWeekStar
    dailyQuestData["gotWeekReward"] = gotWeekReward
    dailyQuestData["refreshData"] = config.getDailyQuestRefreshConf()
    dailyQuestData["refreshedTimes"] = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.refreshDailyQuestTimes)
    return dailyQuestData


def getDailyQuestReward(userId, star, type="day"):
    """
    领取每日任务星级奖励
    """
    from newfish.entity.chest.chest_system import ChestFromType
    fromType = ChestFromType.Daily_Quest_Week_Chest if type == "week" else \
               ChestFromType.Daily_Quest_Daily_Chest
    reason = 0
    rewards = []
    finishedStar = 0
    key = _getUserDailyQuestWeeklyRewardKey(userId)
    ret = json.loads(weakdata.getWeekFishData(userId, key, "{}"))
    finishedWeekStar = ret.get("star", 0)
    gotRewardStars = _getUserQuestRewardData(userId, type)
    questInfo = getUserQuestInfoData(userId)
    all = len(questInfo) == len(config.getDailyQuestGroupOrder())
    if star in gotRewardStars:
        reason = 1  # 已经领取过奖励
    else:
        todayQuest, activeLv = getTodayQuest(userId)
        for k, v in todayQuest.iteritems():
            progress, state = questInfo.get(str(k), [0, QuestTaskState.Normal])
            if state == QuestTaskState.Received:
                finishedStar += v["taskLevel"]
        starConfig = config.getDailyQuestRewardConf(activeLv, all).get(str(star), {})
        if not starConfig or (type == "day" and finishedStar < star) or (type == "week" and finishedWeekStar < star):
            reason = 2  # 未达到领取条件
        else:
            rewards = starConfig.get("rewards")
            code = 0
            _insertQuestRewarded(userId, star, type)
            for reward in starConfig.get("rewards"):
                kindId = reward["itemId"]
                if util.isChestRewardId(kindId):
                    rewards = chest_system.getChestRewards(userId, kindId)
                    code = chest_system.deliveryChestRewards(userId, kindId, rewards, "DTASK_REWARD", fromType=fromType)
                else:
                    code = util.addRewards(userId, [reward], "DTASK_REWARD")
            if code != 0:
                ftlog.error("newfish->getDailyQuestReward =", userId, "rewards =", rewards)
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "dailyReward")
    mo.setResult("star", star)
    mo.setResult("type", type)
    mo.setResult("gotReward", gotRewardStars)
    mo.setResult("reason", reason)
    if reason == 0:
        gotRewardStars.append(star)
        mo.setResult("gotReward", gotRewardStars)
        mo.setResult("rewards", rewards)
        # _insertQuestRewarded(userId, star, type)
        module_tip.cancelModuleTipEvent(userId, "task", star)
    router.sendToUser(mo, userId)
    if ftlog.is_debug():
        ftlog.debug("daily_quest, userId =", userId, "star =", star, "type =", type, "mo =", mo)


def getQuestReward(userId, taskId, rewardflyPos):
    """
    领取每日任务奖励
    """
    code = 1
    reason = 2
    rewards = []
    questInfo = getUserQuestInfoData(userId)
    progress, state = questInfo.get(str(taskId), [0, QuestTaskState.Normal])
    # 未达到领取条件
    if state == QuestTaskState.Normal:
        reason = 2
    # 已经领取过奖励
    elif state == QuestTaskState.Received:
        reason = 1
    elif state == QuestTaskState.Complete:
        reason = 0
        questInfo[str(taskId)] = [progress, QuestTaskState.Received]
        setUserQuestInfoData(userId, questInfo)
        module_tip.cancelModuleTipEvent(userId, "task", taskId)     # -1
        todayQuest, activeLv = getTodayQuest(userId)
        quest = todayQuest.get(taskId, {})
        rewards = _processQuestReward(userId, quest)                # quest.get("rewards", [])
        code = util.addRewards(userId, rewards, "DTASK_REWARD")
        taskLevel = quest.get("taskLevel", 0)
        # 更新周奖励的星级
        finishedWeekStar = _incrDailyQuestWeekStar(userId, taskLevel)
        questData = getDailyQuestData(userId)
        finishedStar = questData.get("finishedStar", 0)
        all = len(questInfo) == len(config.getDailyQuestGroupOrder())
        dailyQuestRewardFinishedStars = config.getDailyQuestRewardFinishedStars("day", all)
        for star in dailyQuestRewardFinishedStars:
            if finishedStar >= star > finishedStar - taskLevel:
                module_tip.addModuleTipEvent(userId, "task", star)
                break
        dailyQuestRewardFinishedWeekStars = config.getDailyQuestRewardFinishedStars("week", all)
        for star in dailyQuestRewardFinishedWeekStars:
            if finishedWeekStar >= star > finishedWeekStar - taskLevel:
                module_tip.addModuleTipEvent(userId, "task", star)
                break
        from newfish.entity.event import DailyTaskRewardEvent
        from newfish.game import TGFish
        event = DailyTaskRewardEvent(userId, FISH_GAMEID, taskId, taskLevel)
        TGFish.getEventBus().publishEvent(event)
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "questReward")
    mo.setResult("taskId", taskId)
    mo.setResult("rewardflyPos", rewardflyPos)
    mo.setResult("reason", reason)
    if reason == 0:
        mo.setResult("code", code)
        mo.setResult("rewards", rewards)
    router.sendToUser(mo, userId)


def getSpareQuest(userId):
    """
    获取可用的备用任务
    """
    todayQuest, _ = getTodayQuest(userId)
    dayOfWeek = datetime.datetime.now().weekday()
    dailyQuestConf = config.getDailyQuestConf()
    spareQuests = []
    for k, v in dailyQuestConf.iteritems():
        if v["spareQuest"] == 0:
            continue
        if int(k) in todayQuest.keys():
            continue
        if 0 in v["showDay"] or (dayOfWeek + 1) in v["showDay"]:
            spareQuests.append(v)
    return spareQuests


def refreshQuestTaskId(userId, taskId):
    """
    手动刷新每日任务
    """
    code = 1
    newTaskId = 0
    spareQuests = getSpareQuest(userId)
    cost = config.getDailyQuestRefreshConf().get("cost")
    if spareQuests and cost:
        todayQuest, _ = getTodayQuest(userId)
        quest = todayQuest.get(taskId, None)
        if ftlog.is_debug():
            ftlog.debug("refreshQuestTaskId", "userId =", userId, "taskId =", taskId, "quest =", quest)
        if quest:
            questInfo = getUserQuestInfoData(userId)
            refreshTimes = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.refreshDailyQuestTimes)
            process, state = questInfo.get(str(taskId), [0, QuestTaskState.Normal])
            if ftlog.is_debug():
                ftlog.debug("refreshQuestTaskId", "questInfo =", questInfo, "refreshTimes =", refreshTimes, process, state)
            if state == QuestTaskState.Normal and refreshTimes < config.getDailyQuestRefreshConf().get("maxTimes", 1):
                succ = True
                for item in cost:
                    if util.balanceItem(userId, item["name"]) < item["count"]:
                        succ = False
                        if ftlog.is_debug():
                            ftlog.debug("refreshQuestTaskId ====>", "资源不足", userId, taskId, item["name"], item["count"])
                        break
                else:
                    if not util.consumeItems(userId, cost, "ITEM_USE"):
                        succ = False
                if succ:
                    code = 0
                    gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.refreshDailyQuestTimes, 1)
                    import random
                    new = random.choice(spareQuests)
                    newTaskId = new["taskId"]
                    if str(taskId) in questInfo:
                        questInfo.pop(str(taskId))
                        if ftlog.is_debug():
                            ftlog.debug("refreshQuestTaskId, pop !", userId, taskId, questInfo)
                    questInfo[str(newTaskId)] = [0, QuestTaskState.Normal]
                    setUserQuestInfoData(userId, questInfo)
            else:
                code = 3
        else:
            code = 2
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "refreshQuest")
    mo.setResult("taskId", taskId)
    mo.setResult("code", code)
    mo.setResult("newTaskId", newTaskId)
    dailyQuestData = getDailyQuestData(userId)
    mo.setResult("dailyTask", dailyQuestData)
    router.sendToUser(mo, userId)


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


def _getUserDailyQuestWeeklyRewardKey(userId):
    """
    每日任务星级周奖励领取存档
    {"star": xx, "got": [star1, start2...]}
    """
    return UserData.fishDailyQuestWeeklyReward % (FISH_GAMEID, userId)


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


def _incQuestValue(userId, taskType, incVlaue, resetTime=0, fishPool=0, fpMultiple=0, gunX=0):
    """
    更新每日任务进度并检测；任务是否完成
    """
    if util.getDayStartTimestamp(resetTime) != util.getDayStartTimestamp(int(time.time())):
        resetTime = weakdata.getDayFishData(userId, "resetTime")
        if not resetTime:
            weakdata.setDayFishData(userId, WeakData.resetTime, int(time.time()))
            refreshDailyQuestData(userId)
    key = _getUserDailyQuestKey(userId)
    newValue = daobase.executeUserCmd(userId, "HINCRBY", key, str(taskType), incVlaue)
    confs = config.getDailyQuestConfsByType(taskType)
    todayQuest, _ = getTodayQuest(userId)
    questInfo = getUserQuestInfoData(userId)
    update = False
    for conf in confs:
        if conf and conf["taskId"] in todayQuest:
            if isinstance(conf.get("fishPool"), list) and conf.get("fishPool") and fishPool not in conf.get("fishPool"):
                continue
            if conf.get("fpMultiple", 0) > 0 and fpMultiple < conf.get("fpMultiple", 0):
                continue
            if conf.get("gunX", 0) > 0 and gunX < conf.get("gunX", 0):
                continue
            taskId = conf["taskId"]
            targetsNum = conf.get("targetsNum")
            process, state = questInfo.get(str(taskId), [0, QuestTaskState.Normal])
            # if newValue >= targetsNum and newValue - incVlaue < targetsNum:
            if state == QuestTaskState.Normal:
                update = True
                questInfo[str(taskId)] = [process + incVlaue, state]
                if process < targetsNum <= process + incVlaue:
                    questInfo[str(taskId)] = [targetsNum, QuestTaskState.Complete]
                    quest = todayQuest[taskId]
                    _sendQuestFinished(userId, quest)
                    module_tip.addModuleTipEvent(userId, "task", taskId)
                    taskLevel = conf.get("taskLevel", 0)
                    # questData = getDailyQuestData(userId)
                    # finishedStar = questData.get("finishedStar", 0)
                    # dailyQuestRewardFinishedStars = config.getDailyQuestRewardFinishedStars()
                    # for star in dailyQuestRewardFinishedStars:
                    #     if finishedStar >= star and finishedStar - taskLevel < star:
                    #         module_tip.addModuleTipEvent(userId, "task", star)
                    #         break
                    # 发送完成任务事件
                    from newfish.entity.event import DailyTaskFinishEvent
                    from newfish.game import TGFish
                    event = DailyTaskFinishEvent(userId, FISH_GAMEID, int(conf["taskId"]), taskLevel)
                    TGFish.getEventBus().publishEvent(event)
                    bireport.reportGameEvent("BI_NFISH_GE_TASK_FINISHED", userId, FISH_GAMEID, 0,
                                             0, int(conf["taskId"]), int(taskLevel), 0, 0, [], util.getClientId(userId))
    if update:
        setUserQuestInfoData(userId, questInfo)


def _sendQuestFinished(userId, quest):
    """发送完成的每日任务"""
    level = util.getUserLevel(userId)
    if level < config.getCommonValueByKey("dailyQuestOpenLevel"):
        return
    lang = util.getLanguage(userId)
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "finished")
    mo.setResult("taskId", quest["taskId"])
    # if quest["taskType"] == TaskType.CoinNum and quest["des"].find("%s") >= 0:
    #    des = quest["des"] % util.formatScore(quest["targetsNum"])
    # elif quest["des"].find("%d") >= 0:
    #    des = quest["des"] % quest["targetsNum"]
    # else:
    #    des = quest["des"]
    questDes = config.getMultiLangTextConf(quest["des"], lang=lang)
    if questDes.find("%s") >= 0:
        des = questDes % util.formatScore(quest["targetsNum"], lang=lang)
    elif questDes.find("%d") >= 0:
        des = questDes % quest["targetsNum"]
    elif questDes.count("{}") >= 2:
        des = questDes.format(quest["gunX"], quest["targetsNum"])
    else:
        des = questDes
    mo.setResult("des", des)
    router.sendToUser(mo, userId)


def _getUserQuestData(userId):
    """
    获取玩家每日任务存档
    """
    key = _getUserDailyQuestKey(userId)
    data = daobase.executeUserCmd(userId, "HGETALL", key)
    if not data:
        data = {}
    else:
        info = {}
        for i in range(0, len(data) - 1, 2):
            info[data[i]] = data[i + 1]
        data = info
    return data


def getUserQuestIdData(userId, questIds):
    """
    获取指定任务完成进度
    """
    if not isinstance(questIds, list):
        questIds = [questIds]
    key = _getUserDailyQuestKey(userId)
    data = daobase.executeUserCmd(userId, "HMGET", key, *questIds)
    return data


def _getUserQuestRewardData(userId, _type="day"):
    """
    获取每日任务星级奖励领取情况
    """
    if _type == "day":
        key = _getUserDailyQuestRewardKey(userId)
        allRewarded = daobase.executeUserCmd(userId, "LRANGE", key, 0, -1)
        if not allRewarded:
            allRewarded = []
    else:
        key = _getUserDailyQuestWeeklyRewardKey(userId)
        allRewarded = weakdata.getWeekFishData(userId, key, "{}")
        allRewarded = json.loads(allRewarded).get("got", [])
    return allRewarded


def _insertQuestRewarded(userId, finishStar, _type="day"):
    """
    添加领取对应星级奖励存档
    """
    if _type == "day":
        key = _getUserDailyQuestRewardKey(userId)
        daobase.executeUserCmd(userId, "RPUSH", key, finishStar)
    else:
        key = _getUserDailyQuestWeeklyRewardKey(userId)
        ret = json.loads(weakdata.getWeekFishData(userId, key, "{}"))
        ret.setdefault("got", []).append(finishStar)
        weakdata.setWeekFishData(userId, key, json.dumps(ret))


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


def getQuestTaskId(groupId, lv, gunLevel, userId):
    """
    根据任务分组和难度等级选择任务id
    """
    dayOfWeek = datetime.datetime.now().weekday()
    lv = max(1, lv)
    taskId = 0
    groupLv = 1
    for k, v in config.getDailyQuestConf().iteritems():
        if v.get("groupId") == int(groupId) and (0 in v["showDay"] or (dayOfWeek + 1) in v["showDay"]):
            if v.get("lv") <= lv and v.get("unlockUserLv") <= gunLevel:
                taskId = v.get("taskId")
                groupLv = v.get("lv")
    groupLv = max(1, groupLv)
    return taskId, groupLv


def refreshDailyQuestGroupLv(userId):
    """
    刷新每日任务难度等级
    """
    gunLevel_m = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    curDayStartTs = util.getDayStartTimestamp(int(time.time()))
    initLv = getInitQuestLv(userId)
    dailyQuestConf = config.getDailyQuestConf()
    key = _getUserDailyQuestGroupLvKey(userId)
    groupLvData = gamedata.getGameAttrJson(userId, FISH_GAMEID, key, {})
    questInfo = getUserQuestInfoData(userId)
    for taskId, state in questInfo.iteritems():
        state = state[-1]
        if ftlog.is_debug():
            ftlog.debug("daily_quest, userId =", userId, taskId, state, dailyQuestConf.get(str(taskId), {}))
        groupId = dailyQuestConf.get(str(taskId), {}).get("groupId", 0)
        if groupId:
            groupId = str(groupId)
            if groupId in groupLvData.keys():
                # 玩家没有连续登陆, 清零难度经验进度
                ts = 0
                if len(groupLvData[groupId]) > 2:
                    ts = groupLvData[groupId][2]
                dayStartTs = util.getDayStartTimestamp(ts)
                if dayStartTs + 86400 < curDayStartTs:
                    groupLvData[groupId][1] = 0
                    if ftlog.is_debug():
                        ftlog.debug("daily_quest, userId =", userId, "groupId =", groupId, "reset exp !")
                else:
                    if state >= QuestTaskState.Complete:        # 完成任务增加难度经验
                        if groupLvData[groupId][1] < 2:
                            groupLvData[groupId][1] += 1
                            if ftlog.is_debug():
                                ftlog.debug("daily_quest, userId =", userId, "groupId =", groupId, "increase exp !")
                    else:                                       # 未完成任务, 且前一天游戏时长超过20分钟则削减难度经验
                        _key = GameData.playGameTime % (FISH_GAMEID, userId, dayStartTs)
                        playGameTime = daobase.executeUserCmd(userId, "GET", _key) or 0
                        if playGameTime >= 20:
                            # 降级变更为1天不完成并且游戏时长大于20分钟就降级,即满足要求+1，不满足-2
                            if groupLvData[groupId][1] > -2 and groupLvData[groupId][0] > 1:
                                groupLvData[groupId][1] -= 2    # 1
                                if ftlog.is_debug():
                                    ftlog.debug("daily_quest, userId =", userId, "groupId =", groupId, "decrease exp !")
                    # if groupLvData[groupId][1] >= 2:
                    #     groupLvData[groupId][0] += 1
                    #     groupLvData[groupId][1] = 0
                    #     ftlog.debug("daily_quest, userId =", userId, "groupId =", groupId, "increase lv !")
                    if groupLvData[groupId][1] <= -2 and groupLvData[groupId][0] > 1:
                        groupLvData[groupId][0] -= 1
                        groupLvData[groupId][1] = 0
                        if ftlog.is_debug():
                            ftlog.debug("daily_quest, userId =", userId, "groupId =", groupId, "decrease lv !")
                groupLvData[groupId][2] = curDayStartTs
            else:
                _, lv = getQuestTaskId(groupId, initLv, gunLevel_m, userId)
                groupLvData[groupId] = [lv, 0, curDayStartTs]
            # groupLvData[groupId][0] = min(10, max(1, groupLvData[groupId][0]))
    if len(groupLvData) == 0:
        groupIdList = config.getDailyQuestGroupOrder()
        for groupId in groupIdList:
            _, lv = getQuestTaskId(groupId, initLv, gunLevel_m, userId)
            groupLvData[groupId] = [lv, 0, curDayStartTs]
    else:
        for k in groupLvData.keys():
            groupLvData[k][2] = curDayStartTs
    gamedata.setGameAttr(userId, FISH_GAMEID, key, json.dumps(groupLvData))
    if ftlog.is_debug():
        ftlog.debug("daily_quest, user =", userId, "groupLvData =", groupLvData)


def _incrDailyQuestWeekStar(userId, taskLevel):
    """
    增加每日任务周奖励的星级
    """
    key = _getUserDailyQuestWeeklyRewardKey(userId)
    ret = json.loads(weakdata.getWeekFishData(userId, key, "{}"))
    ret["star"] = ret.get("star", 0) + taskLevel
    weakdata.setWeekFishData(userId, key, json.dumps(ret))
    return ret["star"]


def incrRecharge(userId, rmbs):
    """充值"""
    _incQuestValue(userId, TaskType.TodayRechargeCount, rmbs)


def _processQuestReward(userId, quest):
    """
    处理每日任务奖励数据
    """
    _rewards = []
    for reward in quest.get("rewards", []):
        dropId = reward["name"]
        dropConf = config.getDropConf(dropId)
        if dropConf:
            _, rds = drop_system.getDropItem(dropId)
            rds["count"] *= reward["count"]
            _rewards.append(rds)
    # 普通奖励
    if not _rewards:
        _rewards = quest.get("rewards", [])
    # 宝箱奖励
    if _rewards and util.isChestRewardId(_rewards[0]["name"]):
        from newfish.entity.chest import chest_system
        _rewards = chest_system.getChestRewards(userId, _rewards[0]["name"])

    rewards = []
    for _, reward in enumerate(_rewards):
        if reward["name"] <= 0:
            continue
        rwDict = {}
        rwDict["name"] = reward["name"]
        rwDict["count"] = reward["count"]
        rewards.append(rwDict)
    return rewards


def triggerCatchEvent(event):
    """捕获事件"""
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    typeName = util.getRoomTypeName(event.roomId)
    fishPool = util.getFishPoolByBigRoomId(bigRoomId)
    fpMultiple = event.fpMultiple if hasattr(event, "fpMultiple") else 0
    userId = event.userId
    fishTypes = event.fishTypes
    gain_chip = event.gainChip
    resetTime = event.resetTime
    gunX = event.gunX * event.gunSkinMul

    fish_boss_num = 0
    fish_multiple_num = 0
    terror_num = 0

    all_fish_num = len(fishTypes)
    for fishType in fishTypes:
        fishConf = config.getFishConf(fishType, typeName)
        if fishConf["type"] in config.BOSS_FISH_TYPE:                   # Boss
            fish_boss_num += 1
        elif fishConf["type"] in config.ROBBERY_BOSS_FISH_TYPE:         # 招财Boss
            fish_boss_num += 1
            all_fish_num -= 1
        elif fishConf["type"] in config.MULTIPLE_FISH_TYPE:             # 倍率鱼
            fish_multiple_num += 1
        elif fishConf["type"] in config.ROBBERY_MULTIPLE_FISH_TYPE:     # 招财倍率鱼
            fish_multiple_num += 1
            all_fish_num -= 1
        if fishConf["type"] in config.TERROR_FISH_TYPE:                 # 特殊鱼
            terror_num += 1
    if fish_boss_num:
        _incQuestValue(userId, TaskType.GunYBossFishNum, fish_boss_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple, gunX=gunX)
    if fish_multiple_num:
        _incQuestValue(userId, TaskType.GunYMultipleFishNum, fish_multiple_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple, gunX=gunX)
    if all_fish_num:
        _incQuestValue(userId, TaskType.GunYFishNum, all_fish_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple, gunX=gunX)
        _incQuestValue(userId, TaskType.FishNum, all_fish_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple)
    if gain_chip:
        _incQuestValue(userId, TaskType.CoinNum, gain_chip, resetTime, fishPool=fishPool, fpMultiple=fpMultiple)
    if terror_num:
        _incQuestValue(userId, TaskType.GunYTerrorFishNum, terror_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple, gunX=gunX)
        _incQuestValue(userId, TaskType.TerrorFishNum, terror_num, resetTime, fishPool=fishPool, fpMultiple=fpMultiple)


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


def triggerBuyChestEvent(event):
    """
    购买宝箱事件
    """
    userId = event.userId
    price = event.price
    if int(price) == 0:
        _incQuestValue(userId, TaskType.FreeChest, 1)


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


def triggerUseSkillItemEvent(event):
    """使用冰冻或者所动道具卡"""
    userId = event.userId
    if event.kindId == config.LOCK_KINDID:
        _incQuestValue(userId, TaskType.UseSkillLockItem, 1)
    elif event.kindId == config.FREEZE_KINDID:
        _incQuestValue(userId, TaskType.UseSkillFreezeItem, 1)


def triggerPrizeWheelSpinEvent(event):
    """转动多少次转盘"""
    userId = event.userId
    _incQuestValue(userId, TaskType.LevelPrizeWheel, 1)


def triggerJoinGrandPrixEvent(event):
    """参加大奖赛次数"""
    userId = event.userId
    _incQuestValue(userId, TaskType.JoinGrandPrix, 1)


_inited = False


def initialize():
    ftlog.info("newfish DailyQuest initialize begin")
    global _inited
    if not _inited:
        _inited = True
    ftlog.info("newfish DailyQuest initialize end")
