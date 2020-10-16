# -*- coding=utf-8 -*-
"""
Created by lichen on 2019-06-26.
主线任务
hset
gamedata:44:116009
currSectionId
641000
del
mainQuest:44:116009
del
questType:44:116009
"""

import time
import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import daobase, gamedata, userchip
from poker.util import strutil
from poker.protocol import router
from newfish.entity import config, util, module_tip
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.chest import chest_system
from newfish.entity.skill import skill_system
from newfish.entity.event import MainQuestSectionFinishEvent
from poker.entity.biz import bireport


class QuestIndex:
    """主线索引"""
    State = 0                   # 主线任务状态
    FinishTime = 1              # 主线任务完成时间/奖励领取时间


class SectionIndex:
    """章节索引"""
    FinishTasks = 0             # 已完成的主线任务
    State = 1                   # 章节奖励状态
    FinishTime = 2              # 章节完成时间/奖励领取时间
    TakenStars = 3              # 已领取的星级奖励


class QuestState:
    """主线状态"""
    Default = 0                 # 未完成
    Completed = 1               # 已完成未领取奖励
    Received = 2                # 已领取奖励


class QuestType:
    """主线任务类型"""
    CatchMultipleFish = 10001   # 捕获倍率鱼数量
    CatchBombFish = 10002       # 捕获炸弹鱼数量                       # 炸弹蟹
    CatchDrillFish = 10003      # 捕获钻头鱼数量
    CatchBossFish = 10004       # 捕获Boss数量

    LevelUp = 10007             # 火炮达到指定等级
    SkillLevel16 = 10014        # 拥有xx个16级以上的技能
    AchievementLevel = 10015    # 荣耀任务达到xx级
    UseSkill = 10016            # 使用技能次数

    # 暂时没用的类型
    HoldCoin = 10005            # 持有金币数量
    HoldGoldBullet = 10006      # 持有黄金招财珠数量
    EnterMatch44102 = 10008     # 欢乐竞技参赛次数
    EnterMatch44103 = 10009     # 王者争霸参赛次数
    ReceiveDailyChest = 10010   # 每日任务活跃宝箱领取次数(包含周活跃宝箱)
    ReceiveWeekChest = 10011    # 每日任务周活跃宝箱领取次数
    TableTaskWin = 10012        # 渔场内比赛(夺宝、奖金)胜利次数
    RobberyProfit = 10013       # 单次招财模式赢取招财珠价值

    # 新增加的类型
    CatchCrocodileFish = 10017  # 捕获鳄鱼的数量
    CatchColorGoldFish = 10018  # 捕获彩金鱼的数量
    CatchTentacleFish = 10019   # 捕获巨妖触手
    CatchMermaidFish = 10020    # 捕获美人鱼
    CatchPlatterFish = 10021    # 捕获大盘鱼
    CatchSharkFish = 10022      # 捕获双髻鲨
    CatchTerrorFish = 10023     # 捕获特殊效果鱼 6种鱼[金钱箱、能量宝珠、...]
    CatchSuperBossFish = 10024  # 捕获超级Boss次数
    CatchQueenFish = 10025      # 击破n次深海女王  破盾|捕获都算
    CatchKylinFish = 10026      # 捕获麒麟
    CatchTridentFish = 10027    # 捕获三叉戟
    CatchDragonFish = 10028     # 击破n只远古寒龙
    CatchDragonEggFish = 10029  # 捕获多少个龙蛋
    CatchCrabFish = 10030       # 捕获多少只深渊螃蟹
    CatchBoxFish = 10031        # 捕获多少只宝箱怪
    CatchTurtle = 10032         # 捕获多少只金财富龟
    CatchGotChip = 10033        # 捕获金币的任意鱼   金币量
    CatchFishNum = 10034        # 捕获n条鱼

    BossExchange = 10035        # 进行n次Boss素材兑换
    PlayMiniGame = 10036        # 进行n次Boss小游戏
    HitPoseidon = 10037         # 魔塔命中波塞冬n次
    JoinGrandPrix = 10038       # 参加大奖赛次数
    JoinMatch = 10039           # 参加回馈赛次数
    JoinRobbery = 10040         # 参加多少次招财
    TreasureLevelUp = 10041     # 将任一宝藏升至n级
    SkillStar = 10042           # 技能星级数
    UserLevelUp = 10043         # 玩家等级达到n级
    UseSkillItemLock = 10044    # 使用n次锁定
    LevelPrizeWheel = 10045     # 转盘的转动
    UseSkillItemFreeze = 10046  # 使用n次冰冻


