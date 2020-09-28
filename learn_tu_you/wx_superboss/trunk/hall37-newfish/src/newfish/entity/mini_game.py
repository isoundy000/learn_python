# -*- coding: utf-8 -*-
"""
Created by zhanglin on：2020-03-20
美人鱼的馈赠和神秘卡牌游戏
"""
import json
import random
from poker.entity.dao import gamedata
import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from newfish.entity.msg import GameMsg
from newfish.entity import change_notify
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID


class MiniGame(object):
    def __init__(self, table, player, miniGameId):
        self.miniGameId = miniGameId
        self.table = table
        self.bigRoomId, _ = util.getBigRoomId(table.roomId)
        self.player = player
        self.conf = config.getMiniGameConf(miniGameId)
        self.minWeaponId = self.conf["minWeaponId"]
        self.minChip = self.conf["minChip"]

    def start(self):
        return {}

    def doAction(self, actType, msg):
        pass

"""    
"miniGame":{
            "28001":{"current": {"cardId":8101, "reward":[1, 2, 1, 3, 2, 2, 3], "locs":[1,9], "totalWin": 0},
            "cardNum": 3, "multi": 3000, "level": 1, "roomId": 28001},
            "28002": {  },
            "history":{"8101": 1}

          }
1: 美人鱼  2 普通  3 女巫


"current": {"cardId":8102, "phase1":{"reward":[1, 2, 4, 3, 5,2,9], "locs":[1,9], "totalWin": 0},
                            "phase2": {"reward": 3, "finish": 0}
            }
"""


class Mermaid(MiniGame):
    """
    美人鱼的馈赠
    """
    def __init__(self, table, player, miniGameId):
        super(Mermaid, self).__init__(table, player, miniGameId)
        self.highRewardProbb = self.conf["highRewardProbb"]
        self.highRewardNum = self.conf["highRewardNum"]
        self.lowRewardProbb = self.conf["lowRewardProbb"]
        self.lowRewardNum = self.conf["lowRewardNum"]
        self.endProbb = self.conf["endProbb"]

    def start(self):
        """
        触发美人鱼的馈赠
        """
        data = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, "miniGame", {})
        roomData = data.get(str(self.bigRoomId))
        playTimes = data.get("history", {}).get(str(self.miniGameId), 0)
        reward = []
        # 第一次触发
        if playTimes == 0:
            reward.append(random.choice([1, 2]))
            tmp = []
            if reward[0] == 1:
                tmp.extend([1] * 2)
                tmp.extend([2] * 3)
            else:
                tmp.extend([2] * 2)
                tmp.extend([1] * 3)
            tmp.append(3)
            random.shuffle(tmp)
            reward.extend(tmp)
            reward.append(3)
        else:
            highP = self.highRewardProbb[1] - self.highRewardProbb[0]
            lowP = self.lowRewardProbb[1] - self.lowRewardProbb[0]
            m = lowP / highP
            m = 1 if m < 1 else m
            rand0 = random.randint(1, m + 1)
            if rand0 == 1:
                reward.append(1)
            else:
                reward.append(2)

            for i in range(11):
                randomx = random.randint(1, 100)
                if self.highRewardProbb[0] <= randomx <= self.highRewardProbb[1]:
                    reward.append(1)
                elif self.lowRewardProbb[0] <= randomx <= self.lowRewardProbb[1]:
                    reward.append(2)
                else:
                    reward.append(3)
        roomData["current"] = {"cardId": self.miniGameId, "reward": reward, "locs": []}
        if "history" not in data:
            data["history"] = {}
        if str(self.miniGameId) not in data["history"]:
            data["history"][str(self.miniGameId)] = 0
        data["history"][str(self.miniGameId)] += 1
        data[str(self.bigRoomId)] = roomData
        gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "miniGame", json.dumps(data))
        return {"reward": reward, "multi": roomData.get("multi", 0)}

    def _rewardLen(self, reward):
        """
        计算包含两个女巫奖励的最短长度
        num3：奖励为女巫的数量
        """
        num3, i = 0, 0
        for i in range(len(reward)):
            if reward[i] == 3:
                num3 += 1
                if num3 == 2:
                    break
        return i + 1

    def doAction(self, actType, msg):
        """
        rw:  1, 2, 3分别表示：美人鱼，金币，女巫
        loc: 金币的位置(0-11)
        """
        if actType == 1:
            reason, rw, chipNum, totalWin, loc  = 0, 0, 0, 0, 0
            data = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, "miniGame", {})
            roomData = data.get(str(self.bigRoomId), {})
            current = roomData.get("current", {})
            cardId = current.get("cardId", 0)
            end = 0
            if cardId != self.miniGameId:
                reason = 1
            else:
                reward = current.get("reward")
                locs = current.get("locs", [])
                if len(locs) >= self._rewardLen(reward):
                    reason = 2
                else:
                    loc = msg.getParam("loc")
                    if loc in locs:
                        reason = 3
                    else:
                        locs.append(loc)
                        roomData["current"]["locs"] = locs
                        multi = roomData["multi"]
                        rw = reward[len(locs) - 1]
                        if len(locs) >= self._rewardLen(reward):
                            end = 1

                        if rw == 1:
                            chipNum = self.highRewardNum * multi
                        elif rw == 2:
                            chipNum = self.lowRewardNum * multi
                        else:
                            chipNum = 0

                        totalWin = roomData["current"].get("totalWin", 0)
                        totalWin += chipNum
                        roomData["current"]["totalWin"] = totalWin
                        if end:
                            if totalWin != 0:
                                rewards = [{"name": 101, "count": totalWin}]
                                code = util.addRewards(self.player.userId, rewards, "BI_NFISH_MINI_GAME_REWARDS",
                                                       int(self.bigRoomId), int(self.miniGameId))
                                if code != 0:
                                    ftlog.error("mini_game_draw, error", self.player.userId, rewards,
                                                int(self.bigRoomId), int(self.miniGameId))
                            del data[str(self.bigRoomId)]
                            self.player.cardNum = 0
                        gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "miniGame", json.dumps(data))
            seatId = msg.getParam("seatId")
            msgRet = MsgPack()
            msgRet.setCmd("mini_game_action")
            msgRet.setResult("actType", actType)
            msgRet.setResult("gameId", FISH_GAMEID)
            msgRet.setResult("seatId", seatId)
            msgRet.setResult("reason", reason)
            if reason == 0:
                msgRet.setResult("reward", rw)
                msgRet.setResult("win", [{"name": 101, "count": chipNum}])
                msgRet.setResult("isEnd", end)
                msgRet.setResult("totalWin", [{"name": 101, "count": totalWin}])
                msgRet.setResult("loc", loc)
            if end:
                GameMsg.sendMsg(msgRet, self.table.getBroadcastUids())
            else:
                GameMsg.sendMsg(msgRet, self.player.userId)
        else:
            ftlog.warn("invalide actType:", msg)


