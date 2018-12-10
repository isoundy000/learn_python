# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
# from learn_4 import *
# print datetime.now()


# def a():
#     while True:
#         while True:
#             raise Exception('111111')


import string
space = string.whitespace


def lspt(userenter):
    data = list(userenter)
    print data, '2222222'
    for i, j in enumerate(data):
        print '11111111', j
        if j not in space:
            break
        data.pop(i)
    return ''.join(data)


if __name__ == '__main__':
    # a()
    UserEnter = raw_input("Enter str: ")
    print lspt(UserEnter)