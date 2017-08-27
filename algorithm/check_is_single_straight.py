# -*- encoding: utf-8 -*-
'''
Created on 2017年8月25日

@author: houguangdong
'''
def check_is_single_straight(myCards) :
    new_old_pai_list = [3, 4, 5, 6, 7]    
    pai_list =[]
    new_start_index = new_old_pai_list[0] + 1
    _length = len(new_old_pai_list)
    player_pokers = myCards
    
    while 14 - (new_start_index -1) >= _length :
        pai_list2 = []
        for index in range(_length) :
            pai_num = new_start_index + index
            if pai_num not in player_pokers :
                continue
            if pai_num == 14 :
                pai_list2.append(1)
                pai_list2.sort()
            else :
                pai_list2.append(new_start_index + index)
        new_start_index += 1
        if len(pai_list2) == _length :
            pai_list.append(pai_list2)
    
    if len(pai_list) == 0 :
        return False
    return True

print check_is_single_straight([4,6,7,8,10,11,12,13,14])