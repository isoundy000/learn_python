#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/7

import json
import time

from freetime.util import log as ftlog
from poker.util import strutil
from poker.entity.dao import daobase
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util, config, module_tip, weakdata
from newfish.entity.chest import chest_system
from newfish.entity.redis_keys import UserData


class ActivityState:
    """
    活动及其任务的状态
    """
    NotOpen = -1        # 未开启
    Normal = 0          # 已开启
    Complete = 1        # 已完成但未领奖
    Received = 2        # 已领取奖励
    NoCount = 3         # 已领完无剩余
    TodayReceived = 4   # 今日已领取
    Expired = 5         # 已过期


class CodeType:
    """
    领取活动奖励消息code
    """
    Received = 1        # 已领取
    NotComplete = 2     # 未完成
    NoCount = 3         # 已经领完 没有剩余个数


class ActivityErrorCode:
    """
    活动错误code
    """
    Success = 0             # 成功
    Received = 1            # 已领取
    UnComplete = 2          # 未完成
    NoReceiveNum = 3        # 今日无剩余领取次数
    NoReward = 4            # 无奖励
    RewardNumError = 5      # 兑换次数限制
    RewardNotOpen = 6       # 兑换未开启
    Expired = 7             # 已过期
    ConditionNotEnough = 8  # 任务条件不满足
    TodayReceived = 9       # 今日已领取
    OtherError = 99         # 其他错误


# 特殊活动类型
# 1、单张宣传图
# 2、一个按钮
# 3、两个按钮
# 6、海星抽奖
# 14、加群得礼包
# 18、渔友竞技
# 28、版本更新
# 32、公告图
class ActivityType:
    """
    活动类型
    """
    LevelRewards = 4            # 冲级礼包
    Present = 5                 # 渔友互赠
    ItemExchange = 7            # 道具转换
    ExchangeEggs = 8            # 节日彩蛋兑换（已废弃）
    ExchangeEggsTask = 9        # 节日彩蛋任务（已废弃）
    JoinMatchReward = 10        # 宝箱奖励回馈赛
    ChestBuyGift = 11           # 宝箱促销活动
    GameTimeLucky = 12          # 游戏时长抽奖活动
    NewPlayerSevenGift = 13     # 新手七日登录
    LuckyEggsByCatchFish = 15   # 捕鱼得扭蛋、全民打Boss
    CatchItemExchange = 16      # 捕获道具鱼兑换活动（铃铛、海螺、粽子)
    GunSkinTask = 17            # 每日皮肤
    RobberyTask = 19            # 招财任务
    SevenSignInTask = 20        # 七日签到
    ExchangeBonusTask = 21      # 河马活动
    BossCardBonusTask = 22      # 招财转转转（大棋牌插件）
    SummerCatchLuckyEggs = 23   # 夏日捕鱼（已废弃）
    RechargeRebate = 24         # 充值返利
    InviteRebate = 25           # 邀请有礼
    InviteGiveGunSkin = 26      # 邀请送皮肤
    AdLuckDraw = 27             # 广告抽奖
    BulletPoolDouble = 29       # 招财翻翻乐
    OneDayClearAc = 30          # 招财送大奖
    AccumulateRecharge = 31     # 累计充值,五月一充值活动
    DailyRecharge = 33          # 每日充值活动（已废弃）
    XLLevelRewards = 34         # 闲来冲级礼包（已废弃）
    TimingAward = 35            # 定时领奖活动
    SlotMachine = 36            # 老虎机(鸿运当头)活动
    MoneyTree = 37              # 摇钱树活动
    FishCan = 38                # 鱼罐头
    SupplyBox = 39              # 补给箱活动
    SuperEgg = 40               # 超级扭蛋
    Vote = 41                   # 倍率模式投票
    FestivalTurntable = 42      # 节日转盘抽大奖活动
    DailyResetTask = 43         # 每日重置的活动类型
    CollectItemExchange = 44    # 收集道具兑换活动（万圣南瓜)
    CollectItemWinGift = 45     # 收集xx道具赢xx活动(赢永久魅影皮肤)
    DailyResetTaskRandomReward = 46 # 每日重置且奖励个数随机的活动
    Competition = 47            # 竞赛活动
    BigPrize = 48               # 幸运降临活动
    PassCard = 49               # 通行证活动
    BindMobilePhone = 50        # 绑定手机号领奖(百万金币免费领)


