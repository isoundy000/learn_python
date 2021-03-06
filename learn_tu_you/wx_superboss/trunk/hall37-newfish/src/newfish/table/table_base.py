# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import random
import time
import json
import traceback
from copy import deepcopy
from collections import OrderedDict

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import onlinedata, userdata, userchip
from poker.entity.game.tables.table import TYTable
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity import datachangenotify
from newfish.entity import config, util, treasure_system, user_system
from newfish.entity.config import FISH_GAMEID, CHIP_KINDID, COUPON_KINDID
from newfish.entity.event import CatchEvent, EnterTableEvent, LeaveTableEvent, CheckLimitTimeGiftEvent
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.normal_fish_group import NormalFishGroup
from newfish.entity.msg import GameMsg
from newfish.entity.skill import skill_release
from newfish.entity.gun import gun_system
from newfish.servers.util.rpc import user_rpc
from newfish.player.player_base import FishPlayer
from newfish.table.table_conf import FishTableConf
from newfish.robot import robotutil
from newfish.entity.honor import honor_system
from newfish.entity.lotterypool.grand_prize_pool import GrandPrizePool
from newfish.entity.task.task_system_table import TaskSystemTable
from newfish.entity.quest import quest_system
from newfish.entity.redis_keys import GameData
from newfish.entity.task.tide_task import TideTask


