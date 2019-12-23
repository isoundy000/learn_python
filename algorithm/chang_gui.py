#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/14 00:24

def low_base(a, b):
    '''
    初级底薪
    :param a: 人次标准
    :param b: 项目数标准
    :return:
    '''
    low_people = [50, 51, 56, 57, 67, 68, 73, 74]
    low_num = [91, 92, 101, 102, 121, 122, 131, 132]
    base = [2000, 2200, 2500, 2800, 3000]
    money = 0
    if a <= low_people[0] and b <= low_num[0]:
        money = base[0]
    elif low_people[1] <= a <= low_people[2] and low_num[1] <= b <= low_num[2]:
        money = base[1]
    elif low_people[3] <= a <= low_people[4] and low_num[3] <= b <= low_num[4]:
        money = base[2]
    elif low_people[5] <= a <= low_people[6] and low_num[5] <= b <= low_num[6]:
        money = base[3]
    elif low_people[7] <= a and low_num[7] <= b:
        money = base[4]
    return money


def middle_base(a, b):
    '''
    中级底薪
    :param a: 人次标准
    :param b: 项目数标准
    :return:
    '''
    middle_people = [65, 66, 71, 72, 82, 83, 88, 89]
    middle_num = [131, 132, 142, 143, 164, 165, 176, 177]
    middle_base = [3500, 3700, 4000, 4300, 4500]
    money = 0
    if a <= middle_people[0] and b <= middle_num[0]:
        money = middle_base[0]
    elif middle_people[1] <= a <= middle_people[2] and middle_num[1] <= b <= middle_num[2]:
        money = middle_base[1]
    elif middle_people[3] <= a <= middle_people[4] and middle_num[3] <= b <= middle_num[4]:
        money = middle_base[2]
    elif middle_people[5] <= a <= middle_people[6] and middle_num[5] <= b <= middle_num[6]:
        money = middle_base[3]
    elif middle_people[7] <= a and middle_num[7] <= b:
        money = middle_base[4]
    return money


def high_base(a, b):
    '''
    高级底薪
    :param a: 人次标准
    :param b: 项目数标准
    :return:
    '''
    high_people = [80, 81, 86, 87, 97, 98, 103, 104]
    high_num = [176, 177, 189, 190, 213, 214, 226, 227]
    high_base = [5000, 5300, 5500, 5700, 6000]
    money = 0
    if a <= high_people[0] and b <= high_num[0]:
        money = high_base[0]
    elif high_people[1] <= a <= high_people[2] and high_num[1] <= b <= high_num[2]:
        money = high_base[1]
    elif high_people[3] <= a <= high_people[4] and high_num[3] <= b <= high_num[4]:
        money = high_base[2]
    elif high_people[5] <= a <= high_people[6] and high_num[5] <= b <= high_num[6]:
        money = high_base[3]
    elif high_people[7] <= a and high_num[7] <= b:
        money = high_base[4]
    return money


def hhigh_base(a, b):
    '''
    高+级底薪
    :param a: 人次标准
    :param b: 项目数标准
    :return:
    '''
    hhigh_people = [95, 96, 101, 102, 107, 108, 113, 114]
    hhigh_num = [209, 210, 222, 223, 235, 236, 248, 249]
    hhigh_base = [6500, 6800, 7000, 7200, 7500]
    money = 0
    if a <= hhigh_people[0] and b <= hhigh_num[0]:
        money = hhigh_base[0]
    elif hhigh_people[1] <= a <= hhigh_people[2] and hhigh_num[1] <= b <= hhigh_num[2]:
        money = hhigh_base[1]
    elif hhigh_people[3] <= a <= hhigh_people[4] and hhigh_num[3] <= b <= hhigh_num[4]:
        money = hhigh_base[2]
    elif hhigh_people[5] <= a <= hhigh_people[6] and hhigh_num[5] <= b <= hhigh_num[6]:
        money = hhigh_base[3]
    elif hhigh_people[7] <= a and hhigh_num[7] <= b:
        money = hhigh_base[4]
    return money