TaskTypeFishTypeMap = {
    QuestType.CatchCrocodileFish:  [11090, 14090],                # 捕获n条鳄鱼
    QuestType.CatchTentacleFish:   [73204, 73205, 73206],         # 巨妖触手
    QuestType.CatchMermaidFish:    [80029],                       # 美人鱼
    QuestType.CatchSharkFish:      [11024, 14024],                # 捕获双髻鲨
    QuestType.CatchQueenFish:      [74207, 74215],                # 捕获深海女王
    QuestType.CatchKylinFish:      [12234],                       # 捕获麒麟
    QuestType.CatchTridentFish:    [78229],                       # 捕获三叉戟
    QuestType.CatchBoxFish:        [71201, 71202, 71203],         # 捕获多少只宝箱怪
    QuestType.CatchDragonFish:     [75208, 75216],                # 击破n只远古寒龙
    QuestType.CatchCrabFish:       [12233],                       # 捕获多少只深渊螃蟹
    QuestType.CatchDragonEggFish:  [75209],                       # 捕获多少个龙蛋
    QuestType.CatchTurtle:         [11231],                       # 捕获多少只金财富龟
}


class MainQuest(object):
    """
    渔场内主线任务
    """
    def __init__(self, player):
        self.player = player
        self.holdCoin = player.holdCoin
        self.refreshCoinTimer = None
        self.refreshTaskTimer = None
        self.currTask = getCurrTaskInfo(self.player.userId)
        self.allHoldCoinTask = config.getMainQuestTasksConfByType(self.player.clientId, QuestType.HoldCoin)
        self.isFinishHoldCoinTask = isFinishAllTask(self.player.userId, QuestType.HoldCoin)
        if not self.isFinishHoldCoinTask:
            # 刷新持有金币任务
            self.refreshCoinTimer = FTLoopTimer(1, -1, self.refreshaHoldCoin)
            self.refreshCoinTimer.start()
            # 刷新任务状态
            self.refreshTaskTimer = FTLoopTimer(60, -1, self.refreshTaskState)
            self.refreshTaskTimer.start()

    def clear(self):
        if self.refreshCoinTimer:
            self.refreshCoinTimer.cancel()
            self.refreshCoinTimer = None
        if self.refreshTaskTimer:
            self.refreshTaskTimer.cancel()
            self.refreshTaskTimer = None

    def dealEnterTable(self, isReconnect):
        """
        进入渔场
        """
        self.refreshTaskState()
        pushCurrTask(self.player.userId)

    def dealLeaveTable(self):
        """
        离开渔场
        """
        self.syncTaskData()
        self.clear()

    def syncTaskData(self):
        """
        同步任务数据
        """
        setQuestTypeData(self.player.userId, QuestType.HoldCoin, self.holdCoin, True)

    def refreshTaskState(self):
        """
        刷新任务状态
        """
        self.syncTaskData()
        self.currTask = getCurrTaskInfo(self.player.userId)
        self.isFinishHoldCoinTask = isFinishAllTask(self.player.userId, QuestType.HoldCoin)
        if self.isFinishHoldCoinTask:
            self.clear()

    def refreshaHoldCoin(self):
        """
        刷新持有金币任务数据
        """
        if self.holdCoin != self.player.holdCoin:
            self.holdCoin = self.player.holdCoin
            finishTask = None
            for taskConf in self.allHoldCoinTask:
                if self.holdCoin >= taskConf["num"]:
                    finishTask = taskConf
            if finishTask:
                self.syncTaskData()
                self.allHoldCoinTask.remove(finishTask)
            if self.currTask and self.currTask["type"] == QuestType.HoldCoin and self.currTask["state"] == QuestState.Default:
                taskConf = config.getMainQuestTaskConf(self.player.clientId, self.currTask["taskId"])
                self.currTask["progress"] = [min(self.holdCoin, taskConf["num"]), taskConf["num"]]
                pushCurrTask(self.player.userId, task=self.currTask)

    def getQuestRewardsInTable(self, taskId):
        """
        在渔场内领取主线任务奖励
        """
        getQuestRewards(self.player.userId, self.player.clientId, taskId)
        self.refreshTaskState()


def _getQuestTypeKey(userId):
    """
    任务类型完成数量存储key
    """
    return UserData.questType % (FISH_GAMEID, userId)


def incrQuestTypeData(userId, questType, value, inTable=False):
    """
    增加任务类型完成数量
    """
    if inTable or not isFinishAllMainQuest(userId):
        totalValue = daobase.executeUserCmd(userId, "HINCRBY", _getQuestTypeKey(userId), questType, value)
        refreshQuestState(userId, questType, totalValue)
        pushCurrTask(userId, questType=questType)


