# -*- coding=utf-8 -*-
"""
Created by zhanglin on 2020/02/06.
红包券抽奖
"""
import json
import time
import random
import copy
import math
import json
from distutils.version import StrictVersion
from poker.entity.dao import daobase, userdata, gamedata
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData, UserData, ABTestData
from newfish.entity.config import FISH_GAMEID

# 红包券抽奖状态
class LTState:
    NOT_DRAW = 0            # 不能抽奖
    CAN_DRAW = 1            # 可抽奖
    NOT_COUNT = 2           # 抽奖次数已经用完


# 红包券存档数据索引
class LTValueIdx:
    STATE = 0             # 红包券抽奖状态
    DRAWCOUNT = 1         # 已抽奖次数
    TAKEN = 2             # 已领取的奖励索引
    REWARD = 3            # 计算好的奖励索引


class LotteryTicket(object):
    default_val = [0, 0, [], []]
    # 红包券抽奖状态，已抽奖次数，已领取的奖励索引，计算好的奖励索引

    def __init__(self, player, fishPool, roomId):
        self.player = player
        self.userId = player.userId
        self.fishPool = fishPool
        self.roomId = roomId
        self.clientId = player.clientId
        self.lang = player.lang
        self.lotteryTicketKey = UserData.lotteryTicketData % (FISH_GAMEID, self.userId)
        self.ltData = {}
        self.lastSendTS = 0
        self.ltConf = config.getLotteryTicActConf(self.clientId)
        self.registeTime = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.registTime)
        self.clientVersion = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.clientVersion)
        self.startTs = util.getTimestampFromStr(self.ltConf.get("startTime", "2020-02-19 00:00:00"))
        self.expireTs = self.registeTime + self.ltConf.get("expire", 0) * 24 * 3600
        self.lastTotalFireCount = -1
        self.lastHasFireCount = -1
        # 服务器主动推送时，cmd由版本号决定；前端请求时，传的cmd是啥就回啥
        if StrictVersion(str(self.clientVersion)) < StrictVersion("2.0.50"):
            self.progressCmd = "lottery_ticket_progress"
        else:
            self.progressCmd = "ticket_progress"
        self.updateCostChipTimer = None
        self.iosClientIds = config.getPublic("multipleLangClientIds", [])
        if self._getData(fishPool)[LTValueIdx.STATE] != LTState.NOT_COUNT and self.effective(str(fishPool)) == 0:
            self.updateCostChipTimer = FTLoopTimer(1, -1, self.sendProgress, 1, "", 0)
            self.updateCostChipTimer.start()

    def clearTimer(self):
        """
        清除定时器
        """
        if self.updateCostChipTimer:
            self.updateCostChipTimer.cancel()
            self.updateCostChipTimer = None

    def effective(self, fishPool):
        """
        检测活动是否有效，code=0活动有效，code=1活动无效
        """
        curTs = int(time.time())
        lowClientVersion = self.ltConf.get("lowClientVersion", "0.0.0")
        code = 1
        if self.startTs < self.registeTime and curTs < self.expireTs and fishPool in self.ltConf.get("showPrize")\
                and self.clientVersion and StrictVersion(str(self.clientVersion)) >= StrictVersion(str(lowClientVersion)):
            code = 0
        return code

    def getLeftTs(self):
        """
        获取活动结束倒计时
        """
        curTs = int(time.time())
        endTs = self.registeTime + self.ltConf.get("expire", 0) * 24 * 3600
        return max(0, endTs - curTs)

    def getFireCount(self):
        """
        获取开火发数
        """
        fishPool = str(self.fishPool)
        ltData = self._getData(fishPool)
        prizeConf = self.getShowPrizeConf(fishPool)
        roomMultiple = prizeConf.get("roomMultiple", 0)
        # 取得当前炮等级
        gunLevel = self.player.nowGunLevel % 100

        costChipConf = self._getCostChip(fishPool, len(ltData[LTValueIdx.TAKEN]))
        totalFireCount = int(math.ceil(costChipConf * 1.0 / (roomMultiple * gunLevel)))
        hasFireCount = int(math.ceil(self.player.lotteryFireCostChip.get(fishPool, 0) * 1.0 / (roomMultiple * gunLevel)))
        rewardConf = self.getRewardConf(fishPool)
        totalDrawCount = rewardConf.get("totalDrawCount", 0)
        if hasFireCount >= totalFireCount:
            if ltData[LTValueIdx.DRAWCOUNT] == totalDrawCount:
                ltData[LTValueIdx.STATE] = LTState.NOT_COUNT
            else:
                ltData[LTValueIdx.STATE] = LTState.CAN_DRAW
            self._setData(fishPool)
        if ftlog.is_debug():
            ftlog.debug("lottery_ticket, userId =", self.userId, "fishPool =", fishPool, "totalFireCount =",
                        totalFireCount, "hasFireCount =", hasFireCount, "gunLevel =", gunLevel)
        return totalFireCount, hasFireCount, max(0, totalFireCount - hasFireCount)

    def getRewardConf(self, fishPool):
        """
        获取红包券奖励配置
        """
        fishPool = str(fishPool)
        return self.ltConf["rewards"].get(fishPool, {})

    def getShowPrizeConf(self, fishPool):
        """
        获取前端显示奖励
        """
        fishPool = str(fishPool)
        return self.ltConf["showPrize"].get(fishPool, {})

    def _getCostChip(self, fishPool, idx):
        """
        获取此次抽奖需要消耗的金币数
        """
        fishPool = str(fishPool)
        costChipConf = self.ltConf["rewards"].get(fishPool, {}).get("costChipList", [])
        try:
            if idx > len(costChipConf) - 1:
                idx = len(costChipConf) - 1
            costChip = costChipConf[idx]
        except:
            ftlog.error("lottery_ticket, userId =", self.userId,
                        "fishPool =", fishPool, "idx =", idx, "costChipConf =", costChipConf)
            costChip = 0
        return costChip

    def draw(self):
        """
        抽奖, 抽奖后应该清空该渔场积攒的能量
        """
        fishPool = str(self.fishPool)
        rewardConf = self.getRewardConf(fishPool)
        rewardListConf = rewardConf.get("rewardList", [])
        totalDrawCount = rewardConf.get("totalDrawCount", 0)
        orderIdx = rewardConf.get("orderIdx", 0)
        ltData = self._getData(fishPool)
        code = 0
        reward = []
        costChip = self._getCostChip(fishPool, len(ltData[LTValueIdx.TAKEN]))
        if ltData[LTValueIdx.DRAWCOUNT] >= totalDrawCount or ltData[LTValueIdx.STATE] != LTState.CAN_DRAW \
                                or self.player.lotteryFireCostChip.get(fishPool, 0) < costChip:
            code = 1
            return code, reward

        if not ltData[LTValueIdx.REWARD]:
            orderRewardList = [x for x in xrange(orderIdx)]
            randomRewardList = [x for x in xrange(orderIdx, totalDrawCount)]
            random.shuffle(randomRewardList)
            rewardList = orderRewardList + randomRewardList
            ltData[LTValueIdx.REWARD] = rewardList
        else:
            if len(ltData[LTValueIdx.REWARD]) != totalDrawCount: # 总抽奖次数发生变化，就再计算一次奖励
                orderRewardList = [x for x in xrange(orderIdx)]
                randomRewardList = [x for x in xrange(orderIdx, totalDrawCount)]
                random.shuffle(randomRewardList)
                rewardList = orderRewardList + randomRewardList
                ltData[LTValueIdx.REWARD] = rewardList

        rewardIdx = ltData[LTValueIdx.DRAWCOUNT]
        reward = [rewardListConf[rewardIdx]]
        util.addRewards(self.userId, reward, "BI_NFISH_LOTTERY_TICKET_REWARDS", int(fishPool))
        ltData[LTValueIdx.DRAWCOUNT] += 1
        ltData[LTValueIdx.TAKEN].append(ltData[LTValueIdx.REWARD][rewardIdx])
        if ltData[LTValueIdx.DRAWCOUNT] == totalDrawCount:
             ltData[LTValueIdx.STATE] = LTState.NOT_COUNT
        else:
            ltData[LTValueIdx.STATE] = LTState.NOT_DRAW
        self._setData(fishPool)
        self.player.lotteryFireCostChip[fishPool] = 0
        ftlog.debug("lottery_ticket_draw userId =", self.userId, "fishPool =", fishPool, "rewardIdx =", rewardIdx,
                    "reward", reward)

        return code, reward

    def sendProgress(self,  isPush, action="", isSend=0):
        """
        发送红包券抽奖积攒进度
        isPush=1表示服务器主动推送，=0表示前端请求
        action: 消息的cmd
        isSend: 为1表示必须回progress， 为0表示可以不回
        """
        fishPool = str(self.fishPool)
        mo = MsgPack()
        if isPush == 1:
            action = self.progressCmd
        mo.setCmd(action)
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("roomId", self.roomId)
        code = self.effective(fishPool)
        if self._isUseOut():
            code = 2
        mo.setResult("code", code)
        if code == 0:
            if isSend == 0:
                totalFireCount, hasFireCount, _ = self.getFireCount()
                if self.lastTotalFireCount != totalFireCount or self.lastHasFireCount != hasFireCount:
                    self.lastTotalFireCount = totalFireCount
                    self.lastHasFireCount = hasFireCount
                else:  # 不开火时，不同步进度
                    return
                mo.setResult("leftTs", self.getLeftTs())
                mo.setResult("accuFireCount", hasFireCount)
                mo.setResult("targetCount", totalFireCount)
                ltData = self._getData(fishPool)
                mo.setResult("state", ltData[LTValueIdx.STATE])
            else:  # 进入渔场一定会发进度消息
                totalFireCount, hasFireCount, _ = self.getFireCount()
                mo.setResult("leftTs", self.getLeftTs())
                mo.setResult("accuFireCount", hasFireCount)
                mo.setResult("targetCount", totalFireCount)
                ltData = self._getData(fishPool)
                mo.setResult("state", ltData[LTValueIdx.STATE])
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("lottery_ticket, userId =", self.userId, "fishPool =", fishPool, "mo =", mo)

    def getLotteryTickInfo(self, action, act=0):
        """
        获取红包券抽奖信息/抽奖
        """
        fishPool = str(self.fishPool)
        mo = MsgPack()
        mo.setCmd(str(action))
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("act", act)
        code = self.effective(fishPool)
        if code == 0:
            _, _, leftFireCount = self.getFireCount()
            if act == 1:    # 抽奖
                code, rewards = self.draw()
                mo.setResult("rewards", rewards)
            ltData = self._getData(fishPool)
            rewardConf = self.getRewardConf(fishPool)
            leftCount = max(0, rewardConf.get("totalDrawCount", 0) - ltData[LTValueIdx.DRAWCOUNT])
            mo.setResult("leftCount", leftCount)
            mo.setResult("state", ltData[LTValueIdx.STATE])
            mo.setResult("leftTs", self.getLeftTs())
            mo.setResult("leftFireCount", leftFireCount)
            ignoreClientIds = config.getCommonValueByKey("ignoreConf")[0].get("clientIds", [])
            if self.clientId in ignoreClientIds:
                mo.setResult("rule", json.loads(config.getMultiLangTextConf(self.ltConf.get("ruleIgnore", ""), lang=self.lang)))
            else:
                mo.setResult("rule", json.loads(config.getMultiLangTextConf(self.ltConf.get("rule", ""), lang=self.lang)))
            prizeConf = self.getShowPrizeConf(fishPool)
            mo.setResult("showPrize", prizeConf.get("prize", []))
            mo.setResult("nextRoomId", prizeConf.get("nextRoomId", 0))
        mo.setResult("code", code)
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("lottery_ticket, userId =", self.userId, "fishPool =", fishPool, "act = ", act,  "mo =", mo)


    def _getData(self, fishPool):
        """
        获取玩家某个渔场的红包券抽奖数据
        """
        fishPool = str(fishPool)
        if fishPool not in self.ltData:
            val = daobase.executeUserCmd(self.userId, "HGET", self.lotteryTicketKey, fishPool)
            val = json.loads(val) if val else copy.deepcopy(self.default_val)
            self.ltData[fishPool] = val
        return self.ltData[fishPool]

    def _isUseOut(self):
        """
        玩家所有的抽奖次数是否已经用完
        """
        fishPoolList = self.ltConf.get("showPrize", {}).keys()
        for _fishPool in fishPoolList:
            if int(_fishPool) != 44001:
                if self._getData(_fishPool)[LTValueIdx.STATE] == LTState.NOT_COUNT:
                    continue
                else:
                    return False
        return True

    def _setData(self, fishPool):
        """
        设置红包券抽奖数据
        """
        fishPool = str(fishPool)
        if self.effective(fishPool) != 0:
            return
        val = self.ltData.get(fishPool)
        if val:
            daobase.executeUserCmd(self.userId, "HSET", self.lotteryTicketKey, fishPool, json.dumps(val))

    def getExchangeInfo(self, action):
        """
        获取兑奖界面信息
        """
        fishPool = str(self.fishPool)
        mo = MsgPack()
        mo.setCmd(str(action))
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        code = self.effective(fishPool)
        mo.setResult("code", code)
        if code == 0:
            ignoreClientIds = config.getCommonValueByKey("ignoreConf")[0].get("clientIds", [])
            if self.clientId in ignoreClientIds:
                exchangeRewardIgnore = self.ltConf.get("exchangeRewardIgnore", {})
                _exchangeRewardIgnore = {
                                          "name": config.getMultiLangTextConf(exchangeRewardIgnore.get("name",""), lang=self.lang),
                                          "id": exchangeRewardIgnore.get("id", 0)
                                        }
                mo.setResult("reward", _exchangeRewardIgnore)
            else:
                exchangeReward = self.ltConf.get("exchangeReward", {})
                _exchangeReward = {
                                    "name": config.getMultiLangTextConf(exchangeReward.get("name",""), lang=self.lang),
                                    "id": exchangeReward.get("id", 0)
                                  }
                mo.setResult("reward", _exchangeReward)
            mo.setResult("leftTs", self.getLeftTs())
            info = []
            fishPoolList = self.ltConf.get("showPrize", {}).keys()
            for _fishPool in fishPoolList:
                if int(_fishPool) != 44001:
                    ltData = self._getData(_fishPool)
                    hasDrawCount = ltData[LTValueIdx.DRAWCOUNT]
                    rewardConf = self.getRewardConf(_fishPool)
                    totalDrawCount = rewardConf.get("totalDrawCount", 0)
                    leftCount = totalDrawCount - hasDrawCount
                    maxPrize = self.ltConf.get("showPrize", {}).get(_fishPool, {}).get("maxPrize", 0)
                    info.append({"leftCount": leftCount, "maxCount": maxPrize, "roomId": rewardConf.get("roomId", 0)})
            mo.setResult("info", info)
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("lottery_ticket, userId =", self.userId, "fishPool =", fishPool, "mo =", mo)


