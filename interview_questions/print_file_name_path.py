# -*- encoding: utf-8 -*-
'''
Created on 2018年5月26日

@author: houguangdong
'''
import os


def search_and_file_path(str1=''):
    path1 = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
    for parent, dirnames, filenames in os.walk(path1):
        # print "父路径: ", parent, "文件夹名: ", dirnames, "文件名: ", filenames
        for filename in filenames:
            if not str1:
                continue
            if os.path.splitext(filename)[0].find(str1) > 0:
                print os.path.join(parent, filename)


def find_index(num, target):
    result = []
    for i, k in enumerate(num):
        num2 = list(num)
        num2.remove(k)
        if target - k in num2:
            result.append(i)
    print result



def main():
    search_and_file_path('bo')
    find_index([3, 1, 7, 3, 4, 5], 6)


if __name__ == '__main__':
    main()