def setQuestTypeData(userId, questType, value, inTable=False):
    """
    设置任务类型完成数量
    """
    if inTable or not isFinishAllMainQuest(userId):
        daobase.executeUserCmd(userId, "HSET", _getQuestTypeKey(userId), questType, value)
        refreshQuestState(userId, questType, value)
        pushCurrTask(userId, questType=questType)


def getQuestTypeData(userId, questType):
    """
    获取该任务类型完成数量
    """
    return daobase.executeUserCmd(userId, "HGET", _getQuestTypeKey(userId), questType) or 0


def _getMainQuestKey(userId):
    """
    主线任务状态数据存储key
    """
    return UserData.mainQuest % (FISH_GAMEID, userId)


def setTask(userId, clientId, taskId, data):
    """
    设置主线任务状态等数据
    """
    daobase.executeUserCmd(userId, "HSET", _getMainQuestKey(userId), taskId, json.dumps(data))
    if data[QuestIndex.State] == QuestState.Received:
        sectionId = getSectionId(taskId)
        sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
        sectionData = getSection(userId, sectionId)
        if taskId not in sectionData[SectionIndex.FinishTasks]:
            sectionData[SectionIndex.FinishTasks].append(taskId)
            # 已完成该章节所有任务，可领取章节奖励
            if len(set(sectionConf["taskIds"]) - set(sectionData[SectionIndex.FinishTasks])) <= 0:
                sectionData[SectionIndex.State] = QuestState.Completed
                sectionData[SectionIndex.FinishTime] = int(time.time())
                module_tip.addModuleTipEvent(userId, "mainquest", sectionId)
            setSection(userId, sectionId, sectionData)


def getTask(userId, taskId):
    """
    获取主线任务状态等数据
    """
    value = daobase.executeUserCmd(userId, "HGET", _getMainQuestKey(userId), taskId)
    if value:
        return strutil.loads(value, False, True)
    return [0, 0]


def setSection(userId, sectionId, data):
    """
    设置主线任务章节任务进度、奖励状态等数据
    """
    daobase.executeUserCmd(userId, "HSET", _getMainQuestKey(userId), sectionId, json.dumps(data))


def getSection(userId, sectionId):
    """
    获取主线任务章节任务进度、奖励状态等数据
    """
    value = daobase.executeUserCmd(userId, "HGET", _getMainQuestKey(userId), sectionId)
    if value:
        ret = strutil.loads(value, False, True)
        if len(ret) <= SectionIndex.TakenStars:
            ret.append([])
        return ret
    return [[], 0, 0, []]


def getSectionId(taskId):
    """
    获取任务ID所属章节ID
    """
    return taskId / 1000 * 1000


def refreshQuestState(userId, questType, totalValue):
    """
    刷新指定任务类型的任务状态
    """
    isComplete = False
    clientId = util.getClientId(userId)
    for taskConf in config.getMainQuestTaskConf(clientId).values():
        if questType == taskConf["type"] and totalValue >= taskConf["num"]:
            state = getTask(userId, taskConf["taskId"])[QuestIndex.State]
            if state == QuestState.Default:
                setTask(userId, clientId, taskConf["taskId"], [QuestState.Completed, int(time.time())])
                isComplete = True
    if isComplete:
        refreshQuestModuleTip(userId, clientId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "task_update")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", util.getClientId(userId))
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)


def refreshQuestModuleTip(userId, clientId):
    """
    刷新当前章节小红点提示数据
    """
    currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)
    if currSectionId:
        sectionConf = config.getMainQuestSectionConf(clientId, currSectionId)
        taskIds = []
        totalStar = _getSectionStar(userId, clientId, currSectionId)
        for _taskId in sectionConf["taskIds"]:
            state = getTask(userId, _taskId)[QuestIndex.State]
            if state == QuestState.Completed:
                taskIds.append(_taskId)
        module_tip.resetModuleTip(userId, "mainquest")
        sectionData = getSection(userId, currSectionId)
        state = sectionData[SectionIndex.State]
        if state == QuestState.Completed:
            module_tip.addModuleTipEvent(userId, "mainquest", currSectionId)
        if taskIds:
            module_tip.addModuleTipEvent(userId, "mainquest", taskIds)
        # 检查主线任务增加的星级能否解锁对应星级奖励.
        for val in sectionConf["starRewards"]:
            if totalStar >= val["star"] and val["star"] not in sectionData[SectionIndex.TakenStars]:
                module_tip.addModuleTipEvent(userId, "mainquest", "star_%d" % val["star"])


def isFinishAllMainQuest(userId):
    """
    是否已完成所有主线任务
    """
    return gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.finishAllMainQuest)    # 1完成


