#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import random

# GRandList = range(101)[1:]
# GRandList = range(1, 101)
# random.shuffle(GRandList)


def randSeedList(seed, seedall):
    """
    生成一个用于随机数的0到99的均匀随机数种子序列
    """
    if seed % seedall != 0:
        print 'randSeedList seed error'
        return None
    tempList = [0] * seed
    tempseed = seed / seedall           # 100 / 10
    for i in range(tempseed):           # 10
        tempIndex = i * seedall         # 0, 10, 20, .... 90
        for j in range(seedall):        # 10
            if j % 2 == 0:
                tempList[tempIndex + j / 2] = j * tempseed + i
            else:
                tempList[tempIndex + (seedall - 1) - j / 2] = j * tempseed + i
    return tempList


GRandList = randSeedList(100, 10)
# print GRandList, len(GRandList)
GIndexList = []


def myRand():
    """
    获取一个1到100中的一个随机数
    """
    # tempIndex = random.randint(0, 99)
    # return GRandList(tempIndex)
    # return random.choice(GRandList)
    templen = len(GIndexList)
    if templen < 1:
        for i in xrange(10):
            for j in xrange(10):
                GIndexList.append(j * 10 + i)
    # print sorted(GRandList)
    tempIndex = random.choice(GIndexList)
    tempX = GRandList[tempIndex]
    GIndexList.remove(tempIndex)

    return tempX


class onlyRand(object):
    """
    在指定范围内，不得到两次相同的随机数
    只能随机整数字，随机其他东西，自己想办法
    """
    def __init__(self, start, end):
        """
        初始化范围
        """
        self.m_start = start
        self.m_list = range(start, end + 1)
        random.shuffle(self.m_list)

    def getRand(self):
        """
        得到一个随机数，取完后，此函数会返回小于start的数字
        """
        if len(self.m_list) <= 1:
            return self.m_start - 100000
        temp = self.m_list[0]               # [1, 2, 3, 4]
        self.m_list[0: 1] = []              # [2, 3, 4]
        return temp

    def removeElement(self, element):
        """
        删除其中的某个元素
        """
        if element in self.m_list:
            self.m_list.remove(element)


class evenRand(object):
    """
    均匀随机数
    """
    m_seedList = []
    m_indexList = []
    m_seed = 0
    m_seedall = 0

    @classmethod
    def set_seed(cls, seed, seedall):
        """
        set rand seed
        """
        if seed == cls.m_seed and seedall == cls.m_seedall:
            return None
        cls.m_indexList = range(seed)
        cls.m_seedList = randSeedList(seed, seedall)    # 100, 10
        cls.m_seed = seed
        cls.m_seedall = seedall

    @classmethod
    def set_dream_seed(cls, seed, seedall):
        """
        set rand dream seed
        """
        # print '(seed, seedall)', seed, seedall
        if seed == cls.m_seed and seedall == cls.m_seedall:
            return None
        temp = seed % seedall
        tempseed = seed
        if temp != 0:
            tempseed += seedall - temp
            cls.set_seed(tempseed, seedall)
            # print 'tempseed', tempseed
            for i in range(seed, tempseed):
                cls.m_seedList.remove(i)
                cls.m_indexList.remove(i)
            cls.m_seed = seed
        else:
            cls.set_seed(tempseed, seedall)

    def __init__(self):
        pass

    def getRand(self):
        """
        return a random number
        """
        templen = len(evenRand.m_indexList)
        if templen < 1:
            for i in range(evenRand.m_seed):
                evenRand.m_indexList.append(i)
        tempIndex = random.choice(evenRand.m_indexList)
        tempX = evenRand.m_seedList[tempIndex]
        evenRand.m_indexList.remove(tempIndex)
        return tempX
