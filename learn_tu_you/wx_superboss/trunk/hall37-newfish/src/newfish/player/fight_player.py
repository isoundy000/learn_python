# -*- coding:utf-8 -*-
"""
Created on 2017年12月26日

@author: haohongxian
"""

from newfish.player.player_base import FishPlayer


class FishFightPlayer(FishPlayer):

    def __init__(self, table, seatIndex, clientId=None):
        super(FishFightPlayer, self).__init__(table, seatIndex, clientId)

    def _checkSkillCondition(self, skillId, select, skillType):
        """检查技能是否满足条件"""
        reason = 0
        skill = self.getSkill(skillId, skillType)
        if skill:
            if select:
                if self.usingSkill:                         # 有之前技能记录
                    lastSkillId = self.usingSkill[-1].get("skillId")
                    lastSkillType = self.usingSkill[-1].get("skillType", 0)
                    lastSkill = self.getSkill(lastSkillId, lastSkillType)
                    if lastSkill and lastSkill.state == 1:  # 如果上一个技能状态为装备中，先取消上一个技能，返还子弹
                        lastSkill.use(0)
                if self.clip < skill.getCost:
                    # bullet = self.tableChip // self.table.runConfig.multiple
                    # if self.clip + bullet >= skill.getCost:
                    #     isOK = self.table.clip_add(self.userId, self.seatId, 0, 1)
                    #     if not isOK:
                    #         reason = 1
                    # else:
                    reason = 1  # 使用技能所需子弹不足
                elif skill.cdTimeLeft > 0 and self.isFinishRedTask:
                    reason = 2  # 技能正在冷却
                elif skill.state == 1:
                    reason = 3  # 技能正在装备中，选中失败
            else:
                if skill.state == 2:
                    reason = 4  # 技能正在使用中，取消失败
        else:
            reason = 5  # 技能槽没有该技能
        return reason