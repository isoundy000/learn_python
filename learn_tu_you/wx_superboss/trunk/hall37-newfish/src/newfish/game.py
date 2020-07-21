# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from poker.entity.game.game import TYGame
from poker.entity.game.rooms import tyRoomConst
from poker.entity.configure import gdata
from newfish.entity import account, config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.lotterypool.normal_lottery_pool import NormalLotteryPool    # 普通渔场房间金币彩池
from newfish.entity.lotterypool.ring_lottery_pool import RingLotteryPool        # 普通渔场房间金环彩池
from newfish.room.normal_room import FishNormalRoom     # 捕鱼普通房间
from newfish.room.newbie_room import FishNewbieRoom     # 捕鱼新手房间
from newfish.room.friend_room import FishFriendRoom     # 捕鱼好友模式房间
from newfish.room.time_match_room import FishTimeMatchRoom  # 捕鱼回馈赛房间
from newfish.room.fight_room import FishFightRoom       # 捕鱼渔友竞技房间
from newfish.room.robbery_room import FishRobberyRoom   # 捕鱼招财模式房间
from newfish.room.time_point_match_room import FishTimePointMatchRoom   # 回馈赛积分房间
from newfish.room.grand_prix_room import FishGrandPrixRoom  # 大奖赛模式房间
from newfish.room.poseidon_room import FishPoseidonRoom     # 捕鱼海皇来袭房间
from newfish.room.multiple_room import FishMultipleRoom     # 捕鱼千炮模式房间



