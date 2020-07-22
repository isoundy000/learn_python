#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/7




class DiamondStoreShop():
    pass



class StoreTabType():
    pass




def getOtherBuyProduct(otherBuyType, buyType):
    """
    获取相应的代购券和钻石商品数据
    """
    otherBuyDict = {}
    for k, v in otherBuyType.iteritems():
        if str(k) == BT_VOUCHER:
            otherBuyDict[BT_VOUCHER] = getVoucherProduct(v)
    # elif str(k) == config.BT_DIAMOND:
    #         otherBuyDict[config.BT_DIAMOND] = getDiamondBuyProduct()
    # if buyType == config.BT_DIAMOND and not otherBuyDict.has_key(config.BT_DIAMOND):
    #     otherBuyDict[config.BT_DIAMOND] = getDiamondBuyProduct()
    return otherBuyDict


def initialize(a):
    pass