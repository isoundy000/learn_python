# -*-coding:utf-8-*-
'''
Created on 2017年6月13日

@author: ghou
'''
# 两个骰子和为7的概率
a = [(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)]
print len(a)/36

# 函数名也是变量
f = abs
print f(-10)

# 既然变量可以指向函数，函数的参数能接收变量，那么一个函数就可以接收另一个函数作为参数，这种函数就称之为高阶函数。
def add(x, y, f):
    return f(x) + f(y)

print add(-5, 6, abs)


# ADBC 取最大字串
# 获取jar的名字
# .*\\(.*\.jar)

z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
    "AAABACADAEAFAGAHAIAJAKALAMANAOAPAQARASATAUAVAWAXAYAZ" \
    "BABBBCBDBEBFBGBHBIBJBKBLBMBNBOBPBQBRBSBTBUBVBWBXBYBZ" \
    "CACBCCCDCECFCGCHCICJCKCLCMCNCOCPCQCRCSCTCUCVCWCXCYCZ"

# k = ""
# for i in range(len(z)):
#     k = k + "C"+ z[i]
# print k

for i in range(len(z)):
    print len(z) / 26

