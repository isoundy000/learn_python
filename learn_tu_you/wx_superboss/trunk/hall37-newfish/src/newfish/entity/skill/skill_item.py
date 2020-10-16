#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11
# 44412.json = {
#     "skill_item": {
#         "14119": {                    //冰冻道具
#             "bind_name": 14176,       //绑定类型的冰冻
#             "bind_count": 1,          //绑定数量
#             "name": 14119,            //冰冻item_id
#             "count_0": 1,             //数量
#             "duration": 10,           //持续时间
#             "cd_time": 1,             //cd时间
#             "replace_name": 1137,     //代替的道具id
#             "count_1": 200,           //代替需要的数量
#         }
#         "14120": {                    //锁定道具
#             "bind_name": 14175,       //绑定类型的锁定
#             "bind_count": 1,          //绑定数量
#             "name": 14120,            //锁定item_id
#             "count_0": 1,             //数量
#             "duration": 18,           //持续时间
#             "cd_time": 1,             //cd时间
#             "replace_name": 1137,     //代替的道具id
#             "count_1": 200,           //代替需要的数量
#         }
#     }
# }
import time
import random
from newfish.entity import config, treasure_system
from newfish.entity.util import balanceItem, consumeItems
from newfish.entity.msg import GameMsg
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog


class State:

    NO_USE = 0          # 未使用
    USING = 1           # 使用中
    PAUSE = 2           # 暂停


