#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

from Source.RedisBase.Common.RedisString import RedisString
from Source.RedisBase.Common.RedisList import RedisList
from Source.RedisBase.Common.RedisSortSet import RedisSortSet


class GloryWarPeriod(RedisString):
    '''
    保存第几届信息 设置第几届  glory_war_period
    '''

    def __init__(self, key_name='period', syst='glory_war'):
        self.period_key = self.init_key(key_name, syst)
        super(GloryWarPeriod, self).__init__('game')


class GloryWarNextPeriod(RedisString):
    '''
    保存上一届信息 glory_war_next
    '''

    def __init__(self, key_name='next', syst='glory_war'):
        self.next_key = self.init_key(key_name, syst)
        super(GloryWarNextPeriod, self).__init__('game')


class GloryWarServer(RedisList):
    '''
    保存分组服务器信息 每个战区包含的服务器
    '''

    def __init__(self, key_name, syst, period, group):
        key = '%s%s%s' % (key_name, period, group)
        self.group_key = self.init_key(key, syst)
        super(GloryWarServer, self).__init__('game')


class GloryWarHistoryChampion(RedisList):
    '''
    保存历届荣耀之战的冠军 每个战区包含历届冠军
    '''

    def __init__(self, key_name='history_champion', syst='glory_war'):
        self.group_key = self.init_key(key_name, syst)
        super(GloryWarHistoryChampion, self).__init__('game')


class GloryWarPlayerData(RedisString):
    '''
    每个战区的玩家数据
    '''

    def __init__(self, key_name, syst, period, group):
        self._attrs = {
            'period': 0,
            'group': 0,
            'uid': 0,
            'gender': '',
            'name': '',
            'vip': 0,
            'level': 0,
            'exp': 0,
            'createtime': '',
            'profile': 0,
            'power': 0,
            'platform': '',
            'lastlogin': ''
        }
        key = '%s%s%s' % (key_name, period, group)
        self.player_key = self.init_key(key, syst)
        super(GloryWarPlayerData, self).__init__('user')


class GloryWarRandomPosition(RedisString):
    '''
    随机战斗位置 所有区都用一个随机各种 random.randint(1, 7)
    '''

    def __init__(self, period, key_name, syst):
        key = '%s%s' % (key_name, period)
        self.random_key = self.init_key(key, syst)
        super(GloryWarRandomPosition, self).__init__('game')


class GloryWarWinNumRank(RedisSortSet):
    '''
    每个玩家获胜的场数
    '''

    def __init__(self, key_name, syst, period, group):
        key = '%s%s%s' % (key_name, period, group)
        self.win_num_rank = self.init_key(key, syst)
        super(GloryWarWinNumRank, self).__init__('game')


class GloryWarScoreRank(RedisSortSet):
    '''
    积分排行榜
    '''

    def __init__(self, key_name, syst, period, group):
        key = '%s%s%s' % (key_name, period, group)
        self.score_rank = self.init_key(key, syst)
        super(GloryWarScoreRank, self).__init__('game')


glory_war_data = GloryWarPeriod()


if __name__ == '__main__':
    a = GloryWarHistoryChampion('history_champion', 'glory_war')
    a.lpush("{1:1}")
    a.lpush("{2:2}")
    a.lpush("{3:3}")
    print a.lrange()