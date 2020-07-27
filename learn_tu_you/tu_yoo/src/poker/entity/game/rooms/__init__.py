#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import freetime.util.log as ftlog
from poker.entity.game.const import BaseConst
from poker.entity.game.rooms.arena_match_room import TYArenaMatchRoom
from poker.entity.game.rooms.big_match_room import TYBigMatchRoom
from poker.entity.game.rooms.custom_room import TYCustomRoom
from poker.entity.game.rooms.club_room import TYClubRoom
from poker.entity.game.rooms.dtg_room import TYDTGRoom
from poker.entity.game.rooms.erdayi_match_room import TYErdayiMatchRoom
from poker.entity.game.rooms.group_match_room import TYGroupMatchRoom
from poker.entity.game.rooms.relaxation_match_room import TYRelaxationMatchRoom
from poker.entity.game.rooms.lts_room import TYLtsRoom
from poker.entity.game.rooms.mtt_room import TYMttRoom
from poker.entity.game.rooms.normal_room import TYNormalRoom
from poker.entity.game.rooms.queue_room import TYQueueRoom
from poker.entity.game.rooms.room_mixin import TYRoomMixin
from poker.entity.game.rooms.score_match_room import TYScoreMatchRoom
from poker.entity.game.rooms.sng_room import TYSngRoom
from poker.entity.game.rooms.vip_room import TYVipRoom
from poker.entity.game.rooms.hundreds_room import TYHundredsRoom
from poker.entity.game.rooms.chip_normal_room import TYChipNormalRoom
from poker.entity.game.rooms.pk_room import TYPkRoom
from poker.entity.game.rooms.quick_upgrade_match_room import TyQuickUpgradeMatchRoom
from poker.entity.game.rooms.queue_mixed_room import TYQueueMixedRoom
from poker.entity.game.rooms.common_arena_match_room import TyCommonArenaMatchRoom
from poker.entity.game.rooms.async_upgrade_hero_match import TyAsyncUpgradeHeroMatchRoom
from poker.entity.game.rooms.async_common_arena_match_room import TyAsyncCommonArenaMatchRoom


class TYRoomConst(BaseConst): pass


tyRoomConst = TYRoomConst()

tyRoomConst.ROOM_TYPE_NAME_NORMAL = 'normal'  # 普通非队列房间
tyRoomConst.ROOM_TYPE_NAME_QUEUE = 'queue'  # 队列房间
tyRoomConst.ROOM_TYPE_NAME_QUEUE_MIXED = 'queue_mixed_room' # 队列混房
tyRoomConst.ROOM_TYPE_NAME_VIP = 'vip'  # 贵宾室房间
tyRoomConst.ROOM_TYPE_NAME_LTS = 'lts'  # 限时积分赛房间
tyRoomConst.ROOM_TYPE_NAME_SNG = 'sng'  # S&G 比赛房间
tyRoomConst.ROOM_TYPE_NAME_MTT = 'mtt'  # MTT 比赛房间
tyRoomConst.ROOM_TYPE_NAME_HUNDREDS = 'hundreds'  # 百人房间
tyRoomConst.ROOM_TYPE_NAME_DTG = 'dtg'  # 打通关房间
tyRoomConst.ROOM_TYPE_NAME_CUSTOM = 'custom'  # 自建房间
tyRoomConst.ROOM_TYPE_NAME_CLUB = 'club'  # 俱乐部房间
tyRoomConst.ROOM_TYPE_NAME_SCORE_MATCH = 'score_match'  # 积分赛房间
tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH = 'big_match'  # 大比赛房间
tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH = 'arena_match'
tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH = 'group_match'
tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH = 'erdayi_match'
tyRoomConst.ROOM_TYPE_NAME_CHIP_NORMAL = 'chip_normal'
tyRoomConst.ROOM_TYPE_NAME_PK = 'pk'  # 好友pk
tyRoomConst.ROOM_TYPE_NAME_QUICK_UPGRADE_MATCH = 'quick_upgrade_match'  # 快速升级赛
tyRoomConst.ROOM_TYPE_NAME_COMMON_ARENA_MATCH = 'common_arena_match' # 通用Arena比赛
tyRoomConst.ROOM_TYPE_ASYNC_UPGRADE_HERO_MATCH = 'async_upgrade_hero_match' # 异步闯关赛
tyRoomConst.ROOM_TYPE_NAME_ASYNC_COMMON_ARENA_MATCH = 'async_common_arena_match' # 通用异步Arena比赛

