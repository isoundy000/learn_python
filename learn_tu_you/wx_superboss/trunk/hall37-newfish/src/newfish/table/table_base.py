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
            "skill_use": self._skill_use,               # 使用技能 1使用 0取消
            "skill_install": self._skill_install,       # 装备、卸下、替换
            "skill_replace": self._skill_replace,       # 技能替换 uninstallSkillId 要卸下的技能ID
            "chat": self._doTableChat,
            "smile": self.doTableSmilies,
            "clip_info": self._clip_info,               # 显示弹药购买详情信息响应
            "clip_add": self._clip_add,                 # 弹药购买
            "clip_alms": self._clip_alms,               # 弹药救济金响应
            "clip_clearing": self._clip_clearing,       # 弹药结算
            "bullet_use": self._bullet_use,
            "refresh_user_data": self._refreshUserData, # 刷新用户VIP等级和金币数
            "achievement_tasks": self._achievement_task,
            "achievement_tasks_reward": self._achievement_reward,
            "honor_push": self._honor_push,
            "honor_replace": self._honor_replace,
            "guns_list": self._guns_list,
            "guns_pool": self._guns_pool,
            "gun_up": self._gun_up,
            "recharge_notify": self._recharge_notify,
            "skill_upgrade": self._skill_upgrade,       # 技能升级、升星
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
            "prize_wheel_info": self._prizeWheelInfo,   # 渔场内经典转盘
            "prize_wheel_bet": self._prizeWheelBet,     # 确定轮盘最终奖励
            "prize_wheel_info_m": self._prizeWheelInfo, # 渔场内千炮转盘
            "prize_wheel_bet_m": self._prizeWheelBet,   # 确定轮盘最终奖励
            "chg_multiple": self._chgMultiple,
            "start_grand_prix": self._startGrandPrix,   # 大奖赛开赛
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
            "fire": self._verifyFire,                   # 验证该次捕获是否有效
            "gchg": self._gunChange,                    # 切换火炮等级
            "chg_gun": self._chgGun,                    # 切换火炮
            "gun_change_skin": self._chgGunSkin,        # 切换火炮皮肤
            "gun_compose_skin": self._composeGunSin,    # 合成火炮皮肤
            "ping": self._ping,                         # 心跳
            "m_surpass": self._surpassTarget,
            "total_catch": self._totalCatch             # 发送圆盘数据
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
        self.normalFishGroups = []              # 普通鱼群  普通鱼群增加一个新的鱼群[group=FishGroup]
        self.callFishGroups = []                # 召唤出来的鱼群对象[group=FishGroup]
        self.fishMap = {}                       # {鱼的唯一ID: 鱼的详细描述}  # 鱼群的鱼   鱼塘包含多个鱼群
        self.ftCount = {}                       # {鱼的ID: 数量}

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
        """普通鱼群，一次生成多个鱼群，一起发给客户端"""
        self.fishGroupSystem.addNormalFishGroups(groupIds)

    def deleteFishGroup(self, group):
        """删除单个鱼群"""
        self.fishGroupSystem.deleteFishGroup(group)

    def _clip_info(self, msg, userId, seatId):
        """显示弹药购买详情信息响应"""
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
            if player.allChip < self.runConfig.minCoin:                 # 所有金币
                user_rpc.sendTodoTaskBuyChip(userId, self.bigRoomId)

    def _clip_alms(self, msg, userId, seatId):
        """弹药救济金响应"""
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
        """购买弹药"""
        bullet = msg.getParam("bullet") or 0
        auto = msg.getParam("auto") or 0
        if ftlog.is_debug():
            ftlog.debug("_clip_add", userId, seatId, bullet, auto)
        self.clip_add(userId, seatId, bullet, auto)

    def clip_add(self, userId, seatId, bullet=0, auto=0):
        """弹药添加"""
        player = self.players[seatId - 1]
        # if (bullet not in self.runConfig.bullets and not auto) or not player:
        #     return False
        reason, info = player.addClip(bullet, auto)
        message = MsgPack()
        message.setCmd("clip_add")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("seatId", seatId)
        message.setResult("info", info)                     # [使用金币数,购买子弹数]
        message.setResult("chip", player.chip)              # 牌桌外金币
        message.setResult("tableChip", player.tableChip)    # 牌桌内金币
        message.setResult("clip", player.clip)              # 剩余子弹数
        message.setResult("auto", auto)                     # 是否自动购买
        message.setResult("reason", reason)                 # 0:成功 1:失败 2:达到上限
        GameMsg.sendMsg(message, self.getBroadcastUids())
        if reason == 0:
            return True
        return False

    def _clip_clearing(self, msg, userId, seatId):
        """弹药结算"""
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
            if gun_system.changeGunSkin(userId, gunId, skinId, self.gameMode):  # 更改火炮皮肤
                if int(gunId) == int(player.gunId):     # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
                    self.syncChgGunData(player, gunId)

    def _composeGunSin(self, msg, userId, seatId):
        """
        合成火炮皮肤
        """
        gunId = msg.getParam("gunId")
        skinId = msg.getParam("skinId")
        player = self.getPlayer(userId)
        if player:
            if gun_system.composeGunSkin(userId, gunId, skinId, self.gameMode):     # 合成火炮皮肤
                if int(gunId) == int(player.gunId):     # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
                    self.syncChgGunData(player, gunId)

    def syncChgGunData(self, player, gunId):
        """
        修改火炮数据并广播通知其他玩家
        """
        player.chgGunData(gunId)        # 切换炮台
        player.sendChgGunInfo()         # 发送火炮修改消息
        gun_system.sendGunListMsg(player.userId, self.gameMode)

    def _refreshUserData(self, msg, userId, seatId):
        """刷新用户数据"""
        player = self.getPlayer(userId)
        if player:
            player.refreshVipLevel()                # 刷新vip等级
            player.refreshHoldCoin()                # 刷新金币数
            message = MsgPack()
            message.setCmd("refresh_user_data")
            message.setResult("gameId", FISH_GAMEID)
            message.setResult("userId", userId)
            message.setResult("seatId", seatId)
            message.setResult("chip", player.chip)
            message.setResult("vip", player.vipLevel)
            message.setResult("reason", 0)
            GameMsg.sendMsg(message, self.getBroadcastUids())

    def _ping(self, msg, userId, seatId):
        """心跳数据"""
        message = MsgPack()
        message.setCmd("ping")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("timestamp", msg.getParam("timestamp"))
        GameMsg.sendMsg(message, userId)

    def _gunChange(self, msg, userId, seatId):
        """炮改变等级 切换火炮等级"""
        player = self.players[seatId - 1]
        if not player:
            return
        gLv = msg.getParam("gLv")
        if not gLv or not config.getGunLevelConf(gLv, self.gameMode):
            ftlog.warn("gchg glv error")
            return
        if player:
            player.gunChange(gLv)
        if player and hasattr(player, "lotteryTicket") and player.lotteryTicket:
            player.lotteryTicket.sendProgress(1, isSend=1)

    def broadcastGunChange(self, player):
        """广播玩家现在的火炮等级"""
        retMsg = MsgPack()
        retMsg.setCmd("gchg")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("gLv", player.nowGunLevel)
        retMsg.setResult("userId", player.userId)
        retMsg.setResult("seatId", player.seatId)
        GameMsg.sendMsg(retMsg, self.getBroadcastUids())

    def fire(self, userId, seatId, fPos, wpId, bulletId, skillId, timestamp, skillType, lockFId=0):
        """开火"""
        fPosx, fPosy = fPos
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)
        player = self.players[seatId - 1]
        wpType = util.getWeaponType(wpId)
        if ftlog.is_debug():
            ftlog.debug("_verifyFire", fPosx, fPosy)
        if player:
            canFire, reason, clip, costBullet, extends, skill = player.checkCanFire(fPos, wpId, bulletId, skillId, skillType)
        else:
            canFire, reason, clip, costBullet, extends, skill = False, 7, 0, 1, [], None

        if canFire:
            costChip = 0
            wpPower = None
            multiple = None
            fpMultiple = player.fpMultiple
            if wpType == config.GUN_WEAPON_TYPE:
                costChip = costBullet * fpMultiple      # 消耗的子弹 * 渔场倍率
                wpPower = wpConf["power"]
                multiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)     # 单倍|双倍炮
            player.addFire(bulletId, wpId, timestamp, fpMultiple, skill, costChip=costChip, power=wpPower, multiple=multiple)
            if wpType == config.GUN_WEAPON_TYPE:
                clip = player.costClip(costBullet, "BI_NFISH_GUN_FIRE")
                _finalPower = player.getFinalWpPower(bulletId)
                gunX = util.getGunX(wpId, self.gameMode)
                player.addBulletPowerPool(_finalPower, fpMultiple, multiple, gunX)

        if player:
            params = {"fPos": fPos, "wpId": wpId, "bulletId": bulletId, "skillId": skillId,
                      "timestamp": timestamp, "canFire": canFire, "reason": reason, "clip": clip,
                      "skillType": skillType, "lockFId": lockFId}
            player.sendFireMsg(userId, seatId, extends, params)

        if canFire and skill and skill.clip == 0 and skill_release.weaponSkillMap.get(wpId):    # skill.clip技能子弹
            skill.end()                                                                         # 结束技能
            player.gchgTimer = FTLoopTimer(skill.interval, 0, self.broadcastGunChange, player)  # 广播玩家现在的火炮等级 技能释放完毕变成原来炮的模样
            player.gchgTimer.start()
        return canFire

    # def fire(self, userId, seatId, fPos, wpId, bulletId, skillId, timestamp):
    #     fPosx, fPosy = fPos
    #     wpConf = config.getWeaponConf(wpId)
    #     skill = None
    #     extends = []
    #     reason = 0
    #     canFire = True
    #     player = self.players[seatId - 1]
    #     clip = player.clip
    #     wpType = util.getWeaponType(wpId)
    #     costBullet = 1
    #     ftlog.debug("_verifyFire", fPosx, fPosy)
    #     if not wpId or not bulletId or not wpConf:
    #         canFire = False
    #         reason = 6
    #         ftlog.warn("_verifyFire param is error", userId, wpId, bulletId, wpConf)
    #     else:
    #         costBullet = self.getCostBullet(player.gunId, player.gunLv, wpConf)
    #         if skillId:
    #             skill = player.getSkill(skillId)
    #             if skill and skillId == skill_release.weaponSkillMap.get(wpId):
    #                 if skillId in player.usingSkill:
    #                     ftlog.debug("player.usingSkill", player.usingSkill, skillId)
    #                     isOK = skill.costClip(bulletId, fPosx, fPosy)
    #                     clip = skill.clip
    #                     if isOK:
    #                         if player and player.getTargetFishs():
    #                             extends.append(1)
    #                     else:
    #                         canFire = False
    #                         reason = 5
    #                 else:
    #                     canFire = False
    #                     reason = 4
    #                     ftlog.warn("_verifyFire usingSkill error", userId, player.usingSkill, skillId)
    #             elif not skill or wpType not in [config.RB_FIRE_WEAPON_TYPE, config.RB_BOMB_WEAPON_TYPE]:
    #                 canFire = False
    #                 reason = 3
    #                 ftlog.warn("_verifyFire skill error", userId, skillId)
    #         elif wpType == config.GUN_WEAPON_TYPE and (wpId > player.gunLevel or player.getUsingSkillInfo()):
    #             canFire = False
    #             reason = 2
    #             ftlog.warn("_verifyFire weapon error", userId, wpId, player.gunLevel)
    #         elif player.clip < costBullet:
    #             canFire = False
    #             reason = 1
    #             ftlog.debug("_verifyFire clip not enough")
    #
    #     retMsg = MsgPack()
    #     retMsg.setCmd("fire")
    #     retMsg.setResult("gameId", FISH_GAMEID)
    #     retMsg.setResult("wpId", wpId)
    #     retMsg.setResult("bulletId", bulletId)
    #     retMsg.setResult("skillId", skillId)
    #     retMsg.setResult("extends", extends)
    #     retMsg.setResult("timestamp", timestamp)
    #     retMsg.setResult("reason", reason)
    #     if canFire:
    #         costChip = 0
    #         wpPower = None
    #         multiple = None
    #         fpMultiple = player.fpMultiple
    #         if wpType == config.GUN_WEAPON_TYPE:
    #             costChip = costBullet * fpMultiple
    #             wpPower = wpConf["power"]
    #             multiple = config.getGunConf(player.gunId, player.gunLv).get("multiple", 1)
    #         player.addFire(bulletId, wpId, timestamp, fpMultiple, skill, costChip=costChip, power=wpPower, multiple=multiple)
    #         if wpType == config.GUN_WEAPON_TYPE:
    #             clip = player.costClip(costBullet, "BI_NFISH_GUN_FIRE")
    #             # _finalPower = player.getFinalWpPower(bulletId)
    #             # player.addBulletPowerPool(_finalPower, fpMultiple, multiple)
    #     retMsg.setResult("clip", clip)
    #     superBullet = player.getFire(bulletId).get("superBullet", {})  # player.isSuperBullet(bulletId)
    #     retMsg.setResult("superBullet", 1 if superBullet else 0)  # 测试代码
    #     GameMsg.sendMsg(retMsg, userId)
    #     if canFire:
    #         retMsg.setResult("fPosx", fPosx)
    #         retMsg.setResult("fPosy", fPosy)
    #         retMsg.setResult("seatId", seatId)
    #         GameMsg.sendMsg(retMsg, self.getBroadcastUids(userId))
    #     if canFire and skill and skill.clip == 0 and skill_release.weaponSkillMap.get(wpId):
    #         skill.end()
    #         player.gchgTimer = FTLoopTimer(skill.interval, 0, self.broadcastGunChange, player)
    #         player.gchgTimer.start()
    #     return canFire

    def _verifyFire(self, msg, userId, seatId):
        """
        验证该次开火是否有效
        """
        wpId = msg.getParam("wpId")                 # 武器ID
        fPosx = msg.getParam("fPosx")               # x轴
        fPosy = msg.getParam("fPosy")               # y轴
        bulletId = msg.getParam("bulletId")         # 子弹ID
        skillId = msg.getParam("skillId")           # 技能ID
        skillType = msg.getParam("skillType", 0)    # 技能类型
        timestamp = msg.getParam("timestamp", 0)    # 开火时间
        lockFId = msg.getParam("lockFId", 0)
        return self.fire(userId, seatId, [fPosx, fPosy], wpId, bulletId, skillId, timestamp, skillType, lockFId)

    def _verifyCatch(self, msg, userId, seatId):
        """
        验证该次捕获是否有效
        """
        wpId = msg.getParam("wpId")                 # 获得武器类型
        fIds = msg.getParam("fIds") or []
        skillId = msg.getParam("skillId")
        skillType = msg.getParam("skillType", 0)
        extends = msg.getParam("extends")           # 扩展、透传参数
        bulletId = msg.getParam("bulletId")
        stageId = msg.getParam("stageId", 0)        # 阶段
        player = self.players[seatId - 1]
        wpIdFire = player.getFireWpId(bulletId)     # 获取子弹开火的武器
        wpType = util.getWeaponType(wpId)
        extendId = 0
        if ftlog.is_debug():
            ftlog.debug("_verifyCatch->wpId =", wpId, "fIds =", fIds, "bulletId =", bulletId, "skillId =", skillId, skillType,
                    "player =", player, "wpIdFire =", wpIdFire, "userId =", userId, "extends =", extends, "stageId =", stageId)

        # 修复猎鱼机甲打不死鱼的补丁！
        if wpId == 2301 and skillId == 0:
            skillId = 5109
            if ftlog.is_debug():
                ftlog.debug("_verifyCatch, hotfix, userId =", userId)

        if wpType < config.RB_BOMB_WEAPON_TYPE and (not wpIdFire or wpIdFire != wpId):      # 武器类型小于4的必须有开火的武器
            ftlog.warn("_verifyCatch wpIdFire error", userId, bulletId, wpId, wpIdFire)
            return
        if wpType >= config.RB_BOMB_WEAPON_TYPE:                                            # 特殊武器 特殊鱼
            if extends:
                # 只有在阶段0才做这种检测.
                if stageId == 0:    # if wpType != config.DRILL_WEAPON_TYPE or stageId == 0:
                    extendId = extends[0]
                    if extendId not in self.fishMap:
                        ftlog.warn("_verifyCatch special extendId error", userId)
                        return
                    fishType = self.fishMap[extendId]["conf"]["fishType"]
                    fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                    if fishConf["type"] in config.ROBOT_FISH_TYPE and wpType == config.RB_BOMB_WEAPON_TYPE: # 机器人爆炸
                        pass
                    elif fishConf["type"] in config.BOMB_FISH_TYPE and wpType == config.BOMB_WEAPON_TYPE: # 炸弹鱼爆炸
                        pass
                    elif fishConf["type"] in config.NUMB_FISH_TYPE and wpType == config.NUMB_WEAPON_TYPE: # 电鳗
                        pass
                    elif fishConf["type"] in config.DRILL_FISH_TYPE and wpType == config.DRILL_WEAPON_TYPE: # 钻头鱼
                        pass
                    elif fishConf["type"] in config.SUPERBOSS_FISH_TYPE and wpType == config.SUPERBOSS_WEAPON_TYPE: # 超级boss
                        pass
                    else:
                        ftlog.warn("_verifyCatch special fish not match", userId)
                        return
            else:
                ftlog.warn("_verifyCatch special fish not extend", userId)
                return

        if skillId:                                                                             # 使用技能捕鱼
            if ftlog.is_debug():
                ftlog.debug("_verifyCatch->skillId", skillId, "userId =", userId)
            skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
            if not skill:
                ftlog.error("_verifyCatch skill error", skillId, "userId =", userId)
                return
            if skill.isReturn == 1 and not fIds:
                skill.returnClip()
            catch, gain, gainChip, exp = skill.catchFish(bulletId, wpId, fIds, extends)         # 技能捕鱼
            fpMultiple = skill.fpMultiple                                                       # 玩家选的渔场倍率
        else:
            catch, gain, gainChip, exp = self._catchFish(player, bulletId, wpId, fIds, extends, stageId)    # 普通捕鱼
            extendId = extends[0] if extends else 0
            fpMultiple = player.getFireFpMultiple(bulletId, extendId)

        self.dealCatch(bulletId, wpId, player, catch, gain, gainChip, exp, fpMultiple, extends, skillId, stageId, skillType=skillType)
        if wpIdFire and wpType != config.SKILL_WEAPON_TYPE:  # 删除非技能子弹
            maxStage = player.getFireMaxStage(bulletId, extendId)
            # 子弹达到最大阶段后销毁.
            if stageId == maxStage:             # if wpType != config.DRILL_WEAPON_TYPE or stageId == 1:
                player.delFire(bulletId, extendId)
        if wpType in [config.SKILL_WEAPON_TYPE, config.RB_FIRE_WEAPON_TYPE, config.RB_BOMB_WEAPON_TYPE,
                      config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE, config.SUPERBOSS_WEAPON_TYPE]:
            ftlog.info("_verifyCatch->", "userId =", userId, "msg =", msg)

    def getCostBullet(self, gunId, gunLevel, wpConf, clientId):
        """
        获取武器消耗的子弹
        :param gunId: 炮Id
        :param gunLevel: 炮等级
        :param wpConf: 武器配置
        """
        gunConf = config.getGunConf(gunId, clientId, gunLevel)
        costBullet = wpConf.get("costBullet", 1) * gunConf.get("multiple", 1)       # 消耗的子弹 * 单倍炮|双倍炮
        return costBullet

    def findFish(self, fId):
        """
        查找鱼
        """
        if fId not in self.fishMap:
            if ftlog.is_debug():
                ftlog.debug("findFish fish is not in fishMap", fId)
            return False
        fishInfo = self.fishMap[fId]            # 鱼的集合
        group = fishInfo.get("group")           # 鱼群详情
        conf = fishInfo.get("conf")             # 鱼的配置
        if not fishInfo["alive"]:
            if ftlog.is_debug():
                ftlog.debug("findFish fish is not alive", fId, group.id, conf)
            return False
        nowTableTime = self._getNowTableTime()
        if ftlog.is_debug():
            ftlog.debug("group desc fish in:", fId, group.desc(), "nowTableTime:", nowTableTime)    # group.desc() 鱼群详情
        if not group.isExist(nowTableTime):
            if ftlog.is_debug():
                ftlog.debug("findFish group not exist", fId, nowTableTime, group.id, conf)
            return False
        if not group.fishExist(nowTableTime, fId):
            if ftlog.is_debug():
                ftlog.debug("findFish fish not exist", fId, nowTableTime, group.id, conf)
            return False
        return True

    def verifyFish(self, userId, fId, wpId=0):
        """
        验证捕到的鱼是否有效 userId捕鱼者 fId鱼Id、wpId武器Id
        """
        catchUserId = userId
        isOK = True
        _buffer = None
        if not self.findFish(fId):
            isOK = False
            return isOK, catchUserId, _buffer
        fishInfo = self.fishMap[fId]
        if fishInfo["buffer"]:
            for buffer in fishInfo["buffer"]:
                skillId = buffer[0]
                skillEndTime = buffer[1]
                releaseUserId = buffer[2]
                if ftlog.is_debug():
                    ftlog.debug("verifyFish->skillId =", skillId, time.time(), skillEndTime, releaseUserId)
                if skillId == 5107:  # 欺诈水晶
                    if time.time() < skillEndTime:
                        catchUserId = releaseUserId
                        _buffer = buffer
                if skillId == 5102:  # 魔术炮(无敌)
                    if time.time() < skillEndTime and userId != releaseUserId:
                        isOK = False
                elif skillId == 5104:  # 极冻炮
                    fishType = fishInfo["conf"]["fishType"]
                    fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                    if fishConf["type"] in config.ICE_FISH_TYPE:  # 冰锥
                        if time.time() >= skillEndTime:
                            if self.fishMap[fId]["alive"]:
                                self.refreshFishTypeCount(self.fishMap[fId])
                            self.fishMap[fId]["alive"] = False
                            isOK = False
                        if userId == releaseUserId:
                            isOK = False
                elif skillId == 5109:  # 猎鱼机甲
                    if time.time() >= skillEndTime:
                        if self.fishMap[fId]["alive"]:
                            self.refreshFishTypeCount(self.fishMap[fId])
                        self.fishMap[fId]["alive"] = False
                        isOK = False
                    if wpId != 2302 and userId == releaseUserId:            # 捕鱼机器人爆炸
                        isOK = False
                if not isOK:
                    break
        return isOK, catchUserId, _buffer

    def _catchFish(self, player, bulletId, wpId, fIds, extends, stageId):
        """
        检测能否捕到鱼
        :param player:
        :param bulletId: 子弹ID
        :param wpId:武器ID
        :param fIds: 鱼
        :param extends: 扩展
        :param stageId: 阶段
        """
        fIdTypes = {}
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        extendId = extends[0] if extends else 0
        # totalProbb, aloofFish = self.getTotalProbb(player, fIds)
        superBullet = player.getFire(bulletId).get("superBullet", {})   # player.isSuperBullet(bulletId)
        gunConf = player.getGunConf(bulletId, extendId)                 # 子弹开火的炮配置
        bufferCoinAdd = player.getCoinAddition(wpId)                    # 获取金币加成
        multiple = player.getFireMultiple(bulletId, extendId)           # 获取开火时的倍率
        if multiple is None:
            multiple = gunConf.get("multiple", 1)
        _fpMultiple = player.getFireFpMultiple(bulletId, extendId)      # 获取开火时的渔场倍率
        # 炮的倍率.
        gunX = util.getGunX(wpId, self.gameMode)
        if ftlog.is_debug():
            ftlog.debug("_catchFish", "userId =", player.userId, "bulletId =", bulletId, "extends =", extends,
                        "wpId =", wpId, "fIds =", fIds, "stageId =", stageId, "bufferCoinAdd =", bufferCoinAdd,
                        "gunConf =", gunConf, "multiple =", multiple, "fire =", player.getFire(extendId), player.getFire(bulletId),
                        "fpMultiple =", _fpMultiple, "superBullet =", superBullet, "gunX =", gunX)
        otherCatch = {}
        isCatch = False
        isInvalid = False
        notCatchFids = []
        gunId = gunConf.get("gunId", 0)
        # 熟练度.
        gunLevel = gunConf.get("gunLevel", 1)
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)     # 获取武器的配置
        wpType = util.getWeaponType(wpId)
        totalCostCoin = self.getCostBullet(gunId, gunLevel, wpConf, player.clientId) * _fpMultiple      # 计算总消耗的金币
        averageCostCoin = float(totalCostCoin) / (len(fIds) or 1)   # 平均消耗的金币
        curveLossCoin = 0
        curveProfitCoin = 0
        aloofOdds = player.dynamicOdds.getOdds(superBullet=superBullet, aloofFish=True, gunConf=gunConf)
        nonAloofOdds = player.dynamicOdds.getOdds(superBullet=superBullet, aloofFish=False, gunConf=gunConf)
        fish_type_list = []

        _datas = {"fpMultiple": _fpMultiple}
        if wpType == config.GUN_WEAPON_TYPE and player.isSupplyBulletPowerMode():   # 火炮/千炮
            _finalPower = player.getFinalWpPower(bulletId)                          # 威力
            player.reduceBulletPowerPool(_finalPower, _fpMultiple, multiple, gunX)
            # 计算网中鱼的总分值.
            totalFishScore = 0
            for fId in fIds:
                if not self.findFish(fId):
                    continue
                fishType = self.fishMap[fId]["conf"]["fishType"]
                fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                totalFishScore += fishConf.get("catchValue", 0)                     # 鱼的价值
            _datas.update({"totalFishScore": totalFishScore, "multiple": multiple, "superBullet": superBullet})
            _datas.update({"bulletPowerPool": player.bulletPowerPool})
        # 清除鱼身上的buffer
        remove_fraud_buffer_fids = {}
        for fId in fIds:
            isOK, catchUserId, _buffer = self.verifyFish(player.userId, fId)
            if isOK:
                # 欺诈针对特殊鱼（炸弹、电鳗、钻头）捕获的鱼，无效
                if wpType in (config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE,
                              config.DRILL_WEAPON_TYPE) and catchUserId != player.userId and self.getPlayer(catchUserId):
                    if ftlog.is_debug():
                        ftlog.debug("remove_buffer_fishes, 1", _buffer)
                    _buffer[1] = time.time()                            # buffer结束时间
                    if ftlog.is_debug():
                        ftlog.debug("remove_buffer_fishes, 2", _buffer)
                    self.setFishBuffer(fId, _buffer)
                    remove_fraud_buffer_fids.setdefault(catchUserId, [])
                    remove_fraud_buffer_fids[catchUserId].append(fId)
                    if ftlog.is_debug():
                        ftlog.debug("_catchFish, use fraud invalid !", fId, catchUserId, player.userId)
                    catchUserId = player.userId
                pass
            else:
                isInvalid = True
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.fishMap[fId]
            originHP = fishInfo["HP"]
            probb = self.getCatchProbb(player, wpConf, fId, len(fIds), superBullet, extendId, aloofOdds, nonAloofOdds, stageId, datas=_datas)
            catchMap["HP"] = self.fishMap[fId]["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                gunMultiple = multiple
                # 欺诈只获得1倍收益.
                if catchUserId != player.userId:
                    gunMultiple = 1
                fishGainChip, fishGain, fishExp = self.dealKillFishGain(fId, player, _fpMultiple, gunMultiple, bufferCoinAdd, wpType=wpType, extends=extends, gunX=gunX)    # 处理打死鱼获得的奖励
                catchMap["reason"] = 0
                for _val in fishGain:
                    if _val.get("fishMultiple"):
                        catchMap["fishMultiple"] = _val.get("fishMultiple")
                        break
                if catchUserId == player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain, catchMap, fishExp)
            else:
                notCatchFids.append(fId)
                if originHP != catchMap["HP"]:
                    catch.append(catchMap)
                fishGainChip, fishGain = self.dealHitBossGain(0, fId, player, originHP)     # 处理打中boss掉落金币
                if catchUserId == player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain)
            fishType = fishInfo["conf"]["fishType"]
            fIdTypes[fId] = fishType
            if wpType == config.GUN_WEAPON_TYPE:
                fish_type_list.append(fishType)
            if self.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
                if wpType == config.GUN_WEAPON_TYPE and not superBullet:    # 火炮打出的普通子弹
                    fishConf = config.getFishConf(fishType, self.typeName, _fpMultiple)
                    if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                        curveLossCoin += averageCostCoin
                        if catchMap["reason"] == 0:
                            curveProfitCoin += fishConf["value"] * multiple * _fpMultiple
        # 清除鱼身上的buffer
        for _uid, _fishes in remove_fraud_buffer_fids.iteritems():
            _player = self.getPlayer(_uid)
            if _fishes and _player:
                self.broadcastSkillEffect(_player, time.time(), _fishes, 5107)
        # 记录普通开火捕鱼成本.
        if fish_type_list:
            total_cost = self.getCostBullet(gunId, gunLevel, wpConf, player.clientId) * _fpMultiple
            per_cost = total_cost / len(fish_type_list)
            for idx, fish_type in enumerate(fish_type_list):
                if idx == len(fish_type_list) - 1:
                    cost = total_cost - per_cost * idx
                else:
                    cost = per_cost
                if ftlog.is_debug():
                    ftlog.debug("report, fish cost", fish_type, player.nowGunLevel, multiple, _fpMultiple, cost)
                self.cb_reporter.add_cost(fish_type, cost)
        if ftlog.is_debug():
            ftlog.debug(
                "_catchFish->", "userId =", player.userId, "catch =", catch, "gain =", gain, "gainChip =", gainChip,
                "curveLossCoin =", curveLossCoin, "curveProfitCoin =", curveProfitCoin, "extendId =", extendId,
                "otherCatch =", otherCatch, "gunX =", gunX
            )
        player.dynamicOdds.updateOdds(curveProfitCoin - curveLossCoin)
        self.dealGunEffect(player, notCatchFids)                        # 1165的火炮ID, 霜冻特性，有几率冰冻鱼
        player.checkConnect(isInvalid)
        if isCatch:
            player.addCombo()
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.getPlayer(userId)
            if otherPlayer:
                self.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                               catchInfo["gainChip"], catchInfo["exp"], _fpMultiple, extends, isFraud=True)
        # 查看特殊鱼捕获数据日志！
        if wpType in [
                config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE,
                config.SUPERBOSS_WEAPON_TYPE
            ]:
            ftlog.info("_catchFish, fish order, userId =", player.userId, "wpType =", wpType, "fIdTypes =", fIdTypes,
                       "fIds =", fIds, "catch =", catch)
        return catch, gain, gainChip, exp

    def _getNowTableTime(self):
        """获取桌子的在线时长"""
        return time.time() - self.startTime
    
    def _surpassTarget(self, msg, userId, seatId):
        pass
    
    def _totalCatch(self, msg, userId, seatId):
        """发送圆盘数据"""
        player = self.getPlayer(userId)
        if player is None:
            return
        wpId = msg.getParam("wpId")
        fResId = msg.getParam("fishResId")
        skillId = msg.getParam("skillId")
        totalCoin = msg.getParam("totalCoin")
        fishId = msg.getParam("fishId")
        multiple = msg.getParam("multiple")
        fpMultiple = msg.getParam("fpMultiple", self.runConfig.multiple)
        wpType = util.getWeaponType(wpId)

        mo = MsgPack()
        mo.setCmd("total_catch")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("seatId", seatId)
        mo.setResult("wpId", wpId)
        mo.setResult("fishResId", fResId)
        mo.setResult("skillId", skillId)
        # mo.setResult("totalCoin", totalCoin)
        mo.setResult("fishId", fishId)
        mo.setResult("multiple", multiple)
        # mo.setResult("fpMultiple", fpMultiple)
        # GameMsg.sendMsg(mo, self.getBroadcastUids(userId))
        if not player.isFpMultipleMode():
            mo.setResult("totalCoin", totalCoin)
            mo.setResult("fpMultiple", fpMultiple)
            GameMsg.sendMsg(mo, self.getBroadcastUids(userId))
        else:
            fpModeUids = []
            for i in xrange(0, self.maxSeatN):
                if self.seats[i].userId != 0 and int(self.seats[i].userId) != int(userId):
                    _player = self.getPlayer(self.seats[i].userId)
                    if _player and _player.isFpMultipleMode():
                        fpModeUids.append(self.seats[i].userId)
            oldModeUids = list(set(self.getBroadcastUids(userId)) - set(fpModeUids))
            if oldModeUids:
                if fpModeUids:
                    mo.setResult("totalCoin", totalCoin)
                    mo.setResult("fpMultiple", fpMultiple)
                    GameMsg.sendMsg(mo, fpModeUids)

                mo.setResult("totalCoin", int(1. * totalCoin * self.runConfig.multiple / fpMultiple))
                mo.setResult("fpMultiple", self.runConfig.multiple)
                GameMsg.sendMsg(mo, oldModeUids)
            else:
                mo.setResult("totalCoin", totalCoin)
                mo.setResult("fpMultiple", fpMultiple)
                GameMsg.sendMsg(mo, self.getBroadcastUids(userId))

        event = CatchEvent(userId, FISH_GAMEID, self.roomId, self.tableId, [], wpId, totalCoin, fpMultiple)
        player.activitySystem and player.activitySystem.dealDrillCatchFish(event)
        if wpType in [config.DRILL_WEAPON_TYPE, config.SUPERBOSS_WEAPON_TYPE]:
            self.checkBigPrize(player, totalCoin / (multiple * fpMultiple), totalCoin, fpMultiple)

        if self.typeName not in [config.FISH_FRIEND]:
            return
        if self.runConfig.fishPool == 44001:
            return
        # 渔场倍率AB测试期间，B模式不开启捕获led
        if config.getPublic("fpMultipleTestMode") is None and player.isFpMultipleMode():
            return
        fishConf = config.getFishConf(fResId, self.typeName, fpMultiple)
        if fishConf.get("type", None) in config.TERROR_FISH_TYPE and totalCoin / fpMultiple >= 1500:
            # msg = u"恭喜%s在%s成功捕获%s，获得%s金币" % \
            mid = "ID_LED_CATCH_TERROR_FISH"
            title = config.getMultiLangTextConf(self.runConfig.title, lang=player.lang)
           # msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
           #         player.name, self.runConfig.title, fishConf["name"], util.formatScore(totalCoin, lang=player.lang))
            msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                    player.name, title, config.getMultiLangTextConf(fishConf["name"], lang=player.lang), util.formatScore(totalCoin, lang=player.lang))
            user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            if ftlog.is_debug():
                ftlog.debug("totalCatch", userId, totalCoin, self.runConfig.multiple, fpMultiple, totalCoin)
    
    def getCatchProbb(self, player, wpConf, fId, fIdsCount=1, superBullet=None, extendId=None, aloofOdds=0, nonAloofOdds=0, stageId=0, datas=None):
        """
        获取捕获概率
        :param player: 玩家
        :param wpConf: 武器配置
        :param fId: 鱼ID
        :param fIdsCount: 一网捞上来鱼的数据
        :param superBullet: 超级子弹
        :param extendId: 扩展ID
        :param aloofOdds: 是否高冷鱼
        :param nonAloofOdds: 没有高冷鱼的概率
        :param stageId: 阶段
        :param datas: 整理的数据
        """
        totalFishScore = datas and datas.get("totalFishScore", 0) or 0      # 鱼的总积分
        multiple = datas and datas.get("multiple", None) or None            # 开火时的倍率
        bulletPowerPool = datas and datas.get("bulletPowerPool", 0) or 0    # 子弹能量池
        _fpMultiple = datas and datas.get("fpMultiple", self.runConfig.multiple) or self.runConfig.multiple
        if ftlog.is_debug():
            ftlog.debug("getCatchProbb", player.userId, wpConf, fId, fIdsCount, superBullet, extendId, aloofOdds, nonAloofOdds, stageId)
        wpId = wpConf["weaponId"]
        wpType = util.getWeaponType(wpId)
        # 炮倍数.
        gunX = util.getGunX(wpId, self.gameMode)
        fishInfo = self.fishMap[fId]
        fishType = fishInfo["conf"]["fishType"]
        fishConf = config.getFishConf(fishType, self.typeName, _fpMultiple)
        _ft = fishConf["type"]
        coefficient = self.getProbbCoefficient(player, fishConf, fishInfo)  # 获取概率系数
        superBullet = superBullet or {}
        # 威力加成
        effectAddition = superBullet.get("effectAddition", 1)
        honorAddition = honor_system.getWeaponPowerAddition(player.ownedHonors, wpId)   # 获得特殊称号的武器威力加成
        bufferAddition = player.getPowerAddition(wpId)
        wpPower = 0
        initWpPower = 0
        if wpType == config.GUN_WEAPON_TYPE:  # 火炮
            wpPower = wpConf["power"] * effectAddition * honorAddition * bufferAddition     # 武器威力
            wpPower = player.processBulletPower(wpPower, totalFishScore, _fpMultiple, multiple, fIdsCount, bulletPowerPool, gunX)
        elif wpType in [config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE, config.SUPERBOSS_WEAPON_TYPE]:  # [炸弹鱼, 电鳗, 钻头鱼]
            wpPower = player.getFirePower(extendId, stageId, wpId=wpId)
            if wpPower <= 0:
                return 0
            wpPower *= honorAddition
            initWpPower = player.getFireInitPower(extendId, stageId) * honorAddition
        # 扣减鱼血量
        fatal = self.dealIceConeEffect(fId, fishConf)
        fishHP = int(self.fishMap[fId]["HP"] - wpPower)
        fishHP = self.dealFishHP(fId, fishHP, fatal)
        # 计算概率
        odds = 0
        probb = 0
        probbRadix = self.getFishProbbRadix(fishInfo, fishConf, player, _fpMultiple, gunX=gunX)
        if probbRadix == 0:         # 捕获概率为0
            if fishHP <= 0:         # 鱼的血量
                probb = 10000
            else:
                probb = 0
        else:
            if wpType == config.GUN_WEAPON_TYPE:        # 火炮
                if _ft in config.NON_ALOOF_FISH_TYPE:   # 非高冷鱼
                    odds = nonAloofOdds
                else:
                    odds = aloofOdds
                probb = float(odds) * (float(wpPower) / fIdsCount / probbRadix * 10000)
                if int(self.runConfig.fishPool) == 44002 and player.level <= 11 and player.holdCoin < 500:
                    oldProbb = probb
                    probb = min(4 * probb, 10000)
                    if ftlog.is_debug():
                        ftlog.debug("increaseCatchProbb", "fishPool =", self.runConfig.fishPool, "userId =", player.userId,
                                "level =", player.level, "chip =", player.holdCoin, "oldProbb =", oldProbb, "probb =", probb)
            elif wpType == config.BOMB_WEAPON_TYPE or (wpType == config.DRILL_WEAPON_TYPE and stageId == 1):   # 炸弹鱼 or 钻头鱼
                if wpPower >= probbRadix:
                    probb = 10000
                else:
                    probb = float(wpPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, probbRadix, stageId)
            elif wpType == config.NUMB_WEAPON_TYPE:   # 电鳗
                if wpPower >= probbRadix:
                    probb = 10000
                else:
                    probb = float(wpPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, probbRadix, stageId)
            elif wpType == config.DRILL_WEAPON_TYPE:   # 钻头鱼
                unitPower = int(initWpPower * float(wpConf.get("wpRatio", 1)))
                costPower = min(wpPower, min(probbRadix, unitPower))
                probb = float(costPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, costPower, stageId)      # 减少子弹威力
            elif wpType == config.SUPERBOSS_WEAPON_TYPE:    # 超级boss
                if wpPower >= probbRadix:
                    probb = 10000
                else:
                    probb = float(wpPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, probbRadix, stageId)
        probb *= coefficient
        if _ft in config.MULTIPLE_FISH_TYPE:                                # 倍率鱼
            isLucky, _ = self.room.lotteryPool.isMultiplePoolLucky()
            if isLucky:
                probb *= 1.2
        elif _ft in config.BOSS_FISH_TYPE:                                  # boss鱼
            gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
            if player.dynamicOdds.currRechargeBonus >= fishConf["value"] * gunMultiple * gunX * _fpMultiple:
                probb *= 2
        elif _ft in config.RED_FISH_TYPE:                                   # 红包鱼
            probb *= player.catchRedFishProbbRatio
            if player.userId in config.getPublic("banRedFishList", []):
                probb *= 0.3

        # gunSkinPoolCoin = player.gunSkinPool.setdefault(str(gunSkinId), 0)
        # costCoin = (effectAddition * 6 / 7) * self.getCostBullet(gunSkinId, gunSkinLevel, wpConf) * self.runConfig.multiple / fIdsCount
        #
        # if superBullet and random.randint(1, 10000) <= 3000:
        #     effectAddition *= 7
        #     if aloofFish:
        #         if gunSkinPoolCoin > costCoin:
        #             player.gunSkinPool[str(gunSkinId)] -= int(abs(costCoin))
        #         else:
        #             effectAddition = superBullet.get("effectAddition", 1)
        # 新手任务6期间普通子弹捕获概率不低于20%，boss除外
        if self.typeName == config.FISH_NEWBIE and not player.redState and wpType == config.GUN_WEAPON_TYPE \
                and player.taskSystemUser and _ft not in config.BOSS_FISH_TYPE:
            taskId = player.taskSystemUser.getCurMainTaskId()
            if taskId == 10006:
                probb = max(2000, probb)
                if ftlog.is_debug():
                    ftlog.debug("unfinishRedTask, userId =", player.userId)

        if ftlog.is_debug():
            ftlog.debug(
                "getCatchProbb->", "userId =", player.userId, "odds =", odds, "probb =", probb, "wpId =", wpId,
                "fId =", fId, "fIdsCount =", fIdsCount, "superBullet =", superBullet, "extendId =", extendId,
                "aloofOdds =", aloofOdds, "nonAloofOdds =", nonAloofOdds, "stageId =", stageId, "fishType =", fishType,
                "coefficient =", coefficient, "effectAddition =", effectAddition, "honorAddition =", honorAddition,
                "bufferAddition =", bufferAddition, "wpPower =", wpPower, "initWpPower =", initWpPower, "fatal =", fatal,
                "fishHP =", fishHP, "probbRadix =", probbRadix, "currRechargeBonus =", player.dynamicOdds.currRechargeBonus,
                "redState =", player.redState, "gunX =", gunX)
        return probb

    def getProbbCoefficient(self, player, fishConf, fishInfo):
        """获取概率系数"""
        return 1

    def isNeedAdjustFishProbbRadix(self, fishConf, player):
        """
        10倍场主线任务处于1-2期间，捕获难度及威力倍率调整
        """
        if self.runConfig.fishPool == 44002 and fishConf["type"] in config.BOMB_FISH_TYPE:
            if player.mainQuestSystem and player.mainQuestSystem.currTask:
                if ftlog.is_debug():
                    ftlog.debug("getFishProbbRadix->userId =", player.userId, "currTask =", player.mainQuestSystem.currTask)
                if player.mainQuestSystem.currTask.get("taskId") == 641002 and player.mainQuestSystem.currTask.get("state") == 0:
                    if ftlog.is_debug():
                        ftlog.debug("getFishProbbRadix->userId =", player.userId, " need adjust radix !")
                    return True
        return False

    def getFishProbbRadix(self, fishInfo, fishConf, player, fpMultiple=None, gunX=1):
        """鱼被捕获的概率基数"""
        if fpMultiple is None:
            fpMultiple = self.runConfig.multiple
        # 10倍场在完成641002时，难度使用200.
        if self.isNeedAdjustFishProbbRadix(fishConf, player):
            return 200
        if fishInfo["HP"] > 0:
            return fishConf["probb2"]
        elif fishConf["type"] in config.CHIP_CHEST_FISH_TYPE:
            if player.userId == fishInfo["owner"]:
                return fishConf["probb1"]
            return fishConf["probb2"]
        elif fishConf["type"] in config.RAINBOW_BONUS_FISH_TYPE:    # 使用彩虹奖池的鱼
            value = fishConf["score"]
            gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
            if fishConf["type"] in config.TERROR_FISH_TYPE:         # 恐怖鱼
                value = config.getWeaponConf(fishConf["weaponId"], False, mode=self.gameMode)["power"]
            if player.dynamicOdds.currRechargeBonus >= value * gunMultiple * gunX * fpMultiple:     # 当前充值奖池
                if ftlog.is_debug():
                    ftlog.debug("getFishProbbRadix->userId =", player.userId, "currRechargeBonus =", player.dynamicOdds.currRechargeBonus, "gunX =", gunX)
                return fishConf["probb1"]
            return fishConf["probb2"]
        else:
            return fishConf["probb1"]

    # 冰锥星级属性(无法被一击必杀)是否生效
    def dealIceConeEffect(self, fId, fishConf):
        """处理冰锥效果"""
        fishInfo = self.fishMap[fId]
        # fishType = fishInfo["conf"]["fishType"]
        # fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
        ftType = fishConf["type"]
        currentFishHP = fishInfo["HP"]
        fatal = 0
        if fishInfo["buffer"]:
            for buffer in fishInfo["buffer"]:
                skillId = buffer[0]
                skillEndTime = buffer[1]
                releaseUserId = buffer[2]
                skillType = buffer[7] if len(buffer) > 7 else 0
                if ftlog.is_debug():
                    ftlog.debug("dealSkillEffect->skillId =", skillId, skillEndTime, releaseUserId, skillType)
                if skillId == 5104 and ftType in config.ICE_FISH_TYPE:  # 冰锥
                    releasePlayer = self.getPlayer(releaseUserId)
                    if releasePlayer and releasePlayer.getSkill(skillId, skillType):
                        skill = releasePlayer.getSkill(skillId, skillType)
                        fatal = skill.fatal
        if ftType in config.ICE_FISH_TYPE and fatal > 0 and currentFishHP >= fishConf["HP"] * fatal:
            return True
        return False

    # 处理鱼的血量
    def dealFishHP(self, fId, fishHP, fatal):
        """
        :param fId: 鱼的ID
        :param fishHP: 鱼的剩余血量
        :param fatal: 冰锥65%以上 不死
        """
        if fishHP > 0:
            self.fishMap[fId]["HP"] = fishHP
        else:
            self.fishMap[fId]["HP"] = 0
            if fatal:
                self.fishMap[fId]["HP"] = 1
        return self.fishMap[fId]["HP"]

    def dealKillFishGain(self, fId, player, fpMultiple, gunMultiple=1, bufferCoinAdd=1, wpType=None, extends=None, gunX=1):
        """
        处理打死鱼获得的奖励
        :param fId: 被捕获鱼的ID
        :param player: 捕鱼者
        :param fpMultiple: 渔场倍率
        :param gunMultiple: 炮的倍率
        :param bufferCoinAdd: buffer加成金币系数
        :param wpType: 武器类型
        :param extends: 扩展
        :param gunX: 炮的倍数
        """
        gainChip = 0
        exp = 0
        gain = []
        gainMap = {}
        fishType = self.fishMap[fId]["conf"]["fishType"]
        fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
        # catchDropConf = config.getCatchDropConf(self.runConfig.fishPool)
        if ftlog.is_debug():
            ftlog.debug("dealKillFishGain", "fId =", fId, "fishConf =", fishConf, "userId =", player.userId,
                        "gunMultiple =", gunMultiple, "gunX =", gunX, "bufferCoinAdd =", bufferCoinAdd)
        # _fishPool = player.getMatchingFishPool(fpMultiple)
        if fishConf["score"] > 0:
            gainMap["type"] = fishConf["type"]
            gainMap["fId"] = fId
            gainMap["itemId"] = int(fishConf["itemId"])     # 掉落的道具
            gainMap["count"] = int(fishConf["score"])       # 掉落的数量
            isLucky = False
            if int(fishConf["itemId"]) == CHIP_KINDID:      # 被捕获后掉落金币
                if fishConf["type"] in config.MULTIPLE_FISH_TYPE:
                    multiple, isLucky = self.getFishMultiple(player, fishConf, fpMultiple, gunX)
                    if ftlog.is_debug():
                        ftlog.debug("getFishMultiple", "userId =", player.userId, "multiple =", multiple, "isLucky =", isLucky)
                    gainMap["count"] = int(fishConf["score"] * multiple)
                    gainMap["fishMultiple"] = multiple
                elif fishConf["type"] in config.CHIP_CHEST_FISH_TYPE:   # 金币宝箱
                    gainMap["count"] = int(self.fishMap[fId]["score"])
                _count = gainMap["count"]
                gainMap["count"] = _count * fpMultiple                  # 获取数量 * 渔场倍率
                gainMap["normalCount"] = _count * self.runConfig.multiple   # 场次倍率
                # # 大奖赛boss掉落金币逻辑.
                # if fishConf["type"] in config.BOSS_FISH_TYPE and self.runConfig.typeName in [config.FISH_GRAND_PRIX]:
                #     minCount = max(1., 0.5 * fishConf["score"] * fpMultiple)
                #     maxCount = 1.5 * fishConf["score"] * fpMultiple
                #     cnt = random.uniform(minCount, maxCount) / 5000
                #     _count = int(cnt)
                #     if random.randint(1, 10000) <= int((cnt - _count) * 10000):
                #         _count += 1
                #     ftlog.debug("grandPrixCoin, userId =", player.userId, "minCount =", minCount, "maxCount =", maxCount,
                #                 "cnt =", cnt, "_count =", _count)
                #     gainMap["count"] = _count * 5000
                #     gainMap["normalCount"] = _count * 5000
                exp = int(fishConf["score"])                            # 升级玩家等级的经验
                gainChip = int(gainMap["count"] * gunMultiple * gunX * bufferCoinAdd)
                # boss单独检测幸运降临
                if fishConf["type"] in config.BOSS_FISH_TYPE:
                    self.checkBigPrize(player, gainChip / (gunMultiple * gunX * fpMultiple), gainChip, fpMultiple, True)
                # 检测非特殊鱼捕获时的幸运降临
                elif wpType not in [config.NUMB_WEAPON_TYPE, config.BOMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE,
                                    config.SUPERBOSS_WEAPON_TYPE]:
                    self.checkBigPrize(player, gainChip / (gunMultiple * gunX * fpMultiple), gainChip, fpMultiple)
            elif int(fishConf["itemId"]) in BULLET_KINDIDS:             # 被捕获后掉落招财珠
                # 10倍场未完成持有10万金币主线任务，将掉落的珠子转成等值金币.
                needExchangeToChip = False
                if self.runConfig.fishPool == 44002 and player.mainQuestSystem and player.mainQuestSystem.currTask:
                    _taskId = player.mainQuestSystem.currTask.get("taskId", 0)
                    if ftlog.is_debug():
                        ftlog.debug("dealKillFishGain, userId =", player.userId, "taskId =", _taskId, "type =", type(_taskId))
                    if player.mainQuestSystem.currTask.get("taskId", 0) <= 642003:
                        needExchangeToChip = True
                # 渔场倍率AB测试特殊处理B模式掉落招财珠数量。
                if player.isFpMultipleMode():
                    minCount = max(1., 0.5 * fishConf["score"] * fpMultiple / player.getMatchingFpMultiple(fpMultiple))
                    maxCount = 1.5 * fishConf["score"] * fpMultiple / player.getMatchingFpMultiple(fpMultiple)
                    cnt = random.uniform(minCount, maxCount)
                    _count = int(cnt)
                    if random.randint(1, 10000) <= int((cnt - _count) * 10000):
                        _count += 1
                    if ftlog.is_debug():
                        ftlog.debug("gainBullet, userId =", player.userId, "minCount =", minCount, "maxCount =", maxCount, "cnt =", cnt, "_count =", _count)
                else:
                    _count = int(fishConf["score"])
                gainMap["count"] = _count
                gainMap["normalCount"] = int(fishConf["score"])
                exp = int(fishConf["score"]) * BULLET_KINDIDS[int(fishConf["itemId"])] / fpMultiple
                if needExchangeToChip:
                    gainMap["itemId"] = CHIP_KINDID
                    gainMap["count"] = int(gainMap["count"] * BULLET_KINDIDS[int(fishConf["itemId"])])
                    gainMap["normalCount"] = int(gainMap["normalCount"] * BULLET_KINDIDS[int(fishConf["itemId"])])
                    gainChip = gainMap["count"]
                    if ftlog.is_debug():
                        ftlog.debug("bulletExchangedToChip", "fishPool =", self.runConfig.fishPool, "userId =", player.userId,
                                "preItem =", fishConf["itemId"], "preCount =", fishConf["score"], "gain =", gainMap)
                chipValue = int(_count * BULLET_KINDIDS[int(fishConf["itemId"])])
                # boss单独处理幸运降临
                if fishConf["type"] in config.BOSS_FISH_TYPE:
                    self.checkBigPrize(player,  chipValue / fpMultiple, chipValue, fpMultiple, True)
            if fishConf["type"] in config.SUPERBOSS_FISH_TYPE:
                gainMap["count"] = random.randint(fishConf["minCount"], fishConf["maxCount"]) * gunMultiple * gunX
            if fishConf["type"] == 13:  # 捕获随机奖券鱼
                _, items = drop_system.getDropItem(fishConf["itemId"])
                gainMap["itemId"] = items["name"]
                gainMap["count"] = items["count"]
            gainMap["count"] *= gunMultiple * gunX * bufferCoinAdd
            if "normalCount" in gainMap:
                gainMap["normalCount"] *= gunMultiple * gunX * bufferCoinAdd
            gain.append(gainMap)
            if isLucky:
                self.room.lotteryPool.deductionMultiplePoolCoin(gainChip)
            if fishConf["type"] in config.CHIP_CHEST_FISH_TYPE and gunMultiple * gunX > 1:      # 金币宝箱
                self.room.lotteryPool.deductionChestPoolCoin(gainChip / (gunMultiple * gunX) / bufferCoinAdd)
            if fishConf["type"] in config.STAR_FISH_TYPE:           # 被捕获后概率掉落海星
                # dropConf = catchDropConf.get(str(STARFISH_KINDID))
                if fishConf["type"] in config.BOSS_FISH_TYPE:       # Boss必定掉落海星
                    dropConf = config.getCatchDropConf(fpMultiple, "BOSS_FISH_TYPE", player.userId)
                else:
                    dropConf = config.getCatchDropConf(fpMultiple, "STAR_FISH_TYPE", player.userId)
                if dropConf and dropConf["probability"] > 0:
                    if fishConf["type"] in config.BOSS_FISH_TYPE:  # Boss必定掉落海星
                        probability = int(dropConf["probability"])
                    else:
                        probability = int(fishConf["score"] / float(dropConf["probability"]) * 10000)
                        if player.gunId == 1290 and player.starfish >= 10000:  # 装备暮刃且今日海星数超过1w，概率减半
                            probability /= 2
                    if random.randint(1, 10000) <= probability:
                        itemGainMap = {}
                        itemGainMap["fId"] = fId
                        itemGainMap["itemId"] = dropConf["kindId"]  # STARFISH_KINDID
                        _count = random.randint(dropConf["min"], dropConf["max"])
                        _count *= gunMultiple * gunX * bufferCoinAdd
                        itemGainMap["normalCount"] = _count
                        itemGainMap["count"] = _count
                        gain.append(itemGainMap)
            if fishConf["type"] in config.PEARL_FISH_TYPE:      # 被捕获后概率掉落珍珠
                # dropConf = catchDropConf.get(str(PEARL_KINDID))
                dropConf = config.getCatchDropConf(fpMultiple, "PEARL_FISH_TYPE", player.userId)
                if dropConf and dropConf["probability"] > 0:
                    probability = int(fishConf["score"] / float(dropConf["probability"]) * 10000)
                    if player.level < 16:                       # 当用户留有珍珠数量大于后2级升级所需之和，则不掉落珍珠
                        upgradeItemsConf1 = gun_system.getUpgradeItemsConf(player.userId, player.gunLevel + 1)
                        upgradeItemsConf2 = gun_system.getUpgradeItemsConf(player.userId, player.gunLevel + 2)
                        totalCount = upgradeItemsConf1.get(str(PEARL_KINDID), 0)
                        totalCount += upgradeItemsConf2.get(str(PEARL_KINDID), 0)
                        if player.pearlCount >= totalCount:
                            probability = 0
                    if 3 <= player.level <= 5:
                        probability *= 5
                    elif player.level < 10:
                        probability *= 2
                    # 在完成新手教学4和5时,若未掉落珍珠,则每累计捕获15条鱼必掉1个珍珠.
                    dropCount = random.randint(dropConf["min"], dropConf["max"])
                    if not player.isFinishRedTask and probability > 0 and player.taskSystemUser and player.taskSystemUser.getCurMainTaskId() in [10004, 10005]:
                        player.killPearlFishCount += 1
                        if player.killPearlFishCount >= 15:
                            player.killPearlFishCount = 0
                            probability = 10000
                            dropCount = 1
                    ratio = player.getPearlDropRatio(str(fpMultiple))
                    # ratio = config.getUlevel(player.level).get(str(self.runConfig.fishPool)）
                    if random.randint(1, 10000) <= min(10000, probability * ratio):
                        player.killPearlFishCount = 0
                        itemGainMap = {}
                        itemGainMap["fId"] = fId
                        itemGainMap["itemId"] = dropConf["kindId"]# PEARL_KINDID
                        itemGainMap["count"] = dropCount# random.randint(dropConf["min"], dropConf["max"])
                        itemGainMap["count"] *= gunMultiple * gunX * bufferCoinAdd
                        gain.append(itemGainMap)
            if fishConf["type"] in config.CRYSTAL_FISH_TYPE:  # 被捕获后概率掉落水晶
                # if random.randint(0, 1):
                #     dropConf = catchDropConf.get(str(config.PURPLE_CRYSTAL_KINDID))
                # else:
                #     dropConf = catchDropConf.get(str(config.YELLOW_CRYSTAL_KINDID))
                dropConf = config.getCatchDropConf(fpMultiple, "CRYSTAL_FISH_TYPE", player.userId)
                if dropConf and dropConf["probability"] > 0:
                    probability = int(fishConf["score"] / float(dropConf["probability"]) * 10000)
                    ratio = player.incrCrystalDropRatio + config.getUlevel(player.level).get(str(fpMultiple), 0)
                    if ftlog.is_debug():
                        ftlog.debug("dropCrystal, userId =", player.userId, ratio, player.incrCrystalDropRatio)
                    if random.randint(1, 10000) <= probability * ratio:
                        itemGainMap = {}
                        itemGainMap["fId"] = fId
                        itemGainMap["itemId"] = dropConf["kindId"]
                        itemGainMap["count"] = random.randint(dropConf["min"], dropConf["max"])
                        itemGainMap["count"] *= gunMultiple * gunX * bufferCoinAdd
                        gain.append(itemGainMap)
            if fishConf["type"] in config.BOSS_FISH_TYPE:       # Boss鱼掉落宝箱
                deductionCoin = fishConf["value"] * gunMultiple * gunX * fpMultiple
                if player.dynamicOdds.currRechargeBonus >= deductionCoin:
                    player.dynamicOdds.deductionRechargeBonus(deductionCoin)
                dropChestList = config.getPublic("bossDropChestConf", {}).get(str(fpMultiple))
                if dropChestList:
                    chestGainMap = {}
                    chestGainMap["fId"] = fId
                    chestGainMap["itemId"] = dropChestList[0]
                    chestGainMap["count"] = 1
                    gain.append(chestGainMap)

            # 记录捕鱼收益数据.
            fish_type = fishType
            if extends and len(extends) > 1 and wpType in (
                    config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE,
                    config.SUPERBOSS_WEAPON_TYPE
                ):
                fish_type = player.getFire(extends[0]).get("fishType")
                if fish_type is None:
                    fish_type = extends[1]
            if fishConf["type"] in config.MULTIPLE_FISH_TYPE:
                benefit = gainChip
            else:
                benefit = fishConf["value"] * fpMultiple * gunMultiple * gunX
            self.cb_reporter.add_benefit(fish_type, benefit)
            if ftlog.is_debug():
                ftlog.debug("report, fish benefit", fish_type, benefit, fishConf["type"], gainChip)
        else:
            if fishConf["type"] in config.BUFFER_FISH_TYPE:  # 捕获buffer鱼
                gainMap["fId"] = fId
                bufferId = player.getCatchBufferId(fishConf["itemId"])
                if bufferId > 0:
                    gainMap["itemId"] = bufferId
                    gainMap["count"] = 1
                gain.append(gainMap)
            elif fishConf["type"] in config.HIPPO_FISH_TYPE:        # 捕获后掉口红的鱼
                gainMap["fId"] = fId
                _, items = drop_system.getDropItem(fishConf["itemId"])
                gainMap["itemId"] = items["name"]
                gainMap["count"] = int(items["count"] * gunMultiple * gunX * bufferCoinAdd)# * 1. * fpMultiple / player.getMatchingFpMultiple(fpMultiple))
                gain.append(gainMap)
        return gainChip, gain, exp

    def getFishMultiple(self, player, fishConf, fpMultiple, gunX):
        """
        获得倍率鱼的倍率
        :return: (倍数, 是否扣减倍率池)
        """
        isHighProbb = False
        isRechargeAddition = False
        isLucky, luckyCount = self.room.lotteryPool.isMultiplePoolLucky()   # 是否为倍率池幸运时间和次数
        gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
        deductionCoin = fishConf["value"] * gunMultiple * gunX * fpMultiple
        if player.dynamicOdds.currRechargeBonus >= deductionCoin:
            isRechargeAddition = True
        if isLucky:
            luckyNum = random.randint(player.level * 20, 10100)
            if luckyCount != player.luckyCount:
                player.luckyNum = luckyNum
                player.luckyCount = luckyCount
            if player.luckyNum < 5000:
                isHighProbb = True
        if ftlog.is_debug():
            ftlog.debug(
                "getFishMultiple->" "userId =", player.userId, "fishConf =", fishConf, "isLucky =", isLucky,
                "luckyCount =", luckyCount, "isHighProbb =", isHighProbb, "isRechargeAddition =", isRechargeAddition,
                "gunMultiple =", gunMultiple, "gunX =", gunX
            )
        randInt = random.randint(1, 10000)
        for multipleMap in config.getMultipleFishConf(self.runConfig.fishPool):
            if isHighProbb:
                if multipleMap.get("highProbb"):
                    probb = multipleMap["highProbb"]
                else:
                    continue
                if probb[0] <= randInt <= probb[-1]:
                    if ftlog.is_debug():
                        ftlog.debug("getFishMultiple->isHighProbb", multipleMap["multiple"], probb, randInt)
                    return multipleMap["multiple"], True
            elif isRechargeAddition:
                if multipleMap.get("rechargeProbb"):
                    probb = multipleMap["rechargeProbb"]
                else:
                    continue
                if probb[0] <= randInt <= probb[-1]:
                    if ftlog.is_debug():
                        ftlog.debug("getFishMultiple->isRechargeAddition", multipleMap["multiple"], probb, randInt)
                    player.dynamicOdds.deductionRechargeBonus(deductionCoin)
                    return multipleMap["multiple"], False
            else:
                probb = multipleMap["probb"]
                if probb[0] <= randInt <= probb[-1]:
                    if ftlog.is_debug():
                        ftlog.debug("getFishMultiple->normal", multipleMap["multiple"], probb, randInt)
                    return multipleMap["multiple"], False
        return 1, False

    # 处理打中boss掉落金币
    def dealHitBossGain(self, power, fId, player, originHP=0, totalProbb=1):
        gainChip = 0
        gain = []
        if player:
            player.addAttackBossNum(self.fishMap[fId])
        # gainMap = {}
        # fishType = self.fishMap[fId]["conf"]["fishType"]
        # fishConf = config.getFishConf(fishType)
        # totalProbb = totalProbb if totalProbb > 0 else fishConf["score"]
        # if fishConf["type"] == 2:
        #     if originHP <= 0:
        #         probb = fishConf["probb1"] if fishConf["probb1"] > 0 else fishConf["score"]
        #     else:
        #         probb = fishConf["probb2"] if fishConf["probb2"] > 0 else fishConf["score"]
        #     ftlog.debug("dealHitBossGain->power =", power, "probb =", probb, "totalProbb", totalProbb,
        #                 "fishPower =", self.fishMap[fId].get("power", 0))
        #     power = power * probb / totalProbb + self.fishMap[fId].get("power", 0)
        #     bearPower = power // 10 * 10
        #     randInt = random.randint(1, 10000)
        #     for multipleMap in config.getHitBossConf():
        #         probb = multipleMap["probb"]
        #         if randInt >= probb[0] and randInt <= probb[-1]:
        #             multiple = multipleMap["multiple"]
        #             gainChip = int(multiple * bearPower * self.runConfig.multiple)
        #             if gainChip > 0:
        #                 ftlog.debug("dealHitBossGain->multiple =", multiple, "bearPower =", bearPower,
        #                             "power =", power)
        #                 if self.room.lotteryPool.getBossPoolCoin() > 0:
        #                     gainChip *= 2
        #                     self.room.lotteryPool.deductionBossPoolCoin(int(gainChip // 2))
        #                 gainMap["fId"] = fId
        #                 gainMap["itemId"] = CHIP_KINDID
        #                 gainMap["count"] = gainChip
        #                 break
        #     power -= bearPower
        #     self.fishMap[fId]["power"] = power
        return gainChip, gain

    # def getTotalProbb(self, player, fIds):
    #     totalProbb = 0
    #     aloofFish = False
    #     for fId in fIds:
    #         isOK, _, _ = self.verifyFish(player.userId, fId)
    #         if not isOK:
    #             continue
    #         fishType = self.fishMap[fId]["conf"]["fishType"]
    #         fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
    #         if fishConf["type"] not in config.NON_ALOOF_FISH_TYPE:
    #             aloofFish = True
    #         if self.fishMap[fId]["HP"] > 0:
    #             if fishConf["probb2"] == 0:
    #                 totalProbb += fishConf["score"]
    #             else:
    #                 totalProbb += fishConf["probb2"]
    #         else:
    #             if fishConf["probb1"] == 0:
    #                 totalProbb += fishConf["score"]
    #             else:
    #                 totalProbb += fishConf["probb1"]
    #     return totalProbb, aloofFish

    def _retVerifyCatch(self, player, bulletId, catch, gain, extends, skillId, stageId, fpMultiple, isFraud=False, skillType=0):
        """
        验证捕获 发送协议
        :param player: 玩家
        :param bulletId: 子弹ID
        :param catch: 捕获
        :param gain: 奖励
        :param extends: 扩展
        :param skillId: 技能
        :param stageId: 阶段
        :param fpMultiple: 渔场倍率
        :param isFraud:
        :param skillType: 技能类型
        :return:
        """
        if not player:
            return
        if skillId:
            skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
        else:
            skill = None
        if (not catch and not gain) and \
                (not skill or skill.isReturn != 1 or StrictVersion(str(player.clientVersion)) < StrictVersion(
                    str("2.0.45"))):
            return
        if ftlog.is_debug():
            ftlog.debug("_retVerifyCatch", player.userId, bulletId, catch, gain, extends, skillId, stageId, fpMultiple, skillType)
        extendId = extends[0] if extends else 0
        clip = 0
        if isFraud:
            multiple = 1
        else:
            if skillId:
                # skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
                if skill:
                    multiple = skill.gunSkinMultiple
                    clip = skill.clip
                else:
                    clip = 0
                    multiple = player.getGunConf(bulletId, extendId).get("multiple", 1)
            else:
                wpId = player.getFireWpId(bulletId)
                wpType = util.getWeaponType(wpId)
                if wpType == config.GUN_WEAPON_TYPE:
                    clip = player.clip
                multiple = player.getFireMultiple(bulletId, extendId)
                if multiple is None:
                    multiple = player.getGunConf(bulletId, extendId).get("multiple", 1)
        retMsg = MsgPack()
        retMsg.setCmd("catch")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("bulletId", bulletId)
        retMsg.setResult("userId", player.userId)
        retMsg.setResult("seatId", player.seatId)
        retMsg.setResult("combo", player.combo)
        retMsg.setResult("fIds", catch)             # 捕获的鱼
        # retMsg.setResult("items", gain)
        retMsg.setResult("skillId", skillId)
        retMsg.setResult("skillType", skillType)
        retMsg.setResult("stageId", stageId)
        retMsg.setResult("multiple", multiple)
        retMsg.setResult("extends", extends)        # 扩展
        retMsg.setResult("fpMultiple", fpMultiple)
        retMsg.setResult("clip", clip)              # 子弹
        userLevelConf = config.getUserLevelConf()
        lvUpExp = userLevelConf[player.level - 1]["exp"] if player.level <= len(userLevelConf) else userLevelConf[-1]["exp"]
        retMsg.setResult("expPct", min(100, max(0, int(player.exp * 100. / lvUpExp))))  # 经验百分比
        # 榴弹炮打空返还子弹只对玩家自己发送catch消息
        if not catch and not gain:
            retMsg.setResult("items", gain)         # 获得的奖励
            GameMsg.sendMsg(retMsg, player.userId)
            return
        if not player.isFpMultipleMode():
            retMsg.setResult("items", gain)
            GameMsg.sendMsg(retMsg, self.getBroadcastUids())
        else:
            fpModeUids = []                         # AB模式下的uids
            for i in xrange(0, self.maxSeatN):
                if self.seats[i].userId != 0:
                    _player = self.getPlayer(self.seats[i].userId)
                    if _player and _player.isFpMultipleMode():
                        fpModeUids.append(self.seats[i].userId)
            oldModeUids = list(set(self.getBroadcastUids()) - set(fpModeUids))
            if oldModeUids:
                retMsg.setResult("items", gain)
                GameMsg.sendMsg(retMsg, fpModeUids)
                for idx, _ in enumerate(gain):
                    if gain[idx].get("normalCount"):
                        gain[idx]["count"] = gain[idx]["normalCount"]
                retMsg.setResult("items", gain)
                retMsg.setResult("fpMultiple", self.runConfig.multiple)
                GameMsg.sendMsg(retMsg, oldModeUids)
            else:
                retMsg.setResult("items", gain)
                GameMsg.sendMsg(retMsg, self.getBroadcastUids())

    def setFishBuffer(self, fId, newBuffer):
        """
        给鱼添加buffer 鱼的buffer 人给鱼buffer
        :param fId: 鱼
        :param newBuffer: 新的buffer
        :return:
        """
        buffers = deepcopy(self.fishMap[fId]["buffer"])
        if buffers:
            for buffer in buffers:
                if newBuffer[0] == buffer[0]:       # 相同buffer会被新buffer替换
                    newBuffer[6] = buffer[6] + 1    # buffer次数
                    buffers.remove(buffer)
                    break
                elif newBuffer[0] == 5104 or buffer[0] == 5104:  # 冰冻buffer可以与其他buffer共存
                    continue
                else:
                    buffers.remove(buffer)          # 除冰冻外的其他buffer会被新buffer替换
                    break
        buffers.append(newBuffer)
        self.fishMap[fId]["buffer"] = buffers

    # 奖励给其他人(鱼处于欺诈水晶状态下)
    def extendOtherCatchGain(self, fId, catchUserId, otherCatch, gainChip, gain, catchMap=None, exp=0):
        """
        :param fId: 鱼ID
        :param catchUserId: 捕鱼者
        :param otherCatch: 其他捕获
        :param gainChip: 捕获获得的金币
        :param gain: 捕获获得的道具
        :param catchMap: 捕获信息列表
        :param exp: 捕获获得的经验
        :return:
        """
        if catchUserId not in otherCatch:
            otherCatch[catchUserId] = {}
            otherCatch[catchUserId]["catch"] = []
            otherCatch[catchUserId]["gain"] = []
            otherCatch[catchUserId]["gainChip"] = 0
            otherCatch[catchUserId]["exp"] = 0
        if catchMap:
            otherCatch[catchUserId]["catch"].append(catchMap)
        otherCatch[catchUserId]["gain"].extend(gain)
        otherCatch[catchUserId]["gainChip"] += int(gainChip)
        otherCatch[catchUserId]["exp"] += exp
        return otherCatch

    def dealCatch(self, bulletId, wpId, player, catch, gain, gainChip, exp, fpMultiple, extends=None, skillId=0, stageId=0, isFraud=False, skillType=0):
        """
        处理捕获
        :param bulletId: 子弹ID
        :param wpId: 武器ID
        :param player: 玩家
        :param catch: 捕获
        :param gain: 捕获道具
        :param gainChip: 捕获金币
        :param exp: 捕获金鱼
        :param fpMultiple: 渔场倍率
        :param extends: 扩展
        :param skillId: 技能
        :param stageId: 阶段Id
        :param isFraud:
        :param skillType: 技能类型0|1
        :return:
        """
        # self._retVerifyCatch(player, bulletId, catch, gain, extends, skillId)
        if ftlog.is_debug():
            ftlog.debug("dealCatch->", player.userId, bulletId, wpId, catch, gain, gainChip, exp, extends, skillId, stageId, fpMultiple)
        gainCoupon = 0
        items = []
        for gainMap in gain:
            gainMap["fishType"] = self.fishMap[gainMap["fId"]]["conf"]["fishType"]
            fishConf = config.getFishConf(gainMap["fishType"], self.typeName, fpMultiple)
            _fType = fishConf["type"]
            if gainMap and gainMap["itemId"] == CHIP_KINDID:
                pass
            elif gainMap and gainMap["itemId"] == COUPON_KINDID:
                gainCoupon += int(gainMap["count"])
            else:
                if _fType in config.BUFFER_FISH_TYPE:
                    player.addOneBufferId(gainMap["itemId"])
                else:
                    items.append(gainMap)
            if _fType in config.RED_FISH_TYPE:
                # 计算累计获得金额及个人奖券鱼捕获次数
                totalEntityAmount = gamedata.getGameAttr(player.userId, FISH_GAMEID, GameData.totalEntityAmount)
                totalEntityAmount = float(totalEntityAmount) if totalEntityAmount else 0
                totalEntityAmount += config.RED_AMOUNTS.get(gainMap["itemId"], 0)
                if gainMap["itemId"] == COUPON_KINDID:
                    totalEntityAmount += gainMap["count"] * config.COUPON_DISPLAY_RATE
                gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.totalEntityAmount, totalEntityAmount)
                if self.fishMap[gainMap["fId"]]["owner"] == player.userId:
                    catchCountDict = gamedata.getGameAttrJson(player.userId, FISH_GAMEID, GameData.catchUserCouponFishCount, {})
                    catchCountDict[str(self.runConfig.fishPool)] = catchCountDict.setdefault(str(self.runConfig.fishPool), 0) + 1
                    gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.catchUserCouponFishCount, json.dumps(catchCountDict))
            if _fType in config.LOG_OUTPUT_FISH_TYPE:
                ftlog.info("dealCatch->fishType",
                           "userId =", player.userId,
                           "fishType =", fishConf["type"],
                           "wpId =", wpId,
                           "gainMap =", gainMap,
                           "gainChip =", gainChip)
            # 捕获了超级boss添加积分到排行榜.
            if _fType in config.SUPERBOSS_FISH_TYPE:
                from newfish.game import TGFish
                from newfish.entity.event import SuperbossPointChangeEvent
                event = SuperbossPointChangeEvent(player.userId, FISH_GAMEID, self.bigRoomId, fishConf["score"])
                TGFish.getEventBus().publishEvent(event)

        # 处理玩家等级升级.
        nowExp = player.incrExp(exp)
        player.incExpLevel(nowExp)

        wpType = util.getWeaponType(wpId)
        if wpType == config.GUN_WEAPON_TYPE:
            gunExp = player.incrGunExp(exp)
            player.incrGunLevel(gunExp)
        if wpType in [
            config.SKILL_WEAPON_TYPE, config.RB_FIRE_WEAPON_TYPE, config.RB_BOMB_WEAPON_TYPE,
            config.BOMB_WEAPON_TYPE, config.NUMB_WEAPON_TYPE, config.DRILL_WEAPON_TYPE, config.SUPERBOSS_WEAPON_TYPE
            ]:
            ftlog.info("dealCatch->wpType", "userId =", player.userId, "wpId =", wpId, "wpType =", wpType, "gainChip =", gainChip)
        player.catchBudget(gainChip, gainCoupon, items, wpId=wpId)
        self._afterCatch(bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends, skillId, isFraud=isFraud, skillType=skillType)
        # self._enterNextRoom(oldLevel, player)
        self._retVerifyCatch(player, bulletId, catch, gain, extends, skillId, stageId, fpMultiple, isFraud=isFraud, skillType=skillType)

    # # 是否可以进入解锁的房间
    # def _enterNextRoom(self, oldLevel, player):
    #     if oldLevel == player.level or util.isFinishAllRedTask(player.userId):
    #         return
    #     allRoomIds = gdata.gameIdBigRoomidsMap()[FISH_GAMEID]
    #     allRoomConf = []
    #     for bigRid in allRoomIds:
    #         conf = gdata.getRoomConfigure(bigRid)
    #         if conf.get("typeName") != config.FISH_FRIEND:
    #             continue
    #         conf["roomId"] = bigRid
    #         allRoomConf.append(conf)
    #     allRoomConf.sort(key=lambda x: x["minLevel"], reverse=True)
    #     for roomConfig in allRoomConf:
    #         if roomConfig["minLevel"] <= oldLevel or roomConfig["minLevel"] > player.level:
    #             continue
    #         # 当超过下个房间准入的3倍时，提示是否进入下个房间
    #         if player.allChip >= roomConfig["minCoin"] * 3:
    #             self._sendEnterNextRoomMsg(roomConfig["roomId"], player)
    #             break

    def _sendEnterNextRoomMsg(self, roomId, player):
        """进入下一个房间"""
        msg = MsgPack()
        msg.setCmd("enter_next_room")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", player.userId)
        msg.setResult("roomId", roomId)
        GameMsg.sendMsg(msg, player.userId)

    def _afterCatch(self, bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends=None, skillId=0, isFraud=False, skillType=0):
        """
        捕获之后
        :param bulletId: 子弹ID
        :param wpId: 武器ID
        :param player: 玩家
        :param catch: 捕获信息
        :param gain: 获得奖励
        :param gainChip: 获取金币
        :param fpMultiple: 渔场倍率
        :param extends: 扩展
        :param skillId: 技能ID
        :param isFraud:
        :param skillType: 技能类型
        :return:
        """
        fIds = []
        fishTypes = []
        extendId = extends[0] if extends else 0
        gunConf = player.getGunConf(bulletId, extendId)
        skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
        player.addProfitCoin(gainChip)
        if isFraud:
            multiple = 1
        else:
            if skillId:
                if skill:
                    multiple = skill.gunSkinMultiple
                else:
                    multiple = gunConf.get("multiple", 1)
            else:
                multiple = player.getFireMultiple(bulletId, extendId)
                if multiple is None:
                    multiple = gunConf.get("multiple", 1)
        catchFishPoints = []
        for catchMap in catch:
            if catchMap["reason"] == 0:
                fId = catchMap["fId"]
                fishType = self.fishMap[fId]["conf"]["fishType"]
                fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
                if ftlog.is_debug():
                    ftlog.debug("_afterCatch", player.userId, fId, fishType)
                if self.fishMap[fId]["alive"]:                      # 鱼活着
                    self.refreshFishTypeCount(self.fishMap[fId])    # 扣除鱼类型的条数
                self.fishMap[fId]["alive"] = False                  # 鱼死
                fIds.append(fId)
                fishTypes.append(fishType)
                if fishConf["itemId"] != config.CHIP_KINDID:
                    # 非金币类鱼，使用其金币价值
                    player.addProfitCoin(fishConf.get("value", 0) * multiple * fpMultiple)
                if fishConf["type"] in config.NORMAL_FISH_TYPE:     # 处理普通鱼捕获（判断金币宝箱鱼是否出现）
                    self.chestFishGroup and self.chestFishGroup.checkCondition(player, fishConf)
                elif fishConf["type"] in config.BOSS_FISH_TYPE:     # 处理boss捕获（全民打boss活动）
                    for player_ in self.players:
                        if player_ and self.fishMap.get(fId):
                            player_.dealCatchBoss(self.fishMap[fId], player.userId)
                elif fishConf["type"] in config.TERROR_FISH_TYPE and "weaponId" in fishConf:  # 特殊鱼增加子弹数据
                    if self.isNeedAdjustFishProbbRadix(fishConf, player):
                        # 10倍场主线任务处于1-2期间，炸弹鱼威力倍率固定为1
                        wpConf = config.getWeaponConf(fishConf["weaponId"], False, mode=self.gameMode)
                    else:
                        wpConf = config.getWeaponConf(fishConf["weaponId"], mode=self.gameMode)
                    power = wpConf["power"]
                    # 钻头鱼
                    if fishConf["type"] in config.DRILL_FISH_TYPE:
                        catchMap["power"] = int(power * 0.4)
                        powerList = [catchMap["power"], power - catchMap["power"]]
                    else:
                        catchMap["power"] = power
                        powerList = [power]
                    # 添加特殊鱼这颗子弹
                    player.addFire(fId, fishConf["weaponId"], int(time.time()), fpMultiple, power=powerList, multiple=multiple,
                                   clientFire=False, fishType=fishType)
                    ftlog.info("addFire, userId =", player.userId, "fId =", fId, "power =", powerList,
                               "multiple =", multiple, "isFraud =", isFraud, "skill =", skill, "gunConf =", gunConf,
                               "extends =", extends, "bulletId =", bulletId, "wpId =", wpId)
                # 超级boss添加子弹数据.
                elif fishConf["type"] in config.SUPERBOSS_FISH_TYPE and self.superBossFishGroup and "weaponId" in fishConf:
                    self.superBossFishGroup.addFire(player, fId, fishConf["weaponId"], fpMultiple, multiple=multiple, fishType=fishType)
                if fishConf["type"] in config.RAINBOW_BONUS_FISH_TYPE:  # 彩虹鱼扣减奖池
                    value = fishConf["score"]
                    gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
                    gunX = util.getGunX(wpId, self.gameMode)
                    if fishConf["type"] in config.TERROR_FISH_TYPE:
                        value = config.getWeaponConf(fishConf["weaponId"], False, self.gameMode)["power"]
                    # 鱼分值/武器能量对应奖池
                    bonus = value * gunMultiple * gunX * fpMultiple
                    # 需扣减奖池
                    deductionBonus = (value - fishConf["probb1"]) * gunMultiple * gunX * fpMultiple
                    if ftlog.is_debug():
                        ftlog.debug("dealCatch->userId =", player.userId,
                                    "currRechargeBonus =", player.dynamicOdds.currRechargeBonus >= bonus,
                                    "getRainbowPoolCoin =", self.room.lotteryPool.getRainbowPoolCoin() >= bonus,
                                    "bonus =", bonus,
                                    "deductionBonus =", deductionBonus,
                                    "gunMultiple =", gunMultiple,
                                    "gunX =", gunX)
                    if player.dynamicOdds.currRechargeBonus >= bonus:
                        # 存在充值奖池
                        player.dynamicOdds.deductionRechargeBonus(deductionBonus)
                    elif self.room.lotteryPool.getRainbowPoolCoin() >= bonus:
                        # 存在彩虹鱼奖池
                        self.room.lotteryPool.deductionRainbowPoolCoin(deductionBonus)
                # 检测是否可以获得巨奖
                # 只有普通鱼可以获得巨奖.
                # if fishConf["type"] not in config.BOSS_FISH_TYPE + config.TERROR_FISH_TYPE + config.MULTIPLE_FISH_TYPE:
                if fishConf["type"] == 1:
                    self.checkGrandPrize(fishConf.get("score", 0), player, fId, fpMultiple)
                # 捕鱼轮盘充能
                if self.typeName in config.NORMAL_ROOM_TYPE:
                    self.addPrizeWheelEnergy(player, fId, fishConf, fpMultiple, multiple)
                # 计算捕鱼积分
                if self.typeName in [config.FISH_GRAND_PRIX] and fishConf.get("probb2", 0) > 0 \
                        and fishConf["type"] not in config.TERROR_FISH_TYPE:
                    point = fishConf["score"]
                    if fishConf["type"] in config.MULTIPLE_FISH_TYPE and catchMap.get("fishMultiple", 1) > 1:
                        point *= catchMap["fishMultiple"]
                        if ftlog.is_debug():
                            ftlog.debug("addGrandPrixFishPoint 2, userId =", player.userId, catchMap["fishMultiple"])
                    point = player.addGrandPrixFishPoint(point, str(fishType))
                    if point:
                        catchFishPoints.append({"fId": fId, "point": point})
        # 特殊鱼捕获时的幸运降临
        if util.getWeaponType(wpId) in [config.NUMB_WEAPON_TYPE, config.BOMB_WEAPON_TYPE]:
            totalCoin = sum([_val.get("count", 0) for _val in gain if _val.get("itemId") == CHIP_KINDID and _val.get("type") not in config.BOSS_FISH_TYPE])
            self.checkBigPrize(player, totalCoin / (multiple * fpMultiple), totalCoin, fpMultiple)

        if self.typeName in [config.FISH_GRAND_PRIX] and catchFishPoints:
            player.sendGrandPrixCatch(catchFishPoints)

        gunId = gunConf.get("gunId", 0)
        gunLevel = gunConf.get("gunLevel", 1)
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)
        self._sendLed(player, gain, fIds, fpMultiple)               # 发送奖励掉落
        player.addCatchFishes(fishTypes)                            # 捕获鱼的条数

        from newfish.game import TGFish
        event = CatchEvent(player.userId, FISH_GAMEID, self.roomId, self.tableId, fishTypes, wpId, gainChip, fpMultiple,
                           catch, gain, player.resetTime, gunConf.get("multiple", 1))
        TGFish.getEventBus().publishEvent(event)
        player.triggerCatchFishEvent(event)                         # 处理捕鱼事件
        if self.superBossFishGroup:                                 # 超级boss鱼群
            self.superBossFishGroup.triggerCatchFishEvent(event)
        if self.bossFishGroup:                                      # boss鱼群
            self.bossFishGroup.triggerCatchFishEvent(event)
        if self.taskSystemTable:
            self.taskSystemTable.dealCatchEvent(event)
        # 检查限时礼包
        if player.isFinishRedTask and player.gameTime >= 3 and player.checkLimitTimeGift:
            player.checkLimitTimeGift = False
            event = CheckLimitTimeGiftEvent(player.userId, FISH_GAMEID, player.level,
                                            player.dynamicOdds.chip, self.runConfig.fishPool, player.clientId)
            TGFish.getEventBus().publishEvent(event)
        # 触发美人鱼的馈赠小游戏
        self._miniMermaidStart(player.seatId, fishTypes)

    def _sendLed(self, player, gain, fIds, fpMultiple):
        """
        发送通讯
        :param player: 玩家
        :param gain: 获取奖励
        :param fIds: 鱼ID
        :param fpMultiple: 渔场倍率
        :return:
        """
        if self.runConfig.fishPool == 44001:
            return
        # 渔场倍率AB测试期间，B模式不开启捕获led
        if config.getPublic("fpMultipleTestMode") is None and player.isFpMultipleMode():
            return
        title = config.getMultiLangTextConf(self.runConfig.title, lang=player.lang)
        for gainMap in gain:
            if not self.fishMap.get(gainMap["fId"]):
                continue
            fishType = self.fishMap[gainMap["fId"]]["conf"]["fishType"]
            fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
            fishName = config.getMultiLangTextConf(fishConf["name"], lang=player.lang)
            if ftlog.is_debug():
                ftlog.debug("fishName--->", fishName, fishConf)
            if fishConf["type"] in [2, 19] and gainMap and gainMap["itemId"] == CHIP_KINDID and gainMap["count"] >= 1500:
                # msg = u"恭喜玩家%s在%s成功捕获%s，获得%s金币" % \
                mid = "ID_LED_CATCH_BOSS_DROP_CHIP"
               # msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
               #         player.name, self.runConfig.title, fishConf["name"],
               #         util.formatScore(gainMap["count"], lang=player.lang))
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName,
                        util.formatScore(gainMap["count"], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif fishConf["type"] == 19:
                # msg = u"恭喜玩家%s在%s成功捕获%s，获得青铜招财珠x%d（价值%s金币）" % \
                mid = "ID_LED_CATCH_FISH_DROP_BRONZE_BULLET"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName, gainMap["count"],
                        util.formatScore(gainMap["count"] * BULLET_KINDIDS[BRONZE_BULLET_KINDID], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif fishConf["type"] == 8:
                # msg = u"恭喜玩家%s在%s成功捕获%s，获得白银招财珠x%d（价值%s金币）" % \
                mid = "ID_LED_CATCH_FISH_DROP_SILVER_BULLET"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName, gainMap["count"],
                        util.formatScore(gainMap["count"] * BULLET_KINDIDS[SILVER_BULLET_KINDID], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif fishConf["type"] == 9:
                # msg = u"恭喜玩家%s在%s成功捕获%s，获得黄金招财珠x%d（价值%s金币）" % \
                mid = "ID_LED_CATCH_FISH_DROP_GOLD_BULLET"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName, gainMap["count"],
                        util.formatScore(gainMap["count"] * BULLET_KINDIDS[GOLD_BULLET_KINDID], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif fishConf["type"] in config.CHIP_CHEST_FISH_TYPE:
                # msg = u"恭喜玩家%s在%s捕获%s，开出%s金币" % \
                mid = "ID_LED_CATCH_FISH_DROP_ITEM"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName,
                        util.formatScore(gainMap["count"], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            # elif fishConf["type"] in config.MULTIPLE_FISH_TYPE and gainMap["count"] / self.runConfig.multiple >= 2000:
            elif fishConf["type"] in config.MULTIPLE_FISH_TYPE and fishConf["score"] >= 200:
                multiple = gainMap["count"] / fishConf["score"] / fpMultiple
                # msg = u"恭喜玩家%s在%s成功捕获%d倍%s，一口气赢得%s金币" % \
                if multiple >= 20:
                    mid = "ID_LED_CATCH_MULTIPLE_FISH"
                    msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                            player.name, title, multiple, fishName,
                            util.formatScore(gainMap["count"], lang=player.lang))
                    user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif gainMap["itemId"] == COUPON_KINDID and gainMap["count"] >= 500:#100:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下%.2f红包券" % \
                mid = "ID_LED_CATCH_COUPON_FISH"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"] * config.COUPON_DISPLAY_RATE,
                        gainMap["count"] * config.COUPON_DISPLAY_RATE)
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif fishConf["type"] in config.TERROR_FISH_TYPE and gainMap["count"] / fpMultiple >= 1500:
                # msg = u"恭喜%s在%s成功捕获%s，获得%s金币" % \
                mid = "ID_LED_CATCH_TERROR_FISH"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, fishName,
                        util.formatScore(gainMap["count"], lang=player.lang))
                user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
            elif gainMap["itemId"] == 4141:
                # msg = u"恭喜玩家%s在%s获得10元话费卡x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_4141"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif gainMap["itemId"] == 4142:
                # msg = u"恭喜玩家%s在%s获得30元话费卡x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_4142"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif gainMap["itemId"] == 4144:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元话费卡x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_4144"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif gainMap["itemId"] == 4233:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元京东卡x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_4233"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif gainMap["itemId"] == 2061:
                # msg = u"恭喜玩家%s在%s获得5元红包x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_2061"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)
            elif gainMap["itemId"] == 2050:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元红包x%d" % \
                mid = "ID_LED_CATCH_FISH_DROP_2050"
                msg = config.getMultiLangTextConf(mid, lang=player.lang).format(
                        player.name, title, gainMap["count"])
                user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=player.lang)

    def _doSit(self, msg, userId, seatId, clientId):
        """
        玩家操作, 尝试再当前的某个座位上坐下
        """
        ret = False
        try:
            ret = self._doSitDown(msg, userId, seatId, clientId)
            if self.hasRobot:
                if not ret and userId < config.ROBOT_MAX_USER_ID:
                    mo = MsgPack()
                    mo.setCmd("robotmgr")
                    mo.setAction("robotSitFailed")
                    mo.setParam("gameId", self.room.gameId)
                    mo.setParam("roomId", self.room.roomId)
                    mo.setParam("tableId", self.tableId)
                    mo.setParam("userId", userId)
                    router.sendRobotServer(mo)
                if userId > config.ROBOT_MAX_USER_ID and self.getRobotUserCount() == 0:
                    robotutil.sendRobotNotifyCallUp(self)
        except Exception, e:
            onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
            ftlog.warn("_doSit error", msg, userId, seatId, clientId, traceback.format_exc())
        return ret

    def _robotLeave(self, msg, userId, seatId):
        """机器人离开房间"""
        if ftlog.is_debug():
            ftlog.debug("robot leave:", userId)
        clientId = msg.getParam("clientId")
        self._doLeave(msg, userId, clientId)

    def clearPlayer(self, player):
        """玩家离开桌子 清理桌子上的玩家|玩家3分钟没有操作"""
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

    def _doLeave(self, msg, userId, clientId):
        """
        玩家操作, 尝试离开当前的桌子
        实例桌子可以覆盖 _doLeave 方法来进行自己的业务逻辑处理
        """
        if ftlog.is_debug():
            ftlog.debug("_doLeave now seats:", self.seats)
        seatId = self._getUserSeatId(userId)
        if not seatId:
            ftlog.warn("user disconnect, not find seatId", userId)
            return

        self._clearPlayer(None, userId, seatId)
        ftlog.info("user disconnect, userId:", userId, seatId)

    def _clearPlayer(self, msg, userId, seatId):
        """玩家主动离开房间、换桌、换渔场"""
        if ftlog.is_debug():
            ftlog.debug("_clearPlayer now seats:", self.seats, "seatId =", seatId, "userId =", userId, self.players, self.runConfig.fishPool)
        if self.seats[seatId - 1].userId != userId:
            ftlog.warn("clear player, user not in seat:", userId, seatId, self.runConfig.fishPool)
            return
        player = self.players[seatId - 1]
        clientId = player.clientId
        player.clearSkills()                        # 清理技能
        player.clear()
        from newfish.game import TGFish
        event = LeaveTableEvent(userId, FISH_GAMEID,
                                self.roomId, self.tableId,
                                seatId, player.enterTime)
        bireport.reportGameEvent("BI_NFISH_TABLE_LEAVE", userId, FISH_GAMEID, self.roomId, self.tableId, player.level, 0, 0, 0, [], clientId)
        self._broadcastPlayerLeave(userId, seatId)
        self.players[seatId - 1] = None
        self.seats[seatId - 1] = TYSeat(self)
        TGFish.getEventBus().publishEvent(event)
        onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
        self.room.updateTableScore(self.getTableScore(), self.tableId, force=True)
        datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["chip", "item"])
        if ftlog.is_debug():
            ftlog.debug("_clearPlayer 2 now seats:", self.seats, "seatId =", seatId, "userId =", userId, self.players, self.runConfig.fishPool)

        # if self.hasRobot:
        #     robotutil.sendRobotNotifyShutDown(self)

    def _doTableManage(self, msg, action):
        """
        桌子内部处理所有的table_manage命令
        桌子同步安全操作方法
        桌子关闭, 此方法由安全进程结束的方法调用
        """
        result = {"action": action, "isOK": True}
        if action == "leave":
            userId = msg.getParam("userId")
            ftlog.info("table manage leave:", userId)
            player = self.getPlayer(userId)
            if player:
                player.offline = 1
                player.lastActionTime = int(time.time())
        return result

    def _doShutDown(self):
        """
        桌子同步安全操作方法
        桌子关闭, 此方法由安全进程结束的方法调用
        """
        if ftlog.is_debug():
            ftlog.debug("_doShutDown->Table !!")
        self._clearTable()

    def _getUserSeatId(self, userId):
        """
        根据userId取得对应的seatId
        """
        for i in range(len(self.seats)):
            if self.seats[i].userId == userId:
                return i + 1
        return None

    def getBroadcastUids(self, filterUid=0):
        """
        获取广播的玩家Uids
        :param filterUid: 过滤的Uid
        """
        uids = []
        for i in range(len(self.seats)):
            uid = self.seats[i].userId
            if uid != 0:
                if filterUid == 0 or uid != filterUid:
                    uids.append(uid)
        return uids

    def _doSitDown(self, msg, userId, seatId, clientId):
        """玩家坐下"""
        ftlog.info("User sit_down seatId =", seatId, ", userId = ", userId, self.seats, self.runConfig.fishPool)
        if seatId != 0:
            if self.seats[seatId - 1].userId == 0:
                onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
                ftlog.warn("reconnect user is cleaned from table",
                           "seats =", self.seats, "userId =", userId)
                return False
            elif userId != self.seats[seatId - 1].userId:
                onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
                ftlog.warn("reconnect user id is not matched",
                           "seats =", self.seats, "userId =", userId)
                return False
            else:
                ftlog.info("user reconect, userId:", userId)
                onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
                self.players[seatId - 1].offline = 1                # 在线
                self.players[seatId - 1].clientId = clientId
                self.players[seatId - 1].lang = util.getLanguage(userId, clientId)
                self.players[seatId - 1].refreshGunSkin()
                self._sendTableInfo(userId, seatId)                 # 发送桌子信息
                self.players[seatId - 1].dealEnterTable()
                self.players[seatId - 1].enterTime = int(time.time())
                self.players[seatId - 1].offline = 0
                FTLoopTimer(0.1, 0, self.asyncEnterTableEvent, userId, seatId, 1).start()
                return True
        else:
            for i in range(len(self.seats)):
                if self.seats[i].userId == userId:
                    ftlog.info("lost user reconect, userId:", userId, "i =", i)
                    onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, i + 1)
                    self.players[i].offline = 1
                    self.players[i].clientId = clientId
                    self.players[i].lang = util.getLanguage(userId, clientId)
                    self.players[i].refreshGunSkin()
                    self._sendTableInfo(userId, i + 1)
                    self.players[i].dealEnterTable()
                    self.players[i].enterTime = int(time.time())
                    self.players[i].offline = 0
                    FTLoopTimer(0.1, 0, self.asyncEnterTableEvent, userId, seatId, 1).start()
                    return True
            if self.getTableScore() == 0:
                ftlog.info("table score is 0, forbid sitting")
                return False
            seatId = self._findIdleSeatId()
            if seatId == 0:
                ftlog.warn("table is full:", self.tableId)
                return False
            self.seats[seatId - 1].userId = userId
            self.players[seatId - 1] = self.createPlayer(self, seatId - 1, clientId)
            onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
            self._sendTableInfo(userId, seatId)
            self.players[seatId - 1].dealEnterTable()
            self.room.updateTableScore(self.getTableScore(), self.tableId, force=True)
            self._broadcastPlayerSit(userId, seatId)
            self.players[seatId - 1].enterTime = int(time.time())
            FTLoopTimer(0.1, 0, self.asyncEnterTableEvent, userId, seatId, 0).start()
            bireport.reportGameEvent("BI_NFISH_TABLE_ENTER", userId, FISH_GAMEID, self.roomId,
                                     self.tableId, self.players[seatId - 1].level, 0, 0, 0, [], clientId)
            if ftlog.is_debug():
                ftlog.debug("_doSitDown now seats:", self.seats, self.runConfig.fishPool, "mo =", msg)
            return True

    def _sendTableInfo(self, userId, seatId):
        """
        发送桌子信息
        """
        msg = MsgPack()
        msg.setCmd("table_info")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("roomId", self.roomId)
        msg.setResult("tableId", self.tableId)
        msg.setResult("seatId", seatId)
        msg.setResult("seatNum", self.maxSeatN)
        msg.setResult("typeName", self.typeName)
        msg.setResult("multiple", self.runConfig.multiple)
        msg.setResult("gameMode", self.gameMode)                # 游戏模式(经典/千炮)
        _player = self.getPlayer(userId)
        if _player and _player.isFpMultipleMode():              # 是否为渔场倍率模式
            multipleLevelDict = {}
            for mul, lv in config.getGunMultipleConf().iteritems():     # 获取炮的等级解锁渔场
                if self.runConfig.minMultiple <= int(mul) <= self.runConfig.maxMultiple:
                    multipleLevelDict[mul] = lv
            if multipleLevelDict:
                msg.setResult("multipleLevelDict", multipleLevelDict)
        msg.setResult("buyLimitChip", self.runConfig.minCoin)           # 最小准入金币
        msg.setResult("maxSkillLevel", self.runConfig.maxSkillLevel)    # 最大技能等级
        msg.setResult("minGunLevel", self.runConfig.minGunLevel)        # 最小火炮等级
        msg.setResult("maxGunLevel", self.runConfig.maxGunLevel)
        msg.setResult("isMatch", self.runConfig.isMatch)                # 是否为比赛
        msg.setResult("matchType", self.runConfig.matchType)
        msg.setResult("tStartTime", self.startTime)                     # 桌子开始时间
        msg.setResult("nowServerTime", time.time())                     # 服务器时间
        msg.setResult("coinShortage", self.runConfig.coinShortage)
        expressionConf = config.getExpressionConf(self.bigRoomId)
        expressions = []
        for _, expression in expressionConf.iteritems():
            expressions.append(expression)
        msg.setResult("expressions", expressions)                       # 表情
        if ftlog.is_debug():
            ftlog.debug("_sendTableInfo->msg =", msg)
        players = []
        for i in xrange(0, self.maxSeatN):
            if self.seats[i].userId != 0 and self.players[i]:
                info = self._getPlayerInfo(i + 1, _player.clientId)
                if info:
                    players.append(info)
            elif self.seats[i].userId != 0 and not self.players[i]:     # 玩家掉线了
                ftlog.error("_sendTableInfo error", self.seats[i].userId, self.tableId)
                self.seats[i] = TYSeat(self)
        msg.setResult("players", players)
        groups = []
        for i in xrange(0, len(self.normalFishGroups)):                 # 普通鱼群
            group = self.normalFishGroups[i]
            if group.isAlive(self._getNowTableTime()):
                groups.append(self._getGroupInfo(group))
        for i in xrange(0, len(self.callFishGroups)):                   # 召唤出来的鱼群对象
            group = self.callFishGroups[i]
            if group.isAlive(self._getNowTableTime(), self) and group.isVisible(self, userId):
                groups.append(self._getGroupInfo(group))

        msg.setResult("groups", groups)
        # 根据clientId判断是否屏蔽兑换提示.
        isIgnored = config.isClientIgnoredConf("exchangeTip", 1, _player.clientId or util.getClientId(userId))
        msg.setResult("ignoreExchageTip", 1 if isIgnored else 0)
        GameMsg.sendMsg(msg, userId)
        if _player and hasattr(_player, "prizeWheel") and _player.prizeWheel:
            _player.prizeWheel.sendEnergyProgress(self.runConfig.fishPool, _player.fpMultiple, self.roomId, 0)
        if _player and _player.compAct:                                 # 竞赛活动
            _player.compAct.sendInspireInfo()
        if _player and hasattr(_player, "lotteryTicket") and _player.lotteryTicket:
            _player.lotteryTicket.sendProgress(1, isSend=1)             # 红包券
        # 发送断线后的小游戏进度信息
        mini_game.sendMiniGameProgress(self, userId, self.roomId, seatId)

    def _getGroupInfo(self, group):
        """
        获取鱼群信息
        :param group: 鱼群ID
        """
        info = {}
        info["grpId"] = group.id
        info["enT"] = round(group.enterTime, 2)
        info["fishesStartId"] = group.startFishId
        info["position"] = group.position               # 鱼群出现的位置
        info["gameResolution"] = group.gameResolution
        diedFish = []
        HPFish = {}
        bufferFish = {}
        multipleFish = {}
        for fId in xrange(group.startFishId, group.startFishId + group.fishCount):
            if not self.fishMap[fId]["alive"]:
                diedFish.append(fId)
            else:
                fishType = self.fishMap[fId]["conf"]["fishType"]
                fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                if fishConf["HP"] > 0:
                    HPFish[fId] = self.fishMap[fId]["HP"]               # 有充值奖池的时候 HP为0的时候, 高概率打死
                if self.fishMap[fId]["buffer"]:
                    bufferFish[fId] = self.fishMap[fId]["buffer"]       # 给鱼添加buffer 冰冻|无敌
                if self.fishMap[fId]["multiple"] > 1:
                    multipleFish[fId] = self.fishMap[fId]["multiple"]
        if diedFish:
            info["died"] = diedFish
        if HPFish:
            info["HP"] = HPFish
        if bufferFish:
            info["buffer"] = bufferFish
        if multipleFish:
            info["multiple"] = multipleFish
        return info

    def _getPlayerInfo(self, seatId, msgOwnerClientId=None):
        """
        获取玩家信息
        :param seatId: 座位ID
        :param msgOwnerClientId: 客户端ID
        :return:
        """
        if ftlog.is_debug():
            ftlog.debug("_getPlayerInfo->seatId =", seatId, "userId =", self.seats[seatId - 1].userId, msgOwnerClientId)
        info = {}
        p = self.players[seatId - 1]
        if not p:
            ftlog.error("_getPlayerInfo error", self.seats[seatId - 1].userId, self.tableId, msgOwnerClientId)
            self.seats[seatId - 1] = TYSeat(self)           # 清空玩家信息
            return info
        info["userId"] = p.userId
        info["seatId"] = seatId
        info["name"] = p.name
        info["offline"] = p.offline                         # 在线1|离线
        info["uLv"] = p.level
        userLevelConf = config.getUserLevelConf()
        lvUpExp = userLevelConf[p.level - 1]["exp"] if p.level <= len(userLevelConf) else userLevelConf[-1]["exp"]  # 用户下一等级需要的经验
        info["expPct"] = min(100, max(0, int(p.exp * 100. / lvUpExp)))
        info["gLv"] = p.gunLevel
        info["gLvNow"] = p.nowGunLevel
        info["gunLevel"] = p.gunLv
        info["exp"] = p.exp
        info["skillSlots"] = p.getSkillSlotsInfo(0)         # 主技能槽的数据
        info["auxiliarySkillSlots"] = p.getSkillSlotsInfo(1)
        info["usingSkill"] = p.getUsingSkillInfo()          # 获取使用中的技能数据
        info["tableChip"] = p.tableChip
        info["clip"] = p.clip
        info["honors"] = honor_system.getHonorList(p.userId)    # 获取称号信息列表
        info["gunId"] = p.gunId                             # 火炮ID
        skins = config.getGunConf(p.gunId, msgOwnerClientId, mode=self.gameMode).get("skins")
        info["gunSkinId"] = p.skinId if p.skinId in skins else skins[0]     # 火炮皮肤
        info["charm"] = p.charm                             # 魅力
        info["sex"] = p.sex
        info["vipLv"] = util.getVipShowLevel(p.userId)      # vip等级
        info["purl"] = p.purl
        info["redState"] = p.redState                       # 新手任务状态
        info["fpMultiple"] = p.fpMultiple
        info["gameResolution"] = p.gameResolution
        info["playMode"] = p.multipleMode                   # 0金币模式 1金环
        return info

    def _broadcastPlayerSit(self, userId, seatId):
        """广播玩家坐下"""
        msg = MsgPack()
        msg.setCmd("sit")
        msg.setResult("gameId", FISH_GAMEID)
        # msg.setResult("info", self._getPlayerInfo(seatId))
        # GameMsg.sendMsg(msg, self.getBroadcastUids(userId))
        uids = self.getBroadcastUids(userId)
        clientUids = {}
        for _uid in uids:
            clientUids.setdefault(util.getClientId(_uid), []).append(_uid)
        for _cli, _uids in clientUids.iteritems():
            msg.setResult("info", self._getPlayerInfo(seatId, _cli))
            GameMsg.sendMsg(msg, _uids)

    def _broadcastPlayerLeave(self, userId, seatId):
        """广播玩家离开"""
        msg = MsgPack()
        msg.setCmd("leave")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("seatId", seatId)
        GameMsg.sendMsg(msg, self.getBroadcastUids())

    def _findIdleSeatId(self):
        """查询空座"""
        idleSids = []
        for i in range(len(self.seats)):
            if self.seats[i].userId == 0:
                idleSids.append(i + 1)
        if len(idleSids) == 0:
            return 0
        else:
            return random.choice(idleSids)

    def _skill_use(self, msg, userId, seatId):
        """使用技能 1使用 0取消"""
        skillId = msg.getParam("skillId")
        select = msg.getParam("select")
        skillType = msg.getParam("skillType", 0)
        player = self.players[seatId - 1]
        if ftlog.is_debug():
            ftlog.debug("_skill_use", userId, skillId, select, skillType)
        player.useSkill(skillId, select, skillType)

    def _skill_install(self, msg, userId, seatId):
        """装备1、卸下0、替换"""
        skillId = msg.getParam("skillId")
        install = msg.getParam("install")
        ignoreFailMsg = msg.getParam("ignoreFailMsg", False)
        skillType = msg.getParam("skillType", 0)
        player = self.players[seatId - 1]
        ftlog.info("_skill_install", userId, skillId, install, player.skills, player.auxiliarySkills)
        player.installSkill(skillId, install, ignoreFailMsg, skillType)

    def _skill_replace(self, msg, userId, seatId):
        """技能替换 uninstallSkillId 要卸下的技能ID"""
        installSkillId = msg.getParam("installSkillId")
        uninstallSkillId = msg.getParam("uninstallSkillId")
        skillType = msg.getParam("skillType", 0)
        player = self.players[seatId - 1]
        if ftlog.is_debug():
            ftlog.debug("_skill_replace", userId, installSkillId, uninstallSkillId, skillType)
        player.replaceSkill(installSkillId, uninstallSkillId, skillType)

    def broadcastSkillUse(self, skill, select, userId, orgState):
        """
        广播选中/取消技能消息
        """
        msg = MsgPack()
        msg.setCmd("skill_use")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", skill.player.userId)
        msg.setResult("seatId", skill.player.seatId)
        msg.setResult("skillId", int(skill.skillId))
        msg.setResult("skillType", skill.skillType)
        msg.setResult("select", select)
        msg.setResult("clip", skill.player.clip)
        msg.setResult("skillClip", skill.clip)
        GameMsg.sendMsg(msg, self.getBroadcastUids())

    def broadcastSkillEnd(self, skill):
        """
        广播技能结束消息
        """
        msg = MsgPack()
        msg.setCmd("skill_end")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", skill.player.userId)
        msg.setResult("seatId", skill.player.seatId)
        msg.setResult("skillId", int(skill.skillId))
        msg.setResult("skillType", skill.skillType)
        msg.setResult("clip", skill.player.clip)
        GameMsg.sendMsg(msg, self.getBroadcastUids())

    def broadcastSkillEffect(self, player, endTime, fishes, skillId):
        """
        广播技能效果(冰冻、欺诈、捕鱼机器人非正常死亡)消息
        """
        if not isinstance(fishes, list):
            fishes = [fishes]
        msg = MsgPack()
        msg.setCmd("skill_effect")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", player.userId)
        msg.setResult("seatId", player.seatId)
        msg.setResult("skillId", skillId)
        msg.setResult("nowServerTime", time.time())
        msg.setResult("endTime", endTime)
        msg.setResult("fishes", fishes)
        GameMsg.sendMsg(msg, self.getBroadcastUids())

    def _doTableChat(self, msg, userId, seatId):
        """
        渔场自定义聊天
        :param chatMsg: 0：自定义纯文本 1：表情 4：系统默认文本
        """
        uids = self.getBroadcastUids()
        player = self.getPlayer(userId)
        isFace = msg.getParam("isFace", 0)
        chatMsg = msg.getParam("chatMsg", "")
        chatMsg = chatMsg[:80]  # 80个字符长度限制
        needProcessChat = False
        if isFace == 0: # 纯文本内容
            util.chatReport(userId, int(time.time()), 1, chatMsg, 0, 0)
            needProcessChat = True
        elif isFace == 4 and chatMsg not in ("string_liaotian1",
                                             "string_liaotian2",
                                             "string_liaotian3",
                                             "string_liaotian4",
                                             "string_liaotian5",
                                             "string_liaotian6"):
            needProcessChat = True
        if needProcessChat:
            punishState = user_system.getChatPunish(userId)
            if player is None:
                uids = [userId]
            elif punishState == 2:
                # chatMsg = u"您已被禁言，详情请联系客服"
                chatMsg = config.getMultiLangTextConf("ID_BANNED_CONTACT_SERVICE", lang=player.lang)
                uids = [userId]
            elif len(chatMsg) and util.isTextCensorLimit(chatMsg):
                # 您的发言含有敏感内容，无法发送！
                chatMsg = config.getMultiLangTextConf("ID_SPEECH_SENSITIVE", lang=player.lang)
                uids = [userId]
            elif config.getVipConf(player.vipLevel).get("enableChat", 0) == 0:
                # 发言需要达到VIP3!
                tip = config.getMultiLangTextConf(config.getVipConf(player.vipLevel).get("limitChatTip", ""), lang=player.lang)
                if len(tip) > 0:
                    chatMsg = tip
                uids = [userId]

        if isFace == 0:
            _uids = [userId]
            chatLimitConf = config.getPublic("chatLimit", {})
            for _uid in uids:
                if _uid != userId:
                    _player = self.getPlayer(_uid)
                    if _player.vipLevel >= chatLimitConf.get("vipLimit", 0) or _player.clientId in chatLimitConf.get("clientLimit", []):
                        _uids.append(_uid)
            uids = _uids
        mo = MsgPack()
        mo.setCmd("table_chat")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("seatId", seatId)
        mo.setResult("isFace", isFace)
        mo.setResult("chatMsg", chatMsg)
        GameMsg.sendMsg(mo, uids)

    def doTableSmilies(self, msg, userId, seatId):
        """
        渔场互动表情（使用渔场外金币）
        """
        code = 0
        player, toPlayer, self_charm, other_charm = None, None, None, None
        playerChip = 0
        smileId = msg.getParam("smileId", 0)
        toSeatId = msg.getParam("toSeatId", 0)
        conf = config.getExpressionConf(self.bigRoomId)
        smileConf = conf.get(str(smileId), {})
        if not smileConf:
            code = 1
        else:
            toPlayer = self.players[toSeatId - 1]
            if not toPlayer:
                code = 2
            else:
                player = self.players[seatId - 1]
                price, self_charm, other_charm = smileConf["price"], \
                                                 smileConf["self_charm"], \
                                                 smileConf["other_charm"]

                trueDelta, playerChip = userchip.incrChip(userId, FISH_GAMEID, -abs(int(price)), 0,
                                                          "EMOTICON_CONSUME", self.roomId, player.clientId,
                                                          roomId=self.roomId, tableId=self.tableId)
                if trueDelta != 0:
                    player.hallCoin = playerChip
                    player.charm = userdata.incrCharm(userId, self_charm)
                    if len(str(player.charm)) >= 11:
                        player.charm = userdata.incrCharm(userId, -abs(player.charm) + self_charm)
                    toPlayer.charm = userdata.incrCharm(toPlayer.userId, other_charm)
                    if len(str(toPlayer.charm)) >= 11:
                        toPlayer.charm = userdata.incrCharm(toPlayer.userId, -abs(toPlayer.charm) + other_charm)
                else:
                    code = 3

        mo = MsgPack()
        mo.setCmd("table_smile")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("smileId", smileId)
        mo.setResult("seatId", seatId)
        mo.setResult("toSeatId", toSeatId)
        mo.setResult("code", code)
        if code == 0:
            mo.setResult("fromCharm", player.charm)
            mo.setResult("toCharm", toPlayer.charm)
            mo.setResult("fromAdd", self_charm)
            mo.setResult("toAdd", other_charm)
            mo.setResult("chip", playerChip)
            GameMsg.sendMsg(mo, self.getBroadcastUids())
            from newfish.game import TGFish
            from newfish.entity.event import UseSmiliesEvent
            event = UseSmiliesEvent(userId, FISH_GAMEID, self.roomId, self.tableId, smileId)
            TGFish.getEventBus().publishEvent(event)
        else:
            GameMsg.sendMsg(mo, userId)

    def doTableSmilies2(self, msg, userId, seatId):
        """
        渔场互动表情（使用渔场内金币）
        """
        code = 0
        player, toPlayer, self_charm, other_charm = None, None, None, None
        smileId = msg.getParam("smileId", 0)
        toSeatId = msg.getParam("toSeatId", 0)
        conf = config.getExpressionConf(self.bigRoomId)
        smileConf = conf.get(str(smileId), {})
        if not smileConf:
            code = 1
        else:
            toPlayer = self.players[toSeatId - 1]
            if not toPlayer:
                code = 2
            else:
                player = self.players[seatId - 1]
                price, self_charm, other_charm = smileConf["price"], \
                                                 smileConf["self_charm"], \
                                                 smileConf["other_charm"]
                # bulletPrice = price // player.fpMultiple # self.runConfig.multiple
                # if player.clip < bulletPrice:
                #     self.clip_add(player.userId, player.seatId, 0, 1)
                # if player.clip >= bulletPrice:
                #     player.costClip(bulletPrice, "EMOTICON_CONSUME")
                #     player.charm = userdata.incrCharm(userId, self_charm)
                #     if len(str(player.charm)) >= 11:
                #         player.charm = userdata.incrCharm(userId, -abs(player.charm) + self_charm)
                #     toPlayer.charm = userdata.incrCharm(toPlayer.userId, other_charm)
                #     if len(str(toPlayer.charm)) >= 11:
                #         toPlayer.charm = userdata.incrCharm(toPlayer.userId, -abs(toPlayer.charm) + other_charm)
                # else:
                #     code = 3
                if player.clip * player.fpMultiple + player.tableChip >= price:
                    player.clipToTableChip()
                    lastCoin = player.holdCoin
                    player.economicData.consumeItem("tableChip", price, "EMOTICON_CONSUME", self.roomId, 1)
                    self.clip_add(player.userId, player.seatId, auto=1)
                    if self.typeName in config.NORMAL_ROOM_TYPE:
                        if player.taskSystemTable and player.taskSystemTable.openBonusPool:
                            self.room.lotteryPool.countBonusConsumeCoin(self.tableId, price)
                        if player.taskSystemTable and player.taskSystemTable.openCmpttPool:
                            self.room.lotteryPool.countCmpttConsumeCoin(self.tableId, price)
                    if lastCoin > self.runConfig.coinShortage > player.holdCoin:
                        coinShortageCount = gamedata.getGameAttrJson(player.userId, FISH_GAMEID,
                                                                     GameData.coinShortageCount, {})
                        coinShortageCount.setdefault(str(self.runConfig.fishPool), 0)
                        coinShortageCount[str(self.runConfig.fishPool)] += 1
                        gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.coinShortageCount,
                                             json.dumps(coinShortageCount))
                        if ftlog.is_debug():
                            ftlog.debug("doTableSmilies2", player.userId, lastCoin, self.runConfig.coinShortage, player.holdCoin,
                                    coinShortageCount)

                    player.charm = userdata.incrCharm(userId, self_charm)
                    if len(str(player.charm)) >= 11:
                        player.charm = userdata.incrCharm(userId, -abs(player.charm) + self_charm)
                    toPlayer.charm = userdata.incrCharm(toPlayer.userId, other_charm)
                    if len(str(toPlayer.charm)) >= 11:
                        toPlayer.charm = userdata.incrCharm(toPlayer.userId, -abs(toPlayer.charm) + other_charm)
                else:
                    code = 3

        mo = MsgPack()
        mo.setCmd("table_smile")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("smileId", smileId)
        mo.setResult("seatId", seatId)
        mo.setResult("toSeatId", toSeatId)
        mo.setResult("code", code)
        if code == 0:
            mo.setResult("fromCharm", player.charm)
            mo.setResult("toCharm", toPlayer.charm)
            mo.setResult("fromAdd", self_charm)
            mo.setResult("toAdd", other_charm)
            mo.setResult("clip", player.clip)
            GameMsg.sendMsg(mo, self.getBroadcastUids())
            from newfish.game import TGFish
            from newfish.entity.event import UseSmiliesEvent
            event = UseSmiliesEvent(userId, FISH_GAMEID, self.roomId, self.tableId, smileId)
            TGFish.getEventBus().publishEvent(event)
        else:
            GameMsg.sendMsg(mo, userId)

    def _bullet_use(self, msg, userId, seatId):
        """
        渔场中使用招财珠
        """
        bullet = msg.getParam("bullet")
        player = self.players[seatId - 1]
        if ftlog.is_debug():
            ftlog.debug("_bullet_use", userId, bullet)
        player.useBullet(bullet)

    def dealGunEffect(self, player, fIds):
        """
        处理火炮皮肤特性
        """
        if player.gunId == 1165:        # 霜冻特性，有几率冰冻鱼
            addTimeGroup = []
            frozenFishes = []
            duration = 3                # 冰冻时间
            if player.skinId == 1472:   # 雪人皮肤特性，冰冻时间加1s
                duration += 1
            endTime = time.time() + duration
            buffer = [5104, endTime, player.userId, 1, 1, duration, 0]
            for fId in fIds:
                count = 0
                buffers = self.fishMap[fId]["buffer"]
                isCoverFrozen = True
                frozenTime = duration
                lastFrozenTime = 0
                for lastBuffer in buffers:
                    if lastBuffer[0] == 5104:
                        count = lastBuffer[6]
                        lastFrozenTime = lastBuffer[5]
                        if endTime > lastBuffer[1]:  # 新冰冻到期时间大于旧冰冻到期时间，覆盖时间
                            # 如果上一个冰冻状态未到期且小于新冰冻到期时间，则鱼在冰冻状态下再次冰冻，实际冰冻时间为间隔时间
                            if time.time() < lastBuffer[1] < endTime:
                                frozenTime = round(endTime - lastBuffer[1], 3)
                        else:
                            isCoverFrozen = False
                if isCoverFrozen:
                    if count == 0:  # 第一次冰冻5%概率
                        isCoverFrozen = True if random.randint(1, 10000) <= 500 else False
                    elif count == 1:
                        isCoverFrozen = True if random.randint(1, 10000) <= 300 else False
                    elif count == 2:
                        isCoverFrozen = True if random.randint(1, 10000) <= 100 else False
                    else:
                        isCoverFrozen = False

                if isCoverFrozen:
                    if ftlog.is_debug():
                        ftlog.debug("dealGunEffect->frozenTime =", fId, frozenTime)
                    buffer[5] = round(lastFrozenTime + frozenTime, 3)
                    self.setFishBuffer(fId, buffer)
                    frozenFishes.append(fId)
                    buffers = self.fishMap[fId]["buffer"]
                    if ftlog.is_debug():
                        ftlog.debug("dealGunEffect->isCoverFrozen->buffer =", fId, buffers)
                    group = self.fishMap[fId]["group"]
                    if group.startFishId not in addTimeGroup:
                        addTimeGroup.append(group.startFishId)
                        group.adjust(frozenTime)
                        self.superBossFishGroup and self.superBossFishGroup.frozen(fId, self.fishMap[fId]["conf"]["fishType"], frozenTime)

            if frozenFishes:  # 广播新处于冰冻状态的鱼
                self.broadcastSkillEffect(player, endTime, frozenFishes, 5104)

    def _achievement_task(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        honorId = msg.getParam("honorId")
        if player and player.achieveSystem:
            player.achieveSystem.updateStateAndSave()
            from newfish.entity.achievement import achievement_system
            achievement_system.doGetAllAchievementTasks(userId, honorId)

    def _achievement_reward(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        taskId = msg.getParam("taskId")
        if player and player.achieveSystem:
            player.achieveSystem.updateStateAndSave()
            from newfish.entity.achievement import achievement_system
            achievement_system.doReceiveTaskReward(userId, taskId)
            player.achieveSystem.refreshAchievementTask()

    def _honor_push(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        player and player.refreshHonor()

    def _honor_replace(self, msg, userId, seatId):
        honorId = msg.getParam("honorId")
        from newfish.entity.honor import honor_system
        reason = honor_system.replaceHonor(userId, honorId, self.getBroadcastUids())
        if reason == 0:
            player = self.getPlayer(userId)
            if player:
                player.honorId = honorId

    def _guns_list(self, msg, userId, seatId):
        """
        发送火炮列表消息
        :param msg: 信息
        :param userId: 玩家Id
        :param seatId: 座位Id
        """
        player = self.getPlayer(userId)
        if player:
            player.dumpGunData()
            gun_system.sendGunListMsg(userId, self.gameMode)

    def _guns_pool(self, msg, userId, seatId):
        """
        炮的奖池信息
        """
        player = self.getPlayer(userId)
        if player:
            gunId = msg.getParam("gunId")
            coin = msg.getParam("coin")
            player.gunPool.setdefault(str(gunId), 0)
            player.gunPool[str(gunId)] += coin
            player.dumpGunData()

    def _gun_up(self, msg, userId, seatId):
        """
        普通炮升级
        """
        protect = msg.getParam("protect")
        player = self.getPlayer(userId)
        player and player.gunUpgrade(protect)

    def _getTableTask(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if player and player.taskSystemUser:
            player.taskSystemUser.getCurTaskInfo()

    def _changeTableTask(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if player and player.taskSystemUser:
            player.taskSystemUser.changeTask(msg)

    def _getRedTaskList(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if player and player.taskSystemUser:
            player.taskSystemUser.getRedTaskList()

    def _recharge_notify(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        player and player.dynamicOdds.refreshRechargeOdds()
        self._refreshUserData(msg, userId, seatId)

    def _takeGiftReward(self, msg, userId, seatId):
        """
        领取礼包奖励
        """
        productId = msg.getParam("productId", "")
        # 转运礼包购买后一定概率转运,当玩家购买任意转运礼包后，如果玩家当前房间所在曲线为6~10，则强制重置当前房间曲线，随机范围1~10
        if productId not in config.getPublic("luckyGiftProductIds", []):
            return
        player = self.getPlayer(userId)
        if player is None or not hasattr(player, "dynamicOdds"):
            return
        waveId = 0
        waveList = [wave["waveId"] for wave in player.dynamicOdds.getWaveList("low")]
        if player.dynamicOdds.waveId in waveList:
            waveId = player.dynamicOdds.getWaveId()
            if waveId:
                player.dynamicOdds.resetOdds(waveId)
        if ftlog.is_debug():
            ftlog.debug("_takeGiftReward", userId, self.bigRoomId, waveList, waveId)

    def _skill_upgrade(self, msg, userId, seatId):
        """技能升级0、升星1"""
        player = self.getPlayer(userId)
        skillId = msg.getParam("skillId")
        actionType = msg.getParam("actionType")
        skillType = msg.getParam("skillType", 0)
        player and player.upgradeSkill(skillId, actionType, skillType)

    def _refresh_skill_cd(self, msg, userId, seatId):
        """刷新cd时间"""
        # 比赛中不可用冷却
        if not self.taskSystemTable or self.taskSystemTable.getTaskState(userId) == 0:
            player = self.getPlayer(userId)
            player and player.refreshSkillCD and player.refreshSkillCD()
        else:
            mo = MsgPack()
            mo.setCmd("refresh_skill_cd")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("code", 3)
            router.sendToUser(mo, userId)

    def _achievement_target(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        # player and player.achieveSystem and player.achieveSystem.sendAchievementTarget()

    def checkGrandPrize(self, fishScore, player, fId, fpMultiple):
        """
        只有普通鱼可以获得巨奖
        :param fishScore: 鱼的分值
        :param player: 玩家
        :param fId: 鱼ID
        :param fpMultiple: 渔场倍率
        :return:
        """
        if ftlog.is_debug():
            ftlog.debug("send grandPrizePool, userId =", player.userId, "fishScore =", fishScore, "fId =", fId)
        if not GrandPrizePool.isRoomEnable(self.roomId):
            return
        bigRoomIdList = config.getGrandPrizeConf().get("roomIds", [])
        if fishScore >= GrandPrizePool.getFishScoreLimit():
            fireCostList = [v for k, v in player.fireCost.iteritems() if int(k) in bigRoomIdList]
            fireCost = sum(fireCostList)
            from newfish.servers.center.rpc import center_remote
            center_remote.checkGrandPrizeReward(player.userId, self.roomId, self.tableId, fId, fireCost, player.seatId, fpMultiple)
            # msg = MsgPack()
            # msg.setCmd("grandPrizePool")
            # msg.setParam("gameId", FISH_GAMEID)
            # msg.setParam("action", "ct_server_catch_fish")
            # msg.setParam("userId", player.userId)
            # msg.setParam("fishId", fId)
            # msg.setParam("fireCost", fireCost)
            # msg.setParam("tableId", self.tableId)
            # msg.setParam("roomId", self.roomId)
            # wrapper.send("CT9999000001", msg, "S2", str(player.userId))
            # router.sendCenterServer(msg, "newfish.table.table_base")
            if ftlog.is_debug():
                ftlog.debug("send grandPrizePool", "fireCost =", player.fireCost, "fireCostList =", fireCostList, "costVal =", fireCost)

    def _getTreasureRewards(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        player and treasure_system.getTreasureRewards(userId, player.allChip)

    def _taskUpdate(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if player:
            player.mainQuestSystem.refreshTaskState()
            quest_system.getQuestInfo(userId, player.clientId)

    def _getMainQuestRewards(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if player and player.mainQuestSystem:
            player.mainQuestSystem.getQuestRewardsInTable(msg.getParam("taskId"))

    def _prizeWheelInfo(self, msg, userId, seatId):
        """
        获取轮盘数据/转动轮盘
        """
        action = msg.getParam("act")
        player = self.getPlayer(userId)
        if player and hasattr(player, "prizeWheel") and player.prizeWheel:
            player.prizeWheel.getInfo(player.fpMultiple, action)

    def _prizeWheelBet(self, msg, userId, seatId):
        """
        确定轮盘最终奖励
        """
        betType = msg.getParam("betType")
        bet = msg.getParam("bet")
        player = self.getPlayer(userId)
        if player and hasattr(player, "prizeWheel") and player.prizeWheel:
            player.prizeWheel.setRewards(player.fpMultiple, bet, betType)

    def checkActivity(self):
        pass

    def _activity_all_btns(self, msg, userId, seatId):
        pass

    def _activity_read(self, msg, userId, seatId):
        pass

    def _activity_reward(self, msg, userId, seatId):
        pass

    def _activity_bonus(self, msg, userId, seatId):
        pass

    def addPrizeWheelEnergy(self, player, fId, fishConf, fpMultiple, gunMultiple):
        """
        增加渔场轮盘能量
        """
        if player and hasattr(player, "prizeWheel") and player.prizeWheel:
            player.prizeWheel.catchFish(fId, fishConf, fpMultiple, gunMultiple)

    def _chgMultiple(self, msg, userId, seatId):
        """
        修改玩家渔场倍率
        """
        fpMultiple = msg.getParam("fpMultiple")
        player = self.getPlayer(userId)
        if player:
            player.changeFpMultiple(fpMultiple)

    def _startGrandPrix(self, msg, userId, seatId):
        pass

    def _endGrandPrix(self, msg, userId, seatId):
        pass

    def _inspireNotify(self, msg, userId, seatId):
        """
        请求鼓舞礼包数据
        """
        player = self.getPlayer(userId)
        if player and player.compAct:
            player.compAct.sendInspireInfo()

    def hasSuperBossFishGroup(self):
        """
        是否存在超级boss
        """
        return self.superBossFishGroup and self.superBossFishGroup.isAppear()

    def checkBigPrize(self, player, score, chip, fpMultiple, isBoss=False, isGrandPriz=False):
        """
        判断是否为幸运降临
        """
        if self.runConfig.typeName not in config.NORMAL_ROOM_TYPE:
            return
        conf = config.getBigPrizeConf()
        bigPrizeScore = conf.get(str(self.bigRoomId))
        if bigPrizeScore is None:
            return
        isTriggerBigPrize = isBoss or isGrandPriz or score >= bigPrizeScore
        if ftlog.is_debug():
            ftlog.debug("checkBigPrize, userId =", player.userId, "score =", score, "chip =", chip,
                    "fpMultiple =", fpMultiple, "isBoss =", isBoss, "isGrandPriz =", isGrandPriz,
                    "isTriggerBigPrize =", isTriggerBigPrize, "bigRoomId =", self.bigRoomId, "bigPrizeScore =", bigPrizeScore)
        # 幸运奖励
        if isTriggerBigPrize:
            if player.compAct:
                point = config.getCompActConf().get("points", {}).get(str(player.fpMultiple), 0)
                # if point == 0:
                #     ftlog.error("addPoint, userId =", player.userId, player.fpMultiple, config.getCompActConf().get("points"))
                # else:
                if point:
                    player.compAct.addPoint(point)
            player.activitySystem and player.activitySystem.addBigPrizeTimes(chip)

    def refreshFishTypeCount(self, val):
        """
        刷新鱼的ID: 数量值
        :param val: 鱼的详细信息
        """
        ft = val.get("fishType")
        group = val.get("group")
        if ft in self.ftCount:
            self.ftCount[ft] -= 1
            if self.ftCount[ft] < 0:
                self.ftCount[ft] = 0
                ftlog.info("refreshFishTypeCount, count error ! group =", group.desc(), "tableId =", self.tableId, "ft =", ft)
        else:
            ftlog.info("refreshFishTypeCount, type error ! group =", group.desc(), "tableId =", self.tableId, "ft =", ft)

    def _lotteryTicketInfo(self, msg, userId, seatId):
        """
        获取红包券抽奖数据/抽奖
        """
        act = msg.getParam("act")
        action = msg.getParam("action")
        player = self.getPlayer(userId)
        if player and hasattr(player, "lotteryTicket") and player.lotteryTicket:
            player.lotteryTicket.getLotteryTickInfo(action, act)

    def _lotteryTicketProgress(self, msg, userId, seatId):
        """
        获取红包券抽奖积攒进度
        """
        action = msg.getParam("action")
        player = self.getPlayer(userId)
        if player and hasattr(player, "lotteryTicket") and player.lotteryTicket:
            player.lotteryTicket.sendProgress( 0, action, 1)

    def _lotteryTicketExchange(self, msg, userId, seatId):
        """
        获取红包券抽奖兑奖界面信息
        """
        action = msg.getParam("action")
        player = self.getPlayer(userId)
        if player and hasattr(player, "lotteryTicket") and player.lotteryTicket:
            player.lotteryTicket.getExchangeInfo(action)

    def _takeNewbie7DaysGift(self, msg, userId, seatId):
        """
        领取新手7日礼包奖励
        """
        from newfish.entity import newbie_7days_gift
        player = self.getPlayer(userId)
        fireCount = player.fireCount if player and hasattr(player, "fireCount") else {}
        level = player.level if player and hasattr(player, "level") else 1
        clientId = msg.getParam("clientId")
        idx = msg.getParam("idx")
        newbie_7days_gift.takeGiftRewards(userId, clientId, idx, fireCount, level)

    def _miniGameStart(self, msg, userId, seatId):
        """
        开始小游戏宝箱
        """
        miniGameLevel = 2
        player = self.players[seatId - 1]
        ret = mini_game.miniGameStart(self, player, miniGameLevel)
        msg = MsgPack()
        msg.setCmd('mini_game_start')
        msg.setResult('gameId', FISH_GAMEID)
        msg.setResult('seatId', seatId)
        for key, value in ret.items():
            msg.setResult(key, value)
        GameMsg.sendMsg(msg, self.getBroadcastUids())

    def _miniMermaidStart(self, seatId, fishTypes):
        """
        开始小游戏美人鱼的馈赠, 8101是美人鱼小游戏id
        """
        bigRoomId, _ = util.getBigRoomId(self.roomId)
        miniGameConf = config.getMiniGameConf(8101)
        if bigRoomId != miniGameConf.get("roomId"):
            return
        miniGameLevel = 1
        player = self.players[seatId - 1]
        isTrigger = False
        if player:
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                if fishConf["type"] in config.BOSS_FISH_TYPE:
                    isTrigger = True
                    break
            if isTrigger and mini_game.addCard(self.roomId, player):
                ret = mini_game.miniGameStart(self, player, miniGameLevel)
                msg = MsgPack()
                msg.setCmd('mini_game_start')
                msg.setResult('gameId', FISH_GAMEID)
                msg.setResult('seatId', seatId)
                for key, value in ret.items():
                    msg.setResult(key, value)
                GameMsg.sendMsg(msg, self.getBroadcastUids())

    def _miniGameAction(self, msg, userId, seatId):
        """
        小游戏抽奖, actType=1表示翻硬币/选择箱子， actType=2表示宝箱抽奖
        """
        mini_game.doAction(msg, self, self.players[seatId - 1])

    def asyncEnterTableEvent(self, userId, seatId, reconnect):
        """
        异步发送进入房间事件
        """
        from newfish.game import TGFish
        event = EnterTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId, reconnect=reconnect)
        TGFish.getEventBus().publishEvent(event)