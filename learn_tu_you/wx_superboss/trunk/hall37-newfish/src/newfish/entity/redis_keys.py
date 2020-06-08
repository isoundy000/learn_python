#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6



class GameData:
    """
    存储在gamedata:gameId:userId数据库中的key值
    """
    pass


class ABTestData:
    """
    新手AB测试相关
    """
    pass


class WeakData:
    """
    存储在weak:xxx:fish:gameId:userId数据库中的key值 临时数据
    """
    pass


class UserData:
    """
    存储在user库中的key值 玩家存档gameId:userId
    """
    # 技能数据
    skill = "skill:%d:%d"
    # 新手期间技能使用次数
    newbieUseSkillTimes = "newbieUseSkillTimes:%d:%d"


class MixData:
    """
    存储在mix库中的key值 全局
    """
    pass