class TGFish(TYGame):
    """
    欢乐捕鱼
    """
    def initGameBefore(self):
        """
        此方法由系统进行调用
        游戏初始化的预处理
        """
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_NORMAL] = FishNormalRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_FRIEND] = FishFriendRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_TIME_MATCH] = FishTimeMatchRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_FIGHT] = FishFightRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_ROBBERY] = FishRobberyRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_NEWBIE] = FishNewbieRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_TIME_POINT_MATCH] = FishTimePointMatchRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_GRAND_PRIX] = FishGrandPrixRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_POSEIDON] = FishPoseidonRoom
        tyRoomConst.ROOM_CLASS_DICT[config.FISH_MULTIPLE] = FishMultipleRoom

    def initGame(self):
        """
        此方法由系统进行调用
        游戏自己初始化业务逻辑模块, 例如: 初始化配置, 建立事件中心等
        执行的时序为：首先调用所有游戏的 initGameBefore()
                    再调用所有游戏的 initGame()
                    最后调用所有游戏的 initGameAfter()
        """
        from newfish.entity import (util, checkin, module_tip,
                                    drop_system, user_system,
                                    store, item, share_system, treasure_system, level_funds, returner_mission,
                                    mail_system)
        from newfish.entity.gift import daily_gift
        from newfish.entity.gift import gift_system
        from newfish.entity.ranking import ranking_system
        from newfish.entity.chest import chest_system
        from newfish.entity.skill import skill_system
        from newfish.entity.quest import quest_system
        from newfish.entity.achievement import achievement_system
        from newfish.entity.honor import honor_system
        from newfish.entity.gun import gun_system
        from newfish.entity.fishactivity import (fish_activity_system, competition_activity,
                                                 canned_fish_factory)
        from newfish.entity import invite_system, fish_notice_system
        from newfish.entity.lotterypool import robbery_lottery_pool
        from newfish.entity.lotterypool import poseidon_lottery_pool
        serverType = gdata.serverType()
        serverNum = gdata.serverNum()
        if serverType == gdata.SRV_TYPE_ROOM or serverType == gdata.SRV_TYPE_TABLE:
            if str(FISH_GAMEID) not in serverNum[:6]:
                return
        # 注册配置事件监听
        config.registerConfigEvent()
        # 配置初始化
        config.initConfig()
        # 用户系统初始化
        user_system.initialize()
        # 引导提示系统初始化
        module_tip.initialize()
        # 宝箱系统初始化
        chest_system.initialize()
        # 技能系统初始化
        skill_system.initialize()
        # 任务系统初始化
        quest_system.initialize()
        # 掉落系统初始化
        drop_system.initialize()
        # 每日签到初始化
        checkin.initialize()
        # 礼包系统初始化
        gift_system.initialize()
        # 每日礼包
        daily_gift.initialize()
        # 活动系统初始化
        fish_activity_system.initialize()
        # 成就系统初始化
        achievement_system.initialize()
        # 称号系统初始化
        honor_system.initialize()
        # 火炮系统初始化
        gun_system.initialize()
        # 招财模式奖池初始化
        robbery_lottery_pool.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 海皇来袭奖池初始化
        poseidon_lottery_pool.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 排行榜系统初始化
        ranking_system.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 工具系统初始化
        util.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 商店初始化
        store.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 道具初始化
        item.initialize()
        # 邀请系统初始化
        invite_system.initialize()
        # 分享系统初始化
        share_system.initialize()
        # 公告系统初始化
        fish_notice_system.initialize()
        # 宝藏系统初始化
        treasure_system.initialize()
        # 竞赛活动系统初始化
        competition_activity.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 回归豪礼初始化
        returner_mission.initialize()
        if serverType == gdata.SRV_TYPE_UTIL:
            from newfish.entity.match_record import MatchRecord
            # 比赛记录初始化
            MatchRecord.initialize(self.getEventBus())
        if serverType == gdata.SRV_TYPE_ROBOT:
            from newfish.robot import robot
            from newfish.robot.robot import FishRobotManager
            self._robotmgr = FishRobotManager()
            # 机器人系统初始化
            robot.initialize()
        if serverType == gdata.SRV_TYPE_CENTER:
            from newfish.entity.lotterypool import grand_prize_pool
            grand_prize_pool.initialize()
        from newfish.entity import piggy_bank, level_rewards, items_monitor
        # 存钱罐
        piggy_bank.initialize()
        # 等级奖励
        level_rewards.initialize()
        # 道具监控
        items_monitor.initialize()
        # 鱼罐厂初始化
        canned_fish_factory.initialize(serverType == gdata.SRV_TYPE_CENTER)
        # 成长基金
        level_funds.initialize()
        # 回归豪礼
        returner_mission.initialize()
        # 邮件初始化
        mail_system.initialize()

    def initGameAfter(self):
        """
        此方法由系统进行调用
        游戏初始化的后处理
        """
        serverType = gdata.serverType()
        if serverType == gdata.SRV_TYPE_TABLE:
            roomIds = gdata.srvIdRoomIdListMap().get(gdata.serverId(), None)
            if roomIds:
                from freetime.core.timer import FTLoopTimer
                from newfish.servers.room.rpc import room_remote
                allRooms = gdata.roomIdDefineMap()
                for roomId in roomIds:
                    ctrlRoomId = allRooms[roomId].parentId
                    tableCount = allRooms[roomId].tableCount
                    # 目前GR、GT是同时启动，GT启动完成时，GR不一定启动完成，所以暂时延后调用
                    FTLoopTimer(3, 0, room_remote.initializedGT, ctrlRoomId, roomId, tableCount).start()

    def gameId(self):
        """
        取得当前游戏的GAMEID, int值
        """
        return FISH_GAMEID

    def newTable(self, room, tableId):
        """
        此方法由系统进行调用
        更具给出的房间的基本定义信息, 创建一个TYTable的实例
        其必须是 poker.entity.game.table.TYTable的子类
        room 桌子所属的房间的TYRoom实例
        tableId 新桌子实例的ID
        """
        typeName = room.roomConf.get("typeName")
        if typeName in (config.FISH_NORMAL,
                        config.FISH_FRIEND,
                        config.FISH_TIME_MATCH,
                        config.FISH_FIGHT,
                        config.FISH_ROBBERY,
                        config.FISH_NEWBIE,
                        config.FISH_TIME_POINT_MATCH,
                        config.FISH_GRAND_PRIX,
                        config.FISH_POSEIDON,
                        config.FISH_MULTIPLE):
            lotteryPool = hasattr(room, "lotteryPool")
            ringLotteryPool = hasattr(room, "lotteryPool")
            if not lotteryPool:
                room.lotteryPool = NormalLotteryPool(room)
            if not ringLotteryPool:
                room.ringLotteryPool = RingLotteryPool(room)
            table = room.newTable(tableId)
            return table

    def getInitDataKeys(self):
        """
        取得游戏数据初始化的字段列表
        """
        return account.getInitDataKeys()

    def getInitDataValues(self):
        """
        取得游戏数据初始化的字段缺省值列表
        """
        return account.getInitDataValues()

    def getGameInfo(self, userId, clientId):
        """
        取得当前用户的游戏账户信息dict
        """
        return account.getGameInfo(userId, clientId)

    def getDaShiFen(self, userId, clientId):
        """
        取得当前用户的游戏账户的大师分信息
        """
        return account.getDaShiFen(userId, clientId)

    def createGameData(self, userId, gameId):
        """
        初始化该游戏的所有的相关游戏数据
        包括: 主游戏数据gamedata, 道具item, 勋章medal等
        返回主数据的键值和值列表
        """
        return account.createGameData(userId, gameId)

    def loginGame(self, userId, gameId, clientId, iscreate, isdayfirst):
        """
        用户登录一个游戏, 游戏自己做一些其他的业务或数据处理
        """
        return account.loginGame(userId, gameId, clientId, iscreate, isdayfirst)


TGFish = TGFish()


def getInstance():
    """
    获取TGFish单例
    """
    return TGFish