def isFinishAllTask(userId, questType):
    """
    是否已完成指定类型的所有任务
    """
    clientId = util.getClientId(userId)
    for _, taskConf in config.getMainQuestTaskConf(clientId).iteritems():
        if questType == taskConf["type"]:
            state = getTask(userId, taskConf["taskId"])[QuestIndex.State]
            if state == QuestState.Default:
                return False
    return True


def triggerCatchEvent(event):
    """
    捕获鱼事件
    """
    userId = event.userId
    fishTypes = event.fishTypes
    roomId = event.roomId
    typeName = util.getRoomTypeName(roomId)
    if util.isNewbieRoom(typeName):
        return
    gainChip = event.gainChip
    for fishType in fishTypes:
        fishConf = config.getFishConf(fishType, typeName)
        questType = None
        if fishConf["type"] in config.MULTIPLE_FISH_TYPE:       # 倍率鱼
            questType = QuestType.CatchMultipleFish
        elif fishConf["type"] in config.BOMB_FISH_TYPE:         # 炸弹鱼|炸弹蟹
            questType = QuestType.CatchBombFish
        elif fishConf["type"] in config.DRILL_FISH_TYPE:        # 钻头鱼
            questType = QuestType.CatchDrillFish
        elif fishConf["type"] in config.PLATTER_FISH_TYPE:      # 大盘鱼
            questType = QuestType.CatchPlatterFish
        elif fishConf["type"] in config.SUPER_BOSS_FISH_TYPE:   # 超级boss
            questType = QuestType.CatchSuperBossFish

        if questType:
            incrQuestTypeData(userId, questType, 1)

        if fishConf["type"] in config.TERROR_FISH_TYPE:         # 特殊鱼
            incrQuestTypeData(userId, QuestType.CatchTerrorFish, 1)
        if fishConf["type"] in config.COlOR_GOLD_FISH_TYPE:     # 捕获彩金鱼
            incrQuestTypeData(userId, QuestType.CatchColorGoldFish, 1)
        if fishConf["type"] in config.BOSS_FISH_TYPE:           # Boss
            incrQuestTypeData(userId, QuestType.CatchBossFish, 1)

        tmpQuestType = None
        for qt, fishTp in TaskTypeFishTypeMap.items():          # 具体的鱼
            if fishConf["fishType"] in fishTp:
                tmpQuestType = qt
                break
        if tmpQuestType:
            incrQuestTypeData(userId, tmpQuestType, 1)
    if gainChip:
        incrQuestTypeData(userId, QuestType.CatchGotChip, gainChip)
    if len(fishTypes):
        incrQuestTypeData(userId, QuestType.CatchFishNum, len(fishTypes))


def triggerItemChangeEvent(event):
    """
    道具/资产变化事件
    """
    if event.type == 0:
        userId = event.userId
        isIn, _, _, _ = util.isInFishTable(userId)
        if not isIn:
            coin = userchip.getChip(userId)
            setQuestTypeData(userId, QuestType.HoldCoin, coin)
        setQuestTypeData(userId, QuestType.HoldGoldBullet, util.balanceItem(userId, config.GOLD_BULLET_KINDID))


def triggerLevelUpEvent(event):
    """
    火炮等级事件 解锁多少倍炮
    """
    userId = event.userId
    if event.gameMode == config.MULTIPLE_MODE:
        setQuestTypeData(userId, QuestType.LevelUp, util.getGunX(event.gunLevel, event.gameMode))          # 解锁多少被炮


def triggerEnterTableEvent(event):
    """
    进入渔场事件
    """
    if event.reconnect:
        return
    userId = event.userId
    bigRoomId, _ = util.getBigRoomId(event.roomId)
    if bigRoomId in range(44101, 44105):
        incrQuestTypeData(userId, QuestType.JoinMatch, 1)                 # 进入回馈赛多少次
    if bigRoomId == 44102:
        incrQuestTypeData(userId, QuestType.EnterMatch44102, 1)
    elif bigRoomId == 44103:
        incrQuestTypeData(userId, QuestType.EnterMatch44103, 1)
    elif bigRoomId in[44301, 44302]:
        incrQuestTypeData(userId, QuestType.JoinRobbery, 1)               # 进入招财多少次


def triggerGainChestEvent(event):
    """
    宝箱奖励事件
    """
    userId = event.userId
    chestFrom = event.chestFrom
    from newfish.entity.quest import quest_system
    from newfish.entity.chest.chest_system import ChestFromType
    if chestFrom in (ChestFromType.Daily_Quest_Daily_Chest, ChestFromType.Daily_Quest_Week_Chest):
        incrQuestTypeData(userId, QuestType.ReceiveDailyChest, 1)
        if chestFrom == ChestFromType.Daily_Quest_Week_Chest:
            incrQuestTypeData(userId, QuestType.ReceiveWeekChest, 1)
        quest_system.getQuestInfo(userId, util.getClientId(userId))


