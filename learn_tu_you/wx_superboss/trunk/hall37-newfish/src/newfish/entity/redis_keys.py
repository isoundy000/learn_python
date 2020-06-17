#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6



class GameData:
    """
    存储在gamedata:gameId:userId数据库中的key值
    """
    # 用户注册时间戳
    registTime = "registTime"
    # 用户上次登录时间戳
    lastloginTime = "lastloginTime"
    # 用户累计登录天数
    loginDays = "loginDays"
    # 用户连续登录天数
    continuousLogin = "continuousLogin"
    # 金币不足次数
    coinShortageCount = "coinShortageCount"
    # 每日游戏时长（有效期2天）,playGameTime:44:uid:当日零点时间戳
    playGameTime = "playGameTime:%d:%d:%d"
    # 玩家游戏昵称
    nickname = "nickname"


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
    # 渔场红包券抽奖数据
    lotteryTicketData = "lotteryTicketData:%d:h:s:%d"


class MixData:
    """
    存储在mix库中的key值 全局
    """
    pass