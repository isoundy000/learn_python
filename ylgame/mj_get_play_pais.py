#-*-coding:utf-8-*-
'''
Created on 2017年9月15日

@author: houguangdong
'''

# [1, [21, [22, 23]]], [2, [23, [24, 25]]]
# 1表示playId 21表示其他玩家打出的牌，[22, 23]表示自己手里的牌

playPais = [[[1, [21, [22, 23]]], [2, [23, [24, 25]]]], [[3, [1, [1, 1]]], [4, [2, [2, 2]]]], [], [], []]
_all_list = [[],[],[],[],[]]
index = 0
for _list in playPais:
    list3 = []
    for _list2 in _list:
        if _list2[1][0] > 0:
            list3.append(_list2[1][0])
        list3 += _list2[1][1]
    _all_list[index] = list3
    index += 1
print _all_list
a = [[1, [2, [2,2]]]]