def triggerWinCmpttTaskEvent(event):
    """
    夺宝赛获胜
    """
    userId = event.userId
    incrQuestTypeData(userId, QuestType.TableTaskWin, 1)


def triggerWinBonusTaskEvent(event):
    """
    奖金赛获胜
    """
    userId = event.userId
    incrQuestTypeData(userId, QuestType.TableTaskWin, 1)


def triggerRobberyBulletProfitEvent(event):
    """
    单次招财模式赢取招财珠对应金币数
    """
    userId = event.userId
    setQuestTypeData(userId, QuestType.RobberyProfit, event.coin)


def triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    userId = event.userId
    clientId = event.clientId
    currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)
    if not currSectionId:
        currSectionId = int(config.getMainQuestSectionConf(clientId).keys()[0])             # 初始化第一章第一节
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.currSectionId, currSectionId)
        sectionConf = config.getMainQuestSectionConf(clientId, currSectionId)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.mainQuestDisplay, sectionConf["display"])
    isIn, _, _, _ = util.isInFishTable(userId)
    if not isIn:
        # setQuestTypeData(userId, QuestType.HoldCoin, userchip.getChip(userId))
        # setQuestTypeData(userId, QuestType.HoldGoldBullet, util.balanceItem(userId, config.GOLD_BULLET_KINDID))
        setQuestTypeData(userId, QuestType.UserLevelUp, gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level))                   # 用户等级
        setQuestTypeData(userId, QuestType.LevelUp, util.getGunX(gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.gunLevel_m), config.MULTIPLE_MODE)) # 皮肤炮等级
        setQuestTypeData(userId, QuestType.AchievementLevel, gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.achievementLevel))   # 荣耀任务等级
        refreshHigherSkillLevel(userId)                                                     # 技能达到16级以上的任务
    refreshQuestModuleTip(userId, clientId)


def triggerAchievementLevelUpEvent(event):
    """
    荣耀任务升级事件
    """
    userId = event.userId
    setQuestTypeData(userId, QuestType.AchievementLevel, gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.achievementLevel))


def triggerSkillLevelUpEvent(event):
    """
    技能升级事件
    """
    userId = event.userId
    refreshHigherSkillLevel(userId)


def triggerUseSkillEvent(event):
    """
    使用技能事件
    """
    userId = event.userId
    roomId = event.roomId
    if util.isNewbieRoom(util.getRoomTypeName(roomId)):
        return
    incrQuestTypeData(userId, QuestType.UseSkill, 1)


def triggerUseSkillItemEvent(event):
    """触发使用道具锁定"""
    userId = event.userId
    if event.kindId == config.LOCK_KINDID:
        incrQuestTypeData(userId, QuestType.UseSkillItemLock, 1)
    elif event.kindId == config.FREEZE_KINDID:
        incrQuestTypeData(userId, QuestType.UseSkillItemFreeze, 1)


def triggerUserLevelUpEvent(event):
    """玩家等级达到n级"""
    userId = event.userId
    setQuestTypeData(userId, QuestType.UserLevelUp, event.level)


def triggerPlayMiniGameEvent(event):
    """玩家完小游戏的次数"""
    userId = event.userId
    count = event.count
    incrQuestTypeData(userId, QuestType.PlayMiniGame, count)


def triggerMiniGameBossExchangeEvent(event):
    """玩家Boss素材兑换"""
    userId = event.userId
    count = event.count
    incrQuestTypeData(userId, QuestType.BossExchange, count)


def triggerHitPoseidonEvent(event):
    """击中波塞冬的次数"""
    userId = event.userId
    count = event.count
    incrQuestTypeData(userId, QuestType.HitPoseidon, count)


def triggerJoinGrandPrixEvent(event):
    """参加大奖赛次数"""
    userId = event.userId
    incrQuestTypeData(userId, QuestType.JoinGrandPrix, 1)


def triggerTreasureLevelUpEvent(event):
    """将任一宝藏升至n级"""
    userId = event.userId
    setQuestTypeData(userId, QuestType.TreasureLevelUp, event.level)


def triggerPrizeWheelSpinEvent(event):
    """转动多少次转盘"""
    userId = event.userId
    incrQuestTypeData(userId, QuestType.LevelPrizeWheel, 1)


def refreshHigherSkillLevel(userId):
    """
    刷新持有技能的等级数据
    """
    levelMap, starMap = skill_system.getHigherSkillLevelInfo(userId)
    # skillCount = levelMap[16]
    # if skillCount > 0:
    setQuestTypeData(userId, QuestType.SkillLevel16, max(levelMap.keys()))
    setQuestTypeData(userId, QuestType.SkillStar, max(starMap.keys()))


