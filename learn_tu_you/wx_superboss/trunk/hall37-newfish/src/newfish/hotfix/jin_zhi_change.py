#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/31

# 2进制，8进制，10进制，16进制在python中的表示方法和互相转换函数
# 2进制：满2进1   , 0b10
# 8进制：满8进1   , 0o10
# 10进制：满10进1  , 10
# 16进制：满16进1  , 0x10
# 时间满60进1
# bin()  转2进制方法
# int()  转10进制方法
# oct()  转8进制方法
# hex()  转16进制方法
print bin(20)               # 20
print bin(0o45)             # 37
print bin(0x1F)             # 0-9 a-f [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf] = xrange(15)
print int(0b10)
print bin(0x10),  '111111'
print bin(0x100), '222222'
print bin(0x1000), '333333'
print bin(0x11), '444444'
print bin(0x10 & 0x11), '555555'
print int(0b11)
print int(0o34)
print int(0x1f)
print int(0x3f)
print hex(100)
print hex(0x1f)
print hex(0o45)
print hex(0b101)
print oct(0x45)
print oct(0b101)