"""
箱子游戏存档结构，phase1表示，选择箱子阶段；phase2表示点击抽奖阶段
"current": {"cardId":8102, 
            "phase1":{"reward":[1, 2, 4, 3, 5,2,9], "locs":[1,9], "totalWin": 0},
            "phase2": {"reward": 3, "finish": 0}
            }
"""


class Roger(MiniGame):
    """
    箱子小游戏
    """
    def __init__(self, table, player, miniGameId):
        super(Roger, self).__init__(table, player, miniGameId)
        self.phase1Conf = self.conf["phase1"]
        self.phase2Conf = self.conf["phase2"]

    def start(self):
        data = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, "miniGame", {})
        roomData = data.get(str(self.bigRoomId))
        reward1 = []

        phase1Probb = self.phase1Conf["probb"]
        phase1Rws = self.phase1Conf["reward"]
        randx = random.randint(1, 10000)
        ind = 0
        for interval in phase1Probb:
            if randx >= interval[0] and randx <= interval[1]:
                reward1.append(phase1Rws[ind])
                break
            else:
                ind += 1

        phase2Probb = self.phase2Conf["probb"]
        randx = random.randint(1, 10000)
        ind = 0
        for interval in phase2Probb:
            if interval[0] <= randx <= interval[1]:
                break
            else:
                ind += 1

        roomData["current"] = {
                               "cardId": self.miniGameId,
                               "phase1": {"reward": reward1, "locs": [], "totalWin": 0},
                               "phase2": {"reward": ind, "finish": 0}
                               }

        if "history" not in data:
            data["history"] = {}
        if str(self.miniGameId) not in data["history"]:
            data["history"][str(self.miniGameId)] = 0
        data["history"][str(self.miniGameId)] += 1
        data[str(self.bigRoomId)] = roomData
        gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "miniGame", json.dumps(data))
        return {"reward1": reward1, "reward2": ind, "multi": roomData.get("multi", 0)}

    def _rewardLen(self, reward):
        i = 0
        for i in range(len(reward)):
            if reward[i] == 0:
                break
        return i + 1

    def doAction(self, actType, msg):
        """
        actType=1表示选择箱子， actType=2表示点击抽奖
        """
        reason, totalWin, reward2Index, chipNum ,end, loc, rw = 0, 0, 0, 0, 0, 0, 0
        data = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, "miniGame", {})
        roomData = data.get(str(self.bigRoomId), {})
        multi = roomData.get("multi", 0)
        current = roomData.get("current", {})
        cardId = current.get("cardId", 0)
        if actType == 1:
            if cardId != self.miniGameId:
                reason = 1
            else:
                phase1 = current.get("phase1")
                reward = phase1.get("reward")
                locs = phase1.get("locs", [])
                if len(locs) >= 1:
                    reason = 2
                else:
                    loc = msg.getParam("loc")
                    locs.append(loc)
                    phase1["locs"] = locs
                    rw = reward[len(locs) - 1]
                    if len(locs) >= self._rewardLen(reward):
                        end = 1
                    chipNum = rw * multi
                    totalWin = phase1.get("totalWin", 0)
                    totalWin += chipNum
                    phase1["totalWin"] = totalWin
                    gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "miniGame", json.dumps(data))
            seatId = msg.getParam("seatId")
            msgRet = MsgPack()
            msgRet.setCmd('mini_game_action')
            msgRet.setResult("actType", actType)
            msgRet.setResult("gameId", FISH_GAMEID)
            msgRet.setResult("reason", reason)
            if reason == 0:
                msgRet.setResult("seatId", seatId)
                msgRet.setResult("reward", rw)
                msgRet.setResult("win", [{"name": 101, "count": chipNum}])
                msgRet.setResult("isEnd", end)
                msgRet.setResult("totalWin", [{"name": 101, "count": totalWin}])
                msgRet.setResult("loc", loc)
            GameMsg.sendMsg(msgRet, self.player.userId)
        elif actType == 2:
            if cardId != self.miniGameId:
                reason = 1
            else:
                phase1 = current.get("phase1")
                reward1 = phase1.get("reward")
                locs = phase1.get("locs", [])
                totalWin = phase1.get("totalWin")
                if len(locs) != self._rewardLen(reward1):
                    reason = 4
                else:
                    phase2 = current.get("phase2")
                    reward2Index = phase2.get("reward")
                    phase2Rws = self.phase2Conf["reward"]
                    reward2 = phase2Rws[reward2Index]
                    tmp = totalWin
                    totalWin = int(totalWin * reward2)
                    rw = totalWin - tmp
                    if totalWin != 0:

                        rewards = [{"name": 101, "count": totalWin}]
                        code = util.addRewards(self.player.userId, rewards, "BI_NFISH_MINI_GAME_REWARDS",
                                               int(self.bigRoomId), int(self.miniGameId))
                        if code != 0:
                            ftlog.error("mini_game_spin, error", self.player.userId, rewards, int(self.bigRoomId),
                                        int(self.miniGameId))
                    del data[str(self.bigRoomId)]
                    self.player.cardNum = 0
                    gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "miniGame", json.dumps(data))
            seatId = msg.getParam("seatId")
            msgRet = MsgPack()
            msgRet.setCmd('mini_game_action')
            msgRet.setResult("actType", actType)
            msgRet.setResult("gameId", FISH_GAMEID)
            msgRet.setResult("reason", reason)
            if reason == 0:
                msgRet.setResult("seatId", seatId)
                msgRet.setResult("reward", reward2Index)
                msgRet.setResult("win", [{"name": 101, "count": rw}])
                msgRet.setResult("totalWin", [{"name": 101, "count": totalWin}])
                GameMsg.sendMsg(msgRet, self.table.getBroadcastUids())
            else:
                GameMsg.sendMsg(msgRet, self.player.userId)

        else:
            ftlog.warn("invalide action:", self.player.userId, msg)


