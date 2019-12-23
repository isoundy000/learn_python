#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import arrow


def main():
    today_begin = arrow.utcnow().to("Asia/Shanghai").floor("day")  # 本地时间今日凌晨
    a = [0, 6, 7, 8, 9, 12, 15, 18, 21]
    time_list = []
    for i in a:
        if i >= 8:
            time_list.append(i - 8)
        else:
            time_list.append(24 - (8 - i))

    print(time_list)
    now_hour = arrow.utcnow().to("Asia/Shanghai").floor("hour")
    flag = 0
    for excute_time in time_list:
        if excute_time == now_hour:
            flag = 1
            break
    print(flag)


if __name__ == '__main__':
    main()