'''
休闲赛(一天内某个时间段，任意打N局, minN<=N<=maxN)，且遇到过的玩家当天本比赛内将不能再组局,
比赛过程中，每局胜利或者和局，会得到配置的积分N-(chip.base)
排名规则：可由自己游戏实现
'''
tyRoomConst.ROOM_TYPE_NAME_RELAXATION_MATCH = 'relaxation_match'

tyRoomConst.ROOM_CLASS_DICT = {
    tyRoomConst.ROOM_TYPE_NAME_NORMAL: TYNormalRoom,
    tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH: TYBigMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH: TYArenaMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH: TYGroupMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH: TYErdayiMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_RELAXATION_MATCH: TYRelaxationMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_VIP: TYVipRoom,
    tyRoomConst.ROOM_TYPE_NAME_QUEUE: TYQueueRoom,
    tyRoomConst.ROOM_TYPE_NAME_SNG: TYSngRoom,
    tyRoomConst.ROOM_TYPE_NAME_MTT: TYMttRoom,
    tyRoomConst.ROOM_TYPE_NAME_LTS: TYLtsRoom,
    tyRoomConst.ROOM_TYPE_NAME_HUNDREDS: TYHundredsRoom,
    tyRoomConst.ROOM_TYPE_NAME_DTG: TYDTGRoom,
    tyRoomConst.ROOM_TYPE_NAME_CUSTOM: TYCustomRoom,
    tyRoomConst.ROOM_TYPE_NAME_CLUB: TYClubRoom,
    tyRoomConst.ROOM_TYPE_NAME_SCORE_MATCH: TYScoreMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_PK: TYPkRoom,
    tyRoomConst.ROOM_TYPE_NAME_CHIP_NORMAL: TYChipNormalRoom,
    tyRoomConst.ROOM_TYPE_NAME_QUICK_UPGRADE_MATCH: TyQuickUpgradeMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_QUEUE_MIXED: TYQueueMixedRoom,
    tyRoomConst.ROOM_TYPE_NAME_COMMON_ARENA_MATCH: TyCommonArenaMatchRoom,
    tyRoomConst.ROOM_TYPE_ASYNC_UPGRADE_HERO_MATCH: TyAsyncUpgradeHeroMatchRoom,
    tyRoomConst.ROOM_TYPE_NAME_ASYNC_COMMON_ARENA_MATCH: TyAsyncCommonArenaMatchRoom,
}


def getInstance(roomdefine):
    # ROOM的基本定义信息RoomDefine:
    # RoomDefine.parentId      int 父级房间ID, 当前为管理房间时, 必定为0 (管理房间, 可以理解为玩家队列控制器)
    # RoomDefine.roomId        int 当前房间ID
    # RoomDefine.gameId        int 游戏ID
    # RoomDefine.playId        int 玩法ID
    # RoomDefine.level         int 级别ID
    # RoomDefine.controlId     int 房间控制ID
    # RoomDefine.shadowId      int 影子ID
    # RoomDefine.configId      int 房间配置ID
    # RoomDefine.tableCount    int 房间中桌子的数量
    # RoomDefine.tableRoomIds  tuple 当房间为管理房间时, 下属的桌子实例房间的ID列表
    # RoomDefine.typeName      str 房间类型的名字
    # 实现方法依据给出的基本定义信息,返回创建房间实例,
    # 其必须是 poker.entity.game.rooms.room.TYRoom的子类
    '''工场设计模式，根据roomTypeName来创建不同类型的room对象
    Raise :
        KeyError : roomTypeName invalid
    '''
    try:
        roomTypeName = roomdefine.configure["typeName"]
        ftlog.debug("create room", "|roomId, roomType:", roomdefine.roomId, roomTypeName)
        roomClass = tyRoomConst.ROOM_CLASS_DICT[roomTypeName]
        if isinstance(roomClass, (list, tuple)):
            from poker.entity.configure import gdata
            roomClass = roomClass[0] if gdata.serverType() == gdata.SRV_TYPE_ROOM else roomClass[1]
        if not TYRoomMixin in roomClass.__bases__:
            roomClass.__bases__ += (TYRoomMixin,)                   # 添加父类
        return roomClass(roomdefine)                                # 获取房间的实例
    except:
        ftlog.info('create room error, please check bigRoomId:', roomdefine.bigRoomId, ' roomId:', roomdefine.roomId)
        raise