miniGameMap = {
                8101: Mermaid,
                8201: Roger
              }


def createMiniGame(miniGameId, table, player):
    """
    获取小游戏实例
    """
    miniGameClass = miniGameMap.get(miniGameId)
    miniGame = None
    if miniGameClass:
        miniGame = miniGameClass(table, player, miniGameId)
    return miniGame


def addCard(roomId, player, gunM):
    """
    增加卡片数量
    """
    userId = player.userId
    bigRoomId, _ = util.getBigRoomId(roomId)
    miniGameData = gamedata.getGameAttrJson(userId, FISH_GAMEID, "miniGame", {})
    roomData = miniGameData.get(str(bigRoomId))
    if not roomData:
        roomData = {"cardNum": 0, "multi": 0, "roomId": bigRoomId}
        miniGameData[str(bigRoomId)] = roomData

    roomData["cardNum"] += 1
    roomData["multi"] = gunM
    gamedata.setGameAttr(userId, FISH_GAMEID, "miniGame", json.dumps(miniGameData))
    player.cardNum = 1
    return roomData


def miniGameStart(table, player, miniGameLevel, gunM=1):
    """
    开始小游戏
    """
    ret = {"reason": 0}
    bigRoomId, _ = util.getBigRoomId(table.roomId)
    addCard(table.roomId, player, gunM)
    miniGameData = gamedata.getGameAttrJson(player.userId, FISH_GAMEID, "miniGame", {})
    roomData = miniGameData.get(str(bigRoomId))
    if not roomData or roomData.get("cardNum", 0) == 0:
        ret["reason"] = 4
    elif roomData.get("current", {}):
        ret["reason"] = 5
    else:
        miniGameIds = config.getMiniGameLevelIds(miniGameLevel)
        if not miniGameIds:
            ret["reason"] = 6
        else:
            selected = random.choice(miniGameIds)
            if ftlog.is_debug():
                ftlog.debug("miniGameStart", player.userId, miniGameIds, selected, config.miniGameConf, config.miniGameLevelMap)
            conf = config.getMiniGameConf(selected)
            if player.clip * player.fpMultiple + player.tableChip < conf["minChip"]:
                if ftlog.is_debug():
                    ftlog.debug("miniGameStart chip not enough", player.userId, player.chip, conf["minChip"])
                ret["reason"] = 2
            elif "minWeaponId" in conf and player.gunLevel < conf["minWeaponId"]:
                if ftlog.is_debug():
                    ftlog.debug("miniGameStart gunLevel not enough", player.userId, player.gunLevel, conf["minWeaponId"])
                ret["reason"] = 1
            elif "minUserLevel" in conf and player.level < conf["minUserLevel"]:
                if ftlog.is_debug():
                    ftlog.debug("miniGameStart minUserLevel not enough", player.userId, player.level, conf["minUserLevel"])
                ret["reason"] = 3
            else:
                ret["cardId"] = selected
                miniGame = createMiniGame(selected, table, player)
                startRet = miniGame.start()
                ret.update(startRet)
    return ret