def pushCurrTask(userId, questType=None, task=None):
    """
    在渔场中推送当前主线任务
    """
    isIn, _, _, _ = util.isInFishTable(userId)
    if not isFinishAllMainQuest(userId) and isIn:
        task = task or getCurrTaskInfo(userId)
        if (task and questType and questType != task["type"] and task["state"] != QuestState.Completed):
            return
        mo = MsgPack()
        mo.setCmd("currMainTask")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("task", task)
        router.sendToUser(mo, userId)


def getCurrTaskInfo(userId):
    """
    获得当前任务信息
    """
    currSectionId = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.currSectionId)
    if currSectionId:
        clientId = util.getClientId(userId)
        lang = util.getLanguage(userId)
        sectionConf = config.getMainQuestSectionConf(clientId, currSectionId)
        defaultTasks, completeTasks, receiveTasks = [], [], []
        for _taskId in sectionConf.get("taskIds", []):
            taskDict = getTaskInfo(userId, clientId, _taskId, lang)
            if taskDict["state"] == QuestState.Default:
                defaultTasks.append(taskDict)
            elif taskDict["state"] == QuestState.Completed:
                completeTasks.append(taskDict)
            elif taskDict["state"] == QuestState.Received:
                receiveTasks.append(taskDict)
        completeTasks.extend(defaultTasks)
        if completeTasks:
            return completeTasks[0]
    return {}


def getTaskInfo(userId, clientId, taskId, lang):
    """
    获得单个任务信息
    """
    taskConf = config.getMainQuestTaskConf(clientId, taskId)
    state = getTask(userId, taskConf["taskId"])[QuestIndex.State]
    if state == QuestState.Default:
        value = getQuestTypeData(userId, taskConf["type"])
        if taskConf["type"] == QuestType.RobberyProfit:
            value = 0
        if value >= taskConf["num"]:
            state = QuestState.Completed
            setTask(userId, clientId, taskConf["taskId"], [state, int(time.time())])        # 任务完成时间
        progress = [min(value, taskConf["num"]), taskConf["num"]]
    else:
        progress = [taskConf["num"], taskConf["num"]]                                       # 完成的进度
    # 招财珠价值任务客户端使用是否完成显示.
    if taskConf["type"] == QuestType.RobberyProfit and taskConf["num"] != 0:
        progress = [val / taskConf["num"] for val in progress]
    taskDict = {}
    taskDict["taskId"] = taskConf["taskId"]
    taskDict["state"] = state
    taskDict["type"] = taskConf["type"]
    taskDict["title"] = taskConf["title"]
    descId = taskConf["desc"]
    desc = config.getMultiLangTextConf(str(descId), lang=lang)
    if desc:
        taskDict["desc"] = desc % util.formatScore(taskConf["num"], lang=lang) if "%s" in desc else desc
    taskDict["progress"] = progress
    taskDict["normalRewards"] = taskConf["normalRewards"]
    chestRewards = taskConf["chestRewards"]
    taskDict["chestInfo"] = chest_system.getChestInfo(chestRewards[0]["name"]) if chestRewards else {}
    taskDict["taskLevel"] = taskConf["star"]
    return taskDict


def getSectionTasksInfo(userId, sectionId=None):
    """
    获取该章节下的所有任务信息
    """
    sectionId = sectionId or gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.currSectionId)
    tasks = []
    if sectionId:
        clientId = util.getClientId(userId)
        lang = util.getLanguage(userId)
        sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
        for taskId in sectionConf["taskIds"]:
            taskDict = getTaskInfo(userId, clientId, taskId, lang)
            tasks.append(taskDict)
    return tasks


