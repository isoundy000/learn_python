# -*-coding:utf-8-*-
'''
Created on 2017年8月16日

@author: houguangdong
'''

# source_data:数据集
# search_num:要查找的数
# mid:中间数的键值
def binary_search(source_data, search_num):
    #传入数据集计算中间数键值
    middle = int(len(source_data)/2)
#     print len(source_data)
    #判断要找的数与中间数比较，如果中间数大于要找的数，要找的数在中间数左边
    if source_data[middle] > search_num:
        source_data = source_data[:middle]
        binary_search(source_data, search_num)
    #如果中间数小于要找的数，要找的数在中间数右边
    elif source_data[middle] < search_num:
        source_data = source_data[middle:]
        binary_search(source_data, search_num)
    else:
        # 中间数正好等于要找的数，则打印出来
        print "找到了",source_data[middle]


def binary_search2(source_data, search_num):
    low = 0
    high = len(source_data) - 1
    while low <= high:
        mid = (low + high) / 2
        if source_data[mid] == search_num:
            # return mid
            return source_data[mid]
        # 左半边
        elif source_data[mid] > search_num:
            high = mid - 1
        # 右半边
        elif source_data[mid] < search_num:
            low = mid + 1
    return source_data[high]
    # print -1
    # return -1

        
if __name__ == '__main__':
    source_data = [1, 3, 5, 7, 9]
    #确认数据集的数据个数大于1
    # if int(len(source_data)) > 1:
    #     binary_search(source_data, 1)
    # else:
    #     #如果等于1输出提示信息
    #     print "就一个数不用搜索"
    binary_search2(source_data, 10)