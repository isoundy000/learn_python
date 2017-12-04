#-*-coding:utf-8-*-
'''
Created on 2017年11月27日

@author: houguangdong
'''
import copy

shou_pai = [24, 17, 31, 12, 1, 13, 33, 22, 17, 17, 17]
shou_pai1 = copy.deepcopy(shou_pai)
copy_kou_pai_list = [24, 17, 31, 12, 1, 13, 33, 22]

def main():
    a = [1, 1]
    if a[0] == 1:
        num = 0
        copy_shou = copy.deepcopy(shou_pai)
        copy_kou_pai_list1 = copy.deepcopy(copy_kou_pai_list)
        for pai1 in copy_shou:
            if pai1 in copy_kou_pai_list1:
                shou_pai.remove(pai1)
                copy_kou_pai_list1.remove(pai1)
                if pai1 == 17:
                    num += 1
                if not copy_kou_pai_list1:
                    break
        print shou_pai, '11111111', num
        shou_pai2 = copy.deepcopy(shou_pai)
        for pai in shou_pai2:
            if pai == 17:
                if num > 1:
                    break
                num += 1
                shou_pai.remove(pai)
        print shou_pai
    if a[1] == 1:
        num = 0
        copy_shou = copy.deepcopy(shou_pai1)
        copy_kou_pai_list2 = copy.deepcopy(copy_kou_pai_list)
        for pai2 in copy_shou:
            if pai2 in copy_kou_pai_list2:
                shou_pai1.remove(pai2)
                copy_kou_pai_list2.remove(pai2)
                if pai2 == 17:
                    num += 1
                if not copy_kou_pai_list2:
                    break
        print shou_pai1, '2222222', num
        shou_pai3 = copy.deepcopy(shou_pai1)
        for pai in shou_pai3:
            if pai == 17:
                if num > 2:
                    break
                num += 1
                shou_pai1.remove(pai)
        print shou_pai1

if __name__ == '__main__':
    main()
