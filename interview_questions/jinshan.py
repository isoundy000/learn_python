# -*-coding:utf-8-*-
'''
Created on 2017年5月17日

@author: ghou
'''

a = ['a', 'b', 'c']
b = ['d', 'e', 'f']
for item in zip(a, b):
    print item

# tuple和list的区别
# Tuple是不可变的list.一是创建了一个tuple就不能以任何方式改变它.
# 定义tuple与定义list的方式相同,除了整个元素集是用小括号包围的而不是方括号.
# Tuple的元素与list一样按定义的次序进行排序.Tuples的索引与list一样从0开始,所以一个非空的tuple的第一个元素总是t[0].
# 负数索引与 list 一样从 tuple 的尾部开始计数。
#  与 list 一样分片 (slice) 也可以使用。注意当分割一个 list 时, 会得到一个新的 list ；当分割一个 tuple 时, 会得到一个新的 tuple。
# Tuple 没有方法：没有 append 或 extend 方法、没有 remove 或 pop 方法、没有 index 方法、可以使用 in 来查看一个元素是否存在于 tuple 中。
c = (1, 2, {1: 4})
c[2][0] = 5
print c

# join比+号操作效率高
d = 'a' + 'b' + 'c'
f = ''.join(['a', 'b', 'c'])    
e = '%s%s%s' % ('a', 'b', 'c')
print d, f, e
# 方法1，使用简单直接，但是网上不少人说这种方法效率低
# 之所以说python 中使用 + 进行字符串连接的操作效率低下，是因为python中字符串是不可变的类型，使用 + 连接两个字符串时会生成一个新的字符串，生成新的字符串就需要重新申请内存，当连续相加的字符串很多时(a+b+c+d+e+f+...) ，效率低下就是必然的了
# 方法2，使用略复杂，但对多个字符进行连接时效率高，只会有一次内存的申请。而且如果是对list的字符进行连接的时候，这种方法必须是首选
# 方法3：字符串格式化，这种方法非常常用，本人也推荐使用该方法

# django http请求
# tornado future
# mysql用的什么引擎