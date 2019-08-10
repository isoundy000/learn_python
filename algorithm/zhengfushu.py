# -*- encoding: utf-8 -*-
'''
Created on 2018年8月14日

@author: houguangdong
'''

a = [-1, -3, 4, 5, -7, -8, -9, 10, -11, 12]

def test1():
    tmp = []
    for _, i in enumerate(a):
        if _ == 0 and i > 0:
            flag = True
        elif _ == 0 and i < 0:
            flag = False

        if _ % 2 == 0:
            tmp.append(abs(i) if flag else -abs(i))
        else:
            tmp.append(-abs(i) if flag else abs(i))


    return tmp


def main(arr):
    '''
    一个正数一个负数的输出
    :param arr:
    :return:
    '''
    arr_index_1 = []
    arr_index_2 = []

    index = 0
    for value in arr:
        if value > 0:
            arr_index_1.append(value)
        elif value < 0:
            arr_index_2.append(value)
        index += 1

    arr = []
    for i in xrange(len(arr_index_1)):
        arr.append(arr_index_1[i])
        arr.append(arr_index_2[i])
    return arr


if __name__ == '__main__':
    print main(a)
    print test1()