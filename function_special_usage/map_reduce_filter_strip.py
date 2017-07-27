# -*-coding:utf-8-*-
'''
Created on 7/27/2017

@author: houguangdong
'''
# map()函数接收两个参数，一个是函数，一个是序列，map将传入的函数依次作用到序列的每个元素，并把结果作为新的list返回。
def f(x):
    return x*x
print map(f, [1,2,3,4,5])
print map(str, [6,7,8])

# 再看reduce的用法。reduce把一个函数作用在一个序列[x1, x2, x3...]上，这个函数必须接收两个参数，reduce把结果继续和序列的下一个元素做累积计算，其效果就是：
def add(x, y):
    return x + y
print reduce(add, [10, 20, 30])

def fn(x, y):
    return x * 10 + y
print reduce(fn, [1, 3, 5, 7, 9])

# 这个例子本身没多大用处，但是，如果考虑到字符串str也是一个序列，对上面的例子稍加改动，配合map()，我们就可以写出把str转换为int的函数：
def char2num(s):
    return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
print reduce(fn, map(char2num, '13579'))
# 整理成一个str2int的函数就是：
def str2int(s):
    def fn1(x, y):
        return x * 10 + y
    def char2num1(s):
        return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
    return reduce(fn1, map(char2num1, s))
# 还可以用lambda函数进一步简化成：
def char2num2(s):
    return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]

def str2int2(s):
    return reduce(lambda x,y: x*10+y, map(char2num2, s))


# 利用map()函数，把用户输入的不规范的英文名字，变为首字母大写，其他小写的规范名字。输入：['adam', 'LISA', 'barT']，输出：['Adam', 'Lisa', 'Bart']。
# Python提供的sum()函数可以接受一个list并求和，请编写一个prod()函数，可以接受一个list并利用reduce()求积。
def change(l):
    return l.capitalize()

name = ['adam', 'LISA', 'barT']
print map(change, name)

def prod(l):
    return reduce(lambda x , y: x * y, l)
print prod([1, 2, 3, 4, 5])


# Python内建的filter()函数用于过滤序列。
# filter()函数是 Python 内置的另一个有用的高阶函数，filter()函数接收一个函数 f 和一个list，这个函数 f 的作用是对每个元素进行判断，返回 True或 False，filter()根据判断结果自动过滤掉不符合条件的元素，返回由符合条件元素组成的新list。
# 例如，要从一个list [1, 4, 6, 7, 9, 12, 17]中删除偶数，保留奇数，首先，要编写一个判断奇数的函数：
def is_odd(x):
    return x % 2 == 1

# 然后，利用filter()过滤掉偶数：
print filter(is_odd, [1, 4, 6, 7, 9, 12, 17])

# 利用filter()，可以完成很多有用的功能，例如，删除 None 或者空字符串：
def is_not_empty(s):
    return s and len(s.strip()) > 0

print filter(is_not_empty, ['test', None, '', 'str', '  ', 'END'])
# filter()删除1~100的素数
def getPrime(num):
    flag = True
    for x in range(1,101):
        if x != 1 and x != num and num%x == 0:  #非质数返回False，被filter过滤掉
            flag = False
    return flag
print filter(getPrime,range(1,101))
# 请利用filter()过滤出1~100中平方根是整数的数，即结果应该是：
# [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
import math
def is_sqr(x):
    return math.sqrt(x) % 1 == 0
print filter(is_sqr, range(1, 101))


# 注意: s.strip(rm) 删除 s 字符串中开头、结尾处的 rm 序列的字符。
# 当rm为空时，默认删除空白符（包括'\n', '\r', '\t', ' ')，如下：
a = ' 123'
a.strip()

a = '\t\t123\r\n'
a.strip()