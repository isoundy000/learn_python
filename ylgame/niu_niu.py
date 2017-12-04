#-*-coding:utf-8-*-
'''
Created on 2017年11月8日

@author: houguangdong
'''
import copy
import itertools


a = [10, 6, 1, 3, 4]
r = 3

def combinations(iterable, r):
    pool = tuple(iterable)          # [10, 9, 1, 3, 4]
    n = len(pool)
    if r > n:
        return
    indices = range(r)              # [0, 1, 2]
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in xrange(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)
        

def is_niu():
    for three in combinations(a, r):
        if sum(three) % 10 == 0:
            left = copy.deepcopy(a)
            for item in three:
                left.remove(item)
            point = sum(left) % 10
            return 10 if point == 0 else point
    return 0


def is_niu_2():
    # combinations(range(4), 3) --> (0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)
    for three in itertools.combinations(a, r):
        if sum(three) % 10 == 0:
            left = copy.deepcopy(a)
            for item in three:
                left.remove(item)
            point = sum(left) % 10
            return 10 if point == 0 else point
    return 0


def big_poker():
    """
    获取最大的那张牌
    """
    def com(x, y):
        x_num = x % 100
        y_num = y % 100
        if x_num > y_num:
            return -1
        elif x_num == y_num:
            if x % 100 > y % 100:
                return -1
            elif x % 100 == y % 100:
                if x / 100 > y / 100:
                    return -1
                else:
                    return 1
            else:
                return 1
        else:
            return 1
    pokers_index = [101, 204, 102, 103, 205]
    pokers_index.sort(com)
    return pokers_index[0]


if __name__ == '__main__':
    print is_niu()
    print is_niu_2()
    print big_poker()