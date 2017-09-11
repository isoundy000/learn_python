# -*-coding:utf-8-*-
'''
Created on 2017年9月9日

@author: houguangdong
'''

# 如何使用python来对二维数组进行复合排序？
# 首先按照第一列排序（索引），在此基础上按第二列排序（索引），在进行第三列排序
import numpy as np
data = np.array([[1,2,3,4,5], [1,2,3,6,7], [2,3,4,5,7], [3,4,5,6,7], [4,5,6,7,8]])
sorted_cols = []
for col_no in range(data.shape[1]):
    sorted_cols.append(data[np.argsort(data[:,col_no])][:,col_no])
sorted_data = np.column_stack(sorted_cols)
print sorted_data


idex=np.lexsort([-1*data[:,2], data[:,1], data[:,0]])
#先按第一列升序，再按第二列升序，再按第三列降序....
#注意先按后边的关键词排序
sorted_data = data[idex, :]
print '111111', sorted_data




# python 按二维数组的某行或列排序 (numpy lexsort)
# lexsort支持对数组按指定行或列的顺序排序；是间接排序，lexsort不修改原数组，返回索引。
# （对应lexsort 一维数组的是argsort a.argsort()这么使用就可以；argsort也不修改原数组， 返回索引）
# 默认按最后一行元素有小到大排序, 返回最后一行元素排序后索引所在位置。
# 设数组a, 返回的索引ind，ind返回的是一维数组
# 对于一维数组, a[ind]就是排序后的数组。
# 对于二维数组下面会详细举例。
 
print a
array([[ 2,  7,  4,  2],
       [35,  9,  1,  5],
       [22, 12,  3,  2]])
 
按最后一列顺序排序
print a[np.lexsort(a.T)]
array([[22, 12,  3,  2],
       [ 2,  7,  4,  2],
       [35,  9,  1,  5]])
 
按最后一列逆序排序
printa[np.lexsort(-a.T)]
array([[35,  9,  1,  5],
       [ 2,  7,  4,  2],
       [22, 12,  3,  2]])
 
按第一列顺序排序
print a[np.lexsort(a[:,::-1].T)]
array([[ 2,  7,  4,  2],
       [22, 12,  3,  2],
       [35,  9,  1,  5]])
 
按最后一行顺序排序
print a.T[np.lexsort(a)].T
array([[ 2,  4,  7,  2],
       [ 5,  1,  9, 35],
       [ 2,  3, 12, 22]])
 
按第一行顺序排序
print a.T[np.lexsort(a[::-1,:])].T
array([[ 2,  2,  4,  7],
       [ 5, 35,  1,  9],
       [ 2, 22,  3, 12]])