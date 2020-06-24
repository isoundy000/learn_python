#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11
# 44412.json = {
#     "skill_item": {
#         "14120": {                    //锁定道具
#             "name": 14120,            //锁定item_id
#             "count_0": 1,             //数量
#             "duration": 18,           //持续时间
#             "cd_time": 1,             //cd时间
#             "replace_name": 1137,     //代替的道具id
#             "count_1": 200,           //代替需要的数量
#             "play_times": 4           //可玩次数  如果是-10000无限制
#         },
#         "14119": {                    //冰冻道具
#             "name": 14119,            //冰冻item_id
#             "count_0": 1,             //数量
#             "duration": 10,           //持续时间
#             "cd_time": 1,             //cd时间
#             "replace_name": 1137,     //代替的道具id
#             "count_1": 200,           //代替需要的数量
#             "play_times": 4           //可玩次数  如果是-10000无限制
#         }
#     }
# }
import time
import random
from newfish.entity import config
from newfish.entity.util import balanceItem, consumeItems
from newfish.entity.msg import GameMsg
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from copy import deepcopy


class State:

    NO_USE = 0          # 未使用
    USING = 1           # 使用中
    PAUSE = 2           # 暂停


class SkillItem(object):
    """
    技能道具的使用
    """

    def __init__(self, table, player, itemId):
        self.table = table
        self.player = player
        self.userId = player.userId
        self.itemId = itemId
        self.initData()

    def initData(self, itemId="", add_times=0):
        """初始化内存数据"""
        itemId = itemId if itemId else self.itemId
        val = self.table.runConfig.skill_item.get(itemId, {})
        # if val["play_times"] > 0:
        #     total_times = val['play_times'] + add_times if add_times else val['play_times']
        # else:
        #     total_times = -10000
        self.player.skills_item_slots[itemId] = {
            "state": State.NO_USE,
            "cost": [{
                "name": val["replace_name"],
                "count": val["count_1"]
            }],
            "progress": [0, val["cd_time"]],              # 1s|18s
            # "cd_time": val["duration"],                 # duration持续时间 10s|18s
            # "remainTimes": total_times,                 # 千炮畅没有次数限制| TODO 大奖赛有次数限制需要保存到数据库中
            # "maxTimes": total_times,
            "start_time": 0,
            "conf": val
        }

    def reason(self, kindId):
        """是否使用道具"""
        if kindId not in self.player.skills_item_slots:
            return 1
        data = self.player.skills_item_slots[kindId]
        if not data:
            return 2
        # if data["remainTimes"] == 0 and data["maxTimes"] != -10000:
        #     return 3
        if data["state"] == State.USING:
            if float('%.2f' % time.time()) - data["start_time"] + data["progress"][0] < data["progress"][1]:
                return 4
            else:
                self.player.end_skill_item(kindId)
                data = self.player.skills_item_slots[kindId]
        if data and data["state"] != State.NO_USE:
            return 5
        conf = data["conf"]
        name = conf["name"]
        count_0 = conf["count_0"]
        replace_name = conf["replace_name"]
        count_1 = conf["count_1"]
        if balanceItem(self.userId, name) >= count_0 and count_0 > 0:                    # 锁定道具不足
            consumeItems(self.userId, [{'name': name, 'count': count_0}], "BI_SKILL_ITEM_CONSUME_%s_%s_%s" % (kindId, name, count_0))
        else:
            if balanceItem(self.userId, replace_name) >= count_1 and count_1 > 0:
                consumeItems(self.userId, [{'name': replace_name, 'count': count_1}], "BI_SKILL_ITEM_CONSUME_ITEM_%s_%s_%s" % (kindId, replace_name, count_1))
            else:
                return 6
        data["state"] = State.USING
        data["start_time"] = float('%.2f' % time.time())
        # if data["maxTimes"] > 0:
        #     data["remainTimes"] -= 1
        return 0

    def use_item(self, seatId, kindId, fIds):
        """
        使用道具
        """
        code = self.reason(kindId)
        msg = MsgPack()
        msg.setCmd('item_use')
        msg.setResult('gameId', config.FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult('seatId', seatId)
        msg.setResult('kindId', kindId)
        msg.setResult('code', code)
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())
        if code == 0 and kindId == "14119":                     # 冰冻特性，有几率冰冻鱼
            self.catchFish(kindId, fIds)
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
            item_data["progress"][0] += float('%.2f' % time.time()) - item_data["start_time"]
            item_data["progress"][0] = min(item_data["progress"][0], item_data["progress"][1])
            item_data["start_time"] = 0
        elif data[kindId]["state"] == State.PAUSE:
            item_data["state"] = State.USING
            item_data["start_time"] = float('%.2f' % time.time())
        self.player.syncSkillItemSlots(kindId)

    def catchFish(self, kindId, fIds=None):
        """
        处理技能道具效果
        """
        data = self.player.skills_item_slots
        if kindId not in data:
            return
        item_data = data[kindId]
        addTimeGroup = []
        frozenFishes = []
        duration = item_data["conf"]["duration"]    # 冰冻时间
        endTime = time.time() + duration
        buffer = [5104, endTime, self.userId, 1, 1, duration, 0]
        for fId in map(int, fIds):
            buffers = self.table.fishMap[fId]["buffer"]
            if ftlog.is_debug():
                ftlog.debug("dealSkillItemEffect->buffers", buffers)
            isCoverFrozen = True
            frozenTime = duration
            lastFrozenTime = 0
            for lastBuffer in buffers:
                if lastBuffer[0] != 5104:
                    continue
                lastFrozenTime = lastBuffer[5]
                if endTime > lastBuffer[1]:             # 新冰冻到期时间大于旧冰冻到期时间，覆盖时间
                    # 如果上一个冰冻状态未到期且小于新冰冻到期时间，则鱼在冰冻状态下再次冰冻，实际冰冻时间为间隔时间
                    if time.time() < lastBuffer[1] < endTime:
                        frozenTime = round(endTime - lastBuffer[1], 3)
                else:
                    isCoverFrozen = False
            if isCoverFrozen:
                isCoverFrozen = True if random.randint(1, 10000) <= config.FREEZE_PROBB else False
            if isCoverFrozen:
                if ftlog.is_debug():
                    ftlog.debug("dealSkillItemEffect->frozenTime =", fId, frozenTime)
                buffer[5] = round(lastFrozenTime + frozenTime, 3)
                self.table.setFishBuffer(fId, buffer)
                frozenFishes.append(fId)
                buffers = self.table.fishMap[fId]["buffer"]
                if ftlog.is_debug():
                    ftlog.debug("dealSkillItemEffect->isCoverFrozen->buffer =", fId, buffers)
                group = self.table.fishMap[fId]["group"]
                if group.startFishId not in addTimeGroup:
                    addTimeGroup.append(group.startFishId)
                    group.adjust(frozenTime)
                    self.table.superBossFishGroup and self.table.superBossFishGroup.frozen(fId, self.table.fishMap[fId]["conf"]["fishType"], frozenTime)

        if frozenFishes:  # 广播新处于冰冻状态的鱼
            self.table.broadcastSkillEffect(self.player, endTime, frozenFishes, 5104)
        self.player.end_skill_item(kindId)