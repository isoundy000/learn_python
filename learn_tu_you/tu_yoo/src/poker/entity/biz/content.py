# -*- coding=utf-8
'''
Created on 2015年6月1日

@author: zhaojiangang
'''

import random
from sre_compile import isstring

import freetime.util.log as ftlog
from poker.entity.biz.confobj import TYConfable, TYConfableRegister
from poker.entity.biz.exceptions import TYBizConfException


class TYContentItem(object):
    def __init__(self, assetKindId, count):
        self.assetKindId = assetKindId
        self.count = count

    @classmethod
    def decodeFromDict(cls, d):
        assetKindId = d.get('itemId')
        count = d.get('count')
        if not isstring(assetKindId):
            raise TYBizConfException(d, 'TYContentItem.itemId must be valid string')
        if not isinstance(count, (int, float)) or count < 0:
            raise TYBizConfException(d, 'TYContentItem.count must be int or float >= 0')
        return TYContentItem(assetKindId, count)

    @classmethod
    def decodeList(cls, l):
        ret = []
        for d in l:
            ret.append(cls.decodeFromDict(d))
        return ret

    @classmethod
    def encodeList(cls, l):
        ret = []
        for c in l:
            ret.append(c.toDict())
        return ret

    def toDict(self):
        return {'itemId': self.assetKindId, 'count': self.count}


class TYContent(TYConfable):
    def __init__(self):
        self.desc = ''

    def getItems(self):
        '''
        @return: list<TYContentItem>
        '''
        raise NotImplemented()

    def decodeFromDict(self, d):
        self.desc = d.get('desc', '')
        self._decodeFromDictImpl(d)
        return self

    def _decodeFromDictImpl(self, d):
        return self


class TYEmptyContent(TYContent):
    TYPE_ID = 'EmptyContent'

    def __init__(self):
        super(TYEmptyContent, self).__init__()

    def getItems(self):
        return []


class TYContentItemGenerator(object):
    @classmethod
    def make(cls, assetKindId, start, stop, step):
        assert (stop is None or stop >= start)
        if stop is None or stop == start:
            return TYContentItemGeneratorFixed(assetKindId, start)
        return TYContentItemGeneratorRange(assetKindId, start, stop, step)

    def __init__(self, assetKindId):
        self.assetKindId = assetKindId

    def generate(self):
        raise NotImplemented()

    @classmethod
    def decodeFromDict(cls, d):
        assetKindId = d.get('itemId')
        count = d.get('count')
        if not isstring(assetKindId):
            raise TYBizConfException(d, 'TYFixedContent.item.itemId must be valid string')
        if count is not None:
            return cls.make(assetKindId, count, count, 1)
        else:
            start = d.get('start', None)
            stop = d.get('stop', None)
            step = d.get('step', None)
            if not isinstance(start, int):
                raise TYBizConfException(d, 'item.start must be int')
            if not isinstance(stop, int):
                raise TYBizConfException(d, 'item.stop must be int')
            if step is not None and (not isinstance(step, int) or step <= 0):
                raise TYBizConfException(d, 'item.step must be int > 0')
            return cls.make(assetKindId, start, stop, step)

    @classmethod
    def decodeList(cls, l):
        ret = []
        for d in l:
            ret.append(cls.decodeFromDict(d))
        return ret


class TYContentItemGeneratorFixed(TYContentItemGenerator):
    def __init__(self, assetKindId, count):
        super(TYContentItemGeneratorFixed, self).__init__(assetKindId)
        self._item = TYContentItem(assetKindId, count)

    def generateMin(self):
        return self._item

    def generate(self):
        return self._item


class TYContentItemGeneratorRange(TYContentItemGenerator):
    def __init__(self, assetKindId, start, stop, step=1):
        assert (stop > start)
        assert (step is None or step > 0)
        super(TYContentItemGeneratorRange, self).__init__(assetKindId)
        self._start = start
        self._stop = stop
        self._step = step

    def generateMin(self):
        return TYContentItem(self.assetKindId, self._start)

    def generate(self):
        count = None
        if self._step:
            count = random.randrange(self._start, self._stop + 1, self._step)
        else:
            count = random.randint(self._start, self._stop)
        return TYContentItem(self.assetKindId, count)


class TYFixedContent(TYContent):
    TYPE_ID = 'FixedContent'

    def __init__(self):
        super(TYFixedContent, self).__init__()
        self._generators = []

    def addItem(self, assetKindId, start, stop=None, step=None):
        self._generators.append(TYContentItemGenerator.make(assetKindId, start, stop, step))

    def getMinItems(self):
        items = []
        for generator in self._generators:
            items.append(generator.generateMin())
        return items

    def getItems(self):
        items = []
        for generator in self._generators:
            items.append(generator.generate())
        return items

    def _decodeFromDictImpl(self, d):
        items = d.get('items')
        if not isinstance(items, list):
            raise TYBizConfException(d, 'TYFixedContent.items must be list')

        for item in items:
            self._generators.append(TYContentItemGenerator.decodeFromDict(item))
        return self


