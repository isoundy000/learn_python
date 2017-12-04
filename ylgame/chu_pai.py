#-*-coding:utf-8-*-
'''
Created on 2017年9月13日

@author: houguangdong
'''
import copy


def get_weight(pokerId):
    num = pokerId % 100
    if num in [17, 16]:        
        return num + 1
    # 牌的权重 3 16
    elif num == 3:
        return 16
    # 牌的权重 2 15
    elif num == 2: 
        return 15
    # 牌的权重 A 14
    elif num == 1:
        return 14
    else:
        return num


def check_play_pai(poker_list, poker_type, state=True):
    '''
    poker_list 出的牌
    poker_type 2: AA
               3: AAA
               4: AAAA
    state 是否检查是不是手牌
    return True [4,4,4,4] 权重
    '''
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
        elif hun_num == 1 and no_hun_length == 1:
            return True, weight_list
        elif no_hun_length == 1:
            return True, weight_list
    elif poker_type == 4 and len(weight_list) == 4:
        if hun_num > 3:
            return True, weight_list
        elif hun_num == 2 and no_hun_length == 1:
            return True, weight_list
        elif hun_num == 1 and no_hun_length == 1:
            return True, weight_list
        elif no_hun_length == 1:
            return True, weight_list
    return False, weight_list


if __name__ == '__main__':
    state1, play_poker_weight1 = check_play_pai([102, 302, 516, 311], 4)
    state, play_poker_weight = check_play_pai([210, 410, 303, 403], 4)
    print state, state1, play_poker_weight, play_poker_weight1
    