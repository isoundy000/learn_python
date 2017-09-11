#-*-coding:utf-8-*-
'''
Created on 2017年9月2日

@author: houguangdong
'''
import copy


def get_next_seat(seat_id):
    """
    获取当前座位的下一个座位号
    """
    if seat_id + 1 > 6:
        return 1
    else:
        return seat_id + 1
    

def get_next_player(seat_id):
    """
    获取指定座位的下一个用户的id
    """
    seat_id = 5
    while True:
        seat_id = get_next_seat(seat_id)
        if seat_id in [1] or seat_id in [6]:
            continue
        else:
            return seat_id


def fa_pai(player_pai_list, pai_list, num):
        for i in range(num):
            if len(pai_list) >= 1:
                player_pai_list.append(pai_list.pop(0))


pai_list = range(1, 55)
def a(pai_list):
    player_poker_list = [[]] * 2
    print player_poker_list
    for i in range(0, 2):
        player_poker_list[i] = copy.deepcopy(player_poker_list[i])
        fa_pai(player_poker_list[i], pai_list, 9)
        print player_poker_list[i], i
    print player_poker_list   


if __name__ == "__main__":
    print get_next_player(1)
    a(pai_list)