class TYRandomContent(TYContent):
    TYPE_ID = 'RandomContent'
    # self._contents索引含义
    QUANTILE_L = 0
    QUANTILE_R = 1
    CONTENT = 2
    HIT_OPENTIMES = 3
    # self._newerContents索引含义
    INTERVENTION_WEIGHT = 0
    INTERVENTION_CONTENT = 1
    INTERVENTION_START = 2
    INTERVENTION_STOP = 3
    INTERVENTION_TEMPLATEID = 4

    def __init__(self):
        super(TYRandomContent, self).__init__()
        self._contents = []
        self._total = 0
        self._newerIntervention = 0
        self._newerContents = []

    def _addNewerContent(self, weight, content, start=-1, stop=-1, newerInterventionTemplateId=-1):
        assert (weight >= 0)
        assert (isinstance(content, TYContent))
        self._newerContents.append((weight, content, start, stop, newerInterventionTemplateId))

    def _selectNewerContent(self, itemKindTotalOpenTimes):
        '''
        选择新手奖励内容，找不到新手奖励模板时，认为不对该打开次数进行概率干预
        '''
        totalWeights = {}
        for content in self._newerContents:
            if content[self.INTERVENTION_START] <= itemKindTotalOpenTimes <= content[self.INTERVENTION_STOP]:
                newerInterventionTemplateId = content[self.INTERVENTION_TEMPLATEID]
                totalWeights[newerInterventionTemplateId] = totalWeights.setdefault(
                    newerInterventionTemplateId, 0) + content[self.INTERVENTION_WEIGHT]
        if totalWeights:
            choiceTemplateId = random.choice(totalWeights.keys())
            totalWeight = totalWeights[choiceTemplateId]
            r_ = random.randint(0, totalWeight - 1)
            startWeight = 0
            stopWeight = 0
            for content in self._newerContents:
                if (content[self.INTERVENTION_START] <= itemKindTotalOpenTimes <= content[self.INTERVENTION_STOP] and
                            content[self.INTERVENTION_TEMPLATEID] == choiceTemplateId):
                    stopWeight = startWeight + content[self.INTERVENTION_WEIGHT]
                    if startWeight <= r_ < stopWeight:
                        return content[self.INTERVENTION_CONTENT]
                    startWeight = stopWeight
        return None

    def addContent(self, weight, content, hitOpenTimes=-1):
        assert (weight >= 0)
        assert (isinstance(content, TYContent))
        self._contents.append((self._total, self._total + weight, content, hitOpenTimes))
        self._total += weight

    def getItems(self):
        content = self._selectContent()
        return content.getItems() if content else []

    def getItemsWithOpenTimes(self, cycleOpenTimes=-1, itemKindTotalOpenTimes=-1):
        ''' cycleOpenTimes:重置周期（采用取模假重置）, itemKindTotalOpenTimes（该类型打开的总次数记录在redis） '''
        content = self._selectContent(cycleOpenTimes, itemKindTotalOpenTimes)
        return content.getItems() if content else []

    @staticmethod
    def _calculateCurOpenTimes(itemKindTotalOpenTimes, cycleOpenTimes):
        if itemKindTotalOpenTimes <= 0 or cycleOpenTimes <= 0:
            return 0
        curOpenTimes = itemKindTotalOpenTimes % cycleOpenTimes
        if curOpenTimes == 0:
            return cycleOpenTimes
        return curOpenTimes

    def _selectContent(self, cycleOpenTimes=-1, itemKindTotalOpenTimes=-1):
        try:
            if itemKindTotalOpenTimes > 0:
                if self._newerIntervention:
                    # 新手干预
                    contentSelected = self._selectNewerContent(itemKindTotalOpenTimes)
                    if contentSelected:
                        return contentSelected
                elif cycleOpenTimes > 0:
                    # 必中
                    curOpenTimes = self._calculateCurOpenTimes(itemKindTotalOpenTimes, cycleOpenTimes)
                    for content in self._contents:
                        if curOpenTimes == content[self.HIT_OPENTIMES]:
                            return content[self.CONTENT]
        except Exception as e:
            ftlog.error('TYRandomContent._selectContent error Exception=', e)

        r = random.randint(0, self._total - 1)
        for content in self._contents:
            if content[self.QUANTILE_L] <= r < content[self.QUANTILE_R]:
                return content[self.CONTENT]
        return None

    def _decodeFromDictImpl(self, d):
        randoms = d.get('randoms')
        if not isinstance(randoms, list):
            raise TYBizConfException(d, 'TYRandomContent.randoms must be list')
        newerIntervention = d.get('newerIntervention', 0)
        if newerIntervention not in (0, 1):
            raise TYBizConfException(d, 'TYRandomContent.newerIntervention must be int in (0,1)')
        self._newerIntervention = newerIntervention
        if not newerIntervention:
            for part in randoms:
                weight = part.get('weight')
                if not isinstance(weight, int):
                    raise TYBizConfException(d, 'randoms.item.weight must be int')

                hitOpenTimes = part.get('hitOpenTimes', -1)
                if not isinstance(hitOpenTimes, int):
                    raise TYBizConfException(d, 'randoms.item.hitOpenTimes must be int')

                subContent = TYContentRegister.decodeFromDict(part)
                self.addContent(weight, subContent, hitOpenTimes)
        else:
            for part in randoms:
                weight = part.get('weight')
                if not isinstance(weight, int):
                    raise TYBizConfException(d, 'randoms.item.weight must be int')

                hitOpenTimes = part.get('hitOpenTimes', -1)
                if not isinstance(hitOpenTimes, int):
                    raise TYBizConfException(d, 'randoms.item.hitOpenTimes must be int')

                newerInterventionTimes = part.get('newerInterventionTimes', {})
                if not isinstance(newerInterventionTimes, dict):
                    raise TYBizConfException(d,
                                             'randoms.item.newerInterventionTimes must be {"start": int,"stop": int}')

                newerInterventionTemplateId = part.get('newerInterventionTemplateId', 0)
                if not isinstance(newerInterventionTemplateId, int):
                    raise TYBizConfException(d, 'randoms.item.newerInterventionTemplateId must be int')

                if not newerInterventionTemplateId or not newerInterventionTimes:
                    subContent = TYContentRegister.decodeFromDict(part)
                    self.addContent(weight, subContent, hitOpenTimes)
                else:
                    start = newerInterventionTimes.get('start', -1)
                    if not isinstance(start, int) or start <= 0:
                        raise TYBizConfException(d, 'randoms.item.newerInterventionTimes.start must be int and >0')
                    stop = newerInterventionTimes.get('stop', -1)
                    if not isinstance(stop, int) or stop < start:
                        raise TYBizConfException(d, 'randoms.item.newerInterventionTimes.stop must be int and >= start')
                    subContent = TYContentRegister.decodeFromDict(part)
                    self._addNewerContent(weight, subContent, start, stop, newerInterventionTemplateId)
            if len(self._contents) == 0:
                raise TYBizConfException(d, 'TYRandomContent.contents default contents must not be []')
        return self


