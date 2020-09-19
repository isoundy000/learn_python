# -*- coding=utf-8 -*-
"""
物品变化监测模块
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/7/10


from freetime.util import log as ftlog
from newfish.entity import config


def _triggerItemChangeEvent(event):
    """触发物品改变事件"""
    userId = event.userId
    changed = event.changed
    eventId = event.changeEventId
    conf = config.getItemMonitorConf().get("datas", {})
    if len(conf) == 0:
        return
    levels = config.getItemMonitorConf().get("levels", {})
    for k, v in levels.iteritems():
        if userId in v:
            idx = int(k)
            break
    else:
        idx = 0
    if not changed.get("items", None):
        return
    for item in changed["items"]:
        kindId = item.get("name", 0)
        count = item.get("count", 0)
        delta = item.get("delta", 0)
        params = conf.get(str(kindId), None)
        if params is None or params.get("enable", 0) == 0:
            continue
        changedCount = params.get("changed", [0])
        changedCount = changedCount[idx] if len(changedCount) > idx else changedCount[-1]
        finalCount = params.get("finalCount", [0])
        finalCount = finalCount[idx] if len(finalCount) > idx else finalCount[-1]
        if (abs(delta) >= changedCount or (delta > 0 and count - delta < finalCount <= count) or
                (delta < 0 and count - delta >= finalCount > count)):
            ftlog.error("[WARNING] item_monitor ! userId =", userId, "name =", params.get("name", ""),
                        "kindId =", kindId, "delta =", delta, "count =", count, "eventId =", eventId)


_inited = False


def initialize():
    ftlog.info("newfish item_monitor initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.game import TGFish
        from newfish.entity.event import ItemMonitorEvent
        TGFish.getEventBus().subscribe(ItemMonitorEvent, _triggerItemChangeEvent)
    ftlog.info("newfish item_monitor initialize end")