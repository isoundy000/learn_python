#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3
"""
游戏基类
"""
from poker.entity.game.game import TYGame


class TGFish(TYGame):
    """
    欢乐捕鱼
    """
    def initGameBefore(self):
        """
        此方法由系统进行调用
        游戏初始化的预处理
        """
        pass



    def initGame(self):
        """
        此方法由系统进行调用
        游戏自己初始化业务逻辑模块, 例如: 初始化配置, 建立事件中心等
        执行的时序为：首先调用所有游戏的 initGameBefore()
                    再调用所有游戏的 initGame()
                    最后调用所有游戏的 initGameAfter()
        """
        from newfish.entity.gun import gun_system


