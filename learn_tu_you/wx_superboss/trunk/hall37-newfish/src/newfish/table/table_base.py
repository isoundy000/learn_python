#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8


import random
import time
import json
import traceback
from copy import deepcopy
from distutils.version import StrictVersion

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.support.tcpagent import wrapper
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata, userdata, userchip
from poker.entity.game.tables.table import TYTable
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity import datachangenotify
from newfish.entity import config, util, weakdata, drop_system, treasure_system, user_system
from newfish.entity.config import FISH_GAMEID, CHIP_KINDID, COUPON_KINDID, STARFISH_KINDID, \
    PEARL_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, BRONZE_BULLET_KINDID, BULLET_KINDIDS
from newfish.entity.event import CatchEvent, EnterTableEvent, LeaveTableEvent, CheckLimitTimeGiftEvent
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.normal_fish_group import NormalFishGroup
from newfish.entity.fishgroup import superboss_fish_group
from newfish.entity.msg import GameMsg
from newfish.entity.skill import skill_release
from newfish.entity.gun import gun_system
from newfish.servers.util.rpc import user_rpc
from newfish.player.player_base import FishPlayer
from newfish.table.table_conf import FishTableConf
from newfish.robot import robotutil
from newfish.entity.honor import honor_system
from newfish.entity.fish_cost_benefit_module import FishCostBenefitModule
from newfish.entity.grand_prize_pool import GrandPrizePool
from newfish.entity.task.task_system_table import TaskSystemTable
from newfish.entity.quest import quest_system
from newfish.entity.redis_keys import GameData
from newfish.entity.lottery_ticket import LTState, LTValueIdx
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity import mini_game