class SkillItem(object):
    """
    技能道具的使用
    """

    FREEZE_NUM = 30     # 30

    def __init__(self, table, player, itemId):
        self.table = table
        self.player = player
        self.userId = player.userId
        self.itemId = itemId
        self.initData(itemId)

    def initData(self, itemId):
        """初始化内存数据"""
        itemId = itemId if itemId else self.itemId
        val = self.table.runConfig.skill_item.get(str(itemId), {})
        self.player.skills_item_slots[itemId] = {
            "state": State.NO_USE,
            "cost": [{
                "name": val["replace_name"],
                "count": val["count_1"],
            }],
            "progress": [0, val["cd_time"]],              # 1s|18s
            "start_time": 0,
            "conf": val
        }
        if val.get("free_times"):
            self.player.skills_item_slots[itemId]["free_times"] = val["free_times"]

    def reason(self, kindId, fIds, lockFid=0):
        """是否使用道具"""
        if kindId not in self.player.skills_item_slots:
            return 1
        if kindId == config.FREEZE_KINDID:
            frozenNum = 0
            for fId in fIds:
                isOK = self.table.findFish(fId)
                if not isOK:
                    continue
                bufferEffect = [1 for buffer in self.table.fishMap[fId]["buffer"] if buffer[0] == 5104 and time.time() < buffer[1]]
                if len(bufferEffect) > 0 and lockFid != fId:
                    frozenNum += 1
                    continue
            if frozenNum >= SkillItem.FREEZE_NUM:
                return 7
        data = self.player.skills_item_slots[kindId]
        if not data:
            return 2
        if data["state"] == State.USING:
            if float("%.2f" % time.time()) - data["start_time"] + data["progress"][0] < data["progress"][1]:
                return 4
            self.player.end_skill_item(kindId)
            data = self.player.skills_item_slots[kindId]
        if data and data["state"] != State.NO_USE:
            return 5
        conf = data["conf"]
        name = conf["name"]
        count_0 = conf["count_0"]
        replace_name = conf["replace_name"]
        count_1 = conf["count_1"]
        bind_name = conf["bind_name"]
        bind_count = conf["bind_count"]
        # 不是新手阶段或者宝藏不消耗道具阶段
        if not (self.table.typeName == config.FISH_NEWBIE or treasure_system.isUseItemFree(self.userId, int(kindId))):
            if balanceItem(self.userId, bind_name) >= bind_count and bind_count > 0:            # 先使用绑定的锁定道具
                consumeItems(self.userId, [{"name": bind_name, "count": bind_count}],
                             "BI_SKILL_ITEM_CONSUME_%s_%s_%s" % (kindId, bind_name, bind_count))
            elif balanceItem(self.userId, name) >= count_0 and count_0 > 0:                     # 在使用锁定道具
                consumeItems(self.userId, [{"name": name, "count": count_0}],
                             "BI_SKILL_ITEM_CONSUME_%s_%s_%s" % (kindId, name, count_0))
            elif balanceItem(self.userId, replace_name) >= count_1 and count_1 > 0:             # 使用珍珠
                consumeItems(self.userId, [{"name": replace_name, "count": count_1}],
                             "BI_SKILL_ITEM_CONSUME_ITEM_%s_%s_%s" % (kindId, replace_name, count_1))
            else:
                return 6
        data["state"] = State.USING
        data["start_time"] = float("%.2f" % time.time())
        return 0

    def use_item(self, seatId, kindId, fIds, lockFid=0):
        """
        使用道具
        """
        code = self.reason(kindId, fIds, lockFid)
        msg = MsgPack()
        msg.setCmd("item_use")
        msg.setResult("gameId", config.FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", seatId)
        msg.setResult("kindId", kindId)
        msg.setResult("code", code)
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())
        if code == 0:
            if kindId == config.FREEZE_KINDID:                     # 冰冻特性，有几率冰冻鱼
                self.catchFish(kindId, fIds, lockFid)
            # 使用技能道具事件
            from newfish.game import TGFish
            from newfish.entity.event import UseSkillItemEvent
            event = UseSkillItemEvent(self.player.userId, config.FISH_GAMEID, self.table.roomId, self.table.tableId, kindId)
            TGFish.getEventBus().publishEvent(event)
            self.player.triggerUseSkillItemEvent(event)
        self.player.syncSkillItemSlots(kindId)

    def pause_and_continue_time(self, kindId):
        """
        使用技能阶段 暂停和继续 锁定的时间
        :return:
        """
        data = self.player.skills_item_slots
        if kindId not in data:
            return
        item_data = data[kindId]
        if data[kindId]["state"] == State.USING:
            item_data["state"] = State.PAUSE
            item_data["progress"][0] += float("%.2f" % time.time()) - item_data["start_time"]
            item_data["progress"][0] = min(item_data["progress"][0], item_data["progress"][1])
            item_data["start_time"] = 0
        elif data[kindId]["state"] == State.PAUSE:
            item_data["state"] = State.USING
            item_data["start_time"] = float("%.2f" % time.time())
        self.player.syncSkillItemSlots(kindId)

    def catchFish(self, kindId, fIds=None, lockFid=0):
        """
        处理技能道具效果
        """
        data = self.player.skills_item_slots
        if kindId not in data:
            return
        item_data = data[kindId]
        addTimeGroups = []
        frozenFishes = []
        duration = item_data["conf"]["duration"]    # 冰冻时间
        endTime = time.time() + duration
        frozenBuffer = [5104, endTime, self.userId, 1, 1, duration, 0]
        frozenNum = 0
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            bufferEffect = [1 for buffer in self.table.fishMap[fId]["buffer"] if buffer[0] == 5104 and time.time() < buffer[1]]
            if len(bufferEffect) > 0 and lockFid != fId:
                frozenNum += 1
                continue
            fishConf = config.getFishConf(self.table.fishMap[fId]["fishType"], self.table.typeName, self.table.runConfig.multiple)
            # 计算能否冰冻
            isCoverFrozen, lastFrozenTime, frozenTime, _ = self.table.checkCoverFrozen(fId, duration, endTime)
            if isCoverFrozen:
                isCoverFrozen = random.randint(1, 10000) <= config.getCommonValueByKey("freezeProbb", 6500)
            if isCoverFrozen:
                frozenFishes.append([fId, lastFrozenTime, frozenTime, fishConf["probb2"]])

        if SkillItem.FREEZE_NUM - frozenNum > 0:
            if len(frozenFishes) >= SkillItem.FREEZE_NUM - frozenNum:
                frozenFishes.sort(key=lambda x: x[-1], reverse=True)
                frozenFishes = frozenFishes[:SkillItem.FREEZE_NUM - frozenNum]
            frozenNewFishes = []
            for frozenInfo in frozenFishes:
                self.table.frozenFish(frozenInfo[0], frozenBuffer, frozenInfo[1], frozenInfo[2], addTimeGroups)
                frozenNewFishes.append(frozenInfo[0])
            if frozenNewFishes:                            # 广播新处于冰冻状态的鱼
                self.table.broadcastSkillEffect(self.player, endTime, frozenNewFishes, 5104, isSkillItem=True)
        self.player.end_skill_item(kindId)
