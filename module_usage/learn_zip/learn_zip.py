# -*- encoding: utf-8 -*-
'''
Created on 2017年9月11日

@author: houguangdong
'''
# Python的zip函数
# zip函数接受任意多个（包括0个和1个）序列作为参数，返回一个tuple列表。具体意思不好用文字来表述，直接看示例：
# 1.示例1
x = [1, 2, 3]
y = [4, 5, 6]
z = [7, 8, 9]
xyz = zip(x, y, z)
print xyz


# 2.示例2：
xy = zip(x, y)
print xy


# 3.示例3：
# x = zip(x)
# print x


# 4.示例4：
# x = zip()
# print x


# 5.示例5：一般认为这是一个unzip的过程，它的运行机制是这样的：
xyz = zip(x, y, z)
# 在运行zip(*xyz)之前，xyz的值是：[(1, 4, 7), (2, 5, 8), (3, 6, 9)]
print xyz
u = zip(*xyz)
# 那么，zip(*xyz) 等价于 zip((1, 4, 7), (2, 5, 8), (3, 6, 9))
print u
# 所以，运行结果是：[(1, 2, 3), (4, 5, 6), (7, 8, 9)]
# 注：在函数调用中使用*list/tuple的方式表示将list/tuple分开，作为位置参数传递给对应函数（前提是对应函数支持不定个数的位置参数）


# 6.示例6：
x = [1, 2, 3]
r = zip(* [x] * 3)
print r
# 运行的结果是：
# [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
# [x]生成一个列表的列表，它只有一个元素x
# [x] * 3生成一个列表的列表，它有3个元素，[x, x, x]
# zip(* [x] * 3)的意思就明确了，zip(x, x, x)


# zip 和 izip , izip_longest比较
# zip是build-in方法
# 而izip是itertools中的一个方法
# 这两个方法的作用是相似的，但是具体使用中有什么区别呢？今天来探究一下。
# zip
# 就是把多个序列或者是迭代器的元素，组合成元组。返回的元组的长度是所有输入序列中最短的
a = ['a', 'b', 'c', 'd', 'e']  
b = range(10)  
print zip(a,b)  
# 组合之后的元组长度是依照两个输入序列中最短的a为准的。
# 如果输入的两个序列都是特别大的情况，zip就会很慢了。使用izip比较下。
a = range(10000000)  
b = range(10000000)
import timeit
# print %timeit(zip(a, b), xrange(1000000)))
import itertools  
# print %timeit(itertools.izip(xrange(10000000), xrange(1000000)))
# 这样看izip会快的多。
# izip
# 把不同的迭代器的元素聚合到一个迭代器中。类似zip（）方法，但是返回的是一个迭代器而不是一个list。用于同步迭代一次几个iterables
# orangleliu： 因为返回的是一个迭代器，并且同步迭代，所以速度比较快。
# izip_longest
# 也就是说这个zip方法使用izip一样的原理，但是会使用最长的迭代器来作为返回值的长度，并且可以使用fillvalue来制定那些缺失值的默认值
a = ['a','b','c']  
b = range(10)  
c = itertools.izip_longest(a,b,fillvalue=-1)  
for i in c:  
    print i  
# 探究一下，基本的区别就是这些，具体的使用要看具体的编程场景。