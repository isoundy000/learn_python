# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from freetime.util import log as ftlog
from newfish.servers.util.rpc import table_remote, user_rpc

_DEBUG = 0


class ChangeDetail(object):
    def __init__(self, eventId, eventParam):
        self.eventId = eventId
        self.eventParam = eventParam
        self.delta = 0


class UserItem(object):
    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.gainDetail = {}
        self.consumeDetail = {}

    @classmethod
    def getEventkey(cls, eventId, eventParam):
        return "%s::%s" % (eventId, str(eventParam))

    @classmethod
    def splitEventkey(cls, key):
        eventId, eventParam = key.split("::")
        return eventId, int(eventParam)

    def addChange(self, delta, eventId, eventParam):
        """添加或者减少"""
        self.count += delta
        key = self.getEventkey(eventId, eventParam)
        if delta >= 0:
            detail = self.gainDetail
        else:
            detail = self.consumeDetail
        if key not in detail:
            detail[key] = ChangeDetail(eventId, eventParam)

        detail[key].delta += delta


class EconomicData(object):
    """
    渔场内资产缓存数据
    """
    def __init__(self, player, table):
        self.player = player
        self.userId = player.userId
        self.clientId = player.clientId
        self.table = table
        self.loadData()
    
    def loadData(self):
        """加载缓存数据"""
        self.itemMap = {}
        ret = table_remote.getUserEconomicData(self.userId, self.table.tableId)
        for k, v in ret.iteritems():
            self.itemMap[k] = UserItem(k, v)
        if _DEBUG:
            ftlog.info("EconomicData load:|", self.userId, "|", ret)

    def abstractItems(self):
        """抽象道具"""
        ret = []
        for k, v in self.itemMap.iteritems():
            ret.append({"name": k, "count": v.count})
        return ret

    def addGain(self, gain, eventId, eventParam):
        """添加资产"""
        if _DEBUG:
            ftlog.info("EconomicData addGain:|", gain, "|", eventId, "|", eventParam, "|", self.userId)
        ud = []
        gd = []
        items = []

        for item in gain:
            count = item["count"]
            assetKindId = item["name"]
            final = self.itemChanged(assetKindId, int(count), eventId, eventParam)
            if assetKindId == "tableChip":
                ud.append({"name": "tableChip", "count": final})
            else:
                items.append({"name": assetKindId, "count": final})

        changed = {}
        if ud:
            changed["ud"] = ud
        if gd:
            changed["gd"] = gd
        if items:
            changed["items"] = items
        return changed

    def consumeAssets(self, assets, eventId, eventParam, opMode=0):
        """消耗资产"""
        ud = []
        gd = []
        items = []

        for item in assets:
            count = item["count"]
            assetKindId = item["name"]
            delta, final = self.consumeItem(assetKindId, count, eventId, eventParam, opMode)
            if delta != 0:
                if assetKindId == "tableChip":
                    ud.append({"name": "tableChip", "count": final})
                else:
                    items.append({"name": assetKindId, "count": final})

        changed = {}
        if ud:
            changed["ud"] = ud
        if gd:
            changed["gd"] = gd
        if items:
            changed["items"] = items
        return changed

    def consumeItem(self, kindId, count, eventId, eventParam, opMode):  # opMode 0: 不操作  1: 清零
        """消耗道具"""
        delta = 0
        final = 0
        if kindId not in self.itemMap:
            delta = 0
        else:
            userItem = self.itemMap[kindId]
            if userItem.count < count:
                if opMode == 1:
                    delta = userItem.count
                    final = 0
                else:
                    delta = 0
                    final = userItem.count
            else:
                delta = count
                final = userItem.count - count
        if delta != 0:
            self.itemChanged(kindId, -delta, eventId, eventParam)
            if _DEBUG:
                ftlog.info("EconomicData consumeItem:|", kindId, "|", count, "|", eventId, "|", eventParam, "|", self.userId)

        return delta, final

    # 增加或者减少已经存在的
    def itemChanged(self, kindId, delta, eventId, eventParam):
        if kindId not in self.itemMap:
            assert (delta >= 0)
            self.itemMap[kindId] = UserItem(kindId, 0)
        self.itemMap[kindId].addChange(delta, eventId, eventParam)
        return self.itemMap[kindId].count

    def getItemCount(self, kindId):
        ret = 0
        if kindId in self.itemMap:
            ret = self.itemMap[kindId].count
        return ret

    @property
    def allChip(self):
        return user_rpc.getUserChipAll(self.userId)

    @property
    def chip(self):
        return user_rpc.getUserChip(self.userId)

    @property
    def tableChip(self):
        """桌子的金币"""
        return self.getItemCount("tableChip")

    @property
    def bulletChip(self):
        """子弹金币"""
        return self.getItemCount("bulletChip")

    def dumpData(self, specifiedKindId=None):
        """添加或者增加缓存资产到身上"""
        gainDetail = self._dumpData("gain", specifiedKindId)
        consumeDetail = self._dumpData("consume", specifiedKindId)
        if gainDetail or consumeDetail:
            table_remote.dumpEconomicData(self.userId, gainDetail, consumeDetail, self.table.roomId, self.table.tableId, self.clientId)

    def _dumpData(self, dtype, specifiedKindId=None):
        """序列化数据 specifiedKindId具体道具"""
        eventMap = {}
        for k, v in self.itemMap.iteritems():
            kindId = k
            if specifiedKindId:
                if kindId != specifiedKindId:
                    continue
            if dtype == "gain":
                changeDetail = v.gainDetail
            else:
                changeDetail = v.consumeDetail
            for chg in changeDetail.values():
                key = UserItem.getEventkey(chg.eventId, chg.eventParam)
                if key not in eventMap:
                    eventMap[key] = {}
                if kindId not in eventMap[key]:
                    eventMap[key][kindId] = 0
                eventMap[key][kindId] += chg.delta
        detailList = []
        for k, v in eventMap.iteritems():
            eventId, eventParam = UserItem.splitEventkey(k)
            gain = []
            for kindId, delta in v.iteritems():
                gain.append({"name": kindId, "count": delta})
            detailList.append([self.userId, gain, eventId, eventParam])
        if _DEBUG:
            ftlog.info("EconomicData dumpData:|", specifiedKindId, "|", detailList, "|", self.userId)
        return detailList

    def refreshChip(self):
        pass
        # del self.itemMap["user:chip"]
        # chip = user_rpc.getTableChip(self.userId, self.table.tableId)
        # self.itemMap["user:chip"] = UserItem("user:chip", chip)
        # ftlog.info("EconomicData refreshChip:|", self.abstractItems(), "|", self.userId)

    def refreshAllData(self):
        """刷新所有金币"""
        self.dumpData()         # 计算
        self.loadData()         # 重新加载

    def chgBulletChip(self, count):
        """改变子弹缓存金币"""
        if "bulletChip" not in self.itemMap:
            assert (count >= 0)
            self.itemMap["bulletChip"] = UserItem("bulletChip", 0)
        self.itemMap["bulletChip"].count += count

    def chgTableChip(self, count):
        """改变桌子缓存金币"""
        if "tableChip" not in self.itemMap:
            assert (count >= 0)
            self.itemMap["tableChip"] = UserItem("tableChip", 0)
        self.itemMap["tableChip"].count += count