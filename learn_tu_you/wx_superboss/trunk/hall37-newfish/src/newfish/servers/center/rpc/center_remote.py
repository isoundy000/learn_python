#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
"""
概述模块或脚本
"""

import freetime.util.log as ftlog
from poker.protocol.rpccore import markRpcCall


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def checkGrandPrizeReward(userId, roomId, tableId, fId, fireCost, seatId, fpMultiple):
    """检查巨奖奖池"""
    ftlog.debug("GrandPrizePool", "userId =", userId, "roomId =", roomId, "tableId =", tableId,
                "fId =", fId, "fireCost =", fireCost, "fpMultiple =", fpMultiple)
    from newfish.entity.lotterypool.grand_prize_pool import grandPrizePoolInst
    if grandPrizePoolInst:
        grandPrizePoolInst.checkSendReward(tableId, roomId, fId, userId, fireCost, seatId, fpMultiple)
    return 1