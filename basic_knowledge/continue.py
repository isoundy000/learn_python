# -*-coding:utf-8-*-
'''
Created on 2017年5月10日

@author: ghou
'''


# Python continue 语句
# 
# Python continue 语句跳出本次循环，而break跳出整个循环。
# 
# continue 语句用来告诉Python跳过当前循环的剩余语句，然后继续进行下一轮循环。
# 
# continue语句用在while和for循环中。
# 
# Python 语言 continue 语句语法格式如下：
# 
# continue
# 
# 流程图：
# cpp_continue_statement
# 
# 实例：
# 实例(Python 2.0+)
# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
#  
# for letter in 'Python':     # 第一个实例
#    if letter == 'h':
#       continue
#    print '当前字母 :', letter
#  
# var = 10                    # 第二个实例
# while var > 0:              
#    var = var -1
#    if var == 5:
#       continue
#    print '当前变量值 :', var
# print "Good bye!"
# 
# 以上实例执行结果：
# 
# 当前字母 : P
# 当前字母 : y
# 当前字母 : t
# 当前字母 : o
# 当前字母 : n
# 当前变量值 : 9
# 当前变量值 : 8
# 当前变量值 : 7
# 当前变量值 : 6
# 当前变量值 : 4
# 当前变量值 : 3
# 当前变量值 : 2
# 当前变量值 : 1
# 当前变量值 : 0
# Good bye!
# 
# ← Python break 语句
# Python pass 语句 →
# 笔记列表
# 
#        airmin
# 
#       lauranceair@gmail.com
# 
#     continue 语句是一个删除的效果，他的存在是为了删除满足循环条件下的某些不需要的成分:
# 
#     #!/usr/bin/python
#     # -*- coding: UTF-8 -*-
# 
#     var = 10
# 
#     while var > 0:
#         var = var -1
#         if var == 5 or var == 8:
#             continue
#         print '当前值 :', var
#     print "Good bye!"
# 
#     这里效果是去掉5和8，执行效果如下:
# 
#     当前值 : 9
#     当前值 : 7
#     当前值 : 6
#     当前值 : 4
#     当前值 : 3
#     当前值 : 2
#     当前值 : 1
#     当前值 : 0
#     Good bye!
# 
#     airmin
# 
#        airmin
# 
#       lauranceair@gmail.com
#     2周前 (04-26)
# 
#        jinchengsong
# 
#       821304345@qq.com
# 
#     我们想只打印0-10之间的奇数，可以用continue语句跳过某些循环：
# 
#     #!/usr/bin/python
#     # -*- coding: UTF-8 -*-
# 
#     n = 0
#     while n < 10:
#         n = n + 1
#         if n % 2 == 0:      # 如果n是偶数，执行continue语句
#             continue        # continue语句会直接继续下一轮循环，后续的print()语句不会执行
#         print(n)