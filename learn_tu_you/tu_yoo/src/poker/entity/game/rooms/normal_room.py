#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
'''普通房间类
'''
from poker.entity.game.game import TYGame
from random import choice
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import daobase
from poker.entity.dao.lua_scripts import room_scripts
from poker.util import strutil



class TYNormalRoom(TYRoom):
    '''普通房间类'''

    def __init__(self, roomDefine):
        super(TYNormalRoom, self).__init__(roomDefine)

        # GT重启创建Room对象时清空牌桌评分历史数据
        daobase.executeTableCmd(self.roomId, 0, "DEL", self.getTableScoresKey(self.roomId))

    def getTableScoresKey(self, shadowRoomId):
        """获取桌子的评分"""
        return "ts:" + str(shadowRoomId)

    def doReloadConf(self, roomDefine):
        '''GT刷新配置时，如果桌子数变了需要清空桌子评分历史数据,
            此处桌子实例数量未改变，redis中也无需改变，换句话而言，不允许动态桌子'''
        # if self.roomDefine.tableCount != roomDefine.tableCount:
        #     daobase.executeTableCmd(self.roomId, 0, "ZREM", self.getTableScoresKey(self.roomId))

        super(TYNormalRoom, self).doReloadConf(roomDefine)

    def dispatchShadowRoomsForClient(self, clientVer):
        """
        客户端版本 更新的范围
        分发到影子桌子房间对于我客户端
        """
        dispatchConf = self.openShadowRoomIdsDispatch
        if not dispatchConf:
            return None
        allShadows = []
        for conf in dispatchConf:
            if clientVer >= conf["version"]["start"] \
                and clientVer < conf["version"]["end"]:
                for rid in range(conf["shadowRoomIds"]["start"], conf["shadowRoomIds"]["end"] + 1):
                    allShadows.append(rid)
                break
        return allShadows

    def getShadowRoomIdx(self, roomDefine, clientId, showHuafei):
        """
        获取影子房间的索引
        :param roomDefine:
        :param clientId:
        :param showHuafei:
        """
        _, clientVer, _ = strutil.parseClientId(clientId)
        if clientVer >= 3.785 and showHuafei or clientId.startswith("robot"):
            allShadows = self.dispatchShadowRoomsForClient(clientVer)
            if not allShadows:
                allShadows = self.openShadowRoomIds
        else:
            allShadows = self.shelterShadowRoomIds
        ftlog.debug("getShadowRoomIdx", 1, allShadows, clientVer)
        selectId = choice(allShadows)
        ftlog.debug("getShadowRoomIdx", clientId, selectId, clientVer)
        return selectId

    def getShadowRoomIdStrategy(self):
        """随机一个shadowRoomId"""
        return choice(self.roomDefine.shadowRoomIds)

    def doQuickStart(self, msg):
        '''
        Note:
            1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
            2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。
            3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
        '''
        assert self.roomId == msg.getParam("roomId")

        userId = msg.getParam("userId")
        gameId = msg.getParam("gameId")
        shadowRoomId = msg.getParam("shadowRoomId")
        tableId = msg.getParam("tableId")
        exceptTableId = msg.getParam("exceptTableId")
        clientId = msg.getParam("clientId")
        showHuafei = msg.getParam("showHuafei")
        ftlog.info(getMethodName(), "<<", "|userId, clientId, roomId, shadowRoomId, tableId:", userId, clientId,
                   self.roomId, shadowRoomId, tableId)
        ftlog.info(getMethodName(), self.roomDefine.shadowRoomIds)
        if tableId == 0:        # 服务器为玩家选择桌子并坐下
            # if gameId == 60:
            #     shadowRoomId = self.getShadowRoomIdx(self.roomDefine, clientId, showHuafei)
            # else:
            shadowRoomId = self.getShadowRoomIdStrategy()
            tableId = self.getBestTableId(userId, shadowRoomId, exceptTableId)
        else:                   # 玩家自选桌子坐下
            assert (isinstance(shadowRoomId, int) and gdata.roomIdDefineMap()[shadowRoomId].bigRoomId == self.roomDefine.bigRoomId)
            tableId = self.enterOneTable(userId, shadowRoomId, tableId)

        if not tableId:
            ftlog.error(getMethodName(), "getFreeTableId timeout", "|userId, roomId, tableId:", userId, self.roomId, tableId)
            return

        if ftlog.is_debug():
            ftlog.info(getMethodName(), "after choose table", "|userId, shadowRoomId, tableId:", userId, shadowRoomId, tableId)

        extParams = msg.getKey('params')
        self.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)

    def getBestTableId(self, userId, shadowRoomId, exceptTableId=None):
        """见getBestTableIdWithScore"""
        tableId, _ = self.getBestTableIdWithScore(userId, shadowRoomId, exceptTableId)

        return tableId

    def getBestTableIdWithScore(self, userId, shadowRoomId, exceptTableId=None):
        '''原子化从redis里获取和删除评分最高的桌子Id
        Return:
            0, 0: tableScores 队列为空， 所有桌子都在分配座位中
        '''
        def getBestTableIdFromRedis(shadowRoomId):
            '''从redis里取出并删除一个评分最高的牌桌
            '''
            tableId, tableScore = 0, 0
            datas = daobase.executeTableLua(shadowRoomId, 0, room_scripts.ALIAS_GET_BEST_TABLE_ID_LUA, 1,
                                            self.getTableScoresKey(shadowRoomId), 0)

            if datas and len(datas) == 2:
                tableId, tableScore = datas[0], datas[1]
                ftlog.info("getBestTableIdFromRedis <<|tableId, tableScore:", tableId, tableScore)
            return tableId, tableScore

        if ftlog.is_debug():
            ftlog.debug("<<", "|shadowRoomId, exceptTableId:", shadowRoomId, exceptTableId, caller=self)

        pigTables = []
        tableId = 0
        tableScore = 0
        for _ in xrange(5):     # 所有桌子有可能正在分配座位，如果取桌子失败，需要休眠后重试
            if gdata.roomIdDefineMap()[shadowRoomId].tableCount == 1:
                tableId = shadowRoomId * 10000 + 1
                tableScore = 100
            else:
                tableId, tableScore = getBestTableIdFromRedis(shadowRoomId)     # 从redis取一个牌桌

                # 该牌桌被客户端指定排除了，另外再取一个牌桌
                if exceptTableId and tableId and exceptTableId == tableId:
                    tableId1, tableScore1 = getBestTableIdFromRedis(shadowRoomId)

                    # 把之前从redis取出的牌桌加回redis
                    self._updateTableScore(shadowRoomId, tableScore, tableId, force=True)
                    tableId, tableScore = tableId1, tableScore1

            if ftlog.is_debug():
                ftlog.debug('getBestTableId shadowRoomId, tableId, tableScore=', shadowRoomId, tableId, tableScore)
            if tableId:
                if TYGame(self.gameId).isWaitPigTable(userId, self, tableId):
                    pigTables.append([shadowRoomId, tableScore, tableId])
                    tableId = 0
                    continue
                else:
                    break
            else:
                FTTasklet.getCurrentFTTasklet().sleepNb(0.2)
        if ftlog.is_debug():
            ftlog.debug('getBestTableId pigTables=', pigTables)
        if pigTables:
            for pig in pigTables:
                self._updateTableScore(pig[0], pig[1], pig[2], False)
        return tableId, tableScore

    def enterOneTable(self, userId, shadowRoomId, tableId):
        '''指定桌子坐下
        Returns
            False: 重试超过次数
        '''
        if ftlog.is_debug():
            ftlog.debug("<< |userId, roomId, shadowRoomId, tableId", userId, self.roomId, shadowRoomId, tableId,
                    caller=self)

        if gdata.roomIdDefineMap()[shadowRoomId].tableCount == 1:
            return tableId

        for _ in xrange(5):     # 这张桌子有可能正在分配座位，如果取桌子失败，需要休眠后重试
            result = daobase.executeTableCmd(shadowRoomId, 0, "ZREM", self.getTableScoresKey(shadowRoomId), tableId)    # ZREM key member删除元素
            if ftlog.is_debug():
                ftlog.debug("after ZREM tableId", "|userId, shadowRoomId, tableId, result:",
                            userId, shadowRoomId, tableId, result, caller=self)
            if result == 1:
                return tableId

            FTTasklet.getCurrentFTTasklet().sleepNb(1)

        return 0

    def _updateTableScore(self, shadowRoomId, tableScore, tableId, force=False):
        """更新桌子的积分"""
        rkey = self.getTableScoresKey(shadowRoomId)
        force = 1 if force else 0
        res = daobase.executeTableLua(shadowRoomId, tableId, room_scripts.ALIAS_UPDATE_TABLE_SCORE_LUA,
                        4, rkey, tableId, tableScore, force)
        if ftlog.is_debug():
            ftlog.debug('_updateTableScore->shadowRoomId, tableScore, tableId, force=', shadowRoomId, tableScore, tableId, force, res)
        return res

    def updateTableScore(self, tableScore, tableId, force=False):
        '''更新redis中的table score, TODO: 改成LUA原子化操作
        Args:
            force:
                True  强制往redis里添加或更新评分，只有玩家sit时做此操作
                False 表示只有redis有该牌桌评分时，才可以更新
        '''
        return self._updateTableScore(self.roomId, tableScore, tableId, force)
        # if force:
        #     result = daobase.executeTableCmd(self.roomId, 0, "ZADD", self.getTableScoresKey(self.roomId), tableScore, tableId)
        #     ftlog.debug("force ZADD tableId", "|roomId, tableId, result:", self.roomId, tableId, result,
        #                     caller=self)
        #     return
        #
        # result = daobase.executeTableCmd(self.roomId, 0, "ZSCORE", self.getTableScoresKey(self.roomId), tableId)
        # ftlog.debug("checkold ZSCORE tableId", "|roomId, tableId, result:", self.roomId, tableId, result,
        #                 caller=self)
        # if result == None:
        #     result = daobase.executeTableCmd(self.roomId, 0, "ZADD", self.getTableScoresKey(self.roomId), tableScore, tableId)
        #     ftlog.debug("after ZADD tableId", "|roomId, tableId, result:", self.roomId, tableId, result,
        #                     caller=self)