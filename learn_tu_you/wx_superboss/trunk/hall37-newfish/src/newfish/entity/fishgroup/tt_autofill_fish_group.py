# -*- coding=utf-8 -*-
"""
渔场任务使用的自动填充鱼阵
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/5/17

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config
from poker.entity.events import tyeventbus
from poker.entity.events.tyevent import EventConfigure


class TTAutofillFishGroup(object):

    def __init__(self, table):
        self.table = table
        self.tasks = config.getNcmpttTaskConf(self.table.runConfig.fishPool)            # 获取限时任务配置
        self.tasks.extend(config.getCmpttTaskConf(self.table.runConfig.fishPool))       # 获取宝藏争夺赛配置
        self.tasks.extend(config.getBonusTaskConf(self.table.runConfig.fishPool))       # 获取奖金赛配置
        self.taskId = {}                                                                # {uid: taskId}
        self.autofillTimerList = {}                                                     # 自动填充鱼{uid: _timer}
        self.overTimeTimer = {}                                                         # 结束任务定时器
        tyeventbus.globalEventBus.subscribe(EventConfigure, self.reloadConf)

    def clearTimer(self):
        for _timer in self.autofillTimerList.values():
            _timer.cancel()
            _timer = None
        for _timer in self.overTimeTimer.values():
            _timer.cancel()
            _timer = None

    def reloadConf(self, event):
        """重新加载配置"""
        # ftlog.debug("TTAutofillFishGroup", event.keylist)
        if "game:44:bonusTask:0" not in event.keylist and "game:44:cmpttTask:0" not in event.keylist and "game:44:ncmpttTask:0" not in event.keylist:
            return
        tasks = config.getNcmpttTaskConf(self.table.runConfig.fishPool)
        tasks.extend(config.getCmpttTaskConf(self.table.runConfig.fishPool))
        tasks.extend(config.getBonusTaskConf(self.table.runConfig.fishPool))
        self.tasks = tasks
        # ftlog.debug("TTAutofillFishGroup, refresh tasks success!", event.keylist)

    def startAutofill(self, uid, taskId):
        """
        开始填充
        """
        if uid is None:
            uid = 0
        else:
            uid = int(uid)
        if taskId == 0 or taskId == self.taskId.get(uid):
            return
        if self.overTimeTimer.get(uid):
            self.overTimeTimer[uid].cancel()
            self.overTimeTimer.pop(uid)
        if self.autofillTimerList.get(uid):
            for _timer in self.autofillTimerList[uid]:
                if _timer:
                    _timer.cancel()
            self.autofillTimerList.pop(uid)
        taskConf = None                                                 # 任务配置
        for val in self.tasks[:]:
            if int(val["taskId"]) == int(taskId):
                taskConf = val
                break
        if taskConf is None:
            ftlog.warn("TTAutofillFishGroup, uid =", uid, "taskId =", taskId, "not find !")
            return
        if taskConf.get("taskType", 0) != 1:
            ftlog.warn("TTAutofillFishGroup, uid =", uid, "taskId =", taskId, "type not match !")
            return
        self.taskId[uid] = taskId
        targets = taskConf.get("targets", {})
        target1 = targets.get("target1", 0)
        inter1 = targets.get("inter1", 0)
        target2 = targets.get("target2", 0)
        inter2 = targets.get("inter2", 0)
        if target1 and inter1:
            FTLoopTimer(0.1, 0, self._addAutofillFishGroup, target1).start()
            _timer = FTLoopTimer(inter1, -1, self._addAutofillFishGroup, target1)
            _timer.start()
            self.autofillTimerList.setdefault(uid, []).append(_timer)
        if target2 and inter2:
            FTLoopTimer(0.1, 0, self._addAutofillFishGroup, target2).start()
            _timer = FTLoopTimer(inter2, -1, self._addAutofillFishGroup, target2)
            _timer.start()
            self.autofillTimerList.setdefault(uid, []).append(_timer)
        self.overTimeTimer[uid] = FTLoopTimer(taskConf.get("timeLong", 60) + 5, 0, self._overTime, uid)
        self.overTimeTimer[uid].start()
        if ftlog.is_debug():
            ftlog.debug("TTAutofillFishGroup, start, uid =", uid, "taskId =", self.taskId)

    def endAutofill(self, uid, taskId):
        """
        结束填充
        """
        if uid is None:
            uid = 0
        else:
            uid = int(uid)
        if self.taskId.get(uid) != taskId:
            return
        if ftlog.is_debug():
            ftlog.debug("TTAutofillFishGroup, uid =", uid, "taskId =", self.taskId[uid])
        self.taskId.pop(uid)
        if self.autofillTimerList.get(uid):
            for _timer in self.autofillTimerList[uid]:
                if _timer:
                    _timer.cancel()
            self.autofillTimerList.pop(uid)
        if self.overTimeTimer.get(uid):
            self.overTimeTimer[uid].cancel()
            self.overTimeTimer.pop(uid)

    def _addAutofillFishGroup(self, fishType):
        """添加自动填充鱼鱼群"""
        if fishType not in self.table.runConfig.allAutofillGroupIds:
            if ftlog.is_debug():
                ftlog.debug("TTAutofillFishGroup, error", self.table.tableId, fishType)
            return
        autofillFishGroupIds = self.table.runConfig.allAutofillGroupIds[fishType]
        if autofillFishGroupIds:
            autofillGroupId = random.choice(autofillFishGroupIds)
            self.table.insertFishGroup(autofillGroupId)
        else:
            if ftlog.is_debug():
                ftlog.debug("TTAutofillFishGroup, not exist fishType group", self.table.tableId, fishType)

    def _overTime(self, uid):
        """结束任务定时器"""
        if self.taskId.get(uid) and ftlog.is_debug():
            ftlog.debug("TTAutofillFishGroup, uid =", uid, "taskId =", self.taskId.get(uid))
        if self.overTimeTimer.get(uid):
            self.overTimeTimer[uid].cancel()
            self.overTimeTimer.pop(uid)
        if self.taskId.get(uid):
            self.taskId.pop(uid)
        if self.autofillTimerList.get(uid):
            for _timer in self.autofillTimerList[uid]:
                if _timer:
                    _timer.cancel()
            self.autofillTimerList.pop(uid)