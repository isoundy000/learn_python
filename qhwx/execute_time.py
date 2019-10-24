#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import arrow


def main():
    today_begin = arrow.utcnow().to("Asia/Shanghai").floor("day")  # 本地时间今日凌晨
    time_list = [i-8 for i in map(int, [0, 6, 9, 12, 15, 18, 21])]
    print time_list
    now_hour = arrow.utcnow().to("Asia/Shanghai").floor("hour")
    flag = 0
    print now_hour, '1111111'
    for i in time_list:
        excute_time = today_begin.shift(hours=+i)

        if excute_time == now_hour:
            flag = 1
            print excute_time, '11111111'
            break
    print flag


if __name__ == '__main__':
    main()