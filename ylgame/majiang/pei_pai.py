#-*-coding:utf-8-*-
'''
Created on 2017年11月23日

@author: houguangdong
'''
import copy

WAN_PAI = [
    1, 2, 3, 4, 5, 6, 7, 8, 9,                  # 万（1-9）
    1, 2, 3, 4, 5, 6, 7, 8, 9,                  # 万（1-9）
    1, 2, 3, 4, 5, 6, 7, 8, 9,                  # 万（1-9）
    1, 2, 3, 4, 5, 6, 7, 8, 9,                  # 万（1-9）
]


TONG_PAI = [
    11, 12, 13, 14, 15, 16, 17, 18, 19,         # 筒（11-19）
    11, 12, 13, 14, 15, 16, 17, 18, 19,         # 筒（11-19）
    11, 12, 13, 14, 15, 16, 17, 18, 19,         # 筒（11-19）
    11, 12, 13, 14, 15, 16, 17, 18, 19,         # 筒（11-19）
]


TIAO_PAI = [
    21, 22, 23, 24, 25, 26, 27, 28, 29,         # 条（21-29）
    21, 22, 23, 24, 25, 26, 27, 28, 29,         # 条（21-29）
    21, 22, 23, 24, 25, 26, 27, 28, 29,         # 条（21-29）
    21, 22, 23, 24, 25, 26, 27, 28, 29,         # 条（21-29）
]


PAI = WAN_PAI + TONG_PAI + TIAO_PAI             # 牌


DONG_FENG = [31, 31, 31, 31]                    # 东
XI_FENG = [32, 32, 32, 32]                      # 西
NAN_FENG = [33, 33, 33, 33]                     # 南
BEI_FENG = [34, 34, 34, 34]                     # 北
ZHONG_FENG = [35, 35, 35, 35]                   # 中
FA_FENG = [36, 36, 36, 36]                      # 发
BAI_FENG = [37, 37, 37, 37]                     # 白


FENG_PAI = DONG_FENG + XI_FENG + NAN_FENG + BEI_FENG

JIAN_PAI = ZHONG_FENG + FA_FENG + BAI_FENG

PAI_FENG = FENG_PAI + JIAN_PAI                  # 东西南北中发白31, 32, 33, 34, 35, 36, 37


a_136 = copy.deepcopy(PAI + PAI_FENG)
b = [1,1,2,3,4,4,4,5,5,5,6,6,6,11,11,12,12,13,13,14,14,15,15,16,16,1,21,21,22,22,23,23,24,24,25,25,3,19,25,31,31,32,32,33,33,34,34,35,35,36,36,37]
qi_shou = [19,19,18,2,16,1]
z = b + qi_shou
def main():
    for pai in z:
        if pai in a_136:
            a_136.remove(pai)
    
if __name__ == '__main__':
    main()