def getMainQuestData(userId, clientId):
    """
    获取主线任务数据
    """
    mainQuestDict = {}
    try:
        if not isFinishAllMainQuest(userId):
            currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)   # 当前章节 642000
            if currSectionId:
                sectionConf = config.getMainQuestSectionConf(clientId, currSectionId)
                finishTaskIds = getSection(userId, currSectionId)[SectionIndex.FinishTasks]
                mainQuestDict["sectionId"] = sectionConf["sectionId"]
                mainQuestDict["sortId"] = sectionConf["sortId"]
                mainQuestDict["progress"] = [len(finishTaskIds), len(sectionConf["taskIds"])]
                # mainQuestDict["honorId"] = sectionConf["honorId"]                             # 勋章Id
                # mainQuestDict["sectionRewards"] = sectionConf["rewards"]                      # 章节奖励
                # mainQuestDict["state"] = getSection(userId, sectionConf["sectionId"])[SectionIndex.State]     # 章节奖励状态
                mainQuestDict["display"] = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.mainQuestDisplay)
                mainQuestDict["tasks"] = getSectionTasksInfo(userId, sectionConf["sectionId"])  # 章节小任务
                starRewards = []
                sectionData = getSection(userId, currSectionId)                                 # 获取章节数据
                gotReward = []
                for val in sectionConf["starRewards"]:
                    chestRewards = []
                    for v in val["rewards"]:
                        itemId = v["itemId"]
                        if util.isChestRewardId(itemId):
                            chestRewards.append({"chestId": itemId, "chestInfo": chest_system.getChestInfo(itemId)})
                    starRewards.append({"rewards": val["rewards"], "finishedStar": val["star"], "chestRewards": chestRewards})
                    if int(val["star"]) in sectionData[SectionIndex.TakenStars]:
                        gotReward.append(int(val["star"]))
                mainQuestDict["rewardData"] = starRewards
                mainQuestDict["finishedStar"] = _getSectionStar(userId, clientId, currSectionId)
                mainQuestDict["gotReward"] = gotReward
    except:
        ftlog.error()
    return mainQuestDict


def setMainQuestDisplay(userId, display):
    """
    设置主线任务是否在渔场显示
    """
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.mainQuestDisplay, display)


def _getSectionStar(userId, clientId, sectionId):
    """
    获取章节总星级 已经完成的任务
    """
    sectionData = getSection(userId, sectionId)
    totalStar = sum([config.getMainQuestTaskConf(clientId, _taskId).get("star", 0) for _taskId in sectionData[SectionIndex.FinishTasks]])
    return totalStar


def getQuestRewards(userId, clientId, taskId):
    """
    领取单个主线任务奖励
    """
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("taskId", taskId)
    mo.setResult("action", "mainReward")
    code = 3
    taskConf = config.getMainQuestTaskConf(clientId, taskId)
    if taskConf:
        state = getTask(userId, taskId)[QuestIndex.State]
        if state == QuestState.Default:
            code = 2
        elif state == QuestState.Received:
            code = 1
        else:
            code = 0
            chestInfo = {}
            rewards = []
            rewards.extend(taskConf["normalRewards"])
            chestRewards = taskConf["chestRewards"]
            if chestRewards:
                chestId = chestRewards[0]["name"]
                chestInfo = chest_system.getChestInfo(chestId)
                _rewards = chest_system.getChestRewards(userId, chestId)
                rewards.extend(_rewards)
            setTask(userId, clientId, taskId, [QuestState.Received, int(time.time())])          # 领取任务奖励
            util.addRewards(userId, rewards, "BI_NFISH_MAIN_QUEST_REWARDS", int(taskId))
            module_tip.cancelModuleTipEvent(userId, "mainquest", taskId)
            # 检查主线任务增加的星级能否解锁对应星级奖励.
            sectionId = getSectionId(taskId)
            sectionData = getSection(userId, sectionId)
            sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
            totalStar = _getSectionStar(userId, clientId, sectionId)
            for val in sectionConf["starRewards"]:
                if totalStar >= val["star"] and val["star"] not in sectionData[SectionIndex.TakenStars]:
                    module_tip.addModuleTipEvent(userId, "mainquest", "star_%d" % val["star"])
            mo.setResult("chestInfo", chestInfo)                                                # 宝箱奖励
            mo.setResult("rewards", rewards)
            bireport.reportGameEvent("BI_NFISH_GE_MAIN_QUEST_TASKID", userId, FISH_GAMEID, 0, 0, 0, 0, 0, 0, [taskId], clientId)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)
    pushCurrTask(userId)


# def getSectionRewards(userId, clientId, sectionId):
#     """
#     领取章节奖励
#     """
#     mo = MsgPack()
#     mo.setCmd("task")
#     mo.setResult("gameId", FISH_GAMEID)
#     mo.setResult("userId", userId)
#     mo.setResult("action", "sectionReward")
#     code = 3
#     sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
#     currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)
#     if sectionConf and sectionId == currSectionId:
#         sectionData = getSection(userId, sectionId)
#         finishTaskIds = sectionData[SectionIndex.FinishTasks]
#         state = sectionData[SectionIndex.State]
#         if len(set(sectionConf["taskIds"]) - set(finishTaskIds)) > 0:
#             code = 2
#         elif state == QuestState.Received:
#             code = 1
#         else:
#             code = 0
#             honorId = sectionConf["honorId"]
#             rewards = sectionConf["rewards"]
#             sectionData[SectionIndex.State] = QuestState.Received
#             sectionData[SectionIndex.FinishTime] = int(time.time())
#             setSection(userId, sectionId, sectionData)
#             util.addRewards(userId, rewards, "BI_NFISH_MAIN_QUEST_REWARDS", int(sectionId))
#             module_tip.cancelModuleTipEvent(userId, "mainquest", sectionId)
#             switchToNextSection(userId, clientId, currSectionId)
#             mo.setResult("honorId", honorId)
#             mo.setResult("rewards", rewards)
#             from newfish.game import TGFish
#             event = MainQuestSectionFinishEvent(userId, FISH_GAMEID, sectionId, honorId)
#             TGFish.getEventBus().publishEvent(event)
#     mo.setResult("code", code)
#     router.sendToUser(mo, userId)
#     pushCurrTask(userId)


