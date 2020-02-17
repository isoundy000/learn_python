#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 一个有趣的python排序模块：bisect
# 今天同事说到了一个python的排序模块bisect，觉得挺有趣的，跟大家分享分享。
#        先看看模块的结构：
import bisect
print dir(bisect)

# 前面五个属性大家感兴趣可以打出来看看数值，这里就不介绍了。
#        先说明的是，使用这个模块的函数前先确保操作的列表是已排序的。
data = [4, 2, 9, 7]
data.sort()
print data

# 先看看 insort  函数：
bisect.insort(data, 3)
print data

# 其插入的结果是不会影响原有的排序。
#        再看看 bisect  函数：
print bisect.bisect(data, 1)
print data

# 其目的在于查找该数值将会插入的位置并返回，而不会插入。
#        接着看 bisect_left 和 bisect_right 函数，该函数用入处理将会插入重复数值的情况，返回将会插入的位置：
print bisect.bisect_left(data, 4)
print bisect.bisect_right(data, 4)
print data

# 其对应的插入函数是 insort_left  和 insort_right ：
bisect.insort_left(data, 4)
print data
data = [2, 3, 4, 7, 9]
bisect.insort_right(data, 4)
print data
# 可见，单纯看其结果的话，两个函数的操作结果是一样的，其实插入的位置不同而已。