def doAction(msg, table, player):
    """
    抽奖或翻硬币，actType=1 表示翻硬币 / 选择箱子； actType=2 表示宝箱抽奖
    """
    miniGameId = msg.getParam("cardId")
    miniGame = createMiniGame(miniGameId, table, player)
    if miniGame:
        actType = msg.getParam("actType", 1)
        miniGame.doAction(actType, msg)
    else:
        ftlog.warn("miniGame doAction error,", msg)


def getRoomMinigame(roomId, userId):
    """
    获取小游戏数据
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    miniGameData = gamedata.getGameAttrJson(userId, FISH_GAMEID, "miniGame", {})
    return miniGameData.get(str(bigRoomId))


def getCardNum(roomId, userId):
    """
    获取玩家卡片数量
    """
    roomData = getRoomMinigame(roomId, userId)
    if not roomData:
        roomData = {}
    return roomData.get("cardNum", 0)


def sendMiniGameProgress(table, userId, roomId):
    """
    发送断线重连后发送进度信息
    """
    roomData = getRoomMinigame(roomId, userId)
    bigRoomId, _ = util.getBigRoomId(roomId)
    if roomData and roomData.get("current", {}):
        locs = roomData.get("current", {}).get("locs", [])
        reward = roomData.get("current", {}).get("reward", [])
        msgRet = MsgPack()
        # 还没有翻完硬币/还未选择箱子
        if len(locs) < len(reward):
            msgRet = MsgPack()
            msgRet.setCmd("mini_game_continue")
            msgRet.setResult("gameState", 1)
            msgRet.setResult("gameId", FISH_GAMEID)
            msgRet.setResult("userId", userId)
            cardId = roomData.get("current", {}).get("cardId", 0)
            msgRet.setResult("locs", locs)
            msgRet.setResult("cardId", cardId)
            msgRet.setResult("reward", reward)
            totalWinCount = roomData.get("current", {}).get("totalWin", 0)
            msgRet.setResult("totalWin", [{"name": 101, "count": totalWinCount}])
        # 已经选择了箱子，但是还没点击转盘抽奖
        elif len(locs) == len(reward):
            msgRet.setCmd("mini_game_continue")
            msgRet.setResult("gameState", 2)
            msgRet.setResult("gameId", FISH_GAMEID)
            msgRet.setResult("userId", userId)
        GameMsg.sendMsg(msgRet, table.getBroadcastUids())
