# -*-coding:utf-8-*-
'''
Created on 2017年5月10日

@author: ghou
'''


# Python for 循环语句
# 
# Python for循环可以遍历任何序列的项目，如一个列表或者一个字符串。
# 
# 语法：
# 
# for循环的语法格式如下：
# 
# for iterating_var in sequence:
#    statements(s)
# 
# 流程图：
# python_for_loop
# 
# 实例：
# 实例
# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
#  
# for letter in 'Python':     # 第一个实例
#    print '当前字母 :', letter
#  
# fruits = ['banana', 'apple',  'mango']
# for fruit in fruits:        # 第二个实例
#    print '当前水果 :', fruit
#  
# print "Good bye!"
# 
# 尝试一下 »
# 
# 以上实例输出结果:
# 
# 当前字母 : P
# 当前字母 : y
# 当前字母 : t
# 当前字母 : h
# 当前字母 : o
# 当前字母 : n
# 当前水果 : banana
# 当前水果 : apple
# 当前水果 : mango
# Good bye!
# 
# 
# 通过序列索引迭代
# 
# 另外一种执行循环的遍历方式是通过索引，如下实例：
# 实例
# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
#  
# fruits = ['banana', 'apple',  'mango']
# for index in range(len(fruits)):
#    print '当前水果 :', fruits[index]
#  
# print "Good bye!"
# 
# 以上实例输出结果：
# 
# 当前水果 : banana
# 当前水果 : apple
# 当前水果 : mango
# Good bye!
# 
# 以上实例我们使用了内置函数 len() 和 range(),函数 len() 返回列表的长度，即元素的个数。 range返回一个序列的数。
# 
# 循环使用 else 语句
# 
# 在 python 中，for … else 表示这样的意思，for 中的语句和普通的没有区别，else 中的语句会在循环正常执行完（即 for 不是通过 break 跳出而中断的）的情况下执行，while … else 也是一样。
# 实例
# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
#  
# for num in range(10,20):  # 迭代 10 到 20 之间的数字
#    for i in range(2,num): # 根据因子迭代
#       if num%i == 0:      # 确定第一个因子
#          j=num/i          # 计算第二个因子
#          print '%d 等于 %d * %d' % (num,i,j)
#          break            # 跳出当前循环
#    else:                  # 循环的 else 部分
#       print num, '是一个质数'
# 
# 尝试一下 »
# 
# 以上实例输出结果：
# 
# 10 等于 2 * 5
# 11 是一个质数
# 12 等于 2 * 6
# 13 是一个质数
# 14 等于 2 * 7
# 15 等于 3 * 5
# 16 等于 2 * 8
# 17 是一个质数
# 18 等于 2 * 9
# 19 是一个质数
# 
# 更多实例：python 打印菱形、三角形、矩形
# ← Python While 循环语句
# Python 循环嵌套 →
# 笔记列表
# 
#        缘分天注定
# 
#       738657641@qq.com
# 
#       参考地址
# 
#     使用内置 enumerate 函数进行遍历:
# 
#     for index, item in enumerate(sequence):
#         process(index, item)
# 
#     实例
# 
#     >>> sequence = [12, 34, 34, 23, 45, 76, 89]
#     >>> for i, j in enumerate(sequence):
#     ...     print i,j
#     ... 
#     0 12
#     1 34
#     2 34
#     3 23
#     4 45
#     5 76
#     6 89
# 
#     缘分天注定
# 
#        缘分天注定
# 
#       738657641@qq.com
# 
#       参考地址
#     2个月前 (02-27)
# 
#        shenwenwin
# 
#       shenwenwin@163.com
#     for 使用案例
# 
#     使用list.append()模块对质数进行输出。
# 
#     #!/usr/bin/python
#     # -*- coding: UTF-8 -*-
# 
#     # 输出 2 到 100 简的质数
#     prime = []
#     for num in range(2,100):  # 迭代 2 到 100 之间的数字
#        for i in range(2,num): # 根据因子迭代
#           if num%i == 0:      # 确定第一个因子
#              break            # 跳出当前循环
#        else:                  # 循环的 else 部分
#           prime.append(num)
#     print prime
# 
#     输出结果：
# 
#     [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
# 
#     shenwenwin
# 
#        shenwenwin
# 
#       shenwenwin@163.com
#     3周前 (04-19)
# 
#        kimiYang
# 
#       943368010@qq.com
# 
#     打印空心等边三角形:
# 
#     #!/usr/bin/python
#     # -*- coding: UTF-8 -*-
# 
#     # 打印空心等边三角形 
#     rows = int(raw_input('输入行数：'))
#     for i in range(0, rows):
#         for k in range(0, 2 * rows - 1):
#             if (i != rows - 1) and (k == rows - i - 1 or k == rows + i - 1):
#                 print " * ",
#             elif i == rows - 1:
#                 if k % 2 == 0:
#                     print " * ",
#                 else:
#                     print "   ",
#             else:
#                 print "   ",
#         print "\n"