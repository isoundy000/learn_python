#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from lib.db import ModelBase
import game_config


class Drama(ModelBase):
    """
    战斗剧情数据
    """
    def __init__(self, uid):
        """
        初始化
        '_drama': [已完成战斗id]
        """
        self.uid = uid

        self._attrs = {
            '_drama': []        # 已完成战斗id
        }
        super(Drama, self).__init__(self.uid)

    def checkFight(self, fightId):
        """
        检查战斗剧情是否已经激活过
        """
        return fightId in self._drama

    def completionFight(self, fightId):
        """
        战斗剧情已经触发过
        """
        self._drama.append(fightId)
        self.save()