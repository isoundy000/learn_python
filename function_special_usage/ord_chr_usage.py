# -*- encoding: utf-8 -*-
'''
Created on 2019年6月5日

@author: houguangdong
'''

# python ord()与chr()用法以及区别
# ord()函数主要用来返回对应字符的ascii码，chr()主要用来表示ascii码对应的字符他的输入时数字，可以用十进制，也可以用十六进制。

# 例如：
print ord('a')
print chr(97)
print chr(0x61)
print "-----------------------"
# 一个简单的程序来灵活运用。

str1 = 'asdfasdf123123'

for i in range(len(str1)):
     print chr(ord(str1[i]) - 1)

# 以上程序主要实现对字符串str1里面所有的字符，转换成ascii码中比他们小一位的字符。

# 题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，乙队为x,y,z三人。
# 已抽签决定比赛名单。有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，请编程序找出三队赛手的名单。

for i in range(ord('x'), ord('z') + 1):
    for j in range(ord('x'), ord('z') + 1):
        if i != j:
            for k in range(ord('x'), ord('z') + 1):
                if (i != k) and (j != k):
                    if (i != ord('x')) and (k != ord('x')) and (k != ord('z')):
                        print 'order is a -- %s\t b -- %s\tc--%s' % (chr(i), chr(j), chr(k))


# 可以用来生成随机验证码：
import random
# 1X3Y3ZX
def make_code(size=7):
    res = ''
    for i in range(size):
        # 循环一次则得到一个随机字符（字母/数字）
        s = chr(random.randint(65, 90))
        num = str(random.randint(0, 9))
        res += random.choice([s, num])
    return res

res = make_code()
print res