# 活动任务类型
class TaskType:
    Default = 0             # 不触发走进度
    LevelUp = 1             # 火炮等级升级
    Autumn = 2              # 中秋活动
    MatchRoom = 3           # 参加比赛
    BuyChest = 4            # 购买宝箱
    CompleteAllGuide = 5    # 完成新手引导
    UsedSkill = 6           # 使用技能
    KillBoss = 7            # 杀死boss
    FishingCoins = 8        # 累计捕鱼获得多少金币
    FishBetFish = 9         # 捕获倍率鱼多少只
    ItemExchange = 10       # 道具兑换
    RobberyTodayTotal = 11  # 今日累计捕鱼数量
    GameTime = 12           # 游戏时长
    ShopBuyBullet = 13      # 在商城购买多少次招财珠商品
    VipUp = 14              # vip升级
    RobberyGainBullet = 15  # 招财模式获得招财珠
    AttackBossNum = 16      # 有效攻击boss数
    LoginNum = 17           # 登陆天数
    ItemBonus = 18          # 道具抽奖
    BossCardGoldType = 19   # 金弹头累计抽奖奖励
    BossCardSilverType = 20 # 银弹头抽奖奖励
    Recharge = 21           # 充值
    InviteFriend = 22       # 邀请新人
    LoginToday = 23         # 今天是否登录
    CatchTargetFishNum = 24 # 捕获xx鱼xx只
    AccumulateRecharge = 25 # 累计充值xx,且达到vip等级xx
    ShopBuy = 26            # 在商城购买xx商品xx次
    CheckIn = 27            # 签到天数
    PrizeWheel = 28         # 在xx场旋转xx次渔场转盘
    EnterRoom = 29          # 进入xx场xx次
    KillCoinValueFish = 30  # 捕获xx金币价值的xx鱼
    WeaponKillCoinValue = 31# 使用xx武器捕获xx金币价值的鱼
    GrandPrixPoint = 32     # 大奖赛单场比赛积分达到xx分
    GrandPrixJoinTime = 33  # 参与大奖赛xx次
    GrandPrixCompleTime = 34# 完成xx次大奖赛
    CollectItem = 35        # 活动中收集xx数量的道具
    CatchMultipleFish = 36  # 捕鱼xx只xx倍的倍率鱼
    BigPrizeTimes = 37      # 幸运降临的次数
    TaskCompleted = 38      # xx任务完成
    HitPoseidon = 39        # 击中波塞冬


# 渔场内频繁更新的任务类型
AcTableTypes = [
    TaskType.UsedSkill,
    TaskType.KillBoss,
    TaskType.FishingCoins,
    TaskType.FishBetFish,
    TaskType.GameTime,
    TaskType.AttackBossNum,
    TaskType.CatchTargetFishNum,
    TaskType.KillCoinValueFish,
    TaskType.WeaponKillCoinValue,
    TaskType.CatchMultipleFish,
    TaskType.BigPrizeTimes
]


AcTaskSortPriority = {
    ActivityState.NotOpen: 2,
    ActivityState.Normal: 1,
    ActivityState.Complete: 0,
    ActivityState.Received: 3,
    ActivityState.NoCount: 3,
    ActivityState.TodayReceived: 3
}


