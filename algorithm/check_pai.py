# -*- encoding: utf-8 -*-
'''
Created on 2017年8月30日

@author: houguangdong
'''

import random
import copy


POKER_LIST = [
    101,102,103,104,105,106,107,108,109,110,111,112,113, # 方块
    201,202,203,204,205,206,207,208,209,210,211,212,213, # 梅花
    301,302,303,304,305,306,307,308,309,310,311,312,313, # 红桃
    401,402,403,404,405,406,407,408,409,410,411,412,413, # 黑桃
    516,517 # 小王 大王
] 


def get_weight(pokerId):
    num = pokerId % 100
    if num in [17, 16]:        
        return num + 1
    elif num == 3:
        return 16
    elif num == 2: 
        return 15
    elif num == 1:
        return 14
    else:
        return num
    

def check_play_pai(poker_list, poker_type):
    hun_num = 0
    weight_list = []
    # 不是混牌的权重
    no_hun_weight = []
    poker_list_copy = copy.deepcopy(poker_list)
    for pokerId in poker_list_copy:
        poker_weight = get_weight(pokerId)
        if poker_weight in [18, 17, 16, 15]:
            hun_num += 1
        else:
            no_hun_weight.append(poker_weight)
        weight_list.append(poker_weight)
    
    weight_list = sorted(weight_list)
    no_hun_length = len(set(copy.deepcopy(no_hun_weight)))
    if poker_type == 2 and len(weight_list) == 2:
        if hun_num >= 1:
            return True, weight_list
        elif no_hun_length == 1:
            return True, weight_list
    elif poker_type == 3 and len(weight_list) == 3:
        if hun_num >= 2:
            return True, weight_list
        elif no_hun_length == 1:
            return True, weight_list
    elif poker_type == 4 and len(weight_list) == 4:
        if hun_num > 3:
            return True, weight_list
        elif no_hun_length == 1:
            return True, weight_list
    return False, weight_list


if __name__ == "__main__":
    for i in range(10):
        pai_list = random.sample(POKER_LIST, 2)
        print pai_list
        print check_play_pai(pai_list, 2)
        print '*' * 10