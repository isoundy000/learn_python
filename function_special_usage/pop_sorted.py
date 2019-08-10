# -*- encoding: utf-8 -*-
'''
Created on 2/27/2017

@author: houguangdong
'''

a = [{1:1}, {2:2}, {3:3}, {4:4}, {5:5}]
for idx, i in enumerate(a):
    if 3 in i.keys() or 5 in i.keys():
        a.pop(idx)
        print a, '3222'
    print a
    
print sorted([36, 5, 12, 9, 21])
# 此外，sorted()函数也是一个高阶函数，它还可以接收一个比较函数来实现自定义的排序。比如，如果要倒序排序，我们就可以自定义一个reversed_cmp函数：
def reversed_cmp(x, y):
    if x > y:
        return -1
    if x < y:
        return 1
    return 0

# 传入自定义的比较函数reversed_cmp，就可以实现倒序排序：
print sorted([36, 5, 12, 8, 21], reversed_cmp)
print sorted([36, 5, 12, 4, 21], lambda x, y: y - x)
print sorted([36, 5, 12, 3, 21])[::-1]
# 默认情况下，对字符串排序，是按照ASCII的大小比较的，由于'Z' < 'a'，结果，大写字母Z会排在小写字母a的前面。
print sorted(['bob', 'about', 'Zoo', 'Credit'])
# 现在，我们提出排序应该忽略大小写，按照字母序排序。要实现这个算法，不必对现有代码大加改动，只要我们能定义出忽略大小写的比较算法就可以：
def cmp_ignore_case(s1, s2):
    u1 = s1.upper()
    u2 = s2.upper()
    if u1 < u2:
        return -1
    if u1 > u2:
        return 1
    return 0

print sorted(['bob', 'about', 'Zoo', 'Credit'], cmp_ignore_case)

# 2.sorted函数按value值对字典排序
# 要对字典的value排序则需要用到key参数，在这里主要提供一种使用lambda表达式的方法，如下：
d = {'lilee': 25, 'wangyan': 21, 'liqun': 32, 'lidaming': 19}
print sorted(d.items(), key=lambda item: item[1])
# 这里的d.items()实际上是将d转换为可迭代对象，迭代对象的元素为（‘lilee’,25）、（‘wangyan’,21）、（‘liqun’,32）、（‘lidaming’,19），
# items()方法将字典的元素转化为了元组，而这里key参数对应的lambda表达式的意思则是选取元组中的第二个元素作为比较参数
#（如果写作key=lambda item:item[0]的话则是选取第一个元素作为比较对象，也就是key值作为比较对象。lambda x:y中x表示输出参数，y表示lambda函数的返回值），
# 所以采用这种方法可以对字典的value进行排序。注意排序后的返回值是一个list，而原字典中的名值对被转换为了list中的元组。