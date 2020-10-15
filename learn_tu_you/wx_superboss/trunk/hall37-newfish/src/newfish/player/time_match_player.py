# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/1/12.
"""

import random

from freetime.util import log as ftlog
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.skill import skill_system
from newfish.player.multiple_player import FishMultiplePlayer
from newfish.entity.match_record import MatchRecord
from newfish.player.player_buffer import FishPlayerBuffer


class FishTimeMatchPlayer(FishMultiplePlayer):
    """
    回馈赛的玩家
    """
    def __init__(self, table, seatIndex, clientId=None):
        super(FishTimeMatchPlayer, self).__init__(table, seatIndex, clientId)

    def _loadUserData(self):
        super(FishTimeMatchPlayer, self)._loadUserData()
        record = MatchRecord.loadRecord(FISH_GAMEID, self.userId, self.table.room.bigmatchId)
        self.matchLuckyValue = record.luckyValue
        self.matchLuckyValue = max(self.matchLuckyValue, 0)
        self.matchLuckyValue = min(self.matchLuckyValue, 10000)

    def addOneBufferId(self, bufferId):
        """添加buff"""
        if bufferId:
            self.bufferRemove(bufferId)
            bufferInfo = FishPlayerBuffer(self, bufferId)
            self.usedBufferInfos.append(bufferInfo)

    def getCatchBufferId(self, bufferIds):
        """获取捕获的bufferId"""
        totalPlayerNum = self.table._match_table_info["playerCount"]
        paramK = int(config.getCommonValueByKey("createBufferParamK"))
        paramD = int(config.getCommonValueByKey("createBufferParamD"))

        k1 = 1 + (self.rank - 1) * (paramK - 1) * 1.0 / max((totalPlayerNum - 1), 1)
        paramL = 2 * k1 - paramK - 1
        paramB = abs(paramL) + paramD
        probs = []

        bufferNum = len(bufferIds)
        if ftlog.is_debug():
            ftlog.debug("getCatchBufferId========>", self.rank, totalPlayerNum, paramK, paramD, paramL, paramB)
        probZs = []
        for i in xrange(bufferNum + 1):
            xn = -1 + 2.0 * i / bufferNum
            yn = paramL * xn + paramB
            # sumNum += int(yn * 1000)
            probs.append(yn)
            if i > 0:
                zn = int((probs[i] + probs[i-1]) * bufferNum * 1000)  # 结果扩大3位数
                probZs.append(zn)
        randNum = random.randint(1, sum(probZs))
        sumNum = 0
        if ftlog.is_debug():
            ftlog.debug("getCatchBufferId========>", randNum, sum(probZs), probZs, probs, paramB)
        for index, num_ in enumerate(probZs):
            if randNum <= sumNum + num_:
                if ftlog.is_debug():
                    ftlog.debug("getCatchBufferId========>", bufferIds[index], sumNum + num_)
                return bufferIds[index]
            sumNum += num_
        if ftlog.is_debug():
            ftlog.debug("getCatchBufferId========>", sumNum, probZs)
        return -1

    def incrExp(self, gainExp):
        return self.exp

    def _refreshSkillSlots(self, skillType=0):
        """
        刷新技能数据 安装技能槽
        """
        if skillType == 0:
            self.skillSlots = {}
        if self.table._matchSkills:
            for idx, skillId in enumerate(self.table._matchSkills):
                skill = skill_system.getSkill(self.userId, skillId)
                starLevel, currentLevel = 1, 1
                if skill[skill_system.INDEX_STAR_LEVEL]:
                    starLevel = skill[skill_system.INDEX_STAR_LEVEL]
                    currentLevel = skill[skill_system.INDEX_CURRENT_LEVEL]
                self.skillSlots[skillId] = [idx + 1, starLevel, currentLevel]
        else:
            super(FishTimeMatchPlayer, self)._refreshSkillSlots(skillType)