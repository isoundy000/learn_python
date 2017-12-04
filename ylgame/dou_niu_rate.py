#-*-coding:utf-8-*-
'''
Created on 2017年11月8日

@author: houguangdong
'''

import os
import cPickle
from copy import copy
from collections import Counter
import itertools
'''
计算斗牛游戏的概率
'''


class Poker():
    '''
    一张牌
    '''
    def __init__(self, num, type):
        self.num = num      # 牌数
        self.type = type    # 花色


class GamePoker():
    '''
    一手牌，即5张Poker
    '''
    COMMON_NIU = 1          # 普通的牛，即牛一-牛七
    NO_NIU = 0              # 没有牛
    EIGHT_NINE_NIU = 2      # 牛九或牛八
    TEN_NIU = 3             # 牛十
    THREE_SAME = 4          # 三条
    FOUR_SAME = 5           # 四条
 
    def __init__(self, pokers):
        assert len(pokers) == 5
        self.pokers = pokers
        self.num_pokers = [p.num for p in self.pokers]
        # self.weight = None # 牌的权重，权重大的牌胜
        # self.money_weight = None # 如果该牌赢，赢钱的权重
        self.result = self.sumary()

    def is_niu(self):
        '''
        是否有牛
        :return:
        '''
        # if self.is_three_same():
        # return 0
        for three in itertools.combinations(self.num_pokers, 3):
            if sum(three) % 10 == 0:
                left = copy(self.num_pokers)
                for item in three:
                    left.remove(item)
                point = sum(left) % 10
                return 10 if point == 0 else point
        return 0

    def is_three_same(self):
        '''
        是否3条
        :return:
        '''
        # if self.is_four_same():
        # return 0
        count = Counter([p.num for p in self.pokers])
        for num in count:
            if count[num] == 3:
                return num
        return 0
 
    def is_four_same(self):
        '''
        是否4条
        :return:
        '''
        count = Counter([p.num for p in self.pokers])
        for num in count:
            if count[num] == 4:
                return num
        return 0
 
    def sumary(self):
        '''
        计算牌
        '''
        if self.is_four_same():
            return GamePoker.FOUR_SAME
        if self.is_three_same():
            return GamePoker.THREE_SAME
        niu_point = self.is_niu()
        if niu_point in (8, 9):
            return GamePoker.EIGHT_NINE_NIU
        elif niu_point == 10:
            return GamePoker.TEN_NIU
        elif niu_point > 0:
            return GamePoker.COMMON_NIU
        else:
            return GamePoker.NO_NIU


def get_all_pokers():
    '''
    生成所有的Poker，共四十个
    :return:
    '''
    pokers = []
    for i in range(1, 11):
        for j in ('A', 'B', 'C', 'D'):
            pokers.append(Poker(i, j))
    return pokers
 
 
def get_all_game_poker(is_new=0):
    '''
    生成所有game_poker
    :param pokers:
    :return:
    '''
    pokers = get_all_pokers()
    game_pokers = []
    if not is_new and os.path.exists('game_pokers'):
        with open('game_pokers', 'r') as f:
            return cPickle.loads(f.read())
    for pokers in itertools.combinations(pokers, 5): # 5代表五张牌
        game_pokers.append(GamePoker(pokers))
    with open('game_pokers', 'w') as f:
        f.write(cPickle.dumps(game_pokers))
    return game_pokers
 

def print_rate(game_pokers):
    total_num = float(len(game_pokers))
    four_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.FOUR_SAME])
    three_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.THREE_SAME])
    ten_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.TEN_NIU])
    eight_nine_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.EIGHT_NINE_NIU])
    common_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.COMMON_NIU])
    no_num = len([game_poker for game_poker in game_pokers if game_poker.result == GamePoker.NO_NIU])
    print '所有牌的组合数：%d' % total_num
    print '出现四条的组合数:%d,概率 :%.2f%%' % (four_num, four_num * 100 / total_num)
    print '出现三条的组合数:%d,概率 :%.2f%%' % (three_num, three_num * 100 / total_num)
    print '出现牛十的组合数:%d,概率 :%.2f%%' % (ten_num, ten_num * 100 / total_num)
    print '出现牛九或牛八的组合数:%d,概率 :%.2f%%' % (eight_nine_num, eight_nine_num * 100 / total_num)
    print '出现牛一到牛七的组合数:%d,概率 :%.2f%%' % (common_num, common_num * 100 / total_num)
    print '出现没有牛的组合数:%d,概率 :%.2f%%' % (no_num, no_num * 100 / total_num)


def main():
    game_pokers = get_all_game_poker() # 658008种
    print_rate(game_pokers)


if __name__ == '__main__':
    main()