class FishActivity(object):
    """捕鱼活动"""
    def __init__(self, userId, activityId, inTable):
        self._initData(userId, activityId, inTable)
        self.dealActivity()

    def _initData(self, userId, activityId, inTable):
        """初始化数据"""
        self.activityId = activityId
        self.userId = userId
        self.inTable = inTable
        # 玩家语言
        self.lang = util.getLanguage(userId)
        # 活动存档
        self.activityData = self._getActivityData()
        # 活动配置
        self.activityConfig = config.getActivityConfigById(activityId)
        # 活动数据是否需要每日重置
        self.isDailyReset = self.activityConfig.get("isDailyReset", 0)
        # 活动数据是否已重置
        self.isReset = weakdata.getDayFishData(userId, activityId, 0) if self.isDailyReset else 1
        # 活动类型
        self.activityType = self.activityConfig.get("type")
        # 玩家是否在渔场中
        self.isPlayerInTable, _, _, _ = util.isInFishTable(userId)
        # 渔场内任务id
        self.inTableTaskIds = []
        # 渔场外任务id
        self.outTableTaskIds = []
        actTasks = self.activityConfig.get("task")
        if actTasks:
            self.inTableTaskIds = [str(taskId) for taskId, task in actTasks.iteritems() if task["type"] in AcTableTypes]
            self.outTableTaskIds = [str(taskId) for taskId, task in actTasks.iteritems() if task["type"] not in AcTableTypes]
        self.desc = None
        self.timeDesc = None
        if self.activityConfig.get("effectiveTime"):
            self.timeDesc = config.getMultiLangTextConf("ID_ACTIVITY_TIME_DESC_2", lang=self.lang) % (
                self.getTimeDescStr(self.activityConfig["effectiveTime"]["start"]),
                self.getTimeDescStr(self.activityConfig["effectiveTime"]["end"]))
        self.taskIndex = 0

    def _getConfigRewards(self, taskId):
        """获取任务配置奖励"""
        return self.activityConfig["task"][taskId]["reward"], 0

    def getAcImgUrl(self):
        """
        根据客户端类型获取不同背景图
        """
        acImgUrl = ""
        if util.isAppClient(self.userId):
            if self.lang == "en":
                acImgUrl = self.activityConfig.get("acImgEN")
            else:
                acImgUrl = self.activityConfig.get("acImgApp")
        elif util.isChannel(self.userId, "xianlai"):
            acImgUrl = self.activityConfig.get("acImgApp")
        elif util.isChannel(self.userId, "qq"):
            acImgUrl = self.activityConfig.get("acImgQQ")
        return acImgUrl or self.activityConfig["acImg"]

    def getButtonParams(self):
        """
        获取活动按钮参数
        """
        buttonParams = self.activityConfig["buttonParams"]
        if self.lang == "en":
            buttonParams = config.rwcopy(self.activityConfig["buttonParams"])
            for _, _params in enumerate(buttonParams):
                if _params.get("btnStrEN"):
                    _params["btnStr"] = _params.get("btnStrEN")
        return buttonParams

    def getTimeDescStr(self, timeStr):
        """
        获取活动时间描述文本
        """
        intTime = util.getTimestampFromStr(timeStr)
        return util.timestampToStr(intTime, config.getMultiLangTextConf("ID_FORMAT_DATE", lang=self.lang))

    def readActivity(self):
        """
        活动标记为已读状态
        """
        assert (self.activityData)
        self.activityData["read"] = 1
        self.saveActivityData()

    def updateProgress(self, taskId=-1, value=-1):
        pass

    def addProgress(self, taskId, value):
        pass

    def receiveActivityReward(self, taskId=None, extend=None):
        """
        领取活动奖励
        """
        assert (self.activityData)
        if self.activityData["state"] == ActivityState.Normal:
            if isinstance(self.activityConfig.get("extends"), dict):
                self.activityData["state"] = self.activityConfig["extends"].get("receiveState", ActivityState.Normal)
        if self.activityData["state"] == ActivityState.Received:
            return CodeType.Received, []
        if self.activityData["state"] == ActivityState.Complete:
            self.activityData["state"] = ActivityState.Received
            self.activityData["receiveTime"] = int(time.time())
            self.saveActivityData()
            rewards = self.activityConfig["reward"]
            code = util.addRewards(self.userId, rewards, "BI_NFISH_ACTIVITY_REWARDS")
            module_tip.cancelModuleTipEvent(self.userId, "activity", self.activityId)
            return code, rewards
        return CodeType.NotComplete, []

    def getBonusResult(self, count, extend=None):
        return CodeType.NotComplete, None, None

    def isRead(self):
        """
        判断这个活动是否已读
        """
        if self.activityData:
            return True if self.activityData["read"] else False
        return False

    def isCompleted(self):
        """
        判断这个活动是否完成
        """
        if self.activityConfig["reward"] and self.activityData["state"] != ActivityState.Received:
            return True
        return False

    def getButtonInfo(self):
        """
        当前按钮数据
        """
        tasks = self._getTaskData()
        if self.isExpireTime() or tasks is None:
            return None, None
        ac_config = {}
        ac_config["Id"] = self.activityConfig["Id"]
        ac_config["name"] = config.getMultiLangTextConf(self.activityConfig["name"], lang=self.lang)
        ac_config["type"] = self.activityConfig["type"]
        ac_config["tabType"] = self.activityConfig["tabType"]
        ac_config["tabName"] = config.getMultiLangTextConf(self.activityConfig["tabName"], lang=self.lang)
        ac_config["order"] = self.activityConfig["order"]
        ac_config["read"] = self.activityData["read"]
        ac_config["activityTag"] = self.activityConfig["activityTag"]
        return ac_config, tasks

    def getActivityInfo(self, extendKey=0):
        """
        当前活动数据
        """
        ac_config, tasks = self.getButtonInfo()
        if not ac_config:
            return None
        ac_config["clientModel"] = self.activityConfig["clientModel"]
        ac_config["modelUIType"] = self.activityConfig["modelUIType"]
        ac_config["reward"] = self.activityConfig["reward"]
        ac_config["timeDesc"] = self.timeDesc or self.activityConfig["effectiveTime"]
        ac_config["desc"] = self.desc or ""
        ac_config["colors"] = self.activityConfig["colors"]
        ac_config["acImg"] = self.getAcImgUrl()
        ac_config["state"] = self.activityData["state"]
        effectiveTime = []
        if self.activityConfig["effectiveTime"]:
            startTs = util.getTimestampFromStr(self.activityConfig["effectiveTime"]["start"])
            endTs = util.getTimestampFromStr(self.activityConfig["effectiveTime"]["end"])
            effectiveTime = [startTs, endTs]
        ac_config["effectiveTime"] = effectiveTime
        ac_config["timeDesc"] = self.timeDesc or self.activityConfig["effectiveTime"]
        if "realAcTime" in self.activityConfig:
            ac_config["realAcTime"] = self.activityConfig["realAcTime"]
        ac_config["buttonParams"] = self.getButtonParams()
        ac_config["taskIndex"] = self.taskIndex
        ac_config["tasks"] = tasks
        return ac_config

    def updateChangeDayData(self):
        """
        离开渔场时、在渔场内跨天会调用该方法（跨天时需要更新活动数据）
        """
        pass

    def dealActivity(self):
        pass

    def _getActivityKey(self):
        """
        活动数据存档key
        """
        return UserData.activity % (FISH_GAMEID, self.userId)

    def _setActivityData(self, value):
        """
        活动数据保存
        """
        ftlog.debug("_setActivityData-> ", self.userId, self.activityId, value)
        if not self.userId or not value:
            ftlog.warn("_setActivityData->11 ", self.userId, self.activityId, value)
            return
        assert (self.userId and value)
        daobase.executeUserCmd(self.userId, "HSET", self._getActivityKey(), self.activityId, json.dumps(value))

    def _updateTaskState(self, taskId):
        pass

    def saveActivityData(self):
        """
        非渔场内活动数据保存
        """
        if self.inTable:
            return
        self._setActivityData(self.activityData)

    def saveTableActivityData(self):
        """
        保存活动数据时只更新渔场任务相关数据，避免渔场旧的缓存数据把最新数据（由于充值等原因在UT进程更新的数据）覆盖
        """
        self.updateChangeDayData()
        acData = self._getActivityData()
        if self.activityConfig.get("task") and self.activityData.get("task"):
            for taskId in self.activityConfig["task"]:
                if self.activityConfig["task"][taskId]["type"] not in AcTableTypes:
                    continue
                if not acData["task"].get(taskId):
                    acData["task"][taskId] = self.activityData["task"][taskId]
                else:
                    acData["task"][taskId]["progress"] = self.activityData["task"][taskId]["progress"]
                self._updateTaskState(taskId)
                acData["task"][taskId]["state"] = self.activityData["task"][taskId]["state"]
        self._setActivityData(acData)

    def updateRedisAcData(self):
        self.activityData = self._getActivityData()

    def _getTaskData(self):
        """
        获取活动中的任务信息
        """
        tasks = []
        if len(self.activityConfig.get("task", {}).keys()) > 0:
            hasNoReceive = False                                            # 默认全部任务奖励都领取
            for taskId in self.activityConfig["task"]:
                if not self._isTaskVisible(taskId):
                    continue
                item = {}
                stateInfo = self._getTaskState(taskId)
                item["id"] = taskId
                item["type"] = self.activityConfig["task"][taskId]["type"]
                item["reward"] = stateInfo["reward"] if "reward" in stateInfo else self._getTaskReward(taskId)
                item["state"] = stateInfo["state"]
                item["progress"] = stateInfo.get("progress", 0)
                item["value"] = self._getTaskTargetValue(taskId)
                # item["taskDesc"] = self.activityConfig["task"][taskId]["taskDesc"]
                if self.activityConfig["task"][taskId]["taskDesc"]:
                    taskDesc = config.getMultiLangTextConf(self.activityConfig["task"][taskId]["taskDesc"], lang=self.lang)
                    if taskDesc:
                        taskValue = self.activityConfig["task"][taskId]["value"]
                        taskValue = taskValue.get("value", 0) or taskValue.get("count", 0)
                        if taskDesc.find("%s") >= 0:
                            item["taskDesc"] = taskDesc % util.formatScore(taskValue, lang=self.lang)
                        elif taskDesc.find("%d") >= 0:
                            item["taskDesc"] = taskDesc % taskValue
                        else:
                            item["taskDesc"] = taskDesc
                else:
                    item["taskDesc"] = ""
                if self.activityConfig["task"][taskId]["taskImg"]:
                    item["taskImg"] = self.activityConfig["task"][taskId]["taskImg"]
                if self.activityConfig["task"][taskId]["taskDisableImg"]:
                    item["taskDisableImg"] = self.activityConfig["task"][taskId]["taskDisableImg"]
                item["leftNum"] = stateInfo["leftNum"] if "leftNum" in stateInfo else 0
                if "chestInfo" in stateInfo and stateInfo["chestInfo"]:
                    item["chestInfo"] = stateInfo["chestInfo"]
                item["upgradeReward"] = self._getTaskUpgradeReward(taskId)
                if item["state"] != ActivityState.Received:
                    hasNoReceive = True
                tasks.append(item)
            if (not hasNoReceive and not self.activityConfig["receivedVisible"]):
                return None
            if self.activityConfig.get("sort", 0):
                tasks.sort(key=lambda info: (AcTaskSortPriority[info["state"]], info["id"]))
            else:
                tasks = sorted(tasks, key=lambda info: info["id"])
        return tasks

    def _isTaskVisible(self, taskId):
        """
        任务是否有效 （可见）
        """
        return self._isTaskOpen(taskId)

    def _isCanUpdateProgress(self, taskId):
        """
        任务开始走进度 (如第几天激活)
        """
        return True

    def _getTaskTargetValue(self, taskId):
        """
        获取任务目标
        """
        return self.activityConfig["task"][taskId]["value"]

    def _getTaskState(self, taskId):
        """
        获取任务状态
        """
        return {"state": 0, "progress": 0}

    def isExpireTime(self):
        """
        是否过期
        """
        if self.activityConfig["overDay"] > 0:
            currentTime = int(time.time())
            intervals = currentTime - self.activityData.get("receiveTime", currentTime)
            if intervals >= self.activityConfig["overDay"] * 24 * 60 * 60:
                return True
        return False

    def _getTaskReward(self, taskId):
        """
        获取任务奖励
        """
        taskReward, _ = self._getConfigRewards(taskId)
        if isinstance(taskReward, list):
            totalRewards = taskReward
        else:
            totalRewards = [taskReward]
        norReward = []
        chestReward = []
        for reward in totalRewards:
            if not self._isChestReward(reward["name"]):
                norReward.append(reward)
            else:
                chestReward.append(reward)
        norReward = util.buildRewards(norReward)
        norReward.extend(chestReward)
        return norReward

    def _getTaskUpgradeReward(self, taskId):
        """
        获取任务升级后奖励
        """
        return []

    def _getTaskReceiveReward(self, taskId, extend):
        """领取任务奖励"""
        rewardInfos, _ = self._getConfigRewards(taskId)
        rewards = []
        chestId = None
        for reward in rewardInfos:
            itemId = reward["name"]
            if self._isChestReward(itemId):
                chestId = itemId
                rds = chest_system.getChestRewards(self.userId, itemId)
                rewards.extend(rds)
            else:
                rewards.append(reward)
        return rewards, chestId

    def _isChestReward(self, itemId):
        # chestType = int(str(itemId)[0:2])
        # if len(str(itemId)) >= 5 and 31 <= chestType <= 37:
        #     return True
        # return False
        return util.isChestRewardId(itemId)

    def _getTaskDesc(self, desc, target):
        """获取任务描素"""
        strutil.replaceParams(desc, {"num": target})

    def _isTaskOpen(self, taskId):
        """
        活动是否开启 对有前置任务的活动
        """
        if not self.activityData or not self.activityConfig \
                or "task" not in self.activityConfig \
                or taskId not in self.activityConfig["task"]\
                or "frontTasks" not in self.activityConfig["task"][taskId]:
            return False
        frontTasks = self.activityConfig["task"][taskId]["frontTasks"]
        for frontId in frontTasks:
            if str(frontId) in self.activityData["task"] and \
               self.activityData["task"][str(frontId)]["state"] < ActivityState.Received:
                return False
        return True

    def _getActivityData(self):
        """
        活动数据
        """
        value = daobase.executeUserCmd(self.userId, "HGET", self._getActivityKey(), self.activityId)
        ftlog.debug("_getActivityData==>", self.userId, self.activityId, value)
        if value:
            value = strutil.loads(value)
        else:
            value = {"read": 0, "state": 0, "task": {}}
            daobase.executeUserCmd(self.userId, "HSETNX", self._getActivityKey(), self.activityId, json.dumps(value))
        return value

    def _fromStrToJson(self, strInfo):
        try:
            jsStr = json.loads(strInfo)
        except:
            jsStr = strInfo
        return jsStr

    def _isNumber(self, strVal):
        try:
            float(strVal)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(strVal)
            return True
        except (TypeError, ValueError):
            pass

        return False