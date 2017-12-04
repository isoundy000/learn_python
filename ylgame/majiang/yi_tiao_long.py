#-*-coding:utf-8-*-
'''
Created on 2017年11月20日

@author: houguangdong
'''
import copy


def check_yi_tiao_long(pai_list):
    """
    一条龙 123456789 (11 11 11 12 12 or 11 12 13 14 14)
    """
    if pai_list.count(1) >= 1 and pai_list.count(2) >= 1 and pai_list.count(3) >= 1 and \
        pai_list.count(4) >= 1 and pai_list.count(5) >= 1 and pai_list.count(6) >= 1 and \
        pai_list.count(7) >= 1 and pai_list.count(8) >= 1 and pai_list.count(9) >= 1:
        for _paiId in xrange(1, 10):
            pai_list.remove(_paiId)
        pai_list.sort()
        for index in range(len(pai_list)):
            if index + 1 < len(pai_list):
                if pai_list[index] == pai_list[index + 1]:
                    tmp_list = copy.copy(pai_list)
                    paiId = pai_list[index]
                    tmp_list.remove(paiId)
                    tmp_list.remove(paiId)
                    if tmp_list[0] == tmp_list[1] and tmp_list[0] == tmp_list[2] or \
                        tmp_list[0] + 1 == tmp_list[1] and tmp_list[0] + 2 == tmp_list[2]:
                        return True
    elif pai_list.count(11) >= 1 and pai_list.count(12) >= 1 and pai_list.count(13) >= 1 and \
        pai_list.count(14) >= 1 and pai_list.count(15) >= 1 and pai_list.count(16) >= 1 and \
        pai_list.count(17) >= 1 and pai_list.count(18) >= 1 and pai_list.count(19) >= 1:
        for _paiId in xrange(11, 20):
            pai_list.remove(_paiId)
        pai_list.sort()
        for index in range(len(pai_list)):
            if index + 1 < len(pai_list):
                if pai_list[index] == pai_list[index + 1]:
                    tmp_list = copy.copy(pai_list)
                    paiId = pai_list[index]
                    tmp_list.remove(paiId)
                    tmp_list.remove(paiId)
                    if tmp_list[0] == tmp_list[1] and tmp_list[0] == tmp_list[2] or \
                        tmp_list[0] + 1 == tmp_list[1] and tmp_list[0] + 2 == tmp_list[2]:
                        return True
    elif pai_list.count(21) >= 1 and pai_list.count(22) >= 1 and pai_list.count(23) >= 1 and \
        pai_list.count(24) >= 1 and pai_list.count(25) >= 1 and pai_list.count(26) >= 1 and \
        pai_list.count(27) >= 1 and pai_list.count(28) >= 1 and pai_list.count(29) >= 1:
        for _paiId in xrange(21, 30):
            pai_list.remove(_paiId)
        pai_list.sort()
        for index in range(len(pai_list)):
            if index + 1 < len(pai_list):
                if pai_list[index] == pai_list[index + 1]:
                    tmp_list = copy.copy(pai_list)
                    paiId = pai_list[index]
                    tmp_list.remove(paiId)
                    tmp_list.remove(paiId)
                    if tmp_list[0] == tmp_list[1] and tmp_list[0] == tmp_list[2] or \
                        tmp_list[0] + 1 == tmp_list[1] and tmp_list[0] + 2 == tmp_list[2]:
                        return True
    return False


if __name__ == '__main__':
    print check_yi_tiao_long([1, 2, 3, 4, 5, 6, 7, 8, 9, 22, 22, 12, 13, 11])