def getSectionStarRewards(userId, clientId, sectionId, star):
    """
    领取章节星级奖励
    """
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "sectionStarReward")
    mo.setResult("star", star)
    code = 1
    # honorId = 0
    sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
    currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)
    gotReward = []
    # 检查领取的章节是否为当前生效章节.
    if sectionConf and sectionId == currSectionId:
        sectionData = getSection(userId, sectionId)
        # 检查该星级是否已经领取过.
        star = int(star)
        if star not in sectionData[SectionIndex.TakenStars]:
            starRewards = sectionConf["starRewards"]
            stars = []
            for val in starRewards:
                stars.append(val["star"])
                if val["star"] == star:
                    code = 0
                    rewards = {"name": val["rewards"][0]["itemId"], "count": val["rewards"][0]["count"]}
                    sectionData[SectionIndex.TakenStars].append(star)
                    gotReward = sectionData[SectionIndex.TakenStars]
                    sectionData[SectionIndex.FinishTime] = int(time.time())
                    kindId = rewards["name"]
                    if util.isChestRewardId(kindId):
                        rewards = chest_system.getChestRewards(userId, kindId)
                        chest_system.deliveryChestRewards(userId, kindId, rewards, "BI_NFISH_MAIN_QUEST_STAR_REWARDS", param01=star)
                    else:
                        util.addRewards(userId, [rewards], "BI_NFISH_MAIN_QUEST_STAR_REWARDS", int(sectionId), star)
                    module_tip.cancelModuleTipEvent(userId, "mainquest", "star_%d" % star)
                    mo.setResult("rewards", rewards)
            if code == 0:
                # 章节任务全部完成并且星级奖励全部领取即可跳转章节.
                finishTaskIds = sectionData[SectionIndex.FinishTasks]
                if len(set(sectionConf["taskIds"]) - set(finishTaskIds)) == 0 and len(set(stars) - set(sectionData[SectionIndex.TakenStars])) == 0:
                    # honorId = sectionConf["honorId"]
                    sectionData[SectionIndex.State] = QuestState.Received                           # 领取星级奖励
                    module_tip.cancelModuleTipEvent(userId, "mainquest", sectionId)
                    switchToNextSection(userId, clientId, currSectionId)                            # 解锁下一个章节
                    from newfish.game import TGFish
                    event = MainQuestSectionFinishEvent(userId, FISH_GAMEID, sectionId, currSectionId)
                    TGFish.getEventBus().publishEvent(event)
                setSection(userId, sectionId, sectionData)                                          # 保存当前章节数据
    mo.setResult("code", code)
    mo.setResult("gotReward", gotReward)
    router.sendToUser(mo, userId)
    pushCurrTask(userId)


def switchToNextSection(userId, clientId, currSectionId):
    """
    主线任务切换到下一个章节
    """
    sectionIds = map(int, sorted(config.getMainQuestSectionConf(clientId).keys()))
    if currSectionId == sectionIds[-1]:                                                             # 完成所有的章节任务
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.finishAllMainQuest, 1)
        return
    index = min(sectionIds.index(currSectionId) + 1, len(sectionIds) - 1)
    sectionId = sectionIds[index]
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.currSectionId, sectionId)
    sectionConf = config.getMainQuestSectionConf(clientId, sectionId)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.mainQuestDisplay, sectionConf["display"])    # 是否在渔场中显示
    refreshQuestModuleTip(userId, clientId)


def refreshCurrSectionId(userId, clientId):
    """
    刷新当前主线任务章节ID
    """
    sectionIds = map(int, sorted(config.getMainQuestSectionConf(clientId).keys()))
    currSectionId = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.currSectionId)
    sectionConf = config.getMainQuestSectionConf(clientId, currSectionId)
    if sectionConf and currSectionId != sectionIds[-1]:
        sectionData = getSection(userId, currSectionId)
        finishTaskIds = sectionData[SectionIndex.FinishTasks]
        state = sectionData[SectionIndex.State]
        if len(set(sectionConf["taskIds"]) - set(finishTaskIds)) == 0 and state == QuestState.Received:
            switchToNextSection(userId, clientId, currSectionId)
