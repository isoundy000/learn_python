#-*-coding:utf-8-*-
'''
Created on 2017年9月2日

@author: houguangdong
'''


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
        


if __name__ == "__main__":
    print get_next_player(1)