#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import game_config
from lib.utils import weight_choice
from return_msg_config import i18n_msg


def add_gift_by_weights(user, gift_config, cur_data={}, save=True):
    """获取礼物
    args：
        user : logics.user 实例
        gift_config： 礼物配置  eg: [[1,0,100,10], [2,0,100,10]]
            1、食品，占位，参数数量,权重；[1,0,100,10]
            2、金属，占位，参数数量,权重；[2,0,100]
            .....
        cur_data: 已获得的礼物数据，用于 多次调用add_gift时候统计总共获得的礼物
    """
    _gift_config = weight_choice(gift_config)
    return add_gift(user, [_gift_config], cur_data=cur_data, save=save)


def add_gift(user, gift_config, cur_data={}, save=True):
    """获取礼物
    args：
        user : logics.user 实例
        gift_config： 礼物配置  eg: [[1,0,100], [2,0,100]]
            1、食品，占位，参数数量；[1,0,100]
            2、金属，占位，参数数量；[2,0,100]
            3、能源，占位，能源数量；[3,0,100]
            4、能晶，占位，能晶数量；[4,0,100]
            5、卡牌，卡牌ID,数量；[5,4,1]
            6、道具，ID,数量；[6,4,1]
            7、装备,ID，数量；[7,4,1]
            8、玩家经验，占位，数值;[8,0,100]
            9、金币,占位，数量;[9,0,1]
            10、强能之尘(dirt_silver)，占位，数量;[10,0,1]
            11、超能之尘(dirt_gold)，占位，数量;[11,0,1]
            12、阵石，占位，数量;[12,0,1]
            13、行动力，占位，数量;[13,0,1]
            14、星灵，占位，数量;[15,0,1]
            15、银卡，占位，数量;[15,0,1]
            16、精炼石，占位，数量;[15,0,1]
            17、神恩
            18、高级神恩
            19、觉醒宝石,ID，数量；[7,4,1]
            20、高级能晶
            21、魔光碎片
            22、新无主之地的种子
            23、装备洗炼的洗炼石
            24、宠物能晶
            25、宠物
            26、宠物经验球
            27、宠物技能石
            29、勋章的材料id
            30、勋章的id
            31、木材
            32、魂石
            33、初级锻造石
            34、中级锻造石
            35、高级锻造石
            36、英魂
            37、经验球
            38、巅峰竞技场积分
            100、竞技场点数，占位，数量;[100,0,1]
            105、卡牌，卡牌id，数量、等级（、权重)[105,6200,1,1,40]
        cur_data: 已获得的礼物数据，用于 多次调用add_gift时候统计总共获得的礼物
    """
    # 收取资源逻辑

    data = {
        'food': 0,
        'coin': 0,
        'silver': 0,
        'metal': 0,
        'metalcore': 0,
        'energy': 0,
        'cards': [],
        'equip': [],
        'item': [],
        # ======= 新加字段 =======
        'crystal': 0,
        'dirt_silver': 0,
        'dirt_gold': 0,
        'action_point': 0,
        'arena_point': 0,
        'star': 0,
        'grace': 0,
        'grace_high': 0,
        'adv_crystal': 0,
        'gem': [],
        'enchant': 0,
        'seed': [],
        'refine_stone': 0,
        'pet_crystal': 0,
        'pets': [],
        'pet_exp_ball': 0,
        'pet_skill_stone': 0,
        'equip_smelting': 0,
        'material': [],
        'medal': [],
        'wood': 0,
        'soul_stone': 0,
        'small_forge_stone': 0,
        'middle_forge_stone': 0,
        'high_forge_stone': 0,
        'soul': [],
        'exp_ball': 0,
        'arena_new_integration': 0,
    }
    data.update(cur_data)

    for pkg in gift_config:
        if(pkg[0] == 1):
            """
            加食品
            """
            user.food += pkg[2]
            data['food'] += pkg[2]
        elif(pkg[0] == 2):
            """
            加金属(铁)
            """
            user.metal += pkg[2]
            data['metal'] += pkg[2]
        elif(pkg[0] == 3):
            """
            加能源
            """
            user.energy += pkg[2]
            data['energy'] += pkg[2]
        elif(pkg[0] == 4):
            """
            加能晶
            """
            user.crystal += pkg[2]
            data['crystal'] += pkg[2]
        elif(pkg[0] == 5):
            """
            加卡牌
            """
            user.user_m._add_model_save(user.cards)
            for i in range(pkg[2]):
                tempid = user.cards.new(int(pkg[1]))
                data['cards'].append(tempid)
        elif pkg[0] == 6:
            """
            道具
            """
            user.user_m._add_model_save(user.item)
            user.item.add_item(pkg[1], pkg[2], immediate=True)
            data['item'].extend([pkg[1]] * pkg[2])
        elif pkg[0] == 7:
            """装备"""
            user.user_m._add_model_save(user.equip)
            for i in range(pkg[2]):
                tempid = user.equip.new(int(pkg[1]))
                data['equip'].append(tempid)
        elif pkg[0] == 8:
            """exp"""
            user.exp += pkg[2]
        elif pkg[0] == 9:
            """金币"""
            user.coin += pkg[2]
            data['coin'] += pkg[2]
        elif pkg[0] == 10:
            """普通尘"""
            user.dirt_silver += pkg[2]
            data['dirt_silver'] += pkg[2]
        elif pkg[0] == 11:
            """超能尘"""
            user.dirt_gold += pkg[2]
            data['dirt_gold'] += pkg[2]
        elif pkg[0] == 13:
            """行动力"""
            user.action_point += pkg[2]
            data['action_point'] += pkg[2]
        elif pkg[0] == 14:
            """star"""
            user.star += pkg[2]
            data['star'] += pkg[2]
        elif pkg[0] == 15:
            """silver"""
            user.silver += pkg[2]
            data['silver'] += pkg[2]
        elif pkg[0] == 16:
            """metalcore"""
            user.metalcore += pkg[2]
            data['metalcore'] += pkg[2]
        elif pkg[0] == 17:
            """神恩"""
            user.grace += pkg[2]
            data['grace'] += pkg[2]
        elif pkg[0] == 18:
            """高级神恩"""
            user.grace_high += pkg[2]
            data['grace_high'] += pkg[2]
        elif pkg[0] == 19:
            """觉醒宝石"""
            user.user_m._add_model_save(user.gem)
            user.gem.add(str(pkg[1]), pkg[2])
            data['gem'].extend([pkg[1]] * pkg[2])
        elif pkg[0] == 20:
            """高级能晶"""
            user.adv_crystal += pkg[2]
            data['adv_crystal'] += pkg[2]
        elif pkg[0] == 21:
            """魔光碎片"""
            user.enchant += pkg[2]
            data['enchant'] += pkg[2]
        elif pkg[0] == 22:
            """无主之地的种子"""
            user.user_m._add_model_save(user.public_land)
            user.public_land.add(pkg[1], pkg[2])
            data['seed'].extend([pkg[1]] * pkg[2])
        elif pkg[0] == 23:
            """洗炼石"""
            user.refine_stone += pkg[2]
            data['refine_stone'] += pkg[2]
        elif pkg[0] == 24:
            """宠物能晶"""
            user.pet_crystal += pkg[2]
            data['pet_crystal'] += pkg[2]
        elif pkg[0] == 25:
            """宠物"""
            save_pets = False
            save_item = False
            for i in range(pkg[2]):
                tempid = user.pets.new(int(pkg[1]))
                if isinstance(tempid, tuple):
                    data['item'].extend([tempid[0]] * tempid[1])
                    save_item = True
                else:
                    data['pets'].append(tempid)
                    save_pets = True
            if save_item:
                user.user_m._add_model_save(user.item)
            if save_pets:
                user.user_m._add_model_save(user.pets)
        elif pkg[0] == 26:
            """宠物经验球"""
            user.pet_exp_ball += pkg[2]
            data['pet_exp_ball'] += pkg[2]
        elif pkg[0] == 27:
            """宠物技能石"""
            user.pet_skill_stone += pkg[2]
            data['pet_skill_stone'] += pkg[2]
        elif pkg[0] == 28:
            """装备熔炼值"""
            user.equip_smelting += pkg[2]
            data['equip_smelting'] += pkg[2]
        elif pkg[0] == 29:
            """勋章材料"""
            user.user_m._add_model_save(user.medal)
            user.medal.add_material(str(pkg[1]), pkg[2])
            data['material'].extend([pkg[1]] * pkg[2])
        elif pkg[0] == 30:
            """勋章"""
            user.user_m._add_model_save(user.medal)
            user.medal.add_medal(str(pkg[1]), pkg[2])
            data['medal'].extend([pkg[1]] * pkg[2])
        elif pkg[0] == 31:
            """木材"""
            user.wood += pkg[2]
            data['wood'] += pkg[2]
        elif pkg[0] == 32:
            """魂石"""
            user.soul_stone += pkg[2]
            data['soul_stone'] += pkg[2]
        elif pkg[0] == 33:
            """初级锻造石"""
            user.small_forge_stone += pkg[2]
            data['small_forge_stone'] += pkg[2]
        elif pkg[0] == 34:
            """中级锻造石"""
            user.middle_forge_stone += pkg[2]
            data['middle_forge_stone'] += pkg[2]
        elif pkg[0] == 35:
            """高级锻造石"""
            user.high_forge_stone += pkg[2]
            data['high_forge_stone'] += pkg[2]
        elif pkg[0] == 36:
            """英魂"""
            user.user_m._add_model_save(user.soul)
            for i in xrange(pkg[2]):
                soul_id = user.soul.new(pkg[1])
                data['soul'].append(soul_id)
        elif pkg[0] == 37:
            """卡牌经验"""
            user.user_m._add_model_save(user.cards)
            user.cards.exp_ball += pkg[2]
            data['exp_ball'] += pkg[2]
        elif pkg[0] == 38:
            """新巅峰竞技场积分"""
            user.user_m._add_model_save(user.arena_new)
            user.arena_new.integration += pkg[2]
            data['arena_new_integration'] += pkg[2]
        elif pkg[0] == 100:
            """竞技场点数"""
            user.user_m._add_model_save(user.arena)
            user.arena.point += pkg[2]
            data['arena_point'] += pkg[2]
        elif(pkg[0] == 105):
            """
            加指定等级的卡牌
            """
            if len(pkg) >= 4:
                lv = pkg[3]
            else:
                lv = 1
            user.user_m._add_model_save(user.cards)
            for i in range(pkg[2]):
                tempid = user.cards.new(int(pkg[1]), lv=lv)
                data['cards'].append(tempid)

    if save:
        user.save()

    return data


