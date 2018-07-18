#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from Source.Log.Write import *

# 变身虎 对敌方全体造成己方阵容平均攻击力*X%的伤害；并使随机b个队友提升c%攻击力，优先后排，持续d回合
def Attack(battle, direct, pos, skill):
    Log.Write("13970", skill)
    Battle = type(battle)
    skillrange = skill["range"]                                     # 修改范围成读取配置 all(全体)、random(随机)、first(前排)、second(后排)、
    randnum = skill["randnum"]                                      # 随机数量
    pet_buff = 0
    round_num = 0
    if "round_num" in skill and skill["round_num"]:                 # 回合数
        round_num = skill["round_num"]
    if "pet_buff" in skill and skill["pet_buff"]:                   # 宠物buff效果倍率
        pet_buff = float(skill["pet_buff"])

    target_func = battle.attack_range_callback["all"]["target"]
    if skillrange == "random":
        targets1 = target_func(battle, direct, pos, randnum)
    else:
        targets1 = target_func(battle, direct, pos)

    sumatk = 0
    sumcount = 0
    for i in xrange(1, 15):
        fighter = battle.GetFighter(direct, i)
        if fighter:
            sumatk += fighter.atk
            sumcount += 1
    atk = int(sumatk * 1.0 / sumcount)                              # 平均攻击力

    attacker = battle.GetFighter(direct, pos)
    old_atk = attacker.atk
    attacker.atk = atk

    for pos1 in targets1:                                           # X%的伤害
        oncedamage = battle.SkillDamageFromTo(skill, direct, pos, pos1, int(skill["count"]))
        battle.AddSumDamage(oncedamage)

    attacker.atk = old_atk

    buff_num = skill["buff_num"]                                    # 随机b个队友
    targets2 = battle.ComputeSecondRandomTargets(not direct, pos, num=buff_num)
    Log.Write("targets2", targets2)
    for pos2 in targets2:
        fighter = battle.GetFighter(direct, pos2)
        battle.AddPromote(fighter, "atk", pet_buff, round_num)      # 提升%c攻击力
    battle.DealCallEx()
    return targets1