#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


energy = {
    1: 1000,
    2: 2000,
    3: 3000,
    4: 4000,
    5: 5000
}

pwData = {1: [1000, 0, 0], 2: [2000, 0, 0], 3: [3000, 0, 0], 4: [3880, 0, 0], 5: [0, 0, 0]}


def _getEnergyIdx(fishPool, fpMultiple):
    """
    获取当前充能阶段的段位
    """
    level = 1
    spin_level = 0
    for lv, val in sorted(energy.items(), key=lambda d: d[0], reverse=True):
        if int(pwData.get(lv, [0])[0]) >= val:
            level = lv + 1
            break
    if level > max(energy.keys()):
        level -= 1
    if level > min(energy.keys()) and level < max(energy.keys()):
        spin_level = level - 1
    if level == max(energy.keys()):
        if pwData.get(level, [0])[0] >= energy.get(level, 0):
            spin_level = level
        else:
            spin_level = level - 1
    return level, spin_level


if __name__ == '__main__':
    print _getEnergyIdx(1, 1)