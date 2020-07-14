#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/13

import time

import stackless
from poker.entity.game.tables.table_timer import TYTableTimer
from poker.protocol import runcmd


class FishTableTimer(TYTableTimer):

    def getTimeLeft(self):
        """
        取得当前计时器的剩余的倒计时时间, 若没有开始倒计时, 那么返回0
        """
        try:
            if self._fttimer:
                if self._fttimer.handle:
                    return self._fttimer.handle.getTime() - time.time()
        except:
            pass
        return 0.0

    def isActive(self):
        if self._fttimer:
            if self._fttimer.handle:
                return self._fttimer.handle.active()
        return False
    

class FishTableTimerOwn(FishTableTimer):
    
    def _onTimeOut(self):
        """
        计时器到时, 触发table的doTableCall方法
        """
        msg = stackless.getcurrent()._fttask.run_argl[0]
        seatId = msg.getParam("seatId")
        if seatId is None:
            seatId = 0
        userId = msg.getParam("userId")
        if userId is None:
            userId = 0
        assert (isinstance(userId, int))
        assert (isinstance(seatId, int))
        action = msg.getParam("action")
        clientId = runcmd.getClientId(msg)
        self._table.doTableCallOwn(msg, userId, seatId, action, clientId)