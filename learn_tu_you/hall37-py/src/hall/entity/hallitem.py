#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2


itemSystem = TYItemSystem()



class TYHallItemBase(TYItem):

    def __init__(self, itemKind, itemId):
        super(TYHallItemBase, self).__init__(itemKind, itemId)

    def visibleInBag(self, timestamp):
        """在背包中是否展示"""
        if (self.needRemoveFromBag(timestamp) or (self.isDied(timestamp) and self.itemKind.findActionByName('repair') is None)):
            return False
        return True



class TYChestItem(TYHallItemBase):
    '''
    捕鱼定时宝箱类道具，到时后可以打开获得东西
    '''

    def __init__(self, itemKind, itemId):
        super(TYChestItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYChestItemKind))
        self.chestId = 0
        self.order = -1
        self.beginTime = 0
        self.totalTime = 0
        self.state = 0

    def _decodeFromItemData(self, itemData):
        self.chestId = itemData.chestId
        self.order = itemData.order
        self.beginTime = itemData.beginTime
        self.totalTime = itemData.totalTime
        self.state = itemData.state

    def _encodeToItemData(self, itemData):
        itemData.chestId = self.chestId
        itemData.order = self.order
        itemData.beginTime = self.beginTime
        itemData.totalTime = self.totalTime
        itemData.state = self.state