def main(money, cost_money, da_monery, jia_ju, jia_fa, bi_li, chen_shui_num, tuo_ke_ka, xin_ke_ka, gong_ling, a, b):
    '''
    底薪+提成
    :param money: 充值的钱数
    :param cost_money: 耗卡的钱数
    :param da_monery: 大项目的汇款金额
    :param jia_ju: 家具产品的金额
    :param jia_fa: 奖罚人数
    :param bi_li: 产品销售占耗卡业绩比例
    :param gong_ling: 工龄n年
    :param a: 人次标准
    :param b: 项目数
    :return:
    '''
    low_t = [8000, 12000, 18000, 21999]
    low_p = [0.07, 0.08, 0.09]
    middle_t = [22000, 28000, 35000, 45000]
    middle_p = [0.08, 0.09, 0.1]
    high_t = [45000, 55000, 65000, 75000]
    high_p = [0.09, 0.1, 0.11]
    hhigh_t = [75000, 85000, 100000, 200000]
    hhigh_p = [0.1, 0.11, 0.12]
    if money < low_t[0]:
        base = 1500
        ti_money = cost_money * low_p[0]
    elif low_t[0] <= money <= low_t[-1]:
        base = low_base(a, b)
        if cost_money < low_t[0]:
            ti_money = cost_money * low_p[0]
        elif low_t[0] <= cost_money < low_t[1]:
            ti_money = cost_money * low_p[0]
        elif low_t[1] <= cost_money < low_t[2]:
            ti_money = cost_money * low_p[1]
        elif low_t[2] <= cost_money <= low_t[3]:
            ti_money = cost_money * low_p[2]
        else:
            ti_money = cost_money * low_p[2]

    elif middle_t[0] <= money <= middle_t[-1]:
        base = middle_base(a, b)
        if cost_money < middle_t[0]:
           ti_money = cost_money * middle_p[0]
        elif middle_t[0] <= cost_money < middle_t[1]:
            ti_money = cost_money * middle_p[0]
        elif middle_t[1] <= cost_money < middle_t[2]:
            ti_money = cost_money * middle_p[1]
        elif middle_t[2] <= cost_money <= middle_t[3]:
            ti_money = cost_money * middle_p[2]
        else:
            ti_money = cost_money * middle_p[2]

    elif high_t[0] <= money <= high_t[-1]:
        base = high_base(a, b)
        if cost_money < high_t[0]:
            ti_money = cost_money * high_t[0]
        elif high_t[0] <= cost_money < high_t[1]:
            ti_money = cost_money * high_p[0]
        elif high_t[1] <= cost_money < high_t[2]:
            ti_money = cost_money * high_p[1]
        elif high_t[2] <= cost_money <= high_t[3]:
            ti_money = cost_money * high_p[2]
        else:
            ti_money = cost_money * high_p[2]

    elif hhigh_t[0] <= money <= hhigh_t[-1]:
        base = hhigh_base(a, b)
        if cost_money < hhigh_t[0]:
            ti_money = cost_money * hhigh_p[0]
        elif hhigh_t[0] <= cost_money < hhigh_t[1]:
            ti_money = cost_money * hhigh_p[0]
        elif hhigh_t[1] <= cost_money < hhigh_t[2]:
            ti_money = cost_money * hhigh_p[1]
        elif hhigh_t[2] <= cost_money <= hhigh_t[3]:
            ti_money = cost_money * hhigh_p[2]
        else:
            ti_money = cost_money * hhigh_p[2]
    else:
        base = 7000
        ti_money = cost_money * hhigh_p[2]

    print('基本工资: %s' % base)
    print('耗卡提成: %s' % ti_money)
    get_money = base + ti_money

    # 大项目提成
    if da_monery:
        print('大项目提成: %s' % (da_monery * 0.06))
        get_money += da_monery * 0.06

    # 家具产品提成
    if jia_ju:
        print('家具产品提成: %s' % (jia_ju * 0.06))
        get_money += jia_ju * 0.06

    # 奖罚部分
    if jia_fa >= 3:
        print('新客成交奖励: 200')
        get_money += 200

    # 产品销售占耗卡业绩比例
    if bi_li < 0.1:
        print('产品销售占耗卡业绩比例没完成 罚钱: 200')
        get_money -= 200
    elif bi_li > 0.25:
        print('产品销售占耗卡业绩比例完成 奖励: 200')
        get_money += 200

    if chen_shui_num:
        print('沉睡顾客唤醒')
        get_money += chen_shui_num * 30

    if tuo_ke_ka:
        print('拓客卡: %s' % (tuo_ke_ka * 50))
        get_money += tuo_ke_ka * 50

    if xin_ke_ka:
        print('新客卡: %s' % (xin_ke_ka * 100))
        get_money += xin_ke_ka * 100

    # 工龄
    if gong_ling:
        print('工龄: %s' % (gong_ling * 50))
        get_money += gong_ling * 50

    # 饭补
    print('饭补: 400')
    get_money += 400

    print('获得的工资: %s' % get_money)


if __name__ == '__main__':
    print "充值钱数_耗卡钱数_大项目钱数_家具产品钱数_奖罚人数_产品销售占耗卡业绩比例_沉睡顾客数量_拓客卡_新客卡_工龄_人次标准_项目数："
    a = str(raw_input('请输入数据 格式为上面'))
    if len(a.strip().split('_')) != 12:
        raise
    ls = map(int, a.split('_'))
    main(*ls)