class TYCompositeContent(TYContent):
    TYPE_ID = 'CompositeContent'

    def __init__(self):
        super(TYCompositeContent, self).__init__()
        self._contents = []

    @property
    def contents(self):
        return self._contents

    def addContent(self, contents):
        assert (isinstance(contents, (TYContent, list)))
        if isinstance(contents, list):
            for content in contents:
                assert (isinstance(content, TYContent))
                self._contents.append(content)
        else:
            self._contents.append(contents)
        return self

    def getItems(self):
        items = []
        for content in self._contents:
            subItems = content.getItems()
            items.extend(subItems)
        return items

    def _decodeFromDictImpl(self, d):
        contentConfList = d.get('list')
        if not contentConfList:
            raise TYBizConfException(d, 'CompositeContent.list must be list')
        for contentConf in contentConfList:
            subContent = TYContentRegister.decodeFromDict(contentConf)
            self.addContent(subContent)
        return self


class TYContentUtils(object):
    @classmethod
    def getFixedContents(cls, content):
        contents = []
        if isinstance(content, TYFixedContent):
            contents.append(content)
        elif isinstance(content, TYCompositeContent):
            for subContent in content.contents:
                if isinstance(subContent, TYFixedContent):
                    contents.append(subContent)
        return contents

    @classmethod
    def getMinFixedAssetCount(cls, content, assetKindId):
        count = 0
        if content:
            contents = cls.getFixedContents(content)
            for fixedContent in contents:
                items = fixedContent.getMinItems()
                for item in items:
                    if item.assetKindId == assetKindId:
                        count += item.count
        return count

    @classmethod
    def mergeContentItemList(cls, contentItemList):
        # itemId, (TYContentItem, pos)
        posMap = {}
        # TYContentItem
        mergedContentItemList = []
        for contentItem in contentItemList:
            contentItemPos = posMap.get(contentItem.assetKindId)
            if contentItemPos:
                mergedContentItemList[contentItemPos[1]].count += contentItem.count
            else:
                pos = len(mergedContentItemList)
                posMap[contentItem.assetKindId] = (TYContentItem(contentItem.assetKindId, contentItem.count), pos)
                mergedContentItemList.append(TYContentItem(contentItem.assetKindId, contentItem.count))
        return mergedContentItemList


class TYContentRegister(TYConfableRegister):
    _typeid_clz_map = {
        TYFixedContent.TYPE_ID: TYFixedContent,
        TYEmptyContent.TYPE_ID: TYEmptyContent,
        TYRandomContent.TYPE_ID: TYRandomContent,
        TYCompositeContent.TYPE_ID: TYCompositeContent
    }


if __name__ == '__main__':
    contentItemList = []
    contentItemList.append(TYContentItem('user:chip', 1))
    contentItemList.append(TYContentItem('user:coupon', 1))
    contentItemList.append(TYContentItem('user:chip', 2))
    contentItemList.append(TYContentItem('user:coupon', 2))
    contentItemList.append(TYContentItem('user:charm', 2))
    contentItemList.append(TYContentItem('user:coupon', 2))

    mergedContentItemList = TYContentUtils.mergeContentItemList(contentItemList)
    for ci in mergedContentItemList:
        print ci.__dict__