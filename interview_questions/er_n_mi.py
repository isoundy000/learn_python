#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import sys
line = sys.stdin.readline()
n = int(line)
if n < 1 or n > 2 ^ 31:
     print 0
else:
    def twopower(n):
        res = 1
        while res < n:
            res = res << 1
        if res == n:
            return 1
        else:
            return 0
    print twopower(int(n))


# 1：while循环判断，注意整数为"0"的测试用例
def isPowerOfTwo(n):
    """
    :type n: int
    :rtype: bool
    """
    if n == 0:
        return False
    while n % 2 == 0:
        n = n / 2
    if n == 1:
        return True
    else:
        return False


# 2：&位与运算（参考他人）
def isPowerOfTwo1(n):
    """
    :type n: int
    :rtype: bool
    """
    if n == 0:
        return False
    n = n & (n - 1)
    if n == 0:
        return True
    else:
        return False