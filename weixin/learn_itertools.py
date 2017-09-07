# -*- encoding: utf-8 -*-
'''
Created on 2017年9月4日

@author: houguangdong
'''
import itertools
for each in itertools.chain('i', 'love', 'python'):
    print each
    
# 返回指定长度的组合
for each in itertools.combinations('abc', 2):
    print each, '1111'

# 返回指定长度的组合 组合内元素可重复
for each in itertools.combinations_with_replacement('abc', 2):
    print each

# 返回指定长度的所有组合  笛卡尔乘积
for each in itertools.product('abc', repeat = 2):
    print each, '2222'

# 返回指定长度为r的排列
for value in itertools.permutations('abc', 2):
    print value

# 返回selector为True的data对应元素
for each in itertools.compress('abcd', [1, 0, 1, 0]):
    print each

# 返回以start开始 step递增的序列，无限递增
i = 0
for each in itertools.count(start=0, step=2):
    print each
    i += 1
    if i > 3:
        break

# 将迭代器进行无限迭代
# for each in itertools.cycle('ab'):
#     print each

# 直到predicate为真，就返回iterable后续数据，否则drop掉
for each in itertools.dropwhile(lambda x: x < 5, [2,1,6,8,2,1]):
    print each

# 返回一组(key, itera), key为iterable的值，itera为等于key的所有项
for key, value in itertools.groupby('aabbbc'):
    print key, list(value)

# 返回predicate结果为True的元素迭代器, 如果predicate为None，则返回所有iterable中为True的项
for value in itertools.ifilter(lambda x: x%2, range(10)):
    print value

# 返回predicate结果为False的元素迭代器, 如果predicate为None，则返回所有iterable中为False的项
for value in itertools.ifilterfalse(lambda x: x % 2, range(10)):
    print value, '333333'
    

# 相当于迭代器方式的map()
for value in itertools.imap(lambda x, y: x+y, (1, 2, 3), (4, 5, 6)):
    print value

# 相当于迭代器方式的切片操作
for value in itertools.islice('abcdefg', 1, 4, 2):
    print value

# 不停的返回object对象，如果指定了times，则返回times次
for value in itertools.repeat('a', 2):
    print value

# 返回function(iter)值，iter为iterable的元素
for value in itertools.starmap(lambda x, y: x * y, [(1, 2), (3, 4)]):
    print value

# 如果predicate为真，则返回iterable元素，如果为假则不再返回break
for value in itertools.takewhile(lambda x: x < 5, [1, 3, 5, 6]):
    print value
