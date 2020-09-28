# -*- coding=utf-8 -*-
"""
easy脚本
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/1/16

import random

from newfish.script.script_base import ScriptBase, FIRE_TARGET_POS


class ScriptEasy1(ScriptBase):

    def __init__(self, player, fireRange, idleRange, leaveRange):
        super(ScriptEasy1, self).__init__(player, fireRange, idleRange, leaveRange)

    def _update(self):
        if self._isNeedCancelTimer():
            return

        if self._isWaitLeave():
            # self._chat()
            return

        if self._isIdle():
            # self._chat()
            return

        self._updateFireTarget()
        self._setFireTimer()

    def _updateFireTarget(self):
        pos1 = FIRE_TARGET_POS[self.seatId]["start"]
        pos2 = FIRE_TARGET_POS[self.seatId]["end"]
        self.fireTargetPos = [pos1[0] + int((pos2[0] - pos1[0]) * random.random()),
                              pos1[1] + int((pos2[1] - pos1[1]) * random.random())]