#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import game_config


def check_time(tformat="%Y-%m-%d,%H:%M", repeat=None, sep=","):
    def trans(x):
        if x is None or not x:
            return False

        if repeat:
            value = x.split(sep)
            for v in value:
                time.strptime(v, tformat)
        else:
            time.strptime(x, tformat)

        return True

    return trans


def check_int_list_args(num):
    """ 检查int_list里面元素的个数

    :param num:
    :return:
    """
    def trans(x):
        if len([i for i in x if isinstance(i, int)]) != len(x):
            return False

        if len(x) != num:
            return False

        return True

    return trans


def check_reward(is_random=False):
    def trans(x):
        lv = 1
        for reward in x:
            if is_random:
                if len(reward) == 4:
                    sort, tid, ran, num = reward
                else:
                    sort, tid, ran, num, lv = reward
                ran = int(ran)
            else:
                if len(reward) == 3:
                    sort, tid, num = reward
                else:
                    sort, tid, num, lv = reward
            sort = int(sort)
            if sort == -1:
                # -1 轮空
                pass
            elif sort in (1, 2, 3, 4, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 23, 24, 26, 27, 100):
                num = int(num)
                if num <= 0:
                    return False
            elif sort == 5:
                # 卡牌
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.character_detail:
                    return False
            elif sort == 6:
                # 道具
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.item:
                    return False
            elif sort == 7:
                # 装备
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.equip:
                    return False
            elif sort == 19:
                # 觉醒宝石
                num = int(num)
                if num <= 0:
                    return False
                tid = str(tid)
                if tid not in game_config.gem:
                    return False
            elif sort == 22:
                # 无主之地的种子
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.seed:
                    return False
            elif sort == 25:
                # 宠物
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.pet_detail:
                    return False
            elif sort == 105:
                # 加指定等级的卡牌
                lv = int(lv)
                num = int(num)
                if num <= 0:
                    return False
                tid = int(tid)
                if tid not in game_config.character_detail:
                    return False
            else:
                return False

        return True

    return trans