# -*- encoding: utf-8 -*-
'''
Created on 2017年3月21日

@author: ghou
'''
import math
import datetime
import string

# 4 题目：输入某年某月某日，判断这一天是这一年的第几天？
year = int(raw_input('year:\n'))
month = int(raw_input('month:\n'))
day = int(raw_input('day:\n'))
months = (0,31,59,90,120,151,181,212,243,273,304,334)
if 0 < month <= 12:
    sum = months[month - 1]
else:
    print 'data error'
sum += day
leap = 0
if (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0)):
    leap = 1
if (leap == 1) and (month > 2):
    sum += 1
print 'it is the %dth day.' % sum

# 5 输入三个整数x,y,z，请把这三个数由小到大输出。
l = []
for i in range(3):
    x = int(raw_input('integer:\n'))
    l.append(x)
l.sort()
print l

# 8 输出 9*9 乘法口诀表。
for i in range(1, 10):
    print 
    for j in range(1, i+1):
        print "%d*%d=%d" % (i, j, i*j),
        
# 11 古典问题：有一对兔子，从出生后第3个月起每个月都生一对兔子，小兔子长到第三个月后每个月又生一对兔子，假如兔子都不死，问每个月的兔子总数为多少？ 
# 程序分析：兔子的规律为数列1,1,2,3,5,8,13,21....
f1 = 1
f2 = 1
for i in range(1,22):
    print '%12ld %12ld' % (f1,f2),
    if (i % 3) == 0:
        print ''
    f1 = f1 + f2
    f2 = f1 + f2

# 题目：判断101-200之间有多少个素数，并输出所有素数。
# 程序分析：判断素数的方法：用一个数分别去除2到sqrt(这个数)，如果能被整除，则表明此数不是素数，反之是素数。 　　　
h = 0
leap = 1
from math import sqrt
from sys import stdout
for m in range(101,201):
    k = int(sqrt(m + 1))
    for i in range(2,k + 1):
        if m % i == 0:
            leap = 0
            break
    if leap == 1:
        print '%-4d' % m
        h += 1
        if h % 10 == 0:
            print ''
    leap = 1
print 'The total is %d' % h

# 13 打印出所有的"水仙花数"，所谓"水仙花数"是指一个三位数，其各位数字立方和等于该数本身。例如：153是一个"水仙花数"，因为153=1的三次方＋5的三次方＋3的三次方。
# 程序分析：利用for循环控制100-999个数，每个数分解出个位，十位，百位。
for n in range(100,1000):
    i = n / 100
    j = n / 10 % 10
    k = n % 10
    if n == i ** 3 + j ** 3 + k ** 3:
        print n

# 14 题目：将一个正整数分解质因数。例如：输入90,打印出90=2*3*3*5。
def reduceNum(n):
    print '{} = '.format(n),
    if not isinstance(n, int) or n <= 0 :
        print '请输入一个正确的数字 !'
        exit(0)
    elif n in [1] :
        print '{}'.format(n)
    while n not in [1] : # 循环保证递归
        for index in xrange(2, n + 1) :
            if n % index == 0:
                n /= index # n 等于 n/index
                if n == 1: 
                    print index 
                else : # index 一定是素数
                    print '{} *'.format(index),
                break
reduceNum(90)

# 16 题目：输出指定格式的日期。
# 程序分析：使用 datetime 模块。
# 输出今日日期，格式为 dd/mm/yyyy。更多选项可以查看 strftime() 方法
print(datetime.date.today().strftime('%d/%m/%Y'))
# 创建日期对象
miyazakiBirthDate = datetime.date(1941, 1, 5)
print(miyazakiBirthDate.strftime('%d/%m/%Y'))
# 日期算术运算
miyazakiBirthNextDay = miyazakiBirthDate + datetime.timedelta(days=1)
print(miyazakiBirthNextDay.strftime('%d/%m/%Y'))
# 日期替换
miyazakiFirstBirthday = miyazakiBirthDate.replace(year=miyazakiBirthDate.year + 1)
print(miyazakiFirstBirthday.strftime('%d/%m/%Y'))

# 17 题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。
s = raw_input('input a string:\n')
letters = 0
space = 0
digit = 0
others = 0
for c in s:
    if c.isalpha():
        letters += 1
    elif c.isspace():
        space += 1
    elif c.isdigit():
        digit += 1
    else:
        others += 1
print 'char = %d,space = %d,digit = %d,others = %d' % (letters,space,digit,others)

# 18 题目：求s=a+aa+aaa+aaaa+aa...a的值，其中a是一个数字。例如2+22+222+2222+22222(此时共有5个数相加)，几个数相加有键盘控制。
#!/usr/bin/python
# -*- coding: UTF-8 -*-
Tn = 0
Sn = []
n = int(raw_input('n = :\n'))
a = int(raw_input('a = :\n'))
for count in range(n):
    Tn = Tn + a
    a = a * 10
    Sn.append(Tn)
    print Tn

Sn = reduce(lambda x,y : x + y,Sn)
print Sn

# 19 题目：一个数如果恰好等于它的因子之和，这个数就称为"完数"。例如6=1＋2＋3.编程找出1000以内的所有完数。
from sys import stdout
for j in range(2,1001):
    k = []
    n = -1
    s = j
    for i in range(1,j):
        if j % i == 0:
            n += 1
            s -= i
            k.append(i)

    if s == 0:
        print j
        for i in range(n):
            stdout.write(str(k[i]))
            stdout.write(' ')
        print k[n]

# 20 一球从100米高度自由落下，每次落地后反跳回原高度的一半；再落下，求它在第10次落地时，共经过多少米？第10次反弹多高？
tour = []
height = []
hei = 100.0 # 起始高度
tim = 10 # 次数
for i in range(1, tim + 1):
    tour.append(hei)
    hei /= 2
    height.append(hei)
print('总高度：tour = {0}'.format(sum(tour)))
print('第10次反弹高度：height = {0}'.format(height[-1]))


# 21 题目：猴子吃桃问题：猴子第一天摘下若干个桃子，当即吃了一半，还不瘾，又多吃了一个第二天早上又将剩下的桃子吃掉一半，又多吃了一个。
# 以后每天早上都吃了前一天剩下的一半零一个。到第10天早上想再吃时，见只剩下一个桃子了。求第一天共摘了多少。
x2 = 1
for day in range(9, 0, -1):
    x1 = (x2 + 1) * 2
    x2 = x1
print x2