# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/7/17.
"""

import random
import json
import time
import math
from copy import deepcopy

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import userdata, gamedata, daobase
from poker.entity.configure import gdata
from poker.entity.events.tyevent import EventUserLogin
from hall.entity import hallvip
from newfish.entity import config, util, treasure_system
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.event import TableTaskEndEvent, CatchEvent, \
    NewSkillEvent, RandomChestShareEvent, MatchOverEvent, GameTimeEvent, \
    ShareFinishEvent
from newfish.servers.util.rpc import user_rpc


INDEX_STATE = 0                     # 第0位:当前分享状态
INDEX_MODE = 1                      # 第1位:当前分享模式
INDEX_POP_COUNT = 2                 # 第2位:当前已弹出次数
INDEX_FINISH_COUNT = 3              # 第3位:当前已完成次数
INDEX_FINISH_TIME = 4               # 第4位:上一次完成时间
INDEX_OTHER_DATA = 5                # 第5位:记录奖励等其他数据
DEFAULT_VALUE = [0, 0, 0, 0, 0, {}] # 分享数据默认值


class ShareState:
    """
    分享状态
    """
    Inactive = 0    # 非激活
    Active = 1      # 已激活


class ShareMode:
    """
    分享模式
    """
    Normal = 0      # 普通分享
    Advert = 1      # 广告
    Group = 2       # 群分享
    DifferGroup = 3 # 群分享（不同群）


class ShareExpiresType:
    """
    分享有效期
    """
    Daily = 0       # 每日重置
    Forever = 1     # 永久


class ShareFinishType:
    """
    分享完成类型
    """
    Own = 0         # 自己分享
    Other = 1       # 他人点击


class ShareRewardState:
    """
    分享奖励状态
    """
    Unavailable = 0 # 不可领取
    Available = 1   # 可领取
    Obtained = 2    # 已领取


class PlayerAction:
    """
    玩家行为与信用值增减关系
    """
    GroupShare = -11
    NormalShare = -16
    InviteFriend = 10
    Advert = 0
    DailyLogin = 30


class FishShare(object):
    TYPEID = None           # 类型ID
    ACTIVE_EVENT = None     # 分享激活事件
    EXTEND_EVENT = None     # 分享数据扩展事件

    def __init__(self, userId):
        self.userId = userId
        self.vipLevel = hallvip.userVipSystem.getVipInfo(self.userId).get("level", 0)
        self.level, self.clientVersion = gamedata.getGameAttrs(self.userId, FISH_GAMEID,
                                                               [GameData.level, GameData.clientVersion])
        self.shareConf = config.getShareConf(typeId=self.TYPEID)
        self.lang = util.getLanguage(self.userId)
        data = daobase.executeUserCmd(self.userId, "HGET", _getUserShareDataKey(self.userId), str(self.shareConf["shareId"]))
        self.shareData = strutil.loads(data, False, True, deepcopy(DEFAULT_VALUE))
        self.finishCountLimit = self.shareConf["finishCountLimit"]

    @property
    def isVisible(self):
        """
        分享是否可以显示
        """
        if (self.shareData[INDEX_POP_COUNT] >= self.shareConf["popCountLimit"] or
            self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit or
            not self.isVisibleFromConf):
            return False
        return True

    @property
    def isVisibleFromConf(self):
        """
        分享是否可以显示（配置控制）
        """
        if (self.vipLevel < self.shareConf["vipLimit"] or
            self.level < self.shareConf["levelLimit"]):
            return False
        return True

    @property
    def desc(self):
        """
        分享描述
        """
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            return self.shareConf["desc2"]
            #return config.getMultiLangTextConf(self.shareConf["desc2"], lang=self.lang)
        return self.shareConf["desc1"]
        #return config.getMultiLangTextConf(self.shareConf["desc1"], lang=self.lang)

    @property
    def rewards(self):
        """
        分享奖励
        """
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            return self.shareConf["rewards2"]
        return self.shareConf["rewards1"]

    @property
    def ownRewards(self):
        """
        自己的分享奖励(他人点击分享)
        """
        return self.rewards[0] if len(self.rewards) == 2 else self.rewards

    @property
    def otherRewards(self):
        """
        他人的分享奖励(他人点击分享)
        """
        return self.rewards[1] if len(self.rewards) == 2 else self.rewards

    @property
    def extends(self):
        """
        分享扩展字段
        """
        return {}

    def active(self):
        """
        激活分享
        """
        mode = self.getMode()
        if mode is not None:
            self.shareData[INDEX_STATE] = ShareState.Active
            self.shareData[INDEX_MODE] = mode
            self.shareData[INDEX_POP_COUNT] += 1
            self.saveData()
            if (len(self.shareConf["modes"]) > 1 and self.shareData[INDEX_MODE] != ShareMode.Advert):
                value = PlayerAction.GroupShare if self.shareConf["groupType"] else PlayerAction.NormalShare
                updateCreditValue(self.userId, value)
            return True
        return False

    def getMode(self):
        """
        获得分享模式
        """
        mode = self.shareConf["modes"][0]
        if len(self.shareConf["modes"]) == 1:   # 只有一种分享模式时直接返回，不扣减信用值
            return mode
        if self.shareConf["timeLimit"]:         # 时间范围限制
            startTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][0])
            endTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][1])
            if startTime <= int(time.time()) <= endTime:
                mode = ShareMode.Advert
        if self.shareConf["locationLimit"]:     # 地区限制
            if util.isLocationLimit(self.userId, self.shareConf["locationLimit"]):
                mode = ShareMode.Advert
        if (self.clientVersion in util.getReviewVersionList(self.userId) or
            self.clientVersion in self.shareConf["versionLimit"]):  # 版本限制
            mode = ShareMode.Advert
        creditValue = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.creditValue)
        if creditValue < 10:                    # 信用值限制
            mode = ShareMode.Advert
        if mode not in self.shareConf["modes"]: # 不支持的模式不弹出分享
            mode = None
        return mode

    def finish(self, finishType, invitedUserId):
        """
        完成分享
        """
        if (self.shareData[INDEX_STATE] != ShareState.Active or
            self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit or
            self.shareConf["finishType"] != finishType):
            return
        if finishType == ShareFinishType.Own:
            self.ownFinish()
        elif finishType == ShareFinishType.Other:
            self.otherFinish(invitedUserId)
        self.shareData[INDEX_FINISH_COUNT] += 1
        self.shareData[INDEX_FINISH_COUNT] = min(self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit)
        self.shareData[INDEX_FINISH_TIME] = int(time.time())
        self.saveData()

    def click(self, shareUserId):
        """
        点击分享
        """
        user_rpc.finishShare(shareUserId, self.userId, self.shareConf["shareId"])

    def receiveRewards(self):
        """
        手动领取奖励
        """
        raise NotImplementedError

    def recycle(self):
        """
        回收分享
        """
        raise NotImplementedError

    def saveData(self):
        """
        保存分享数据
        """
        daobase.executeUserCmd(self.userId, "HSET", _getUserShareDataKey(self.userId),
                               str(self.shareConf["shareId"]), json.dumps(self.shareData))

    def addRewards(self, userId=None):
        """
        发放分享奖励
        """
        if not userId:
            userId = self.userId
        if self.rewards:
            util.addRewards(userId, self.rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])

    def ownFinish(self):
        """
        自己分享（分享完成类型）
        """
        self.addRewards()
        msg = MsgPack()
        msg.setCmd("fish_share_rewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("shareId", self.shareConf["shareId"])
        msg.setResult("typeId", self.TYPEID)
        msg.setResult("rewards", self.rewards)
        msg.setResult("extends", self.extends)
        router.sendToUser(msg, self.userId)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            updateCreditValue(self.userId, PlayerAction.Advert)

    def otherFinish(self, invitedUserId):
        """
        他人点击分享（分享完成类型）
        """
        invitedUserIds = self.shareData[INDEX_OTHER_DATA].get("invitedUserIds", [])
        if invitedUserId not in invitedUserIds:
            invitedUserIds.append(invitedUserId)
            self.shareData[INDEX_OTHER_DATA]["invitedUserIds"] = invitedUserIds
            updateCreditValue(self.userId, PlayerAction.InviteFriend)
            # 给他人(被邀请人)发奖
            util.addRewards(invitedUserId, self.otherRewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
            # 给自己(邀请人)发奖
            inviterName = util.getNickname(invitedUserId)
            from newfish.entity import mail_system
            lang = util.getLanguage(self.userId)
            invitedLang = util.getLanguage(invitedUserId)
            message = config.getMultiLangTextConf("ID_INVITE_SUCCESS_REWARD_MEG", lang=lang) % inviterName
            mail_system.sendSystemMail(self.userId, mail_system.MailRewardType.ShareReward, self.ownRewards, message)
            # 给双方发Toast
            toastInfoDict = {
                invitedUserId: config.getMultiLangTextConf("ID_INVITE_SUCCESS_OTHER_TOAST", lang=invitedLang) % util.buildRewardsDesc(self.otherRewards, lang),
                self.userId: config.getMultiLangTextConf("ID_INVITE_SUCCESS_TOAST", lang=lang) % inviterName
            }
            for userId, toastInfo in toastInfoDict.iteritems():
                msg = MsgPack()
                msg.setCmd("fishToast")
                msg.setResult("gameId", FISH_GAMEID)
                msg.setResult("userId", userId)
                msg.setResult("info", toastInfo)
                router.sendToUser(msg, userId)

    def refreshData(self):
        """
        刷新分享数据
        """
        daobase.executeUserCmd(self.userId, "HSETNX", _getUserShareDataKey(self.userId),
                               str(self.shareConf["shareId"]), json.dumps(DEFAULT_VALUE))
        if self.shareConf["expiresType"] == ShareExpiresType.Daily and self.shareData[INDEX_STATE] == ShareState.Active:
            lastTimestamp = self.shareData[INDEX_FINISH_TIME]
            if util.getDayStartTimestamp(int(time.time())) != util.getDayStartTimestamp(lastTimestamp):
                self.resetData()

    def resetData(self):
        """
        重置分享数据
        """
        self.shareData = deepcopy(DEFAULT_VALUE)
        self.saveData()

    @classmethod
    def dealShareEvent(cls, event):
        """
        处理分享激活事件
        """
        if cls.checkActiveConditions(event):
            shareClass = cls(event.userId)
            if shareClass.isVisible and shareClass.active():
                sendShareInfo(event.userId, shareClass.TYPEID)

    @classmethod
    def checkActiveConditions(cls, event):
        """
        检查分享激活条件
        """
        return False

    @classmethod
    def dealShareExtendEvent(cls, event):
        """
        处理分享数据扩展事件
        """
        raise NotImplementedError

    def getShareDetail(self):
        """
        获取分享详情
        """
        shareDetail = {}
        shareDetail["shareId"] = self.shareConf["shareId"]
        shareDetail["typeId"] = self.TYPEID
        shareDetail["title"] = self.shareConf["title"]
        shareDetail["desc"] = self.desc
        shareDetail["mode"] = self.shareData[INDEX_MODE]
        shareDetail["progress"] = [self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit]
        shareDetail["rewards"] = self.rewards
        shareDetail["extends"] = self.extends
        return shareDetail


class FirstLimitTaskFinish(FishShare):
    """
    首次完成限时任务
    """
    TYPEID = "limit_task_finish_1"
    ACTIVE_EVENT = TableTaskEndEvent

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.taskId == 10003:
            return True
        return False


class FirstBucketGold(FishShare):
    """
    第一桶金
    """
    TYPEID = "first_bucket_gold"
    ACTIVE_EVENT = TableTaskEndEvent

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.taskId == 10004:
            return True
        return False


class GunObtain(FishShare):
    """
    分享获得皮肤炮
    """
    TYPEID = "gun_obtain"
    ACTIVE_EVENT = TableTaskEndEvent

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.taskId == 10005:
            return True
        return False


class GunPresent(FishShare):
    """
    赠送皮肤炮
    """
    TYPEID = "gun_present"
    ACTIVE_EVENT = TableTaskEndEvent

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.taskId == 10009:
            return True
        return False

    def otherFinish(self, invitedUserId):
        super(GunPresent, self).otherFinish(invitedUserId)
        from newfish.entity.gun import gun_system
        # TODO.现在仅切换了玩家当前使用的模式对应的炮台。
        gunMode = gamedata.getGameAttr(invitedUserId, FISH_GAMEID, GameData.gunMode)
        gun_system.changeGun(invitedUserId, self.otherRewards[0]["name"], gunMode)


class LimitTaskFail(FishShare):
    """
    任务失败分享加速
    """
    TYPEID = "limit_task_fail"
    ACTIVE_EVENT = TableTaskEndEvent

    def addRewards(self, userId=None):
        isIn, roomId, tableId, seatId = util.isInFishTable(self.userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "task_expedite")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", util.getClientId(self.userId))
            mo.setParam("userId", self.userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("taskExpedite", config.getCommonValueByKey("shareTaskExpedite"))
            router.sendTableServer(mo, roomId)

    @classmethod
    def checkActiveConditions(cls, event):
        if not event.isComplete and event.taskId == 10010:
            return True
        return False


class FirstMultipleFishCatch(FishShare):
    """
    首次捕获倍率鱼
    """
    TYPEID = "multiple_fish_catch_1"
    ACTIVE_EVENT = CatchEvent

    @classmethod
    def checkActiveConditions(cls, event):
        for fishType in event.fishTypes:
            typeName = util.getRoomTypeName(event.roomId)
            if config.getFishConf(fishType, typeName)["type"] in config.MULTIPLE_FISH_TYPE:
                return True
        return False


class Checkin(FishShare):
    """
    每日签到分享
    """
    TYPEID = "checkin"

    @property
    def extends(self):
        # data = {
        #     "kindId": self.shareData[INDEX_OTHER_DATA].get("kindId", 0)
        # }
        data = {k: v for k, v in self.shareData[INDEX_OTHER_DATA].iteritems() if k != "totalRewards"}
        return data

    @property
    def rewards(self):
        return self.shareData[INDEX_OTHER_DATA].get("totalRewards", [])

    def getShareDetail(self):
        from newfish.entity import checkin
        if checkin.getCheckinDay(self.userId):
            self.refreshData()
            self.active()
            # kindId, rewards, _ = checkin.getTodayCheckinRewards(self.userId, True)
            # self.shareData[INDEX_OTHER_DATA]["kindId"] = kindId
            # self.shareData[INDEX_OTHER_DATA]["rewards"] = rewards
            _, totalRewards, rd = checkin.getTodayCheckinRewards(self.userId, True)
            for k, v in rd.iteritems():
                self.shareData[INDEX_OTHER_DATA][k] = v
            self.shareData[INDEX_OTHER_DATA]["totalRewards"] = totalRewards
            self.saveData()
        return super(Checkin, self).getShareDetail()

    def addRewards(self, userId=None):
        from newfish.entity import checkin
        super(Checkin, self).addRewards(userId)
        checkin.finishCheckin(self.userId)

    @classmethod
    def checkActiveConditions(cls, event):
        return True


class CoinStore(FishShare):
    """
    分享获得金币
    """
    TYPEID = "coin_store"

    @classmethod
    def checkActiveConditions(cls, event):
        return True

    def getShareDetail(self):
        self.refreshData()
        self.active()
        return super(CoinStore, self).getShareDetail()

    def finish(self, finishType, invitedUserId):
        super(CoinStore, self).finish(finishType, invitedUserId)
        sendShareInfo(self.userId, self.TYPEID)


class RedOpen(FishShare):
    """
    万元红包立即开启
    """
    TYPEID = "red_open"
    ACTIVE_EVENT = TableTaskEndEvent

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.taskId == 10009:
            return True
        return False


class RandomChest(FishShare):
    """
    随机分享宝箱
    """
    TYPEID = "random_chest"
    ACTIVE_EVENT = CatchEvent
    EXTEND_EVENT = GameTimeEvent

    @property
    def extends(self):
        from newfish.entity.chest import chest_system
        fishType = self.shareData[INDEX_OTHER_DATA].get("fishType", 0)
        rewardData = self.shareConf["rewards1"][str(fishType)]
        data = {
            "state": self.shareData[INDEX_OTHER_DATA].get("state", 0),
            "expiresTime": self.shareData[INDEX_OTHER_DATA].get("expiresTime", 0),
            "info": chest_system.getChestInfo(rewardData["rewards"][0]["name"]),
            "saleRewards": rewardData["sale"]
        }
        return data

    @property
    def rewards(self):
        fishType = self.shareData[INDEX_OTHER_DATA].get("fishType", 0)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            return self.shareConf["rewards2"][str(fishType)]["rewards"]
        return self.shareConf["rewards1"][str(fishType)]["rewards"]

    @classmethod
    def dealShareEvent(cls, event):
        fishType = cls.checkActiveConditions(event)
        if fishType:
            shareClass = cls(event.userId)
            if shareClass.isVisible and shareClass.active():
                shareClass.shareData[INDEX_OTHER_DATA]["fishType"] = fishType
                shareClass.shareData[INDEX_OTHER_DATA]["state"] = ShareRewardState.Unavailable
                shareClass.shareData[INDEX_OTHER_DATA]["expiresTime"] = int(time.time()) + 60
                shareClass.saveData()
                sendShareInfo(event.userId, shareClass.TYPEID)

    @classmethod
    def checkActiveConditions(cls, event):
        for fishType in event.fishTypes:
            typeName = util.getRoomTypeName(event.roomId)
            if config.getFishConf(fishType, typeName)["type"] in config.SHARE_CHEST_FISH_TYPE:
                return fishType
        return 0

    @classmethod
    def dealShareExtendEvent(cls, event):
        if event.isFinishRedTask:
            shareClass = cls(event.userId)
            shareClass.shareData[INDEX_STATE] = ShareState.Active
            playTime = shareClass.shareData[INDEX_OTHER_DATA].get("playTime", 0) + 1
            shareClass.shareData[INDEX_OTHER_DATA]["playTime"] = playTime
            shareClass.shareData[INDEX_OTHER_DATA]["lastTimestamp"] = int(time.time())
            state = shareClass.shareData[INDEX_OTHER_DATA].get("state", 0)
            expiresTime = shareClass.shareData[INDEX_OTHER_DATA].get("expiresTime", 0)
            if time.time() <= expiresTime:
                return
            elif time.time() > expiresTime and state != ShareRewardState.Available:
                shareClass.shareData[INDEX_OTHER_DATA]["state"] = ShareRewardState.Unavailable
            shareClass.refreshData()
            shareClass.saveData()

    def getMode(self):
        """
        获得分享模式
        """
        mode = self.shareConf["modes"][0]
        if len(self.shareConf["modes"]) == 1:   # 只有一种分享模式时直接返回，不扣减信用值
            return mode
        if self.shareConf["timeLimit"]:         # 时间范围限制
            startTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][0])
            endTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][1])
            if startTime <= int(time.time()) <= endTime:
                mode = ShareMode.Advert
        if self.shareConf["locationLimit"]:     # 地区限制
            if util.isLocationLimit(self.userId, self.shareConf["locationLimit"]):
                mode = ShareMode.Advert
        if (self.clientVersion in util.getReviewVersionList(self.userId) or
            self.clientVersion in self.shareConf["versionLimit"]):  # 版本限制
            mode = ShareMode.Advert
        if mode not in self.shareConf["modes"]: # 不支持的模式不弹出分享
            mode = None
        return mode

    def active(self):
        """
        激活分享
        """
        mode = self.getMode()
        if mode is not None:
            self.shareData[INDEX_STATE] = ShareState.Active
            self.shareData[INDEX_MODE] = mode
            self.shareData[INDEX_POP_COUNT] += 1
            self.saveData()
            return True
        return False

    def refreshData(self):
        daobase.executeUserCmd(self.userId, "HSETNX", _getUserShareDataKey(self.userId),
                               str(self.shareConf["shareId"]), json.dumps(DEFAULT_VALUE))
        if self.shareConf["expiresType"] == ShareExpiresType.Daily:
            lastTimestamp = self.shareData[INDEX_OTHER_DATA].get("lastTimestamp", 0)
            expiresTime = self.shareData[INDEX_OTHER_DATA].get("expiresTime", 0)
            state = self.shareData[INDEX_OTHER_DATA].get("state", 0)
            if util.getDayStartTimestamp(int(time.time())) != util.getDayStartTimestamp(lastTimestamp):
                if state != ShareRewardState.Available and time.time() > expiresTime:
                    self.resetData()

    def ownFinish(self):
        state = self.shareData[INDEX_OTHER_DATA].get("state", 0)
        if state == ShareRewardState.Unavailable:
            self.shareData[INDEX_OTHER_DATA]["state"] = ShareRewardState.Available
            self.saveData()
            sendShareInfo(self.userId, self.TYPEID)

    def otherFinish(self, invitedUserId):
        invitedUserIds = self.shareData[INDEX_OTHER_DATA].get("invitedUserIds", [])
        if invitedUserId not in invitedUserIds:
            invitedUserIds.append(invitedUserId)
            self.shareData[INDEX_OTHER_DATA]["invitedUserIds"] = invitedUserIds
            updateCreditValue(self.userId, PlayerAction.InviteFriend)
            state = self.shareData[INDEX_OTHER_DATA].get("state", 0)
            expiresTime = self.shareData[INDEX_OTHER_DATA].get("expiresTime", 0)
            if state == ShareRewardState.Unavailable and time.time() <= expiresTime:
                self.shareData[INDEX_OTHER_DATA]["state"] = ShareRewardState.Available
                self.saveData()
                sendShareInfo(self.userId, self.TYPEID)

    def receiveRewards(self):
        if (self.shareData[INDEX_STATE] != ShareState.Active or
            self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit):
            return
        state = self.shareData[INDEX_OTHER_DATA].get("state", 0)
        if state == ShareRewardState.Available:
            rewards = self.rewards
            if util.isChestRewardId(self.rewards[0]["name"]):
                from newfish.entity.chest import chest_system
                from newfish.entity.chest.chest_system import ChestFromType
                rewards = chest_system.getChestRewards(self.userId, self.rewards[0]["name"])
                chest_system.deliveryChestRewards(self.userId, self.rewards[0]["name"], rewards, "BI_NFISH_SHARE_REWARDS", fromType=ChestFromType.Share_Chest_Fish)
            else:
                util.addRewards(self.userId, self.rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
            msg = MsgPack()
            msg.setCmd("fish_share_rewards")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("shareId", self.shareConf["shareId"])
            msg.setResult("typeId", self.TYPEID)
            msg.setResult("rewards", rewards)
            msg.setResult("extends", self.extends)
            router.sendToUser(msg, self.userId)
            if self.shareData[INDEX_MODE] == ShareMode.Advert:
                updateCreditValue(self.userId, PlayerAction.Advert)
            self.shareData[INDEX_FINISH_COUNT] += 1
            self.shareData[INDEX_FINISH_COUNT] = min(self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit)
            self.shareData[INDEX_FINISH_TIME] = int(time.time())
            self.shareData[INDEX_OTHER_DATA]["state"] = ShareRewardState.Obtained
            self.shareData[INDEX_OTHER_DATA]["playTime"] = 0
            self.saveData()

    def recycle(self):
        """
        回收分享
        """
        fishType = self.shareData[INDEX_OTHER_DATA].get("fishType", 0)
        rewards = self.shareConf["rewards1"][str(fishType)]["sale"]
        if rewards:
            util.addRewards(self.userId, rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
            msg = MsgPack()
            msg.setCmd("fish_share_recycle")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("shareId", self.shareConf["shareId"])
            msg.setResult("typeId", self.TYPEID)
            msg.setResult("rewards", rewards)
            router.sendToUser(msg, self.userId)

    def getShareDetail(self):
        shareDetail = {}
        state = self.shareData[INDEX_OTHER_DATA].get("state", 0)
        expiresTime = self.shareData[INDEX_OTHER_DATA].get("expiresTime", 0)
        if (state == ShareRewardState.Available or
           (state == ShareRewardState.Unavailable and time.time() <= expiresTime)):
            shareDetail["shareId"] = self.shareConf["shareId"]
            shareDetail["typeId"] = self.TYPEID
            shareDetail["title"] = self.shareConf["title"]
            shareDetail["desc"] = self.desc
            shareDetail["mode"] = self.shareData[INDEX_MODE]
            shareDetail["progress"] = [self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit]
            shareDetail["rewards"] = self.rewards
            shareDetail["extends"] = self.extends
        return shareDetail


class BossFishCatch(FishShare):
    """
    捕获BOSS分享
    """
    TYPEID = "boss_fish_catch"
    ACTIVE_EVENT = CatchEvent

    @property
    def extends(self):
        data = {
            "fishType": self.shareData[INDEX_OTHER_DATA].get("fishType", 0)
        }
        return data

    @classmethod
    def dealShareEvent(cls, event):
        fishType = cls.checkActiveConditions(event)
        if fishType:
            shareClass = cls(event.userId)
            if shareClass.isVisible and shareClass.active():
                shareClass.shareData[INDEX_OTHER_DATA]["fishType"] = fishType
                shareClass.saveData()
                sendShareInfo(event.userId, shareClass.TYPEID)

    @classmethod
    def checkActiveConditions(cls, event):
        for fishType in event.fishTypes:
            typeName = util.getRoomTypeName(event.roomId)
            if config.getFishConf(fishType, typeName)["type"] in config.BOSS_FISH_TYPE and util.isFinishAllNewbieTask(event.userId):
                return fishType
        return 0


class MultipleFishCatch(FishShare):
    """
    捕获倍率鱼分享
    """
    TYPEID = "multiple_fish_catch"
    ACTIVE_EVENT = CatchEvent

    @classmethod
    def checkActiveConditions(cls, event):
        for fishType in event.fishTypes:
            typeName = util.getRoomTypeName(event.roomId)
            if config.getFishConf(fishType, typeName)["type"] in config.MULTIPLE_FISH_TYPE and util.isFinishAllNewbieTask(event.userId):
                return True
        return False


class LimitTaskSuccess(FishShare):
    """
    限时任务完成分享双倍奖励
    """
    TYPEID = "limit_task_success"
    ACTIVE_EVENT = TableTaskEndEvent

    @property
    def rewards(self):
        return self.shareData[INDEX_OTHER_DATA].get("rewards", [])

    @classmethod
    def dealShareEvent(cls, event):
        if cls.checkActiveConditions(event):
            shareClass = cls(event.userId)
            if shareClass.isVisible and shareClass.active():
                shareClass.shareData[INDEX_OTHER_DATA]["rewards"] = event.rewards
                shareClass.saveData()
                sendShareInfo(event.userId, shareClass.TYPEID)

    @classmethod
    def checkActiveConditions(cls, event):
        if event.isComplete and event.isLimitTime and event.taskId > 10010:
            return True
        return False


class MatchEnd(FishShare):
    """
    比赛结束分享
    """
    TYPEID = "match_end"
    ACTIVE_EVENT = MatchOverEvent

    @classmethod
    def checkActiveConditions(cls, event):
        return True


class SkillCooldown(FishShare):
    """
    技能刷新CD分享
    """
    TYPEID = "skill_cooldown"

    def getMode(self):
        mode = super(SkillCooldown, self).getMode()
        if self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit:
            mode = ShareMode.Group
        return mode

    def getShareDetail(self):
        self.refreshData()
        self.active()
        return super(SkillCooldown, self).getShareDetail()


class ChestAccelerate(FishShare):
    """
    宝箱加速分享
    """
    TYPEID = "chest_accelerate"

    def getShareDetail(self):
        self.refreshData()
        self.active()
        return super(ChestAccelerate, self).getShareDetail()

    def otherFinish(self, invitedUserId):
        invitedUserIds = self.shareData[INDEX_OTHER_DATA].get("invitedUserIds", []) # 我已经邀请过的人
        if invitedUserId not in invitedUserIds:
            invitedUserIds.append(invitedUserId)
            self.shareData[INDEX_OTHER_DATA]["invitedUserIds"] = invitedUserIds
            updateCreditValue(self.userId, PlayerAction.InviteFriend)
            self.saveData()
            from newfish.entity.chest import chest_system
            chest_system.chestOpeningToOpened(self.userId)


class FlyingPig(FishShare):
    """
    飞猪（金猪）
    """
    TYPEID = "flying_pig"
    EXTEND_EVENT = GameTimeEvent
    DIRECT_COUNT = 3    # 前N次可直接领取

    @property
    def extends(self):
        flyPigFinishCount = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.flyPigFinishCount)
        data = {
            "state": self.shareData[INDEX_OTHER_DATA].get("state", 0),
            "kindId": self.shareData[INDEX_OTHER_DATA].get("kindId", 0),
            "direct": 1 if flyPigFinishCount < self.DIRECT_COUNT else 0     # 金猪分享前N次可直接领取
        }
        return data

    @property
    def rewards(self):
        if self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit:
            return []
        return self.shareData[INDEX_OTHER_DATA].get("rewards", [])

    @classmethod
    def dealShareExtendEvent(cls, event):
        try:
            roomConf = gdata.getRoomConfigure(event.roomId)
            if not roomConf or roomConf.get("typeName") not in config.QUICK_START_ROOM_TYPE:
                return
            if ftlog.is_debug():
                ftlog.debug("dealShareExtendEvent", event.userId)
            shareClass = cls(event.userId)
            if shareClass.shareData[INDEX_FINISH_COUNT] >= shareClass.finishCountLimit:
                return
            shareClass.shareData[INDEX_STATE] = ShareState.Active
            state = shareClass.shareData[INDEX_OTHER_DATA].get("state", 0)
            playTime = shareClass.shareData[INDEX_OTHER_DATA].get("playTime", 0) + 1
            shareClass.shareData[INDEX_OTHER_DATA]["playTime"] = playTime
            if state == 0:  # 金猪不存在
                flyPigFinishCount = gamedata.getGameAttrInt(event.userId, FISH_GAMEID, GameData.flyPigFinishCount)
                # 前N次时间间隔单独处理
                if flyPigFinishCount < len(config.getCommonValueByKey("flyPigInitInterval", [])):
                    appearInterval = config.getCommonValueByKey("flyPigInitInterval")[flyPigFinishCount]
                else:
                    # N次之后时间间隔走统一算法
                    # appearInterval = (2 * shareClass.shareData[INDEX_FINISH_COUNT] + 1) * 60
                    count = shareClass.shareData[INDEX_FINISH_COUNT] + 1
                    appearInterval = 150 * math.exp(0.24 * count)
                if playTime * 60 >= appearInterval: # 达到出现要求
                    if shareClass.isVisible and shareClass.active():
                        shareClass.shareData[INDEX_OTHER_DATA]["state"] = 1
                        # 前N次固定奖励
                        if flyPigFinishCount < len(config.getCommonValueByKey("flyPigInitInterval", [])):
                            rewards = [shareClass.shareConf["rewards1"][shareClass.shareData[INDEX_FINISH_COUNT]]]
                            if shareClass.shareData[INDEX_MODE] == ShareMode.Advert:
                                rewards = [shareClass.shareConf["rewards2"][shareClass.shareData[INDEX_FINISH_COUNT]]]
                        else:
                            # N次之后奖励随机
                            flyPigRewardConf = config.getFlyPigRewardConf(event.fishPool)
                            rewards = shareClass.getRandomRewards(flyPigRewardConf)
                        if rewards:
                            shareClass.shareData[INDEX_OTHER_DATA]["rewards"] = rewards
                            shareClass.shareData[INDEX_OTHER_DATA]["kindId"] = rewards[0]["name"]
                            shareClass.saveData()
                            sendShareInfo(event.userId, shareClass.TYPEID)
                else:
                    shareClass.saveData()
        except Exception as e:
            ftlog.error("dealShareExtendEvent", event.userId, e)

    def active(self):
        """
        激活分享
        """
        mode = self.getMode()
        if mode is not None:
            self.shareData[INDEX_STATE] = ShareState.Active
            self.shareData[INDEX_MODE] = mode
            self.shareData[INDEX_POP_COUNT] += 1
            self.saveData()
            return True
        return False

    def refreshData(self):
        daobase.executeUserCmd(self.userId, "HSETNX", _getUserShareDataKey(self.userId),
                               str(self.shareConf["shareId"]), json.dumps(DEFAULT_VALUE))
        if self.shareConf["expiresType"] == ShareExpiresType.Daily and self.shareData[INDEX_STATE] == ShareState.Active:
            lastTimestamp = self.shareData[INDEX_FINISH_TIME]
            if lastTimestamp and util.getDayStartTimestamp(int(time.time())) != util.getDayStartTimestamp(lastTimestamp):
                self.resetData()

    def getShareDetail(self):
        self.refreshData()
        return super(FlyingPig, self).getShareDetail()

    def ownFinish(self):
        """
        分享/看广告完成，多倍领取
        """
        rewards = []
        for reward in self.rewards:
            item = {}
            item["name"] = reward["name"]
            item["count"] = reward["count"] * reward["multiple"]
            rewards.append(item)
        if not rewards:
            return
        if util.isChestRewardId(rewards[0]["name"]):
            from newfish.entity.chest import chest_system
            from newfish.entity.chest.chest_system import ChestFromType
            rewards = chest_system.getChestRewards(self.userId, rewards[0]["name"])
            chest_system.deliveryChestRewards(self.userId, rewards[0]["name"], rewards, "BI_NFISH_SHARE_REWARDS", fromType=ChestFromType.Fly_Pig_Chest)
        else:
            util.addRewards(self.userId, rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
        msg = MsgPack()
        msg.setCmd("fish_share_rewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("shareId", self.shareConf["shareId"])
        msg.setResult("typeId", self.TYPEID)
        msg.setResult("rewards", rewards)
        msg.setResult("extends", self.extends)
        router.sendToUser(msg, self.userId)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            updateCreditValue(self.userId, PlayerAction.Advert)
        self.shareData[INDEX_OTHER_DATA]["state"] = 0
        self.shareData[INDEX_OTHER_DATA]["playTime"] = 0
        gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.flyPigFinishCount, 1)
        self.saveData()

    def receiveRewards(self):
        """
        普通领取(放弃奖励)
        """
        if (self.shareData[INDEX_STATE] != ShareState.Active or
            self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit):
            return
        if not self.rewards:
            return
        flyPigFinishCount = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.flyPigFinishCount)
        if flyPigFinishCount < self.DIRECT_COUNT:
            reward = self.rewards[0]
            rewards = [{"name": reward["name"], "count": reward["count"]}]
            if reward["saleCoin"] > 0:
                rewards = [{"name": config.CHIP_KINDID, "count": reward["saleCoin"]}]
                self.shareData[INDEX_OTHER_DATA]["kindId"] = config.CHIP_KINDID
            util.addRewards(self.userId, rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
            msg = MsgPack()
            msg.setCmd("fish_share_rewards")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("shareId", self.shareConf["shareId"])
            msg.setResult("typeId", self.TYPEID)
            msg.setResult("rewards", rewards)
            msg.setResult("extends", self.extends)
            router.sendToUser(msg, self.userId)
        self.shareData[INDEX_FINISH_COUNT] += 1
        self.shareData[INDEX_FINISH_COUNT] = min(self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit)
        self.shareData[INDEX_FINISH_TIME] = int(time.time())
        self.shareData[INDEX_OTHER_DATA]["state"] = 0
        self.shareData[INDEX_OTHER_DATA]["playTime"] = 0
        gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.flyPigFinishCount, 1)
        self.saveData()

    def getRandomRewards(self, flyPigRewardConf):
        """
        获得随机奖励
        """
        rewards = []
        randInt = random.randint(1, 10000)
        for item in flyPigRewardConf:
            probb = item["probb"]
            if probb[0] <= randInt <= probb[1]:
                multiple = item["shareMultiple"]
                if self.shareData[INDEX_MODE] == ShareMode.Advert:
                    multiple = item["advertMultiple"]
                rewards = [
                    {
                        "name": item["kindId"],
                        "count": item["displayCount"],
                        "multiple": multiple,
                        "saleCoin": item["saleCoin"]
                    }
                ]
                break
        return rewards


class RedFishCatch(FishShare):
    """
    红包鱼
    """
    TYPEID = "red_fish_catch"
    ACTIVE_EVENT = CatchEvent

    @classmethod
    def checkActiveConditions(cls, event):
        for fishType in event.fishTypes:
            typeName = util.getRoomTypeName(event.roomId)
            if config.getFishConf(fishType, typeName)["type"] in config.SHARE_COUPON_FISH_TYPE:
                return True
        return False

    @classmethod
    def dealShareEvent(cls, event):
        if cls.checkActiveConditions(event):
            shareClass = cls(event.userId)
            if shareClass.isVisible and shareClass.active():
                shareClass.shareData[INDEX_OTHER_DATA] = {}
                bigRoomId, _ = util.getBigRoomId(event.roomId)
                shareClass.shareData[INDEX_OTHER_DATA]["roomId"] = str(bigRoomId)
                # shareClass.shareData[INDEX_OTHER_DATA]["fishPoolMini"] = int(str(fishPool)[-1]) -1
                rewardData = shareClass.getRewardData()
                shareClass.shareData[INDEX_OTHER_DATA]["randomCount"] = random.choice(rewardData["share"]["randomArray"])
                shareClass.saveData()
                sendShareInfo(event.userId, shareClass.TYPEID)

    @property
    def rewards(self):
        rewardData = self.getRewardData()
        return [
            {
                "name": rewardData["share"]["name"],
                "count": self.shareData[INDEX_OTHER_DATA]["randomCount"]
            }
        ]

    @property
    def extends(self):
        rewardData = self.getRewardData()
        roomId = self.shareData[INDEX_OTHER_DATA]["roomId"]
        if not rewardData.get(roomId):
            return {
                "saleRewards": None
            }
        return {
            "saleRewards": {
                "name": rewardData.get(roomId, {}).get("name"),
                "count": rewardData.get(roomId, {}).get("count")
            }
        }

    def getMode(self):
        """
        获得分享模式
        """
        mode = self.shareConf["modes"][0]
        if len(self.shareConf["modes"]) == 1:   # 只有一种分享模式时直接返回，不扣减信用值
            return mode
        if self.shareConf["timeLimit"]:         # 时间范围限制
            startTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][0])
            endTime = util.getTodayTimestampFromStr(self.shareConf["timeLimit"][1])
            if startTime <= int(time.time()) <= endTime:
                mode = ShareMode.Advert
        if self.shareConf["locationLimit"]:     # 地区限制
            if util.isLocationLimit(self.userId, self.shareConf["locationLimit"]):
                mode = ShareMode.Advert
        if (self.clientVersion in util.getReviewVersionList(self.userId) or
            self.clientVersion in self.shareConf["versionLimit"]):  # 版本限制
            mode = ShareMode.Advert
        if mode not in self.shareConf["modes"]: # 不支持的模式不弹出分享
            mode = None
        return mode

    def active(self):
        """
        激活分享
        """
        mode = self.getMode()
        if mode is not None:
            self.shareData[INDEX_STATE] = ShareState.Active
            self.shareData[INDEX_MODE] = mode
            self.shareData[INDEX_POP_COUNT] += 1
            self.saveData()
            return True
        return False

    def getRewardData(self):
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            rewardData = self.shareConf["rewards2"]
        else:
            rewardData = self.shareConf["rewards1"]
        return rewardData

    def addRewards(self, userId=None):
        """
        发放分享奖励
        """
        super(RedFishCatch, self).addRewards(userId)
        for reward in self.rewards:
            if reward["name"] == config.COUPON_KINDID:
                totalEntityAmount = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.totalEntityAmount)
                totalEntityAmount = float(totalEntityAmount) if totalEntityAmount else 0
                totalEntityAmount += reward["count"] * config.COUPON_DISPLAY_RATE
                gamedata.setGameAttr(userId, FISH_GAMEID, GameData.totalEntityAmount, totalEntityAmount)

    def receiveRewards(self):
        """
        出售奖励
        """
        if (self.shareData[INDEX_STATE] != ShareState.Active or
            self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit):
            return
        extends = self.extends["saleRewards"]
        if not extends.get("name") or not extends.get("count"):
            return 
        rewards = [{"name": extends["name"], "count": extends["count"]}]
        util.addRewards(self.userId, rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
        msg = MsgPack()
        msg.setCmd("fish_share_rewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("shareId", self.shareConf["shareId"])
        msg.setResult("typeId", self.TYPEID)
        msg.setResult("rewards", rewards)
        msg.setResult("extends", self.extends)
        router.sendToUser(msg, self.userId)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            updateCreditValue(self.userId, PlayerAction.Advert)
        self.shareData[INDEX_FINISH_COUNT] += 1
        self.shareData[INDEX_FINISH_COUNT] = min(self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit)
        self.shareData[INDEX_FINISH_TIME] = int(time.time())
        self.saveData()


class AlmsCoin(FishShare):
    """
    救济金分享
    """
    TYPEID = "alms_coin"

    def __init__(self, userId):
        super(AlmsCoin, self).__init__(userId)
        self.almsRate = 0
        # self.finishCountLimit += treasure_system.getAlmsCountAdd(self.userId)

    @property
    def extends(self):
        """
        领取救济金前需要等待的时间(秒)
        """
        waitTime = min(120, self.shareData[INDEX_FINISH_COUNT] * 30)
        data = {
            "waitTime": waitTime,
        }
        return data

    @property
    def rewards(self):
        rewards = self.shareConf["rewards1"]
        rewards = config.rwcopy(rewards)
        treasureAlmsCoin = treasure_system.getAlmsCoin(self.userId)
        if treasureAlmsCoin:
            for item in rewards:
                if item["name"] == config.CHIP_KINDID:
                    item["count"] = treasureAlmsCoin
        return rewards
        # vipAlmsRate = config.getVipConf(self.vipLevel).get("almsRate", 0)
        # treasureAlmsRate = treasure_system.getAlmsRateAdd(self.userId)
        # self.almsRate = vipAlmsRate + treasureAlmsRate
        # rewards = self.shareConf["rewards1"]
        # if self.shareData[INDEX_MODE] == ShareMode.Advert:
        #     rewards = self.shareConf["rewards2"]
        # rewards = config.rwcopy(rewards)
        # if self.almsRate > 0:
        #     for item in rewards:
        #         item["count"] = int(self.almsRate * item["count"])
        # return rewards

    @classmethod
    def checkActiveConditions(cls, event):
        return True

    def getShareDetail(self):
        self.refreshData()
        if self.shareConf["rewards1"] and self.shareConf["rewards2"]:
            self.active()
            return super(AlmsCoin, self).getShareDetail()
        else:
            return {}

    def ownFinish(self):
        rewards = []
        for reward in self.rewards:
            item = {}
            item["name"] = reward["name"]
            item["count"] = reward["count"] * reward["multiple"]
            rewards.append(item)
        util.addRewards(self.userId, rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
        msg = MsgPack()
        msg.setCmd("fish_share_rewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("shareId", self.shareConf["shareId"])
        msg.setResult("typeId", self.TYPEID)
        msg.setResult("rewards", rewards)
        msg.setResult("extends", self.extends)
        router.sendToUser(msg, self.userId)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            updateCreditValue(self.userId, PlayerAction.Advert)

    def receiveRewards(self):
        if self.shareData[INDEX_STATE] != ShareState.Active or self.shareData[INDEX_FINISH_COUNT] >= self.finishCountLimit:
            return
        util.addRewards(self.userId, self.rewards, "BI_NFISH_SHARE_REWARDS", self.shareConf["shareId"])
        msg = MsgPack()
        msg.setCmd("fish_share_rewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("shareId", self.shareConf["shareId"])
        msg.setResult("typeId", self.TYPEID)
        msg.setResult("rewards", self.rewards)
        msg.setResult("extends", self.extends)
        router.sendToUser(msg, self.userId)
        if self.shareData[INDEX_MODE] == ShareMode.Advert:
            updateCreditValue(self.userId, PlayerAction.Advert)
        self.shareData[INDEX_FINISH_COUNT] += 1
        self.shareData[INDEX_FINISH_COUNT] = min(self.shareData[INDEX_FINISH_COUNT], self.finishCountLimit)
        self.shareData[INDEX_FINISH_TIME] = int(time.time())
        self.saveData()

class FreeCoinLuckyTree(FishShare):
    """
    分享获得金币
    """
    TYPEID = "free_coin_lucky_tree"

    @classmethod
    def checkActiveConditions(cls, event):
        return True

    def getShareDetail(self):
        self.refreshData()
        self.active()
        return super(FreeCoinLuckyTree, self).getShareDetail()

def _getUserShareDataKey(userId):
    return UserData.share % (FISH_GAMEID, userId)


def sendShareInfo(userId, typeId, extends=None):
    """
    发送分享详情
    """
    if typeId in allTypeIdClass:
        shareClass = allTypeIdClass[typeId](userId)
        if shareClass.isVisibleFromConf:
            msg = MsgPack()
            msg.setCmd("fish_share_info")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", userId)
            msg.setResult("share", shareClass.getShareDetail())
            msg.setResult("extends", extends or {})
            router.sendToUser(msg, userId)


def updateCreditValue(userId, value):
    """
    更新分享信用值
    """
    creditValue = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.creditValue)
    creditValue += value
    creditValue = min(max(0, creditValue), 100)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.creditValue, creditValue)


def finishShare(userId, shareId, finishType=ShareFinishType.Own, invitedUserId=None):
    """
    完成分享
    :param userId: 分享人
    :param shareId: 分享ID
    :param finishType: 分享类型
    :param invitedUserId: 邀请到的人
    """
    shareMode = ShareMode.Normal
    typeId = config.getShareConf(shareId).get("typeId")
    if typeId in allTypeIdClass:
        shareClass = allTypeIdClass[typeId](userId)
        shareClass.finish(finishType, invitedUserId)
        shareMode = shareClass.shareData[INDEX_MODE]
    if finishType == ShareFinishType.Own:
        from newfish.game import TGFish
        event = ShareFinishEvent(userId, FISH_GAMEID, shareId, typeId, shareMode)
        TGFish.getEventBus().publishEvent(event)


def clickShare(userId, shareId, shareUserId):
    """
    被邀请人点击分享
    :param userId: 被邀请人
    :param shareId: 分享ID
    :param shareUserId: 分享人
    """
    typeId = config.getShareConf(shareId).get("typeId")
    if typeId in allTypeIdClass:
        shareClass = allTypeIdClass[typeId]
        shareClass(userId).click(shareUserId)


def receiveShareRewards(userId, shareId):
    """
    用户手动领取分享奖励
    """
    typeId = config.getShareConf(shareId).get("typeId")
    if typeId in allTypeIdClass:
        shareClass = allTypeIdClass[typeId]
        shareClass(userId).receiveRewards()


def recycleShare(userId, shareId):
    """
    回收分享
    """
    typeId = config.getShareConf(shareId).get("typeId")
    if typeId in allTypeIdClass:
        shareClass = allTypeIdClass[typeId]
        shareClass(userId).recycle()


def _triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    gamedata.setnxGameAttr(event.userId, FISH_GAMEID, GameData.creditValue, 100)
    for _, shareClass in allTypeIdClass.iteritems():
        shareClass(event.userId).refreshData()
    if event.dayFirst:
        updateCreditValue(event.userId, PlayerAction.DailyLogin)


def _triggerDealShareEvent(event):
    """
    触发分享弹出检测
    """
    for _, shareClass in allTypeIdClass.iteritems():
        if shareClass.ACTIVE_EVENT and isinstance(event, shareClass.ACTIVE_EVENT):
            shareClass.dealShareEvent(event)


def _triggerDealShareExtendEvent(event):
    """
    触发分享扩展数据变更
    """
    for _, shareClass in allTypeIdClass.iteritems():
        if shareClass.EXTEND_EVENT and isinstance(event, shareClass.EXTEND_EVENT):
            shareClass.dealShareExtendEvent(event)


_inited = False
allTypeIdClass = {
    GunObtain.TYPEID: GunObtain,
    GunPresent.TYPEID: GunPresent,
    Checkin.TYPEID: Checkin,
    CoinStore.TYPEID: CoinStore,
    RandomChest.TYPEID: RandomChest,
    BossFishCatch.TYPEID: BossFishCatch,
    MultipleFishCatch.TYPEID: MultipleFishCatch,
    LimitTaskSuccess.TYPEID: LimitTaskSuccess,
    SkillCooldown.TYPEID: SkillCooldown,
    ChestAccelerate.TYPEID: ChestAccelerate,
    FlyingPig.TYPEID: FlyingPig,
    RedFishCatch.TYPEID: RedFishCatch,
    AlmsCoin.TYPEID: AlmsCoin,
    FreeCoinLuckyTree.TYPEID: FreeCoinLuckyTree
}


def initialize():
    ftlog.debug("newfish share_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.game import TGFish
        # TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        # TGFish.getEventBus().subscribe(TableTaskEndEvent, _triggerDealShareEvent)
        # TGFish.getEventBus().subscribe(CatchEvent, _triggerDealShareEvent)
        # TGFish.getEventBus().subscribe(NewSkillEvent, _triggerDealShareEvent)
        # TGFish.getEventBus().subscribe(RandomChestShareEvent, _triggerDealShareEvent)
        # TGFish.getEventBus().subscribe(MatchOverEvent, _triggerDealShareEvent)
        # TGFish.getEventBus().subscribe(GameTimeEvent, _triggerDealShareExtendEvent)
    ftlog.debug("newfish share_system initialize end")
