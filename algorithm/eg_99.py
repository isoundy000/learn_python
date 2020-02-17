#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/28 16:43

# 有两个磁盘文件A和B,各存放一行字母,要求把这两个文件中的信息合并(按字母顺序排列), 输出到一个新文件C中。
# fp = open('test1.txt')
# a = fp.read()
# fp.close()
#
# fp = open('test2.txt')
# b = fp.read()
# fp.close()
#
# fp = open('test3.txt', 'w')
# l = list(a + b)
# l.sort()
# s = ''.join(l)
# fp.write(s)
# fp.close()
#
#
# def read(filename):
#     f = open(filename, "r+")
#     a = f.readlines()
#     return a
#
# s = list("".join(read("test1.txt") + read("test2.txt")))
# s.sort()
# s1 = "".join(s)
# t = open("test.txt", "w+")
# t.writelines(s1)
# t.close()


# python3的一个参考方法：
with open('test1.txt') as f1, open('test2.txt') as f2, open('2.txt', 'w') as f3:
    for a in f1:
        print(a)
        b = f2.read()
        print(b)
        c = list(a + b)
        c.sort()
        d = ''.join(c)
        f3.write(d)