class FishTable(TYTable):
    """捕鱼桌子基类"""
    def __init__(self, room, tableId):
        super(FishTable, self).__init__(room, tableId)
        self.clear()                                                        # 清理桌子
        # 状态检查间隔时间
        self._checkStateSeconds = 60
        # 用户离线等待时间
        self._offlineWaitSeconds = 60
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 180
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 180
        # 渔场内任务系统
        self.taskSystemTable = None
        # 鱼阵相关
        self.initFishGroupData()
        self.startFishGroup()
        # 循环检查牌桌内用户状态
        FTLoopTimer(self._checkStateSeconds, -1, self.checkState).start()
        # 循环检查渔场内用户活动开启状态
        FTLoopTimer(31, -1, self.checkActivity).start()

        self.actionMap = {
            "leave": self._clearPlayer,                                 # 玩家
            "robot_leave": self._robotLeave,                            # 机器人离开房间
            "catch": self._verifyCatch,                                 # 验证该次捕获是否有效
            "skill_use": self._skill_use,                               # 使用技能 1使用 0取消
            "skill_install": self._skill_install,                       # 技能装备1、卸下0
            "skill_replace": self._skill_replace,                       # 技能替换 uninstallSkillId 要卸下的技能ID
            "skill_upgrade": self._skill_upgrade,                       # 技能升级0、升星1
            "chat": self._doTableChat,                                  # 渔场自定义聊天
            "smile": self.doTableSmilies,                               # 渔场互动表情
            "clip_info": self._clip_info,                               # 显示弹药购买详情信息响应
            "clip_add": self._clip_add,                                 # 弹药购买
            "clip_alms": self._clip_alms,                               # 弹药救济金响应
            "clip_clearing": self._clip_clearing,                       # 弹药结算
            "bullet_use": self._bullet_use,                             # 使用招财珠
            "refresh_user_data": self._refreshUserData,                 # 刷新用户VIP等级和金币数
            "achievement_tasks": self._achievement_task,                # 荣耀任务
            "achievement_tasks_reward": self._achievement_reward,       # 领取荣耀任务奖励
            "honor_push": self._honor_push,                             # 刷新称号
            "honor_replace": self._honor_replace,                       # 更换称号(暂时不用)
            "guns_list": self._guns_list,                               # 发送火炮列表消息
            "guns_pool": self._guns_pool,                               # 更新炮的奖池
            "gun_up": self._gun_up,                                     # 普通炮升级
            "recharge_notify": self._recharge_notify,                   # 充值通知
            "refresh_skill_cd": self._refresh_skill_cd,                 # 刷新技能cd时间
            "achievement_target": self._achievement_target,             # 成就任务(暂时不用)
            "fishActivityBtns": self._activity_all_btns,                # 所有活动按钮
            "fishActivityRead": self._activity_read,                    # 读活动
            "fishActivityReceive": self._activity_reward,
            "fishActivityBonusResult": self._activity_bonus,
            "take_gift_reward": self._takeGiftReward,                   # 领取礼包奖励
            "treasure_rewards": self._getTreasureRewards,
            "task_update": self._taskUpdate,
            "main_reward": self._getMainQuestRewards,
            "prize_wheel_info": self._prizeWheelInfo,                   # 渔场内经典转盘
            "prize_wheel_bet": self._prizeWheelBet,                     # 确定轮盘最终奖励
            "prize_wheel_info_m": self._prizeWheelInfo,                 # 渔场内千炮转盘
            "prize_wheel_bet_m": self._prizeWheelBet,                   # 确定轮盘最终奖励
            "comp_act_notify": self._inspireNotify,
            "newbie_7_gift_take": self._takeNewbie7DaysGift,            # 领取新手7日礼包奖励
            "item_use": self.item_use,                                  # 使用道具技能
            "use_gun_effect": self.gun_effect_use                       # 使用皮肤炮的特殊效果
        }

        self.actionMap2 = {
            "fire": self._verifyFire,                                   # 验证该次捕获是否有效
            "gchg": self._gunChange,                                    # 切换火炮等级
            "chg_gun": self._chgGun,                                    # 切换火炮
            "gun_change_skin": self._chgGunSkin,                        # 切换火炮皮肤
            "gun_compose_skin": self._composeGunSin,                    # 合成火炮皮肤
            "ping": self._ping,                                         # 心跳
            "m_surpass": self._surpassTarget,                           # 回馈赛需要超越的玩家
            "total_catch": self._totalCatch                             # 发送圆盘数据
        }
        self.tideTaskSystem = TideTask(self)                            # 鱼潮任务
        if "table" in self.runConfig.taskSystemType:                    # 使用的任务系统
            self.taskSystemTable = TaskSystemTable(self)                # 渔场内任务管理系统
            self.systemTableActionMap = {
                "task_ready": self.taskSystemTable.taskReady,           # 任务准备
                "task_start": self.taskSystemTable.taskStart,           # 开始
                "task_end": self.taskSystemTable.taskEnd,               # 结束
            }
        elif "user" in self.runConfig.taskSystemType:                   # 玩家的自身任务
            self.actionMap["table_task_info"] = self._getTableTask      # 获取当前任务信息
            self.actionMap["table_task_change"] = self._changeTableTask # 改变任务
            self.actionMap["red_task_list"] = self._getRedTaskList      # 新手任务列表
            self.actionMap["skip_newbie_guide"] = self.skip_newbie_guide    # 跳过新手引导

    def _doTableCall(self, msg, userId, seatId, action, clientId):
        """
        桌子内部处理所有的table_call命令  大厅转发过来的table_call
        子类需要自行判定userId和seatId是否吻合
        """
        if 0 < seatId <= self.maxSeatN:
            player = self.players[seatId - 1]
            seat = self.seats[seatId - 1]
            if (not userId or not player or player.userId != userId or seat.userId != userId):
                playerUid = player.userId if player else 0
                ftlog.warn("_doTableCall, the userId is wrong !", playerUid, msg)
                return True
        else:
            if action not in ["add_fish_group", "robot_leave"]:
                ftlog.warn("invalid seatId", userId, action)
                return False

        func = self.actionMap.get(action)
        if ftlog.is_debug():
            ftlog.debug("_doTableCall", userId, action)
        if func:
            func(msg, userId, seatId)
            return True
        else:
            ftlog.warn("unrecognized action", userId, msg)
            return False

    def doTableCallOwn(self, msg, userId, seatId, action, clientId):
        """
        桌子内部处理所有的fish_table_call命令
        """
        if 0 < seatId <= self.maxSeatN:
            player = self.players[seatId - 1]
            seat = self.seats[seatId - 1]
            # 开火时更新活动时间
            if player and action == "fire":
                player.lastActionTime = int(time.time())                                        # 更新最后action的时间
            if (not userId or not player or player.userId != userId or seat.userId != userId):
                if action != "ping":
                    playerUid = player.userId if player else 0
                    ftlog.warn("doTableCallOwn, the userId is wrong !", playerUid, msg)
                return True

        else:
            ftlog.warn("invalid seatId", userId, action)
            return False

        func = self.actionMap2.get(action)
        if ftlog.is_debug():
            ftlog.debug("doTableCallOwn", userId, action)
        if func:
            func(msg, userId, seatId)
            return True
        else:
            ftlog.warn("unrecognized action", userId, msg)
            return False

    def clear(self):
        """
        完全清理桌子数据和状态, 恢复到初始化的状态
        """
        if ftlog.is_debug():
            ftlog.debug("clear-->begin")
        self._resetTableConf()                  # 重置桌子的配置
        self.processing = False                 # 重置分桌时桌子的处理状态
        self.startTime = time.time()            # 重置桌子开始时间
        for x in xrange(len(self.seats)):
            self.seats[x] = TYSeat(self)        # 清理座位状态
            self.players[x] = None              # 清理玩家信息
        if ftlog.is_debug():
            ftlog.debug("clear-->done")

    def initFishGroupData(self):
        """
        初始化鱼阵数据
        """
        self.fishGroupSystem = FishGroupSystem(self)
        self.superBossFishGroup = None          # 超级Boss
        self.tideFishGroup = None               # 鱼潮
        self.resetFishGroupData()

    def resetFishGroupData(self):
        """
        重置鱼阵数据
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
        self.terrorFishGroup = None             # 获取恐怖鱼鱼阵
        self.platterFishGroup = None            # 获取大盘鱼鱼群
        self.miniGameFishGroup = None           # 小游戏鱼阵
        self.ttAutofillFishGroup = None         # 渔场任务使用的自动填充鱼阵
        self.normalFishGroups = OrderedDict()   # 该渔场的普通鱼群队列 {鱼群自增ID: 鱼群对象}
        self.callFishGroups = OrderedDict()     # 该渔场的召唤鱼群队列 {鱼群自增ID: 鱼群对象}
        self.fishMap = {}                       # 该渔场的所有鱼对象 {渔场里鱼的自增ID: 鱼的详细数据}
        self.fishCountMap = {}                  # 该渔场的所有鱼数量 {fish配置表中的鱼种ID: 数量}

    def startFishGroup(self):
        """
        启动鱼阵
        """
        if self.runConfig.allNormalGroupIds:
            self.normalFishGroup = NormalFishGroup(self)

    def clearFishGroup(self):
        """
        清除鱼阵
        """
        self.activityFishGroup and self.activityFishGroup.clearTimer()
        self.autofillFishGroup and self.autofillFishGroup.clearTimer()
        self.bossFishGroup and self.bossFishGroup.clearTimer()
        self.bufferFishGroup and self.bufferFishGroup.clearTimer()
        self.chestFishGroup and self.chestFishGroup.clearTimer()
        self.couponFishGroup and self.couponFishGroup.clearTimer()
        self.grandPrixFishGroup and self.grandPrixFishGroup.clearTimer()
        self.multipleFishGroup and self.multipleFishGroup.clearTimer()
        self.normalFishGroup and self.normalFishGroup.clearTimer()
        self.rainbowFishGroup and self.rainbowFishGroup.clearTimer()
        self.shareFishGroup and self.shareFishGroup.clearTimer()
        self.terrorFishGroup and self.terrorFishGroup.clearTimer()
        self.platterFishGroup and self.platterFishGroup.clearTimer()
        self.miniGameFishGroup and self.miniGameFishGroup.clearTimer()
        self.ttAutofillFishGroup and self.ttAutofillFishGroup.clearTimer()
        self.fishGroupSystem.clear()
        self.resetFishGroupData()

    def _checkReloadRunConfig(self):
        """
        检查并重新载入配置
        """
        self._resetTableConf()
        if ftlog.is_debug():
            ftlog.debug("_checkReloadRunConfig->", self.tableId, self.playersNum, self.configChanged, self._runConfig)

    def _resetTableConf(self):
        """
        重置桌子的配置
        """
        runconf = deepcopy(self.room.roomConf)
        runconf.update(deepcopy(self.config))
        self._runConfig = FishTableConf(runconf)

    def _clearTable(self):
        """
        清理桌子
        """
        for i in range(self.maxSeatN):
            player = self.players[i]
            if player and player.userId:
                self.clearPlayer(player)
        ftlog.info("clear table end")

    def checkState(self):
        """
        检查玩家状态
        """
        for player in self.players:
            if not (player and player.userId):
                continue
            intervalTime = int(time.time()) - player.lastActionTime
            # 用户空闲超时时间 3分钟 | 用户离线等待时间 1分钟 | 用户无子弹时超时时间 3分钟
            if (intervalTime >= self._idleTimeOutSeconds) or \
               (intervalTime >= self._offlineWaitSeconds and player.offline) or \
               (intervalTime >= self._inactiveTimeOutSeconds and player.clip == 0):
                self.clearPlayer(player)

    def getPlayer(self, userId):
        """
        获取玩家对象
        """
        for p in self.players:
            if p and p.userId == userId and userId != 0:
                return p
        return None

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建玩家对象
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
        该房间游戏模式(0:经典 1:千炮)
        """
        return self._runConfig.gameMode

    def insertFishGroup(self, groupNames, position=None, HP=None, buffer=None, userId=None, score=None,
                        sendUserId=None, gameResolution=None):
        """召唤鱼群"""
        return self.fishGroupSystem.insertFishGroup(groupNames, position, HP, buffer, userId, score,
                                                    sendUserId, gameResolution)

    def addNormalFishGroups(self, groupNames):
        """
        普通鱼群，一次生成多个鱼群，一起发给客户端
        """
        self.fishGroupSystem.addNormalFishGroups(groupNames)

    def deleteFishGroup(self, group):
        """
        删除单个鱼群
        """
        self.fishGroupSystem.deleteFishGroup(group)

    def getNextGroupEnterTime(self):
        """
        获得下一个普通鱼群的入场时间
        （等于当前渔场普通鱼群队列最后一个鱼群里最后一条鱼的出场时间）
        """
        if len(self.normalFishGroups):
            group = self.normalFishGroups.values()[-1]
            return group.getNextGroupTime()
        else:
            return time.time() - self.startTime + 1

    def _clip_info(self, msg, userId, seatId):
        """显示弹药购买详情信息响应"""
        player = self.players[seatId - 1]
        if player:
            message = MsgPack()
            message.setCmd("clip_info")
            message.setResult("gameId", FISH_GAMEID)
            message.setResult("userId", userId)
            message.setResult("seatId", seatId)
            message.setResult("chip", player.chip)                  # 牌桌外金币
            message.setResult("clip", player.clip)                  # 剩余子弹数
            message.setResult("lack", self.runConfig.lack)          # 不足多少子弹数时自动购买
            message.setResult("bullets", self.runConfig.bullets)    # 购买子弹数列表
            message.setResult("multiple", self.runConfig.multiple)  # 渔场倍率
            message.setResult("fpMultiple", player.fpMultiple)      # 玩家实际选择的倍率
            GameMsg.sendMsg(message, userId)
            if player.allChip < self.runConfig.minCoin:             # 所有金币
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
        reason = 0
        player = self.players[seatId - 1]
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
        if not player:
            return
        player.gunEffectState(0, player.gunId)
        userGunIds = gun_system.getGunIds(userId, self.gameMode)
        if gunId not in userGunIds:
            return
        self.syncChgGunData(player, gunId)
        player.gunEffectState(1)

    def _chgGunSkin(self, msg, userId, seatId):
        """
        切换火炮皮肤
        """
        gunId = msg.getParam("gunId")
        skinId = msg.getParam("skinId")
        player = self.getPlayer(userId)
        if not player:
            return
        if not gun_system.changeGunSkin(userId, gunId, skinId, self.gameMode):  # 更改火炮皮肤
            return
        if int(gunId) == int(player.gunId):     # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
            self.syncChgGunData(player, gunId)

    def _composeGunSin(self, msg, userId, seatId):
        """
        合成火炮皮肤
        """
        gunId = msg.getParam("gunId")
        skinId = msg.getParam("skinId")
        player = self.getPlayer(userId)
        if not player:
            return
        if not gun_system.composeGunSkin(userId, gunId, skinId, self.gameMode):     # 合成火炮皮肤
            return
        if int(gunId) == int(player.gunId):     # 如果皮肤归属的火炮处于装备状态，则通知客户端火炮皮肤改变
            self.syncChgGunData(player, gunId)

    def syncChgGunData(self, player, gunId):
        """
        修改火炮数据并广播通知其他玩家
        """
        player.chgGunData(gunId)        # 切换炮台
        player.sendChgGunInfo()         # 发送火炮修改消息
        gun_system.sendGunListMsg(player.userId, self.gameMode)
        if hasattr(player, "tableMaxGunLevel") and self.typeName in config.MULTIPLE_MODE_ROOM_TYPE:
            player.tableMaxGunLevel(True)

    def _refreshUserData(self, msg, userId, seatId):
        """刷新用户数据"""
        player = self.getPlayer(userId)
        if player:
            player.refreshVipLevel()                # 刷新vip等级
            player.refreshHoldCoin()                # 刷新金币数
            player.refreshGunLevel()                # 刷新炮等级
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
            superBullet = None
            gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
            gunMultiple = skill.gunSkinMultiple if skill else gunMultiple
            gunX = util.getGunX(player.nowGunLevel, self.gameMode)
            fpMultiple = player.fpMultiple
            if wpType == config.GUN_WEAPON_TYPE:
                costChip = costBullet * fpMultiple      # 消耗的子弹 * 渔场倍率
                wpPower = wpConf["power"]
                if self.gameMode == config.MULTIPLE_MODE:
                    # 增加狂暴弹期间子弹威力
                    wpPower, superBullet = player.gunEffectState(6, player.gunId, wpConf["power"], gunX * gunMultiple)
                clip = player.costClip(costBullet, "BI_NFISH_GUN_FIRE")
            player.addFire(bulletId, wpId, timestamp, fpMultiple, gunMultiple=gunMultiple, gunX=gunX,
                           skill=skill, power=wpPower, costChip=costChip, superBullet=superBullet)

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
        extendId = extends[0] if extends else 0
        player = self.players[seatId - 1]
        fireWpId = player.getFireWpId(bulletId, extendId)   # 获取子弹所属的武器ID
        wpType = util.getWeaponType(wpId)
        extendId = 0
        if ftlog.is_debug():
            ftlog.debug("_verifyCatch->userId =", userId, msg, fireWpId, wpType)
        if not self._verifyCatchParams(player, wpId, fireWpId, wpType, bulletId, extends, stageId):
            return
        if skillId:
            # 使用技能判断是否捕获鱼
            skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
            if not skill:
                ftlog.error("_verifyCatch skill error", skillId, "userId =", userId)
                return
            if skill.isReturn == 1 and not fIds:    # 技能打空返还技能子弹
                skill.returnClip()
            catch, gain, gainChip, exp = skill.catchFish(bulletId, wpId, fIds, extends)
            fpMultiple = skill.fpMultiple
            gunMultiple = skill.gunSkinMultiple
            gunX = skill.gunX
        else:
            # 使用普通火炮或特殊武器（炸弹鱼、电鳗鱼等）判断是否捕获鱼
            catch, gain, gainChip, exp = self._catchFish(player, bulletId, wpId, fIds, extends, stageId)
            extendId = extends[0] if extends else 0
            fpMultiple = player.getFireFpMultiple(bulletId, extendId)
            gunMultiple = player.getFireGunMultiple(bulletId, extendId)
            gunX = player.getFireGunX(bulletId, extendId)
        # 处理捕获之后的一些逻辑
        self.dealCatch(bulletId, wpId, player, catch, gain, gainChip, exp, fpMultiple, gunMultiple, gunX,
                       extends=extends, skillId=skillId, stageId=stageId)
        if fireWpId and wpType != config.SKILL_WEAPON_TYPE:  # 删除非技能子弹
            maxStage = player.getFireMaxStage(bulletId, extendId)
            # 子弹达到最大阶段后销毁.
            if stageId == maxStage:
                player.delFire(bulletId, extendId)
        if wpType in config.LOG_OUTPUT_WEAPON_TYPE_SET:
            ftlog.info("_verifyCatch->", "userId =", userId, "msg =", msg)

    def _verifyCatchParams(self, player, wpId, fireWpId, wpType, bulletId, extends, stageId):
        """
        验证客户端上报的捕获消息相关数据是否合法
        """
        # 普通炮和技能等武器类型只校验子弹数据
        if not fireWpId or fireWpId != wpId:
            ftlog.warn("_verifyCatch fireWpId error", player.userId, bulletId, wpId, fireWpId)
            return False
        # 特殊武器类型（鱼死亡后会成为武器发起捕获，以死亡时的fId为子弹ID，放入extends中，校验其数据）
        elif wpType in config.SPECIAL_WEAPON_TYPE_SET:
            extendId = extends[0] if extends else None
            maxStage = player.getFireMaxStage(bulletId, extendId)
            if stageId > maxStage:
                ftlog.warn("_verifyCatch special fish not match", player.userId, wpId, stageId)
        return True

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
                ftlog.warn("findFish fish is not in fishMap", fId, self.tableId)
            return False
        fishInfo = self.fishMap[fId]            # 鱼的集合
        group = fishInfo.get("group")           # 鱼群详情
        conf = fishInfo.get("conf")             # 鱼的配置
        if not fishInfo["alive"]:
            if ftlog.is_debug():
                ftlog.warn("findFish fish is not alive", fId, group.id, conf, self.tableId)
            return False
        nowTableTime = self._getNowTableTime()
        if ftlog.is_debug():
            ftlog.debug("group desc fish in:", fId, group.desc(), "nowTableTime:", nowTableTime, self.tableId)
        if not group.isExist(nowTableTime):
            if ftlog.is_debug():
                ftlog.warn("findFish group not exist", fId, nowTableTime, group.id, conf, self.tableId)
            return False
        if not group.fishExist(nowTableTime, fId):
            if ftlog.is_debug():
                ftlog.warn("findFish fish not exist", fId, nowTableTime, group.id, conf, self.tableId)
            return False
        return True

    def verifyFish(self, userId, fId, wpId=0):
        """
        验证捕到的鱼是否有效 userId捕鱼者 fId鱼Id、wpId武器Id
        """
        catchUserId = userId
        isOK = True
        if not self.findFish(fId):
            isOK = False
            return isOK, catchUserId
        fishInfo = self.fishMap[fId]
        if not fishInfo["buffer"]:
            return isOK, catchUserId
        for buffer in fishInfo["buffer"]:
            skillId = buffer[0]
            skillEndTime = buffer[1]
            releaseUserId = buffer[2]
            if ftlog.is_debug():
                ftlog.debug("verifyFish->skillId =", skillId, time.time(), skillEndTime, releaseUserId)
            if skillId == 5107:                                 # 欺诈水晶（附带欺诈效果）
                if time.time() < skillEndTime:
                    catchUserId = releaseUserId
            if skillId == 5102:                                 # 魔术炮（附带无敌效果）
                if time.time() < skillEndTime and userId != releaseUserId:
                    isOK = False
            elif skillId == 5104:                               # 极冻炮（附带冰冻效果）
                if fishInfo["type"] in config.ICE_FISH_TYPE:    # 冰锥
                    if time.time() >= skillEndTime:
                        self.setFishDied(fId)
                        isOK = False
                    if userId == releaseUserId:
                        isOK = False
            elif skillId == 5109:                               # 猎鱼机甲（倒计时后消失）
                if time.time() >= skillEndTime:
                    self.setFishDied(fId)
                    isOK = False
                if wpId != 2302 and userId == releaseUserId:    # 猎鱼机甲不会被自己捕获
                    isOK = False
            if not isOK:
                break
        return isOK, catchUserId

    def setFishDied(self, fId):
        """
        标记鱼为死亡状态
        """
        fishInfo = self.fishMap.get(fId)
        if fishInfo:
            if fishInfo["alive"]:
                self.refreshFishTypeCount(fishInfo)
            self.fishMap[fId]["alive"] = False
            return True
        return False

    def _catchFish(self, player, bulletId, wpId, fIds, extends, stageId):
        """
        检测能否捕到鱼
        :param player: 玩家
        :param bulletId: 子弹Id
        :param wpId: 武器ID
        :param fIds: 鱼
        :param extends: 扩展数据
        :param stageId: 阶段Id
        """
        fIdTypes = {}
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        extendId = extends[0] if extends else 0
        superBullet = player.getFire(bulletId).get("superBullet", {})   # 超级子弹数据 player.isSuperBullet(bulletId)
        gunConf = player.getGunConf(bulletId, extendId)                 # 子弹开火的炮配置
        bufferCoinAdd = player.getCoinAddition(wpId)                    # 获取金币加成
        fpMultiple = player.getFireFpMultiple(bulletId, extendId)       # 获取开火时的渔场倍率
        gunMultiple = player.getFireGunMultiple(bulletId, extendId)     # 获取开火时的武器倍率
        gunMultiple = gunMultiple or gunConf.get("multiple", 1)         # 单|双倍
        gunX = player.getFireGunX(bulletId, extendId)                   # 炮的倍率
        if ftlog.is_debug():
            ftlog.debug("_catchFish->userId =", player.userId, "bulletId =", bulletId, "extends =", extends,
                        "wpId =", wpId, "fIds =", fIds, "stageId =", stageId, "bufferCoinAdd =", bufferCoinAdd,
                        "gunConf =", gunConf, "gunMultiple =", gunMultiple, "fire =", player.getFire(bulletId, extendId),
                        "fpMultiple =", fpMultiple, "superBullet =", superBullet, "gunX =", gunX)
        otherCatch = {}
        isCatch = False
        isInvalid = False
        notCatchFids = []
        gunId = gunConf.get("gunId", 0)
        gunLevel = gunConf.get("gunLevel", 1)   # 经典模式下火炮熟练度等级
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)     # 获取武器的配置
        wpType = util.getWeaponType(wpId)
        totalCostCoin = self.getCostBullet(gunId, gunLevel, wpConf, player.clientId) * fpMultiple  # 计算总消耗的金币
        averageCostCoin = float(totalCostCoin) / (len(fIds) or 1)   # 平均消耗的金币
        curveLossCoin = 0
        curveProfitCoin = 0
        aloofOdds = player.dynamicOdds.getOdds(superBullet=superBullet, aloofFish=True, gunConf=gunConf)
        nonAloofOdds = player.dynamicOdds.getOdds(superBullet=superBullet, aloofFish=False, gunConf=gunConf)
        fish_type_list = []

        _datas = {"fpMultiple": fpMultiple, "gunMultiple": gunMultiple}
        for fId in fIds:
            isOK, catchUserId = self.verifyFish(player.userId, fId)
            if isOK:
                pass
            else:
                isInvalid = True
                continue
            catchMap = {"fId": fId, "reason": 1}
            fishInfo = self.fishMap[fId]
            originHP = fishInfo["HP"]
            probb = self.getCatchProbb(player, bulletId, wpConf, fId, fIdsCount=len(fIds), superBullet=superBullet, extendId=extendId,
                                       aloofOdds=aloofOdds, nonAloofOdds=nonAloofOdds, stageId=stageId, datas=_datas)
            catchMap["HP"] = self.fishMap[fId]["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:                    # 被捕获
                # 欺诈只获得1倍收益
                if catchUserId != player.userId:
                    gunMultiple = 1
                # 处理打死鱼获得的奖励
                fishGainChip, fishGain, fishExp = self.dealKillFishGain(fId, player, fpMultiple, gunMultiple=gunMultiple,
                                                                        bufferCoinAdd=bufferCoinAdd, wpType=wpType,
                                                                        extends=extends, gunX=gunX)
                catchMap["reason"] = 0
                if catchUserId == player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
            else:
                notCatchFids.append(fId)
                if originHP != catchMap["HP"]:
                    catch.append(catchMap)

            fishType = fishInfo["fishType"]
            fIdTypes[fId] = fishType
            if wpType == config.GUN_WEAPON_TYPE:
                fish_type_list.append(fishType)
            if self.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
                if wpType == config.GUN_WEAPON_TYPE and not superBullet:    # 火炮打出的普通子弹
                    fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
                    if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                        curveLossCoin += averageCostCoin
                        if catchMap["reason"] == 0:
                            curveProfitCoin += fishConf["value"] * fpMultiple * gunMultiple

        if ftlog.is_debug():
            ftlog.debug(
                "_catchFish->userId =", player.userId, "catch =", catch, "gain =", gain, "gainChip =", gainChip,
                "curveLossCoin =", curveLossCoin, "curveProfitCoin =", curveProfitCoin, "extendId =", extendId,
                "otherCatch =", otherCatch, "gunX =", gunX
            )
        player.dynamicOdds.updateOdds(curveProfitCoin - curveLossCoin)
        self.dealGunEffect(player, notCatchFids)                        # 1165的火炮ID, 霜冻特性，有几率冰冻鱼
        player.checkConnect(isInvalid)
        if isCatch:
            player.addCombo()
        if wpType in config.LOG_OUTPUT_WEAPON_TYPE_SET:
            ftlog.info(
                "_catchFish, userId =", player.userId,
                "wpType =", wpType,
                "fIdTypes =", fIdTypes,
                "catch =", catch,
                "gain =", gain
            )
        return catch, gain, gainChip, exp

    def _getNowTableTime(self):
        """获取当前桌子从创建至今已经走过的时间(秒)"""
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
        gunM = msg.getParam("gunM")
        stageCount = msg.getParam("stageCount")
        fpMultiple = self.runConfig.multiple
        wpType = util.getWeaponType(wpId)

        mo = MsgPack()
        mo.setCmd("total_catch")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("seatId", seatId)
        mo.setResult("wpId", wpId)
        mo.setResult("fishResId", fResId)
        mo.setResult("skillId", skillId)
        mo.setResult("fishId", fishId)
        # mo.setResult("gunMultiple", gunMultiple)
        mo.setResult("totalCoin", totalCoin)
        # mo.setResult("fpMultiple", fpMultiple)
        GameMsg.sendMsg(mo, self.getBroadcastUids(userId))

        event = CatchEvent(userId, FISH_GAMEID, self.roomId, self.tableId, [], wpId, totalCoin, fpMultiple)
        player.activitySystem and player.activitySystem.dealDrillCatchFish(event)
        if wpType in [config.DRILL_WEAPON_TYPE, config.SUPER_BOSS_WEAPON_TYPE]:
            self.checkBigPrize(player, totalCoin / (gunM * fpMultiple), totalCoin, fpMultiple)

        if self.typeName not in config.NORMAL_ROOM_TYPE:
            return
        fishConf = config.getFishConf(fResId, self.typeName, fpMultiple)
        if fishConf.get("type", None) in config.TERROR_FISH_TYPE and totalCoin / fpMultiple >= 1500 and (self.runConfig.fishPool == 44004 or self.runConfig.fishPool == 44005):
            # msg = u"恭喜%s击杀%s总计%s分，获得%s金币！" % \
            title = config.getMultiLangTextConf(self.runConfig.title, lang=player.lang)
            fishName = config.getMultiLangTextConf(fishConf["name"], lang=player.lang)
            self._sendFormatLed(player, "ID_LED_CATCH_TERROR_FISH", player.name, fishName,
                                util.formatScore(totalCoin, lang=player.lang))
        elif fishConf.get("type", None) in [5, 28, 29, 35] and totalCoin >= 5000000 and gunM >= 10000:
            # msg = u"恭喜%s用%s倍炮击杀%s获得%s分，共%s金币" % \
            fishName = config.getMultiLangTextConf(fishConf["name"], lang=player.lang)
            totalValue = totalCoin / gunM
            self._sendFormatLed(player, "ID_LED_CATCH_TERROR_FISH_VALUE", player.name, gunM,
                                fishName, util.formatScore(totalCoin, lang=player.lang))
        elif fishConf.get("type", None) in [33, 34, 31] and stageCount >= 5 and gunM >= 10000:
            # msg = u"恭喜%s用%s倍炮击杀%s共爆炸%s次，获得%s金币！" % \
            fishName = config.getMultiLangTextConf(fishConf["name"], lang=player.lang)
            self._sendFormatLed(player, "ID_LED_CATCH_TERROR_FISH_COUNT", player.name, gunM,
                                fishName, stageCount, util.formatScore(totalCoin, lang=player.lang))

    def getCatchProbb(self, player, bulletId, wpConf, fId, fIdsCount=1, superBullet=None, extendId=0,
                      aloofOdds=0, nonAloofOdds=0, stageId=0, datas=None):
        return self._getCatchProbb(player, bulletId, wpConf, fId, fIdsCount, superBullet, extendId,
                                   aloofOdds, nonAloofOdds, stageId, datas)

    def _getCatchProbb(self, player, bulletId, wpConf, fId, fIdsCount=1, superBullet=None, extendId=0,
                       aloofOdds=0, nonAloofOdds=0, stageId=0, datas=None):
        """
        获取捕获概率
        :param player: 玩家
        :param wpConf: 子弹所属武器配置
        :param fId: 鱼Id
        :param fIdsCount: 网鱼数量
        :param superBullet: 超级子弹
        :param extendId: 扩展Id
        :param aloofOdds: 高冷鱼概率系数
        :param nonAloofOdds: 非高冷鱼的概率系数
        :param stageId: 阶段Id
        :param datas: 整理的数据
        """
        gunMultiple = datas and datas.get("gunMultiple", None) or 1                 # 开火时的武器倍率
        fpMultiple = datas and datas.get("fpMultiple", self.runConfig.multiple) or self.runConfig.multiple
        if ftlog.is_debug():
            ftlog.debug("getCatchProbb", player.userId, bulletId, wpConf, fId, fIdsCount, superBullet, extendId,
                        aloofOdds, nonAloofOdds, stageId, datas)
        wpId = wpConf["weaponId"]
        wpType = util.getWeaponType(wpId)
        fishInfo = self.fishMap[fId]
        fishType = fishInfo["fishType"]
        ftType = fishInfo["type"]
        fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
        coefficient = self.getProbbCoefficient(player, fishInfo)          # 获取概率系数
        superBullet = superBullet or {}
        # 威力加成
        effectAddition = superBullet.get("effectAddition", 1)
        honorAddition = honor_system.getWeaponPowerAddition(player.ownedHonors, wpId)   # 获得特殊称号的武器威力加成
        bufferAddition = player.getPowerAddition(wpId)
        wpPower = 0
        initWpPower = 0
        if wpType == config.GUN_WEAPON_TYPE:  # 火炮
            wpPower = wpConf["power"] * effectAddition * honorAddition * bufferAddition     # 武器威力
        elif wpType in config.SPECIAL_WEAPON_TYPE_SET:  # [炸弹鱼, 电鳗, 钻头鱼, 超级boss, 能量宝珠, 三叉戟, 金钱箱]
            wpPower = max(player.getFirePower(extendId, stageId, wpId=wpId), 0) * honorAddition     # 特殊鱼子弹的威力
            initWpPower = player.getFireInitPower(extendId, stageId) * honorAddition

        # 扣减鱼血量
        fatal = self.dealIceConeEffect(fId, fishConf)
        fishHP = int(self.fishMap[fId]["HP"] - wpPower)
        fishHP = self.dealFishHP(fId, fishHP, fatal)
        # 计算概率
        odds = 0
        probb = 0
        probbRadix = self.getFishProbbRadix(fishInfo, fishConf, player, fpMultiple)
        if probbRadix == 0:                         # 捕获概率为0
            probb = 10000 if fishHP <= 0 else 0
        else:
            if wpType == config.GUN_WEAPON_TYPE:    # 火炮
                if ftType in config.NON_ALOOF_FISH_TYPE:   # 非高冷鱼
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
            elif wpType == config.BOMB_WEAPON_TYPE or (wpType == config.DRILL_WEAPON_TYPE and stageId == 1):    # 炸弹鱼 or 钻头鱼
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
            elif wpType == config.DRILL_WEAPON_TYPE:  # 钻头鱼
                unitPower = int(initWpPower * float(wpConf.get("wpRatio", 1)))
                costPower = min(wpPower, min(probbRadix, unitPower))
                probb = float(costPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, costPower, stageId)      # 减少子弹威力
            elif wpType == config.SUPER_BOSS_WEAPON_TYPE:                   # 超级boss
                if wpPower >= probbRadix:
                    probb = 10000
                else:
                    probb = float(wpPower) / probbRadix * 10000
                player.decreaseFirePower(extendId, probbRadix, stageId)
        probb *= coefficient
        if ftType in config.MULTIPLE_FISH_TYPE:                                # 倍率鱼
            if self.room.lotteryPool:
                isLucky, _ = self.room.lotteryPool.isMultiplePoolLucky()
                if isLucky:
                    probb *= 1.2
        elif ftType in config.BOSS_FISH_TYPE:                                  # boss鱼
            if player.dynamicOdds.currRechargeBonus >= fishConf["value"] * fpMultiple * gunMultiple:
                probb *= 2
        elif ftType in config.RED_FISH_TYPE:                                   # 红包鱼
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

        if ftlog.is_debug():
            ftlog.debug(
                "getCatchProbb->", "userId =", player.userId, "odds =", odds, "probb =", probb, "wpId =", wpId,
                "fId =", fId, "fIdsCount =", fIdsCount, "superBullet =", superBullet, "extendId =", extendId,
                "aloofOdds =", aloofOdds, "nonAloofOdds =", nonAloofOdds, "stageId =", stageId, "fishType =", fishType,
                "coefficient =", coefficient, "effectAddition =", effectAddition, "honorAddition =", honorAddition,
                "bufferAddition =", bufferAddition, "wpPower =", wpPower, "initWpPower =", initWpPower, "fatal =", fatal,
                "fishHP =", fishHP, "probbRadix =", probbRadix, "currRechargeBonus =", player.dynamicOdds.currRechargeBonus,
                "redState =", player.redState)
        return probb

    def getProbbCoefficient(self, player, fishInfo):
        """获取概率系数"""
        return 1

    def isNeedAdjustFishProbbRadix(self, fishConf, player):
        """
        10倍场主线任务处于1-2期间，捕获难度及威力倍率调整
        """
        # if self.runConfig.fishPool == 44002 and fishConf["type"] in config.BOMB_FISH_TYPE:
        #     if player.mainQuestSystem and player.mainQuestSystem.currTask:
        #         if ftlog.is_debug():
        #             ftlog.debug("getFishProbbRadix->userId =", player.userId, "currTask =", player.mainQuestSystem.currTask)
        #         if player.mainQuestSystem.currTask.get("taskId") == 641002 and player.mainQuestSystem.currTask.get("state") == 0:
        #             if ftlog.is_debug():
        #                 ftlog.debug("getFishProbbRadix->userId =", player.userId, " need adjust radix !")
        #             return True
        return False

    def getFishProbbRadix(self, fishInfo, fishConf, player, fpMultiple=None, gunX=1):
        """鱼被捕获的概率基数"""
        if fpMultiple is None:
            fpMultiple = self.runConfig.multiple
        if fishInfo["HP"] > 0:
            return fishConf["probb2"]
        elif fishInfo["type"] in config.CHIP_CHEST_FISH_TYPE:
            if player.userId == fishInfo["owner"]:
                return fishConf["probb1"]
            return fishConf["probb2"]
        elif fishInfo["type"] in config.RAINBOW_BONUS_FISH_TYPE:    # 使用彩虹奖池的鱼
            value = fishConf["score"]
            gunMultiple = config.getGunConf(player.gunId, player.clientId, player.gunLv, self.gameMode).get("multiple", 1)
            if fishInfo["type"] in config.TERROR_FISH_TYPE:         # 恐怖鱼
                value = config.getWeaponConf(fishConf["weaponId"], False, mode=self.gameMode)["power"]
            if player.dynamicOdds.currRechargeBonus >= value * gunMultiple * gunX * fpMultiple:     # 当前充值奖池
                if ftlog.is_debug():
                    ftlog.debug("getFishProbbRadix->userId =", player.userId,
                            "currRechargeBonus =", player.dynamicOdds.currRechargeBonus, "gunX =", gunX)
                return fishConf["probb1"]
            return fishConf["probb2"]
        else:
            return fishConf["probb1"]

    def dealIceConeEffect(self, fId, fishConf):
        """
        处理冰锥效果(冰锥星级属性,无法被一击必杀是否生效)
        """
        fishInfo = self.fishMap[fId]
        ftType = fishInfo["type"]
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

    def dealFishHP(self, fId, fishHP, fatal=False):
        """
        处理鱼的血量
        :param fId: 鱼的ID
        :param fishHP: 鱼的剩余血量
        :param fatal: 不会被一击必杀 冰锥65%以上 不死
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
        :param bufferCoinAdd: buffer加成金币系数（非回馈赛暂时无用）
        :param wpType: 武器类型
        :param extends: 扩展数据
        :param gunX: 炮的倍数
        """
        raise NotImplementedError

    def getKillFishExp(self, player, fishConf, fpMultiple):
        """
        获得捕获鱼所得经验值
        """
        raise NotImplementedError

    def dealKillFishFixedDropGain(self, player, fId, fishConf, fpMultiple, gunMultiple, gunX, wpType):
        """
        处理捕获鱼所获得的固定掉落奖励
        """
        raise NotImplementedError

    def dealKillFishExtraDropGain(self, player, fId, fishConf, fpMultiple, gunMultiple, gunX):
        """
        处理捕获鱼所获得的额外掉落奖励
        """
        raise NotImplementedError

    def getKillFishCoinGain(self, player, fId, fishConf, fpMultiple, gunMultiple, gunX, gainMap):
        """
        获得捕获鱼的基础金币奖励
        """
        raise NotImplementedError

    def getKillFishBulletGain(self, player, fId, fishConf, fpMultiple, gunMultiple, gunX, gainMap):
        """
        获得捕获鱼的基础招财珠奖励
        """
        raise NotImplementedError

    def getMultipleFishMultiple(self, player, fishConf, fpMultiple, gunMultiple, gunX):
        """
        获得倍率鱼的倍率
        """
        raise NotImplementedError

    def getBossFishMultiple(self, player, fishConf, fpMultiple, gunMultiple, gunX):
        """
        获得Boss的倍率
        """
        raise NotImplementedError

    def dealHitBossGain(self, power, fId, player, originHP=0, totalProbb=1):
        """
        处理打中boss掉落金币
        """
        raise NotImplementedError

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
        :param isFraud: 是否为欺诈
        :param skillType: 技能类型
        :return:
        """
        if not player:
            return
        if skillId:
            skill = player.getFireSkill(bulletId) or player.getSkill(skillId, skillType)
        else:
            skill = None
        if (not catch and not gain) and (not skill or skill.isReturn != 1):
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
                multiple = player.getFireGunMultiple(bulletId, extendId)
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
        retMsg.setResult("skillId", skillId)
        retMsg.setResult("skillType", skillType)
        retMsg.setResult("stageId", stageId)
        retMsg.setResult("multiple", gunMultiple)
        retMsg.setResult("gunX", gunX)
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
        retMsg.setResult("items", gain)
        GameMsg.sendMsg(retMsg, self.getBroadcastUids())

    def setFishBuffer(self, fId, newBuffer):
        """
        给鱼添加buffer 鱼的buffer 人给鱼buffer
        :param fId: 鱼ID
        :param newBuffer: 新的buffer
        """
        buffers = deepcopy(self.fishMap[fId]["buffer"])
        if buffers:
            for buffer in buffers:
                if newBuffer[0] == buffer[0]:       # 相同buffer会被新buffer替换
                    newBuffer[6] = buffer[6] + 1    # 施加buffer的次数
                    buffers.remove(buffer)
                    break
                elif newBuffer[0] == 5104 or buffer[0] == 5104:  # 冰冻buffer可以与其他buffer共存
                    continue
                else:
                    buffers.remove(buffer)  # 除冰冻外的其他buffer会被新buffer替换
                    break
        buffers.append(newBuffer)
        self.fishMap[fId]["buffer"] = buffers

    def extendOtherCatchGain(self, fId, catchUserId, otherCatch, gainChip, gain, catchMap=None, exp=0):
        """
        奖励给其他人(鱼处于欺诈水晶状态下)
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
        :param exp: 捕获经验
        :param fpMultiple: 渔场倍率
        :param extends: 扩展数据
        :param skillId: 技能Id
        :param stageId: 阶段Id
        :param isFraud: 是否存在欺诈水晶效果
        :param skillType: 技能类型0|1
        :return:
        """
        if ftlog.is_debug():
            ftlog.debug("dealCatch->", player.userId, bulletId, wpId, catch, gain, gainChip, exp, extends, skillId, stageId, fpMultiple)
        gainCoupon = 0
        items = []
        catchFishMultiple = {}
        for gainMap in gain:
            fishConf = config.getFishConf(gainMap["fishType"], self.typeName, fpMultiple)
            if gainMap and gainMap["itemId"] == CHIP_KINDID:
                pass
            elif gainMap and gainMap["itemId"] == COUPON_KINDID:
                gainCoupon += int(gainMap["count"])
            else:
                items.append(gainMap)
            if gainMap.get("fishMultiple"):
                catchFishMultiple[gainMap["fId"]] = gainMap.get("fishMultiple")
            if fishConf["type"] in config.RED_FISH_TYPE:
                # 计算累计获得金额及个人奖券鱼捕获次数
                totalEntityAmount = gamedata.getGameAttr(player.userId, FISH_GAMEID, GameData.totalEntityAmount)
                totalEntityAmount = float(totalEntityAmount) if totalEntityAmount else 0
                totalEntityAmount += config.RED_AMOUNTS.get(gainMap["itemId"], 0)
                if gainMap["itemId"] == COUPON_KINDID:
                    totalEntityAmount += gainMap["count"] * config.COUPON_DISPLAY_RATE
                gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.totalEntityAmount, totalEntityAmount)
                if self.fishMap[gainMap["fId"]]["owner"] == player.userId:
                    catchCountDict = gamedata.getGameAttrJson(player.userId, FISH_GAMEID, GameData.catchUserCouponFishCount, {})        # 通过捕鱼累计获得奖券和实物卡金额
                    catchCountDict[str(self.runConfig.fishPool)] = catchCountDict.setdefault(str(self.runConfig.fishPool), 0) + 1
                    gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.catchUserCouponFishCount, json.dumps(catchCountDict))
            if fishConf["type"] in config.LOG_OUTPUT_FISH_TYPE:
                ftlog.info("dealCatch->fishType",
                           "userId =", player.userId,
                           "fishType =", fishConf["type"],
                           "wpId =", wpId,
                           "gunMultiple =", gunMultiple,
                           "gunX =", gunX,
                           "gainMap =", gainMap,
                           "gainChip =", gainChip)
            # 捕获了超级boss添加积分到排行榜.
            # if fishConf["type"] in config.SUPER_BOSS_FISH_TYPE:
            #     from newfish.game import TGFish
            #     from newfish.entity.event import SuperbossPointChangeEvent
            #     event = SuperbossPointChangeEvent(player.userId, FISH_GAMEID, self.bigRoomId, fishConf["score"])
            #     TGFish.getEventBus().publishEvent(event)

        # 处理玩家等级升级
        player.incrExp(exp)
        wpType = util.getWeaponType(wpId)
        if wpType == config.GUN_WEAPON_TYPE:
            gunExp = player.incrGunExp(exp)
            player.incrGunLevel(gunExp)
        # 捕获奖励结算
        player.catchBudget(gainChip, gainCoupon, items, wpId=wpId)
        self._afterCatch(bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends, skillId, catchFishMultiple=catchFishMultiple)
        self._retVerifyCatch(player, bulletId, catch, gain, extends, skillId, stageId, fpMultiple)

    def _afterCatch(self, bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends=None, skillId=0, isFraud=False, skillType=0, catchFishMultiple=None):
        """
        捕获结算之后
        :param bulletId: 子弹ID
        :param wpId: 武器ID
        :param player: 玩家
        :param catch: 捕获信息
        :param gain: 获得奖励
        :param gainChip: 获取金币
        :param fpMultiple: 渔场倍率
        :param gunMultiple: 武器倍率
        :param gunX: 炮倍数
        :param extends: 扩展数据
        :param skillId: 技能ID
        :param catchFishMultiple: {fId:fishMultiple} 鱼倍率字典
        """
        fishTypes = []
        extendId = extends[0] if extends and not skillId else None  # 激光炮extends有特殊含义，代表判定次数
        gunX = player.getFireGunX(bulletId, extendId)
        if isFraud:
            gunMultiple = 1
        else:
            gunMultiple = player.getFireGunMultiple(bulletId, extendId)  # 获取开火时的武器倍率
        player.addProfitCoin(gainChip)
        catchFishPoints = []
        for catchMap in catch:
            if catchMap["reason"] == 0:
                fId = catchMap["fId"]
                fishType = self.fishMap[fId]["fishType"]
                fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
                if ftlog.is_debug():
                    ftlog.debug("_afterCatch", player.userId, fId, fishType)
                self.setFishDied(fId)
                fishTypes.append(fishType)
                # 处理活动等数据
                if fishConf["itemId"] != config.CHIP_KINDID:
                    # 非金币类鱼，使用其金币价值
                    player.addProfitCoin(fishConf.get("value", 0) * gunMultiple * fpMultiple)
                if fishConf["type"] in config.NORMAL_FISH_TYPE:     # 处理普通鱼捕获（判断金币宝箱鱼是否出现）
                    self.chestFishGroup and self.chestFishGroup.checkCondition(player, fishConf)
                elif fishConf["type"] in config.BOSS_FISH_TYPE:     # 处理boss捕获（全民打boss活动）
                    for player_ in self.players:
                        if player_ and self.fishMap.get(fId):
                            player_.dealCatchBoss(self.fishMap[fId], player.userId)
                # 捕获倍率
                if catchFishMultiple and catchFishMultiple.get(fId):
                    catchMap["fishMultiple"] = catchFishMultiple.get(fId)
                # 特殊鱼死亡后爆炸
                if fishConf["type"] in config.SPECIAL_WEAPON_FISH_TYPE:
                    catchMap = self.dealSpecialFishFire(player, fishConf, fpMultiple, gunMultiple, gunX, catchMap)
                # 彩虹鱼扣减奖池
                if fishConf["type"] in config.RAINBOW_BONUS_FISH_TYPE:
                    value = fishConf["score"]
                    if fishConf["type"] in config.TERROR_FISH_TYPE:
                        value = config.getWeaponConf(fishConf["weaponId"], False, self.gameMode)["power"]
                    # 鱼分值/武器能量对应奖池
                    bonus = value * gunMultiple * fpMultiple
                    # 需扣减奖池
                    deductionBonus = (value - fishConf["probb1"]) * gunMultiple * fpMultiple
                    if ftlog.is_debug():
                        ftlog.debug(
                            "dealCatch->userId =", player.userId, "currRechargeBonus =", player.dynamicOdds.currRechargeBonus >= bonus,
                            "getRainbowPoolCoin =", self.room.lotteryPool.getRainbowPoolCoin() >= bonus, "bonus =", bonus,
                            "deductionBonus =", deductionBonus, "gunMultiple =", gunMultiple
                        )
                    if player.dynamicOdds.currRechargeBonus >= bonus:
                        # 存在充值奖池
                        player.dynamicOdds.deductionRechargeBonus(deductionBonus)
                    elif self.room.lotteryPool and self.room.lotteryPool.getRainbowPoolCoin() >= bonus:
                        # 存在彩虹鱼奖池
                        self.room.lotteryPool.deductionRainbowPoolCoin(deductionBonus)
                # 检测是否可以获得巨奖
                # 只有普通鱼可以获得巨奖.
                # if fishConf["type"] not in config.BOSS_FISH_TYPE + config.TERROR_FISH_TYPE + config.MULTIPLE_FISH_TYPE:
                if fishConf["type"] == 1:
                    self.checkGrandPrize(fishConf.get("score", 0), player, fId, fpMultiple)
                # 捕鱼轮盘充能
                if self.typeName in config.NORMAL_ROOM_TYPE:
                    self.addPrizeWheelEnergy(player, fId, fishConf, fpMultiple, gunMultiple * gunX)
                # 大奖赛计算捕鱼积分
                if self.typeName in [config.FISH_GRAND_PRIX] and fishConf.get("probb2", 0) > 0 \
                        and fishConf["type"] not in config.TERROR_FISH_TYPE:
                    point = fishConf["score"]
                    if fishConf["type"] in config.MULTIPLE_FISH_TYPE and catchMap.get("fishMultiple", 1) > 1:
                        point *= catchMap["fishMultiple"]
                        if ftlog.is_debug():
                            ftlog.debug("addGrandPrixFishPoint 2, userId =", player.userId, catchMap["fishMultiple"])
                    point = player.addGrandPrixFishPoint(point, str(fishType), gunMultiple * gunX)
                    if point:
                        catchFishPoints.append({"fId": fId, "point": point})
        # 特殊鱼捕获时的幸运降临 炸弹鱼
        if util.getWeaponType(wpId) in [config.NUMB_WEAPON_TYPE, config.BOMB_WEAPON_TYPE]:
            totalCoin = sum([_val.get("count", 0) for _val in gain if _val.get("itemId") == CHIP_KINDID and _val.get("type") not in config.BOSS_FISH_TYPE])
            self.checkBigPrize(player, totalCoin / (gunMultiple * fpMultiple), totalCoin, fpMultiple)

        # 大奖赛主动推送捕鱼积分信息
        if self.typeName in [config.FISH_GRAND_PRIX] and catchFishPoints:
            player.sendGrandPrixCatch(catchFishPoints)

        self._sendLed(player, gain, fpMultiple, gunMultiple, gunX)  # 发送奖励掉落
        player.addCatchFishes(fishTypes)                            # 捕获鱼的条数

        from newfish.game import TGFish
        event = CatchEvent(player.userId, FISH_GAMEID, self.roomId, self.tableId, fishTypes, wpId, gainChip, fpMultiple,
                           catch, gain, player.resetTime, gunMultiple, gunX=gunX)
        TGFish.getEventBus().publishEvent(event)
        player.triggerCatchFishEvent(event)                         # 处理捕鱼事件
        if self.superBossFishGroup:                                 # 超级boss鱼群
            self.superBossFishGroup.triggerCatchFishEvent(event)
        if self.bossFishGroup:                                      # boss鱼群
            self.bossFishGroup.triggerCatchFishEvent(event)
        if self.taskSystemTable:                                    # 处理限时任务、奖金赛、夺宝赛捕鱼进度
            self.taskSystemTable.dealCatchEvent(event)
        if self.tideTaskSystem:                                     # 鱼潮任务捕获
            self.tideTaskSystem.dealCatchEvent(event)
        # 检查限时礼包
        if player.isFinishRedTask and player.gameTime >= 3 and player.checkLimitTimeGift:
            player.checkLimitTimeGift = False
            event = CheckLimitTimeGiftEvent(player.userId, FISH_GAMEID, player.level, player.dynamicOdds.chip, self.runConfig.fishPool, player.clientId)
            TGFish.getEventBus().publishEvent(event)
        # 触发美人鱼的馈赠小游戏
        if self.gameMode == config.MULTIPLE_MODE:
            player._miniMermaidStart(fishTypes, gunMultiple * gunX)            # 开始小游戏美人鱼的馈赠, 8101是美人鱼小游戏id
            # self._miniMermaidStart(player, fishTypes, gunMultiple * gunX)            # 开始小游戏美人鱼的馈赠, 8101是美人鱼小游戏id


    def dealSpecialFishFire(self, player, fishConf, fpMultiple, gunMultiple, gunX, catchMap):
        """
        处理特殊鱼死亡后变为武器新增的子弹数据
        """
        fId = catchMap["fId"]
        fishType = fishConf["fishType"]
        weaponId = fishConf.get("weaponId", 0)
        # 计算爆炸阶段次数
        stageCount = util.selectIdxByWeight(config.getWeaponStageCountConf(weaponId, self.gameMode)) + 1
        if stageCount > 0:
            powerList = []
            for _ in xrange(stageCount):
                wpConf = config.getWeaponConf(weaponId, mode=self.gameMode)
                powerList.append(wpConf["power"])
            # 通过catchMap["power"]告知客户端爆炸威力。客户端穿透鱼时需要递减威力（钻头鱼、电鳗采用该算法）
            if fishConf["type"] in config.DRILL_FISH_TYPE:  # 钻头鱼
                power = powerList[0]
                catchMap["power"] = int(power * 0.4)
                powerList = [catchMap["power"], power - catchMap["power"]]
            else:
                catchMap["power"] = powerList[0]
            catchMap["fishType"] = fishType
            catchMap["stageCount"] = stageCount
            # 增加子弹数据
            player.addFire(catchMap["fId"], weaponId, int(time.time()), fpMultiple,
                           power=powerList, gunMultiple=gunMultiple,
                           clientFire=False, fishType=fishType, gunX=gunX)
            ftlog.info("dealSpecialFishFire, userId =", player.userId,
                       "fId =", fId,
                       "fishType =", fishType,
                       "gunMultiple =", gunMultiple,
                       "gunX =", gunX,
                       "weaponId =", weaponId,
                       "stageCount =", stageCount,
                       "powerList =", powerList)
        return catchMap

    def _sendLed(self, player, gain, fpMultiple, gunMultiple, gunX):
        """
        发送全服通知
        :param player: 玩家
        :param gain: 获取奖励
        :param fpMultiple: 渔场倍率
        :return:
        """
        if self.runConfig.fishPool == 44499:
            return
        gunM = gunMultiple * gunX
        title = config.getMultiLangTextConf(self.runConfig.title, lang=player.lang)
        for gainMap in gain:
            if not self.fishMap.get(gainMap["fId"]):
                continue
            fishType = self.fishMap[gainMap["fId"]]["fishType"]
            fishConf = config.getFishConf(fishType, self.typeName, fpMultiple)
            fishName = config.getMultiLangTextConf(fishConf["name"], lang=player.lang)
            if ftlog.is_debug():
                ftlog.debug("fishName--->", fishName, fishConf)
            if fishConf["type"] in [2, 19, 8, 9] and gainMap and gainMap["itemId"] == CHIP_KINDID and (self.runConfig.fishPool == 44004 or self.runConfig.fishPool == 44005):
                # msg = u"恭喜玩家%s在%s成功捕获%s，获得%s金币" % \
                self._sendFormatLed(player, "ID_LED_CATCH_BOSS_DROP_CHIP", player.name, title, fishName,
                                    util.formatScore(gainMap["count"], lang=player.lang))
            elif fishConf["type"] in config.MULTIPLE_FISH_TYPE and fishConf["score"] >= 200 and (self.runConfig.fishPool == 44004 or self.runConfig.fishPool == 44005):
                multiple = gainMap["count"] / fishConf["score"] / fpMultiple
                # msg = u"恭喜%s击杀%s获得X%d倍，总计%d倍，共%s金币！", " % \
                totalMultiple = 2000 * multiple if self.runConfig.fishPool == 44004 else 5000 * multiple
                if multiple >= 20:
                    self._sendFormatLed(player, "ID_LED_CATCH_MULTIPLE_FISH", player.name, fishName, multiple, totalMultiple,
                                        util.formatScore(gainMap["count"], lang=player.lang))
            elif gainMap["itemId"] == COUPON_KINDID and gainMap["count"] >= 1000:    # 500:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下%.2f红包券" % \
                self._sendFormatLed(player, "ID_LED_CATCH_COUPON_FISH", player.name, title, gainMap["count"] * config.COUPON_DISPLAY_RATE)
            elif fishConf["type"] in config.TERROR_FISH_TYPE and gainMap["count"] / fpMultiple >= 1500 and self.runConfig.fishPool == 44004 or self.runConfig.fishPool == 44005:
                # msg = u"恭喜%s击杀%s总计%s分，获得%s金币！" % \
                self._sendFormatLed(player, "ID_LED_CATCH_TERROR_FISH", player.name, fishName,
                                    util.formatScore(gainMap["count"], lang=player.lang))
            elif gainMap["itemId"] == 4141:
                # msg = u"恭喜玩家%s在%s获得10元话费卡x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_4141", player.name, title, gainMap["count"])
            elif gainMap["itemId"] == 4142:
                # msg = u"恭喜玩家%s在%s获得30元话费卡x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_4142", player.name, title, gainMap["count"])
            elif gainMap["itemId"] == 4144:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元话费卡x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_4144", player.name, title, gainMap["count"])
            elif gainMap["itemId"] == 4233:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元京东卡x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_4233", player.name, title, gainMap["count"])
            elif gainMap["itemId"] == 2061:
                # msg = u"恭喜玩家%s在%s获得5元红包x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_2061", player.name, title, gainMap["count"])
            elif gainMap["itemId"] == 2050:
                # msg = u"恭喜玩家%s在%s凭借超凡的智慧和华丽的操作瞬间拿下100元红包x%d" % \
                self._sendFormatLed(player, "ID_LED_CATCH_FISH_DROP_2050", player.name, title, gainMap["count"])
            elif fishConf["type"] == 2 and gunM >= 10000:
                # msg = u"好运爆表！恭喜%s用%s倍炮击杀%s获得%s金币" % \
                self._sendFormatLed(player, "ID_LED_CATCH_BOSS_MULTIPL", player.name, gunM, fishName,
                                    util.formatScore(gainMap["count"], lang=player.lang))
            elif fishConf["type"] in config.MULTIPLE_FISH_TYPE and gainMap["itemId"] == CHIP_KINDID and gainMap["count"] >= 4000000 and gunM >= 10000:
                multiple = gainMap["count"] / fishConf["score"] / gunM
                totalMultiple = gainMap["count"] / gunM
                # msg = u"恭喜%s用%s倍炮击杀%s获得X%d倍，总计%d倍，共%s金币！" % \
                if multiple >= 4 and totalMultiple >= 200:
                    self._sendFormatLed(player, "ID_LED_CATCH_MULTIPLE_FISH_MULTIPL", player.name, gunM, fishName, multiple, totalMultiple,
                                        util.formatScore(gainMap["count"], lang=player.lang))
            elif fishConf["type"] in config.TERROR_FISH_TYPE and gainMap["itemId"] == CHIP_KINDID and gainMap["count"] >= 5000000 and gunM >= 10000:
                # msg = u"恭喜%s用%s倍炮击杀%s获得%s分，共%s金币" % \
                # totalValue = gainMap["count"] / gunM
                self._sendFormatLed(player, "ID_LED_CATCH_TERROR_FISH_VALUE", player.name, gunM,
                                fishName, util.formatScore(gainMap["count"], lang=player.lang))
            elif fishConf["type"] == 31 and gunM >= 10000:
                # msg = u"实力超群！恭喜%s用%s倍炮击杀%s获得%s金币，额外获得%s个%s！" % \
                self._sendFormatLed(player, "ID_LED_CATCH_SUPER_BOSS_MULTIPL", player.name, gunM, fishName,
                                    util.formatScore(gainMap["count"], lang=player.lang))

    def _sendFormatLed(self, player, mid, *args):
        """
        格式化Led消息并发送
        """
        try:
            msg = config.getMultiLangTextConf(mid, lang=player.lang).format(*args)
            user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=player.lang)
        except Exception as e:
            ftlog.error("_sendFormatLed error", player.userId, mid, args, e)

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
        player.end_skill_item()                     # 玩家离开渔场清理道具技能
        player.clear()
        from newfish.game import TGFish
        event = LeaveTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId, player.enterTime)
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
                # 收到玩家杀进程的请求
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
        msg.setResult("gameMode", self.gameMode)                        # 游戏模式(经典/千炮)
        player = self.getPlayer(userId)
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
        for _, expression in expressionConf.iteritems():                # 表情包
            expressions.append(expression)
        msg.setResult("expressions", expressions)                       # 表情
        if ftlog.is_debug():
            ftlog.debug("_sendTableInfo->msg =", msg)
        players = []
        for i in xrange(self.maxSeatN):
            if self.seats[i].userId != 0:
                info = self._getPlayerInfo(i + 1, player.clientId)
                info and players.append(info)
        msg.setResult("players", players)
        msg.setResult("groups", self._getTableGroups(userId))
        # 根据clientId判断是否屏蔽兑换提示.
        isIgnored = config.isClientIgnoredConf("exchangeTip", 1, player.clientId or util.getClientId(userId))
        msg.setResult("ignoreExchageTip", 1 if isIgnored else 0)
        GameMsg.sendMsg(msg, userId)
        self._afterSendTableInfo(userId)

    def _afterSendTableInfo(self, userId):
        """
        发送桌子信息之后
        """
        player = self.getPlayer(userId)
        if player and hasattr(player, "prizeWheel") and player.prizeWheel:  # 转盘
            player.prizeWheel.sendEnergyProgress(self.runConfig.fishPool, player.fpMultiple, self.roomId, 0)
        if player and player.compAct:                                       # 竞赛活动
            player.compAct.sendInspireInfo()
        player.gunEffectState(5)                                                            # 狂暴炮的状态和时间进度

    def _getTableGroups(self, userId):
        """
        获取渔场里所有鱼群信息
        """
        groups = []
        for group in self.normalFishGroups.itervalues():
            if group.isAlive(self._getNowTableTime()):
                groups.append(self._getGroupInfo(group))
        for group in self.callFishGroups.itervalues():
            if group.isAlive(self._getNowTableTime(), self) and group.isVisible(self, userId):
                groups.append(self._getGroupInfo(group))
        return groups

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
        if group.gameResolution:
            info["gameResolution"] = group.gameResolution
        diedFish = []
        HPFish = {}
        bufferFish = {}
        multipleFish = {}
        for fId in xrange(group.startFishId, group.startFishId + group.fishCount):
            # if fId not in self.fishMap:
            #     if ftlog.is_debug():
            #         ftlog.debug("_getGroupInfo", group.id, group.startFishId, group.fishCount, fId, self.fishMap.keys())
            #     continue
            if self.fishMap[fId]["alive"]:
                fishType = self.fishMap[fId]["fishType"]
                fishConf = config.getFishConf(fishType, self.typeName, self.runConfig.multiple)
                if fishConf["HP"] > 0:
                    HPFish[fId] = self.fishMap[fId]["HP"]
                if self.fishMap[fId]["buffer"]:
                    bufferFish[fId] = self.fishMap[fId]["buffer"]
                if self.fishMap[fId]["multiple"] > 1:
                    multipleFish[fId] = self.fishMap[fId]["multiple"]
            else:
                diedFish.append(fId)
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
        info["offline"] = p.offline                         # 是否离线(0:否 1:是)
        info["uLv"] = p.level
        _, expPct = util.getUserLevelExpData(p.userId, p.level, p.exp)
        info["expPct"] = expPct
        info["gLv"] = p.gunLevel                            # 炮的等级
        info["gLvNow"] = p.nowGunLevel                      # 现在炮的等级
        info["gunLevel"] = p.gunLv
        info["exp"] = p.exp
        info["skillSlots"] = p.getSkillSlotsInfo()          # 主技能槽的数据
        info["usingSkill"] = p.getUsingSkillInfo()          # 获取使用中的技能数据
        info["chip"] = p.chip
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
        info["playMode"] = p.playMode                       # 0金币模式 1金环
        info["itemSlots"] = p.getSkillItemInfo()            # 获取道具技能槽信息
        if self.gameMode == config.MULTIPLE_MODE:
            info["gunEffect"] = p.gunEffect.getGunEffectInfo(p.gunId)    # 获取其他玩家的狂暴炮效果
            info["tableMaxGunLevel"] = p.tableMaxGunLevel() if hasattr(p, "tableMaxGunLevel") else self.runConfig.maxGunLevel
        return info

    def _broadcastPlayerSit(self, userId, seatId):
        """广播玩家坐下"""
        msg = MsgPack()
        msg.setCmd("sit")
        msg.setResult("gameId", FISH_GAMEID)
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
        """技能装备:1、卸下:0"""
        skillId = msg.getParam("skillId")
        install = msg.getParam("install")
        ignoreFailMsg = msg.getParam("ignoreFailMsg", False)
        skillType = msg.getParam("skillType", 0)
        player = self.players[seatId - 1]
        ftlog.info("_skill_install", userId, skillId, install, player.skills)
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

    def broadcastSkillEffect(self, player, endTime, fishes, skillId, isSkillItem=False):
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
        if isSkillItem:
            msg.setResult("isSkillItem", 1)
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
        chatMsg = chatMsg[:80]                              # 80个字符长度限制
        needProcessChat = False
        if isFace == 0:                                     # 纯文本内容
            util.chatReport(userId, int(time.time()), 1, chatMsg, 0, 0)
            needProcessChat = True
        elif isFace == 4 and chatMsg not in ("string_liaotian1", "string_liaotian2", "string_liaotian3", "string_liaotian4", "string_liaotian5", "string_liaotian6"):
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
                price, self_charm, other_charm = smileConf["price"], smileConf["self_charm"], smileConf["other_charm"]
                trueDelta, playerChip = userchip.incrChip(userId, FISH_GAMEID, -abs(int(price)), 0, "EMOTICON_CONSUME",
                    self.roomId, player.clientId, roomId=self.roomId, tableId=self.tableId)
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
                        player.countLotteryConsumeCoin(price)
                    if lastCoin > self.runConfig.coinShortage > player.holdCoin:
                        coinShortageCount = gamedata.getGameAttrJson(player.userId, FISH_GAMEID, GameData.coinShortageCount, {})
                        coinShortageCount.setdefault(str(self.runConfig.fishPool), 0)
                        coinShortageCount[str(self.runConfig.fishPool)] += 1
                        gamedata.setGameAttr(player.userId, FISH_GAMEID, GameData.coinShortageCount, json.dumps(coinShortageCount))
                        if ftlog.is_debug():
                            ftlog.debug("doTableSmilies2", player.userId, lastCoin, self.runConfig.coinShortage, player.holdCoin, coinShortageCount)

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
        处理霜冻皮肤炮特性
        """
        if player.gunId == 1165:        # 霜冻特性，有几率冰冻鱼
            addTimeGroups = []
            frozenFishes = []
            duration = 3                # 冰冻时间
            if player.skinId == 1472:   # 雪人皮肤特性，冰冻时间加1s
                duration += 1
            endTime = time.time() + duration
            buffer = [5104, endTime, player.userId, 1, 1, duration, 0]
            for fId in fIds:
                isCoverFrozen, lastFrozenTime, frozenTime, frozenCount = self.checkCoverFrozen(fId, duration, endTime)
                if isCoverFrozen:
                    if frozenCount == 0: # 第一次冰冻5%概率
                        isCoverFrozen = True if random.randint(1, 10000) <= 500 else False
                    elif frozenCount == 1:
                        isCoverFrozen = True if random.randint(1, 10000) <= 300 else False
                    elif frozenCount == 2:
                        isCoverFrozen = True if random.randint(1, 10000) <= 100 else False
                    else:
                        isCoverFrozen = False

                if isCoverFrozen:
                    self.frozenFish(fId, buffer, lastFrozenTime, frozenTime, addTimeGroups)
                    frozenFishes.append(fId)

            if frozenFishes:            # 广播新处于冰冻状态的鱼
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
        """充值通知"""
        player = self.getPlayer(userId)
        player and player.dynamicOdds.refreshRechargeOdds()
        self._refreshUserData(msg, userId, seatId)

    def _takeGiftReward(self, msg, userId, seatId):
        """
        领取礼包奖励
        """
        pass

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
        """检查活动是否开启"""
        pass

    def _activity_all_btns(self, msg, userId, seatId):
        pass

    def _activity_read(self, msg, userId, seatId):
        pass

    def _activity_reward(self, msg, userId, seatId):
        pass

    def _activity_bonus(self, msg, userId, seatId):
        pass

    def addPrizeWheelEnergy(self, player, fId, fishConf, fpMultiple, gunX):
        """
        增加渔场轮盘能量
        """
        if player and hasattr(player, "prizeWheel") and player.prizeWheel:
            player.prizeWheel.catchFish(fId, fishConf, fpMultiple, gunX)

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

    def hasTideFishGroup(self):
        """
        是否存在鱼潮
        """
        return self.tideFishGroup and self.tideFishGroup.isAppear()

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
        if ft in self.fishCountMap:
            self.fishCountMap[ft] -= 1
            if self.fishCountMap[ft] < 0:
                self.fishCountMap[ft] = 0
                ftlog.info("refreshFishTypeCount, count error ! group =", group.desc(), "tableId =", self.tableId, "ft =", ft)
        else:
            ftlog.info("refreshFishTypeCount, type error ! group =", group.desc(), "tableId =", self.tableId, "ft =", ft)

    def _takeNewbie7DaysGift(self, msg, userId, seatId):
        """
        领取新手7日礼包奖励
        """
        from newfish.entity.gift import newbie_7days_gift
        player = self.getPlayer(userId)
        fireCount = player.fireCount if player and hasattr(player, "fireCount") else {}
        level = player.level if player and hasattr(player, "level") else 1
        clientId = msg.getParam("clientId")
        idx = msg.getParam("idx")
        newbie_7days_gift.takeGiftRewards(userId, clientId, idx, fireCount, level)

    def item_use(self, msg, userId, seatId):
        """
        使用道具技能卡
        """
        kindId = msg.getParam("kindId")
        fIds = msg.getParam("fIds") or []
        lockFid = msg.getParam("lockFid") or 0
        player = self.players[seatId - 1]
        self.lastActionTime = int(time.time())
        if player and hasattr(player, "skill_item"):
            player.skill_item[kindId].use_item(seatId, kindId, fIds, lockFid)

    def asyncEnterTableEvent(self, userId, seatId, reconnect):
        """
        异步发送进入房间事件
        """
        from newfish.game import TGFish
        event = EnterTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId, reconnect=reconnect)
        TGFish.getEventBus().publishEvent(event)

    def gun_effect_use(self, msg, userId, seatId):
        """
        使用皮肤炮的狂暴效果
        """
        player = self.players[seatId - 1]
        if player and hasattr(player, "gunEffect") and player.gunEffect:
            player.gunEffect.useEffect()

    def skip_newbie_guide(self, msg, userId, seatId):
        player = self.getPlayer(userId)
        if ftlog.is_debug():
            ftlog.debug("table_base.skip_newbie_guide IN",
                        "userId=", userId,
                        "seatId=", seatId,
                        "player=", player)
        if player:
            code, rewards = player.taskSystemUser.skipRedTask()
            if ftlog.is_debug():
                ftlog.debug("table_base.skip_newbie_guide get ret",
                            "code=", code,
                            "rewards=", rewards)
            if code == 0:
                allGuideIds = config.getPublic("allGuideIds", [])
                gamedata.setGameAttr(userId, FISH_GAMEID, GameData.userGuideStep, json.dumps(allGuideIds))
                bireport.reportGameEvent("BI_NFISH_GE_GUIDE_STEP", userId, FISH_GAMEID, 0,
                                         0, 0, 0, 0, 0, [], player.clientId)
                from newfish.entity.event import GuideChangeEvent
                from newfish.game import TGFish
                event = GuideChangeEvent(userId, FISH_GAMEID, True)
                TGFish.getEventBus().publishEvent(event)

            msg = MsgPack()
            msg.setCmd("skip_newbie_guide")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", userId)
            msg.setResult("seatId", seatId)
            msg.setResult("code", code)
            msg.setResult("rewards", rewards)
            router.sendToUser(msg, userId)

    def checkCoverFrozen(self, fId, duration, endTime):
        """
        检查能否覆盖鱼的冰冻数据
        @param fId:鱼Id
        @param duration:冰冻持续时间
        @param endTime:冰冻结束时间
        @return:是否覆盖, 被冰冻次数, 上次冰冻时长, 本次冰冻时长
        """
        buffers = self.fishMap[fId]["buffer"]
        isCoverFrozen = True
        frozenTime = duration
        lastFrozenTime = 0
        frozenCount = 0
        for lastBuffer in buffers:
            if lastBuffer[0] != 5104:
                continue
            lastFrozenTime = lastBuffer[5]
            frozenCount = lastBuffer[6]
            if endTime > lastBuffer[1]:  # 新冰冻到期时间大于旧冰冻到期时间，覆盖时间
                # 如果上一个冰冻状态未到期且小于新冰冻到期时间，则鱼在冰冻状态下再次冰冻，实际冰冻时间为间隔时间
                if time.time() < lastBuffer[1] < endTime:
                    frozenTime = round(endTime - lastBuffer[1], 3)
            else:
                isCoverFrozen = False
        return isCoverFrozen, lastFrozenTime, frozenTime, frozenCount

    def frozenFish(self, fId, buffer, lastFrozenTime, frozenTime, addTimeGroups):
        """
        把鱼冰冻住
        @param fId: 鱼Id
        @param buffer: 冰冻buffer数据
        @param lastFrozenTime: 上次冰冻时长
        @param frozenTime: 本次冰冻时长
        @param addTimeGroups: 已修改了冻结时长的鱼群
        """
        buffer[5] = round(lastFrozenTime + frozenTime, 3)
        self.setFishBuffer(fId, buffer)
        group = self.fishMap[fId]["group"]
        if group.startFishId not in addTimeGroups:
            addTimeGroups.append(group.startFishId)
            group.adjust(frozenTime)
            if self.superBossFishGroup:
                self.superBossFishGroup.frozen(fId, self.fishMap[fId]["fishType"], frozenTime)