class FishTable(TYTable):

    def __init__(self, room, tableId):
        super(FishTable, self).__init__(room, tableId)
        self.clear()
        # 状态检查间隔时间
        self._checkStateSeconds = 60
        # 用户离线等待时间
        self._offlineWaitSeconds = 60
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 180      # 300 3分钟
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 180  # 60 3分钟
        # 渔场内任务系统
        self.taskSystemTable = None
        # 游戏模式(经典/千炮)
        # self._gameMode = config.CLASSIC_MODE
        self._gameMode = config.CLASSIC_MODE if self.typeName == config.FISH_FRIEND else config.MULTIPLE_MODE
        # 鱼阵相关
        self.initFishGroupData()
        self.startFishGroup()
        # 循环检查牌桌内用户状态
        FTLoopTimer(self._checkStateSeconds, -1, self.checkState).start()
        # 捕鱼成本收益
        self.cb_reporter = FishCostBenefitModule(self.roomId, tableId, self)

        # 循环检查渔场内用户活动开启状态
        FTLoopTimer(31, -1, self.checkActivity).start()

        self.actionMap = {
            "leave": self._clearPlayer,                 # 玩家
            "robot_leave": self._robotLeave,
            "catch": self._verifyCatch,                 # 验证该次捕获是否有效
            "skill_use": self._skill_use,
            "skill_install": self._skill_install,
            "skill_replace": self._skill_replace,
            "chat": self._doTableChat,
            "smile": self.doTableSmilies,
            "clip_info": self._clip_info,               # 显示弹药购买详情信息响应
            "clip_add": self._clip_add,                 # 弹药购买
            "clip_alms": self._clip_alms,               # 弹药救济金响应
            "clip_clearing": self._clip_clearing,       # 弹药结算
            "bullet_use": self._bullet_use,
            "refresh_user_data": self._refreshUserData,
            "achievement_tasks": self._achievement_task,
            "achievement_tasks_reward": self._achievement_reward,
            "honor_push": self._honor_push,
            "honor_replace": self._honor_replace,
            "guns_list": self._guns_list,
            "guns_pool": self._guns_pool,
            "gun_up": self._gun_up,
            "recharge_notify": self._recharge_notify,
            "skill_upgrade": self._skill_upgrade,
            "refresh_skill_cd": self._refresh_skill_cd,
            "achievement_target": self._achievement_target,
            "fishActivityBtns": self._activity_all_btns,
            "fishActivityRead": self._activity_read,
            "fishActivityReceive": self._activity_reward,
            "fishActivityBonusResult": self._activity_bonus,
            "take_gift_reward": self._takeGiftReward,
            "treasure_rewards": self._getTreasureRewards,
            "task_update": self._taskUpdate,
            "main_reward": self._getMainQuestRewards,
            "prize_wheel_info": self._prizeWheelInfo,  # 渔场内经典转盘
            "prize_wheel_bet": self._prizeWheelBet,  # 确定轮盘最终奖励
            "prize_wheel_info_m": self._prizeWheelInfo,  # 渔场内千炮转盘
            "prize_wheel_bet_m": self._prizeWheelBet,  # 确定轮盘最终奖励
            "chg_multiple": self._chgMultiple,
            "start_grand_prix": self._startGrandPrix,
            "end_grand_prix": self._endGrandPrix,
            "comp_act_notify": self._inspireNotify,
            "lottery_ticket_info": self._lotteryTicketInfo,
            "lottery_ticket_progress": self._lotteryTicketProgress,
            "lottery_ticket_exchange": self._lotteryTicketExchange,
            "ticket_info": self._lotteryTicketInfo,
            "ticket_progress": self._lotteryTicketProgress,
            "ticket_interface": self._lotteryTicketExchange,
            "newbie_7_gift_take": self._takeNewbie7DaysGift,
            "mini_game_start": self._miniGameStart,
            "mini_game_action": self._miniGameAction,   # 小游戏抽奖
        }
        
        self.actionMap2 = {
            "fire": self._verifyFire,
            "gchg": self._gunChange,
            "chg_gun": self._chgGun,                    # 切换火炮
            "gun_change_skin": self._chgGunSkin,        # 切换火炮皮肤
            "gun_compose_skin": self._composeGunSin,    # 合成火炮皮肤
            "ping": self._ping,
            "m_surpass": self._surpassTarget,
            "total_catch": self._totalCatch
        }
        
        if "table" in self.runConfig.taskSystemType:    # 使用的任务系统
            self.taskSystemTable = TaskSystemTable(self)
            self.systemTableActionMap = {
                "task_ready": self.taskSystemTable.taskReady,
                "task_start": self.taskSystemTable.taskStart,
                "task_end": self.taskSystemTable.taskEnd,
            }
        elif "user" in self.runConfig.taskSystemType:
            self.actionMap["table_task_info"] = self._getTableTask
            self.actionMap["table_task_change"] = self._changeTableTask
            self.actionMap["red_task_list"] = self._getRedTaskList
        
    def _doTableCall(self, msg, userId, seatId, action, clientId):
        """
        桌子内部处理所有的table_call命令
        子类需要自行判定userId和seatId是否吻合
        """
        if 0 < seatId <= self.maxSeatN:
            player = self.players[seatId - 1]
            if (not player or userId != player.userId
                or self.seats[seatId - 1].userId != userId or userId == 0):
                playerUid = player.userId if player else 0
                ftlog.warn("_doTableCall, the userId is wrong !", userId, seatId, action,
                           "player.userId=", playerUid, clientId)
                return True
        else:
            if action not in ["add_fish_group", "robot_leave"]:
                ftlog.warn("invalid seatId", userId, action)
                return False

        func = self.actionMap.get(action)
        ftlog.debug("_doTableCall", userId, action, func)
        if func:
            func(msg, userId, seatId)
            return True
        else:
            ftlog.warn("not reconized action:", userId, action)     # 不认识的action
            return False

    def doTableCallOwn(self, msg, userId, seatId, action, clientId):
        '''自己调用TableCall方法'''
        if 0 < seatId <= self.maxSeatN:
            player = self.players[seatId - 1]
            if player and action == "fire":                 # 开火
                player.lastActionTime = int(time.time())    # 更新最后action的时间
            if (not player or userId != player.userId
                or self.seats[seatId - 1].userId != userId
                or userId == 0):
                if action != "ping":                        # ping协议
                    playerUid = player.userId if player else 0
                    ftlog.warn("doTableCallOwn, the userId is wrong !", userId, seatId, action,
                               "player.userId=", playerUid, clientId)
                return True

        else:
            ftlog.warn("invalid seatId", userId, action)
            return False

        func = self.actionMap2.get(action)
        if func:
            func(msg, userId, seatId)
            return True
        else:
            ftlog.warn("not reconized action:", userId, action)
            return False

    def clear(self):
        """
        完全清理桌子数据和状态, 恢复到初始化的状态
        """
        if ftlog.is_debug():
            ftlog.debug("clear-->begin")
        self._resetTableConf()                  # 重置桌子的配置
        self.processing = False
        self.startTime = time.time()
        # 清理座位状态, 玩家信息
        for x in xrange(len(self.seats)):
            self.seats[x] = TYSeat(self)        # 清理座位的类
            self.players[x] = None              # 清理桌面玩家
        if ftlog.is_debug():
            ftlog.debug("clear-->done")

    def initFishGroupData(self):
        """
        初始化鱼阵数据
        """
        self.activityFishGroup = None           # 活动的鱼阵
        self.autofillFishGroup = None           # 自动填充的鱼阵
        self.bossFishGroup = None               # boss鱼阵
        self.bufferFishGroup = None             # buffer鱼阵
        self.chestFishGroup = None              # 宝箱鱼阵
        self.couponFishGroup = None             # 奖券鱼阵
        self.grandPrixFishGroup = None          # 大奖赛鱼阵
        self.multipleFishGroup = None           # 千炮鱼阵
        self.normalFishGroup = None             # 普通鱼阵
        self.rainbowFishGroup = None            # 彩虹鱼鱼群
        self.shareFishGroup = None              # 分享宝箱鱼群
        self.superBossFishGroup = None          # 超级boss鱼阵
        self.terrorFishGroup = None             # 获取恐怖鱼配置
        self.ttAutofillFishGroup = None         # 渔场任务使用的自动填充鱼阵
        self.normalFishGroups = []              # 普通鱼群
        self.callFishGroups = []
        self.fishMap = {}
        self.ftCount = {}

    def startFishGroup(self):
        """
        启动鱼阵
        """
        self.fishGroupSystem = FishGroupSystem(self)
        if self.runConfig.allNormalGroupIds:
            self.normalFishGroup = NormalFishGroup(self)

    def clearFishGroup(self):
        """
        清除鱼阵
        """
        self.activityFishGroup and self.activityFishGroup.clearTimer()      # 活动的鱼阵
        self.autofillFishGroup and self.autofillFishGroup.clearTimer()      # 自动填充的鱼阵
        self.bossFishGroup and self.bossFishGroup.clearTimer()
        self.bufferFishGroup and self.bufferFishGroup.clearTimer()
        self.chestFishGroup and self.chestFishGroup.clearTimer()
        self.couponFishGroup and self.couponFishGroup.clearTimer()
        self.grandPrixFishGroup and self.grandPrixFishGroup.clearTimer()
        self.multipleFishGroup and self.multipleFishGroup.clearTimer()
        self.normalFishGroup and self.normalFishGroup.clearTimer()
        self.rainbowFishGroup and self.rainbowFishGroup.clearTimer()
        self.shareFishGroup and self.shareFishGroup.clearTimer()
        self.superBossFishGroup and self.superBossFishGroup.clearTimer()
        self.terrorFishGroup and self.terrorFishGroup.clearTimer()
        self.ttAutofillFishGroup and self.ttAutofillFishGroup.clearTimer()
        self.fishGroupSystem.clear()                                        # 渔场鱼群管理系统  删除全部鱼群
        self.initFishGroupData()                                            # 初始化鱼群

    def _checkReloadRunConfig(self):
        '''检查重新载入配置'''
        if ftlog.is_debug():
            ftlog.debug("_checkReloadRunConfig->", self.configChanged, self.playersNum)
        self._resetTableConf()
        if ftlog.is_debug():
            ftlog.debug("self._runConfig->", self._runConfig)

    def _resetTableConf(self):
        '''重置桌子的配置'''
        runconf = deepcopy(self.room.roomConf)
        runconf.update(deepcopy(self.config))
        self._runConfig = FishTableConf(runconf)

    def _clearTable(self):
        '''清理桌子'''
        for i in range(self.maxSeatN):
            player = self.players[i]
            if player and player.userId:
                self.clearPlayer(player)
        ftlog.info("clear table end")

    def checkState(self):
        '''检查玩家状态'''
        for player in self.players:
            if player and player.userId:
                intervalTime = int(time.time()) - player.lastActionTime             # 间隔时间
                if (intervalTime >= self._idleTimeOutSeconds or                     # 用户空闲超时时间 3分钟
                        (intervalTime >= self._offlineWaitSeconds and player.offline) or        # 用户离线等待时间 1分钟
                        (intervalTime >= self._inactiveTimeOutSeconds and player.clip == 0)):   # 用户无子弹时超时时间 3分钟
                    self.clearPlayer(player)

    def getPlayer(self, userId):
        '''获取玩家'''
        for p in self.players:
            if p and p.userId == userId and userId != 0:
                return p
        return None

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishPlayer(table, seatIndex, clientId)

    def getTableScore(self):
        """
        取得当前桌子的快速开始的评分  覆盖父类的方法
        越是最适合进入的桌子, 评分越高, 座位已满评分为0
        """
        if self.maxSeatN <= 0:
            return 1
        if self.playersNum == self.maxSeatN:
            return 0
        return (self.playersNum + 1) * 100 / self.maxSeatN

    def getRobotUserCount(self):
        """
        取得当前桌子中, 机器人的数量
        """
        count = 0
        for player in self.players:
            if player and player.isRobotUser:
                count += 1
        return count

    @property
    def bigRoomId(self):
        """
        44101、44102、44103、44104
        取得当前房间的配置ID,再配置系统中,房间的附属配置均以此为键值进行配置
        """
        return self.room.roomDefine.bigRoomId

    @property
    def runConfig(self):
        """
        取得当前的基本配置, 当系统的配置内容更新时, 如果桌子再游戏中, 那么等下次开局时配置才真正的更新
        """
        return self._runConfig

    @property
    def hasRobot(self):
        """
        判定是否有机器人
        """
        return self.runConfig.hasRobot

    @property
    def matchType(self):
        """
        取得当前比赛类型
        """
        return self._runConfig.matchType

    @property
    def typeName(self):
        """
        获取房间类型
        """
        return self._runConfig.typeName

    @property
    def gameMode(self):
        """
        该房间游戏模式
        """
        return self._gameMode


    def insertFishGroup(self, groupName, position=None, HP=None, buffer=None, userId=None, score=None,
                        sendUserId=None, gameResolution=None):
        """召唤鱼群"""
        return self.fishGroupSystem.insertFishGroup(groupName, position, HP, buffer, userId, score,
                                                    sendUserId, gameResolution)

    def addNormalFishGroups(self, groupIds):
        '''普通鱼群，一次生成多个鱼群，一起发给客户端'''
        self.fishGroupSystem.addNormalFishGroups(groupIds)

    def deleteFishGroup(self, group):
        '''删除单个鱼群'''
        self.fishGroupSystem.deleteFishGroup(group)

    def _clip_info(self, msg, userId, seatId):
        '''显示弹药购买详情信息响应'''
        player = self.players[seatId - 1]
        if player:
            message = MsgPack()
            message.setCmd("clip_info")
            message.setResult("gameId", FISH_GAMEID)
            message.setResult("userId", userId)
            message.setResult("seatId", seatId)
            message.setResult("chip", player.chip)                      # 牌桌外金币
            message.setResult("clip", player.clip)                      # 剩余子弹数
            message.setResult("lack", self.runConfig.lack)              # 不足多少子弹数时自动购买
            message.setResult("bullets", self.runConfig.bullets)        # 购买子弹数列表
            message.setResult("multiple", self.runConfig.multiple)      # 渔场倍率
            message.setResult("fpMultiple", player.fpMultiple)          # 玩家实际选择的倍率
            GameMsg.sendMsg(message, userId)
            if player.allChip < self.runConfig.minCoin:
                user_rpc.sendTodoTaskBuyChip(userId, self.bigRoomId)

    def _clip_alms(self, msg, userId, seatId):
        '''弹药救济金响应'''
        player = self.players[seatId - 1]
        # if player and player.level < 10 and self.runConfig.fishPool == 44001:
        #     almsCount = weakdata.incrDayFishData(userId, "almsCount", 1)
        #     if almsCount > 3:
        #         return
        #     roomConfig = gdata.getRoomConfigure(self.bigRoomId)
        #     allChip = player.allChip
        #     minTableChip = roomConfig["bullets"][0] * roomConfig["multiple"]
        #     if allChip < minTableChip:
        #         delta, _ = userchip.incrChip(userId, FISH_GAMEID, minTableChip - allChip, 1,
        #                                      "BI_NFISH_NEW_USER_REWARDS", 0, player.clientId)
        #         datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, "chip")
        #         message = MsgPack()
        #         message.setCmd("clip_alms")
        #         message.setResult("gameId", FISH_GAMEID)
        #         message.setResult("userId", userId)
        #         message.setResult("seatId", seatId)
        #         message.setResult("chip", delta)
        #         GameMsg.sendMsg(message, userId)

    def _clip_add(self, msg, userId, seatId):
        bullet = msg.getParam("bullet") or 0
        auto = msg.getParam("auto") or 0
        if ftlog.is_debug():
            ftlog.debug("_clip_add", userId, seatId, bullet, auto)
        self.clip_add(userId, seatId, bullet, auto)

    def clip_add(self, userId, seatId, bullet=0, auto=0):
        '''弹药添加'''
        player = self.players[seatId - 1]
        # if (bullet not in self.runConfig.bullets and not auto) or not player:
        #     return False
        reason, info = player.addClip(bullet, auto)
        message = MsgPack()
        message.setCmd("clip_add")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("seatId", seatId)
        message.setResult("info", info)             # [使用金币数,购买子弹数]
        message.setResult("chip", player.chip)      # 牌桌外金币
        message.setResult("tableChip", player.tableChip)    # 牌桌内金币
        message.setResult("clip", player.clip)              # 剩余子弹数
        message.setResult("auto", auto)                     # 是否自动购买
        message.setResult("reason", reason)                 # 0:成功 1:失败 2:达到上限
        GameMsg.sendMsg(message, self.getBroadcastUids())
        if reason == 0:
            return True
        return False

    def _clip_clearing(self, msg, userId, seatId):
        '''弹药结算'''
        player = self.players[seatId - 1]
        reason = 0
        if not player:
            reason = 1
        player.clearingClip()
        message = MsgPack()
        message.setCmd("clip_clearing")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("seatId", seatId)
        message.setResult("reason", reason)
        if reason == 0:
            message.setResult("chip", player.chip)
        GameMsg.sendMsg(message, self.getBroadcastUids())

    def _chgGun(self, msg, userId, seatId):
        """
        切换火炮
        """
        gunId = msg.getParam("gunId")
        player = self.getPlayer(userId)
        if player:
            userGunIds = gun_system.getGunIds(userId, self.gameMode)
            if gunId in userGunIds:
                self.syncChgGunData(player, gunId)

    def _chgGunSkin(self, msg, userId, seatId):
        """
        切换火炮皮肤
        """
        gunId = msg.getParam("gunId")
        skinId = msg.getParam("skinId")
        player = self.getPlayer(userId)
        if player:
            if gun_system.changeGunSkin(userId, gunId, skinId, self.gameMode): # 更改火炮皮肤
                if int(gunId) == int(player.gunId): # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
                    self.syncChgGunData(player, gunId)

    def _composeGunSin(self, msg, userId, seatId):
        """
        合成火炮皮肤
        """
        gunId = msg.getParam("gunId")
        skinId = msg.getParam("skinId")
        player = self.getPlayer(userId)
        if player:
            if gun_system.composeGunSkin(userId, gunId, skinId, self.gameMode): # 合成火炮皮肤
                if int(gunId) == int(player.gunId): # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
                    self.syncChgGunData(player, gunId)





    def clearPlayer(self, player):
        '''玩家离开桌子'''
        ftlog.info("clearPlayer->", player.userId, player.lastActionTime, self.runConfig.fishPool)
        msg = MsgPack()
        msg.setCmdAction("table_call", "leave")
        msg.setParam("gameId", FISH_GAMEID)
        msg.setParam("clientId", player.clientId)
        msg.setParam("userId", player.userId)
        msg.setParam("roomId", self.roomId)
        msg.setParam("tableId", self.tableId)
        msg.setParam("seatId", player.seatId)
        action = msg.getParam("action")
        self.doTableCall(msg, player.userId, player.seatId, action, player.clientId)
        
    def checkActivity(self):
        pass

    def _miniGameAction(self, msg, userId, seatId):
        """
        小游戏抽奖, actType=1表示翻硬币/选择箱子， actType=2表示宝箱抽奖
        """
        mini_game.doAction(msg, self, self.players[seatId - 1])