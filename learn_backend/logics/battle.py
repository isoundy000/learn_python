#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import copy
import random
import itertools

from lib import utils
from lib.utils import real_rand
from lib.utils import weight_choice
from lib.utils.debug import print_log

import settings
import game_config
from lib.utils import add_dict

from logics.skill_logic import skill
from logics.skill_logic import skill_tregger_def
from logics.skill_logic import hero_skill
from logics.skill_logic import pet_skill

MyDebug = False                 # ghou this 战斗是否开启debug模式

FLAGKEY = 'flag'
PARAMETERKEY = 'param'
BATTLEFLAG = {
    'attack': 'attack',     # 普通攻击标记
    'death': 'death',       # 死亡
    'sort': 'sort',         # 排序
    'winer': 'winer',       # 获胜者
    'substitution': 'sbt',  # 替补上场
    'next': 'next',         # 跳过出手
}

"""
    flag标记对应参数
    attack: {
        'src': positionid,   # 出手位置id
        'des': tempDid,      # 挨揍位置id
        'act': 0,            # 动作编号
        'hurt': temphurt,    # 受伤值
        'spc': tempspc       # 速度损失值
    }       
    death: positionid        # 死亡者位置id
    sort:［位置id顺序由出手最后到出手最前］
    winer: positionid             # positionid < 5 攻方获胜 positionid > 5守方获胜
    subistitution: positionid     # 需要替补的位置id
"""


class Battle(object):
    """
    this is a test battle class
    """
    ATT_ATTRS = ['tempEarth', 'tempWater', 'tempFire', 'tempWind']
    DEF_ATTRS = ['tempEarth_dfs', 'tempWater_dfs', 'tempFire_dfs', 'tempWind_dfs']

    def __init__(self, attacker, defender, **kwargs):
        """
        初始化战场环境
        :param attacker: 攻击者obj
        :param defender: 防御者obj
        :param kwargs: 扩展参数
            search_treasure: 逻辑宝藏专用
            maze:               迷之回廊专用
            escort:             押镖专用
            attacker_addition:  攻击方属性加成
            defender_addition:  防守方属性加成
            attacker_add_value: 攻击方属性加值
            defender_add_value: 防守方属性加值
            battle_skill:       战斗前的技能, 通过脚本给双方增加buff, 值为[script_name, script_name][技能脚本名, 技能脚本名]

        m_tAtkFormation: 攻方阵容
        m_tDfdFormation: 守方阵容
        m_tAtkArray:     攻方队伍
            {id,phsc(物理攻),mgc(魔法攻),dfs(防御),hp(血),speed(速),lv(等级),crit(暴击率),dr(闪避率),hr(命中率),subhurt(伤害减免),race(种族),career(职业)}
        m_tDfdArray:     守方队伍
            {id,phsc(物理攻),mgc(魔法攻),dfs(防御),hp(血),speed(速),lv(等级),crit(暴击率),dr(闪避率),hr(命中率),subhurt(伤害减免),race(种族),career(职业)}
        m_tSortArray:    出手排序
        m_nCurtIndex:    当前出手索引
        m_dMsg:          战斗流水数据
        m_nDeathSpeed:   死亡出手顺序
        m_tSkillMap:     技能对象表
        m_tHistoryHp:    根据id存储历史
        m_nHistoryAttck: 记录当前攻击者id
        m_tHistoryDataAll:  纪录历史数据，发送一次后数据刷新，每次同步所有数据一次。

        m_tAnger:        英雄怒气，大于100时释放怒气技能,0为攻方,1为守方
        m_tHeroSkill:    英雄技能包列表，两项0为攻方，1为守方，1可能没有
        m_tHeroSkillTree: 英雄技能树

        m_tBuffList:     buff列表

        m_bNextLoop:     跳过本次出手战斗循环标记，True为跳过，False为不跳过

        m_bRoundNum:     回合数纪录

        m_tHadAttackedId: 记录已攻击的id

        m_tHistorySubSpeed: 记录此回合每个id的减少总值
        玩家位置id
            0       100
            1       101
            2       102
            3       103
            4       104
            100       100
            101       101
            102       102
            103       103
            104       104
        """
        # phsc(物理攻), mgc(魔法攻), speed速度、dfs(防御)、hp(血)、crit(暴击率), hr(命中率), subhurt(伤害减免), dr(闪避率)                     火、风、水、地
        ATTRS = ['phsc', 'mgc', 'speed', 'dfs', 'hp', 'crit', 'hr', 'subhurt', 'dr',
                 'fire', 'water', 'wind', 'earth', 'fire_dfs', 'water_dfs', 'wind_dfs', 'earth_dfs']

        # 通过攻击者id获得攻击者阵容信息
        self.attacker = attacker
        self.defender = defender
        self.drama = copy.copy(getattr(self.defender, 'pve_drama', None))   # 战斗剧情
        # 检查战斗剧情是否已经激活过
        if self.attacker.drama.checkFight(self.defender.uid):
            self.drama = None

        # 用来记录战前技能释放
        self.pre_skill = {}
        
        # 传输装备信息
        self.equip_pos_att = {}
        self.equip_att = {}
        self.equip_pos_def = {}
        self.equip_def = {}
        # 装备锻造减少的效果值
        self.attacker_decrease_defender = {}
        self.defender_decrease_attacker = {}
        # HAS_LEADER 打人还是打怪
        if self.attacker.HAS_LEADER and len(self.attacker.equip.equip_pos) > 1:
            self.equip_pos_att = self.attacker.equip.equip_pos
            # for _equip_ids in self.equip_pos_att.itervalues():
            equip_forge_temp = {}
            for i, v in enumerate(self.equip_pos_att):
                _equip_ids = self.equip_pos_att[v]
                if v not in self.equip_att:
                    self.equip_att[v] = dict.fromkeys(ATTRS, 0)
                for _equip_id in _equip_ids:
                    if _equip_id != 0:
                        # 创建一件装备 并且执行装备的加成
                        temp_equip = self.attacker.equip.single_info(_equip_id)
                        # 组织锻造减少的百分比
                        equip_forge_temp = self.attacker.equip.attack_and_defender_attr_point(_equip_id, equip_forge_temp)
                        for _attr in ATTRS:
                            self.equip_att[v][_attr] += temp_equip.get(_attr, 0)
                # 装备套装的效果
                suit_effect_func = getattr(self.attacker.equip, 'suit_effect', None)
                if callable(suit_effect_func):
                    temp = suit_effect_func(v, _equip_ids)
                    if temp:
                        for _attr in ATTRS:
                            self.equip_att[v][_attr] += temp.get(_attr, 0)
            self.attacker_decrease_defender = equip_forge_temp

        if self.defender.HAS_LEADER and len(self.defender.equip.equip_pos) > 1:
            self.equip_pos_def = self.defender.equip.equip_pos
            # for _equip_ids in self.equip_pos_def.itervalues():
            equip_forge_temp = {}
            for i, v in enumerate(self.equip_pos_def):
                _equip_ids = self.equip_pos_def[v]
                if v not in self.equip_def:
                    self.equip_def[v] = dict.fromkeys(ATTRS, 0)
                for _equip_id in _equip_ids:
                    if _equip_id != 0:
                        temp_equip = self.defender.equip.single_info(_equip_id)
                        # 组织锻造减少的百分比
                        equip_forge_temp = self.defender.equip.attack_and_defender_attr_point(_equip_id, equip_forge_temp)
                        for _attr in ATTRS:
                            self.equip_def[v][_attr] += temp_equip.get(_attr, 0)
                suit_effect_func = getattr(self.defender.equip, 'suit_effect', None)
                if callable(suit_effect_func):
                    temp = suit_effect_func(v, _equip_ids)
                    if temp:
                        for _attr in ATTRS:
                            self.equip_def[v][_attr] += temp.get(_attr, 0)
            self.defender_decrease_attacker = equip_forge_temp

        key_key = [
            ('card_id', 'c_id'),
            ('pos', 'pos'),
            ('phsc', 'patk'),
            ('mgc', 'matk'),
            ('dfs', 'def'),
            ('hp', 'hp'),
            ('speed', 'speed'),
            ('boss', 'is_boss'),
            ('lv', 'lv'),
            ('hr', 'hr'),
            ('dr', 'dr'),
            ('crit', 'crit'),
            ('race', 'race'),
            ('career', 'career'),
            ('exp', 'exp'),
            ('subhurt', 'subhurt'),
            ('fire', 'fire'),
            ('water', 'water'),
            ('wind', 'wind'),
            ('earth', 'earth'),
            ('fire_dfs', 'fire_dfs'),
            ('water_dfs', 'water_dfs'),
            ('wind_dfs', 'wind_dfs'),
            ('earth_dfs', 'earth_dfs'),
        ]

        key_key_dict = {
            'c_id': 'card_id',
            'pos': 'pos',
            'patk': 'phsc',
            'matk': 'mgc',
            'def': 'dfs',
            'hp': 'hp',
            'speed': 'speed',
            'is_boss': 'boss',
            'lv': 'lv',
            'hr': 'hr',
            'dr': 'dr',
            'crit': 'crit',
            'race': 'race',
            'career': 'career',
            'exp': 'exp',
            'subhurt': 'subhurt',
            'fire': 'fire',
            'water': 'water',
            'wind': 'wind',
            'earth': 'earth',
            'fire_dfs': 'fire_dfs',
            'water_dfs': 'water_dfs',
            'wind_dfs': 'wind_dfs',
            'earth_dfs': 'earth_dfs',
        }

        # self.m_tAtkFormation = [0, 1, 0, 1, 0]    # 攻击者阵型
        # self.m_tDfdFormation = [0, 1, 0, 1, 0]    # 防守者阵型

        # pve 时候生成monster的formation 数据在models.fake.map_battle_user 中生成
        # 攻方阵容
        self.m_tAtkFormation = attacker.cards.formation["current"] - 1
        # 守方阵容
        self.m_tDfdFormation = defender.cards.formation["current"] - 1
        # if attacker.HAS_LEADER:
        #     self.m_tAtkFormation = attacker.cards.formation["current"] - 1
        # else:
        #     self.m_tAtkFormation = game_config.map_fight[str(attacker.uid)]["formation_id"] - 1
        # if defender.HAS_LEADER:
        #     self.m_tDfdFormation = defender.cards.formation["current"] - 1
        # else:
        #     self.m_tDfdFormation = game_config.map_fight[str(defender.uid)]["formation_id"] - 1

        self.m_tAFormationDetail = [0] * 5  # 攻击方的前后排标记, 0为后排, 1为前排
        self.m_tAAlternate = [0] * 5        # 攻击方替补索引   1>=v>=3
        self.m_tDFormationDetail = [0] * 5  # 防守方的前后排标记，0为后排，1为前排
        self.m_tDAlternate = [0] * 5        # 防守方替补索引   1>=v>=3

        self.m_tAPosition = [-1] * 6        # 攻击方位置信息
        self.m_tDPosition = [-1] * 6        # 防守方位置信息

        self.m_tASelectEnim = game_config.formation_attack[self.m_tAtkFormation + 1]    # 攻击方选择默认目标敌人
        self.m_tDSelectEnim = game_config.formation_attack[self.m_tDfdFormation + 1]    # 防守方选择默认目标敌人

        # 攻击方阵型相关问题
        tempFormation = game_config.formation[self.m_tAtkFormation + 1]
        for i, v in enumerate("abcdef"):
            tempIndex = tempFormation["position_" + v]
            if tempIndex > 0:
                if i > 3:
                    self.m_tAFormationDetail[tempIndex - 1] = 1
                else:
                    self.m_tAFormationDetail[tempIndex - 1] = 0
                self.m_tAPosition[i] = tempIndex - 1
        for i, v in enumerate("12345"):
            self.m_tAAlternate[i] = tempFormation["alternate" + v]

        # 防守方阵型相关问题
        tempFormation = game_config.formation[self.m_tDfdFormation + 1]
        for i, v in enumerate("abcdef"):
            tempIndex = tempFormation["position_" + v]
            if tempIndex > 0:
                if i > 3:
                    self.m_tDFormationDetail[tempIndex - 1] = 1
                else:
                    self.m_tDFormationDetail[tempIndex - 1] = 0
                self.m_tDPosition[i] = tempIndex - 1 + 100
        for i, v in enumerate("12345"):
            self.m_tDAlternate[i] = tempFormation["alternate" + v]

        # 所有的战斗前技能
        self.all_battle_skill = kwargs.get('battle_skill', [])

        # 英雄技能装载
        self.m_tHeroSkillTree = [{}, {}]    # 英雄技能树，0为攻方英雄技能树，1为守方英雄技能树, 取得技能全部信息
        self.m_tAnger = [0] * 2             # 英雄怒气
        self.m_tHeroSkill = [0] * 2         # 英雄技能包

        def load_leader_skill(id):
            self.m_tHeroSkillTree[id] = attacker.skill.get_skill_copy() if id == 0 else defender.skill.get_skill_copy()
            # 英雄技能假数据
            # self.m_tHeroSkillTree[id]['skill'][433] = 3     # 用户已经学会的主角技能，对应等级
            # self.m_tHeroSkillTree[id]['skill_1'] = 433      # 用户装载的第一个技能，0表示没有
            # self.m_tHeroSkillTree[id]['skill'] = attacker.skill.skill   # 英雄学会的所有的技能

            tempSkillList = []
            for i in range(1, 4):           # 用户3个技能
                tempSkillId = int(self.m_tHeroSkillTree[id]['skill_' + str(i)])
                # print "-----------------ghou log-----------------hero skill bundle", tempSkillId
                if tempSkillId > 0:
                    tempTheConfig = game_config.leader_skill[tempSkillId]
                    # 创建英雄技能包，［名字，等级，cd时间, 准备的cd时间］
                    tempScript = tempTheConfig['script']
                    tempLv = self.m_tHeroSkillTree[id]['skill'][tempSkillId]
                    tempCd = tempTheConfig['cd']
                    tempCurCd = tempTheConfig['ready_time']
                    if len(tempScript) > 0:
                        tempSkillList.append([tempScript, tempLv, tempCd, tempCurCd])
            self.m_tHeroSkill[id] = hero_skill.heroSkillFactory(tempSkillList)

        def load_leader_skill_test(id):
            pass

        if False:
            # print '----------------------------ghou log-------------------------this is test'
            if attacker.HAS_LEADER:
                load_leader_skill_test(0)
            if defender.HAS_LEADER:
                load_leader_skill_test(1)
        else:
            if attacker.HAS_LEADER:
                # print '--------------ghou log------------not have left hero'
                load_leader_skill(0)
            if defender.HAS_LEADER:
                # print '--------------ghou log------------not have right hero'
                load_leader_skill(1)

        # 宠物技能装载
        self.m_tPet = [{}, {}]              # 宠物数据 0为攻击宠物 1为防守宠物
        self.m_tPetSkillTree = [{}, {}]     # 宠物技能树，0为攻方宠物技能树，1为守方宠物技能树, 取得技能全部信息
        self.m_tPetSkill = [0] * 2          # 宠物技能包
        self.pet_id_att = 0                 # 攻击方宠物位置
        self.pet_id_def = 0                 # 防守方宠物位置

        def load_pet_skill(sort):
            """ 加载宠物技能, sort 0为攻击方  1为防守方
            """
            if sort == 0:
                if not hasattr(attacker, 'pets'):
                    return
                if not attacker.pets.pet_pos:
                    return
                pet_key = attacker.pets.pet_pos[0]
                pet_obj = attacker.pets
            else:
                if not hasattr(defender, 'pets'):
                    return
                if not defender.pets.pet_pos:
                    return
                pet_key = defender.pets.pet_pos[0]
                pet_obj = defender.pets

            if pet_key in ('-1', '0'):
                return

            pet_skills = {}
            for i in '12':
                pet_skill_info = pet_obj._pets[pet_key]['s_%s' % i]
                pet_skills['s_%s' % i] = pet_skill_info
            self.m_tPetSkillTree[sort] = copy.deepcopy(pet_skill)

            self.m_tPet[sort] = pet_obj.single_pet_info(pet_key)
            if sort == 0:
                self.pet_id_att = pet_key
            else:
                self.pet_id_def = pet_key

            pet_skill_list = []
            for i in xrange(1, 3):
                tempSkill = self.m_tPetSkillTree[sort]['s_%s' % i]
                if tempSkill['avail'] == 2:
                    pet_skill_config = game_config.pet_skill_detail[tempSkill['s']]
                    # 创建宠物技能包，［名字，等级，cd时间］
                    pet_skill_script = pet_skill_config['sprite_py']                # 技能脚本名字
                    if not pet_skill_script:
                        continue
                    pet_skill_lv = tempSkill['lv']                                  # 技能等级 技能列表 [[技能脚本名字, 等级, cd时间, 第几回合放, 技能类型]]
                    pet_skill_cd = pet_skill_config['cd']                           # 技能cd
                    pet_skill_pre_cd = pet_skill_config['pre_cd']                   # 第几回合放
                    pet_skill_skill_type = pet_skill_config['skill_type']           # 技能类型 战斗前触发 m_tTreggerFlag
                    pet_skill_effect = pet_skill_config['effect']                   # m_tEffect
                    pet_skill_effect_lvchange = pet_skill_config['effect_lvchange'] # m_tEffect
                    pet_skill_attr_effect = pet_skill_config['attr_effect']         # m_tAttrEffect
                    pet_skill_list.append([pet_skill_script, pet_skill_lv,
                                           pet_skill_cd, pet_skill_pre_cd, pet_skill_skill_type,
                                           pet_skill_effect, pet_skill_effect_lvchange, pet_skill_attr_effect])
            self.m_tPetSkill[sort] = pet_skill.petSkillFactory(pet_skill_list)

        load_leader_skill(0)
        load_leader_skill(1)

        # import random
        # attacker.cards.reset()
        # defender.cards.reset()
        self.m_tAtkArray = [0] * 10                             # 攻击卡牌所有属性值
        self.m_tDfdArray = [0] * 10

        self.m_tHistoryHp = {}                                  # 出战卡牌血量 攻击|防御
        self.m_tSkillMap = {}                                   # 出战卡牌的技能信息 攻击|防御

        # 传输卡牌信息
        self.card_att = {}                                      # 攻击方出战卡牌信息
        self.card_def = {}

        # 攻击方初始血量
        self.attacker_hp = {}                                   # 攻击方初始化血量
        self.defender_hp = {}

        search_treasure = kwargs.get('search_treasure')         # 逻辑宝藏专用
        maze = kwargs.get('maze')                               # 迷之回廊专用
        escort_atk = kwargs.get('escort_atk')                   # 押镖专用
        escort_dfd = kwargs.get('escort_dfd')

        attacker_addition = kwargs.get('attacker_addition')     # 攻击方属性加成
        defender_addition = kwargs.get('defender_addition')
        attacker_add_value = kwargs.get('attacker_add_value')   # 攻击方属性加值
        defender_add_value = kwargs.get('defender_add_value')
        attacker_cards = kwargs.get('attacker_cards')
        defender_cards = kwargs.get('defender_cards')

        for card_id, card_dict in attacker.cards._cards.iteritems():
            if not attacker_cards:                              # 没有攻击卡牌
                pos = card_dict['pos']
                if pos <= 0: continue
            else:
                pos = 1                                         # 单张卡的位置
                if card_id not in attacker_cards:
                    continue
            if escort_atk and escort_atk.rest_hp.get(card_id, 0) <= 0:
                continue
            card_info = attacker.cards.single_card_info(card_dict, for_battle=True)
            a = {}
            a['id'] = str(attacker.uid) + '_' + str(card_info['id'])    # uid_card-id
            for k in key_key:
                a[k[0]] = card_info.get(k[1], 0)
            a['bre'] = card_info.get('bre', 0)                  # changed by ghou on 2014,6,3, the attribute is new
            # 添加字段供前端使用
            a['animation'] = card_info.get('animation', '')     # 动画
            a['rgb_sort'] = card_info.get('rgb_sort', 0)
            # 超进化的卡牌作为出战卡牌 添加字段供前端使用
            a['super_quality_1'] = card_info.get('super_quality_1', 0)
            a['super_quality_2'] = card_info.get('super_quality_2', 0)

            if pos < 10:
                self.m_tAtkArray[pos - 1] = a                   # 出战卡牌的卡牌信息
                pos = pos - 1
            elif pos > 10:
                self.m_tAtkArray[pos % 10 + 4] = a
                pos = pos % 10 + 4

            self.m_tSkillMap[a['id']] = skill.skillFactory(
                [[card_info[s_n]['s'], card_info[s_n]['lv']] for s_n in ('s_1', 's_2', 's_3', 's_4', 's_5') if s_n in card_info and card_info[s_n]['s'] and card_info[s_n]['avail'] == 2]
            )

            for s_id in ('s_1', 's_2', 's_3', 's_4', 's_5'):
                if s_id in card_info and card_info[s_id]['s'] and card_info[s_id]['avail'] == 2:
                    a[card_info[s_id]['s']] = card_info[s_id]['lv']     # 技能和id等级

            self.m_tHistoryHp[a['id']] = a['hp']                # 卡牌血量
            self.card_att[a['id']] = card_info

            # 装备效果生效
            if pos in self.equip_att:
                for _attr in ATTRS:
                    a[_attr] += self.equip_att[pos][_attr]

            if attacker_addition:
                for k, v in attacker_addition.iteritems():
                    a[k] += int(a[k] * v / 100.0)

            if attacker_add_value:
                for k, v in attacker_add_value.iteritems():
                    a[k] += int(v)

            if maze:
                # a['hp'] = maze.get_hp(card_id)
                rate = maze.get_battle_hp_rate()
                a['hp'] = rate * a['hp']

            if search_treasure:
                a['hp'] = search_treasure.get_hp(card_id)

                add_property = search_treasure.get_battle_property_add()

                for k, v in add_property.iteritems():
                    if k == 'hp':
                        continue
                    a[k] += a[k] * v / 100.0

            # 装备锻造的效果
            decrease_effect_value = self.get_equip_forge_values(card_dict['c_id'], key_key_dict,
                                                                self.defender_decrease_attacker)
            for attr, attr_value in decrease_effect_value.iteritems():
                a[attr] -= int(attr_value)

            # 减伤效果最大值为80
            if 'subhurt' in a and a['subhurt'] > 80:
                a['subhurt'] = 80

            if escort_atk:
                a['hp'] = escort_atk.rest_hp.get(card_id, 0)

            # 记录初始血量
            self.attacker_hp[a['id']] = a['hp']

        for card_id, card_dict in defender.cards._cards.iteritems():
            if not defender_cards:
                pos = card_dict['pos']
                if pos <= 0: continue
            else:
                pos = 1
                if card_id not in defender_cards:
                    continue

            if escort_dfd and escort_dfd.rest_hp.get(card_id, 0) <= 0:
                continue
            card_info = defender.cards.single_card_info(card_dict, for_battle=True)
            a = {}
            a['id'] = str(defender.uid) + '_' + str(card_info['id'])
            # print card_info
            for k in key_key:
                a[k[0]] = card_info.get(k[1], 0)
            a['bre'] = card_info.get('bre', 0)        # changed by ghou on 2014,6,3, the attribute is new
            # 添加字段供前端使用
            a['animation'] = card_info.get('animation', '')
            a['rgb_sort'] = card_info.get('rgb_sort', 0)
            # 超进化的卡牌作为出战卡牌 添加字段供前端使用
            a['super_quality_1'] = card_info.get('super_quality_1', 0)
            a['super_quality_2'] = card_info.get('super_quality_2', 0)
            if pos < 10:
                self.m_tDfdArray[pos - 1] = a
                pos = pos - 1
            elif pos > 10:
                self.m_tDfdArray[pos % 10 + 4] = a
                pos = pos % 10 + 4
            self.m_tSkillMap[a['id']] = skill.skillFactory(
                [[card_info[s_n]['s'], card_info[s_n]['lv']] for s_n in ('s_1', 's_2', 's_3', 's_4', 's_5') if s_n in card_info and card_info[s_n]['s'] and card_info[s_n]['avail'] == 2]
            )

            for s_id in ('s_1', 's_2', 's_3', 's_4', 's_5'):
                if (s_id in card_info and card_info[s_id]['s'] and card_info[s_id]['avail'] == 2):
                    a[card_info[s_id]['s']] = card_info[s_id]['lv']

            self.m_tHistoryHp[a['id']] = a['hp']
            self.card_def[a['id']] = card_info

            if pos in self.equip_def:
                for _attr in ATTRS:
                    a[_attr] += self.equip_def[pos][_attr]

            if defender_addition:
                for k, v in defender_addition.iteritems():
                    a[k] += int(a[k] * v / 100.0)

            if defender_add_value:
                for k, v in defender_add_value.iteritems():
                    a[k] += int(v)

            # 装备锻造的效果
            decrease_effect_value = self.get_equip_forge_values(card_dict['c_id'], key_key_dict, self.attacker_decrease_defender)
            for attr, attr_value in decrease_effect_value.iteritems():
                a[attr] -= int(attr_value)

            if 'subhurt' in a and a['subhurt'] > 80:
                a['subhurt'] = 80

            if escort_dfd:
                a['hp'] = escort_dfd.rest_hp.get(card_id, 0)

            # 记录初始血量
            self.defender_hp[a['id']] = a['hp']

        # 速度减少历史
        self.m_tHistorySubSpeed = {}
        # 以下的不用动
        self.m_nCurtIndex = 9
        self.m_dMsg = {}
        self.m_dMsg['init'] = {}
        self.m_dMsg['battle'] = {}
        # 标记给前端看 战斗是打人 还是打怪
        self.m_dMsg['fight_user'] = self.defender.HAS_LEADER
        self.m_nRecord = 1
        self.m_nDeathSpeed = -1
        self.m_nHistoryAttack = 0
        self.m_bNextLoop = False
        self.m_nRoundNum = 0            # 战斗回合数
        self.m_bBeHurting = False       # 是否在伤害中
        self.m_bHeroSkilling = False    # 英雄是否正在施放技能
        self.m_bBuffSkilling = False
        # 用来加在战前技能后的msg
        self.tmp_m_dMsg = []

        self.m_tBuffList = [[], [], [], [], [], [], [], [], [], []]

        # 出手排序
        self.m_tSortArray = [0] * 10

        atkSkillid = [0] * 3
        dfdSkillid = [0] * 3
        if attacker.HAS_LEADER:         # 攻击方3个技能
            for i in range(1, 4):
                atkSkillid[i - 1] = int(self.m_tHeroSkillTree[0]['skill_' + str(i)])

        if defender.HAS_LEADER:
            for i in range(1, 4):
                dfdSkillid[i - 1] = int(self.m_tHeroSkillTree[1]['skill_' + str(i)])

        self.m_dMsg['init']['atk'] = copy.deepcopy(self.m_tAtkArray)        # 攻击方卡牌所有属性值
        self.m_dMsg['init']['aform'] = self.m_tAtkFormation + 1             # 攻方阵容
        self.m_dMsg['init']['dfd'] = copy.deepcopy(self.m_tDfdArray)        # 防守方卡牌所有属性值
        self.m_dMsg['init']['dform'] = self.m_tDfdFormation + 1             # 防守方阵容
        self.m_dMsg['init']['equip_pos_att'] = self.equip_pos_att           # 攻击方装备
        self.m_dMsg['init']['equip_pos_def'] = self.equip_pos_def           # 防守方装备
        self.m_dMsg['init']['equip_att'] = self.equip_att                   # 攻击方装备属性加成
        self.m_dMsg['init']['equip_def'] = self.equip_def                   # 防守方装备属性加成
        self.m_dMsg['init']['card_att'] = self.card_att                     # 攻击方出战卡牌信息
        self.m_dMsg['init']['card_def'] = self.card_def                     # 防守方出战卡牌信息
        self.m_dMsg['init']['pet_att'] = {self.pet_id_att: self.m_tPet[0]} if self.pet_id_att else {}   # 攻击宠物key, 攻击方宠物信息
        self.m_dMsg['init']['pet_def'] = {self.pet_id_def: self.m_tPet[1]} if self.pet_id_def else {}   # 防守宠物key, 防守方宠物信息
        self.m_dMsg['init']['pet_id_att'] = self.pet_id_att                 # 攻击宠物key
        self.m_dMsg['init']['pet_id_def'] = self.pet_id_def                 # 防守宠物key
        self.m_dMsg['init']['sort_array'] = []
        self.m_dMsg['init']['atk_role'] = self.attacker.role                # 攻击头像
        self.m_dMsg['init']['dfd_role'] = self.defender.role                # 防守头像
        self.m_dMsg['init']['atk_skill'] = atkSkillid                       # 攻击方英雄的3个技能
        self.m_dMsg['init']['dfd_skill'] = dfdSkillid                       # 防守方英雄的3个技能
        self.m_dMsg['init']['atk_lv'] = self.attacker.level                 # 攻击等级
        self.m_dMsg['init']['dfd_lv'] = self.defender.level                 # 防守等级
        self.m_dMsg['init']['atk_friend'] = self.attacker.cards.assistant + self.attacker.cards.destiny   # 攻方助威和命运
        self.m_dMsg['init']['dfd_friend'] = self.defender.cards.assistant + self.defender.cards.destiny   # 防守助威和命运

        if self.attacker.HAS_LEADER:
            self.m_dMsg['init']['atk_name'] = self.attacker.name            # 攻击名字
        else:
            self.m_dMsg['init']['atk_name'] = ""

        if self.defender.HAS_LEADER or getattr(self.defender, 'name', None):
            self.m_dMsg['init']['dfd_name'] = self.defender.name
        else:
            self.m_dMsg['init']['dfd_name'] = ""

        if hasattr(self.attacker, 'rob_name'):
            self.m_dMsg['init']['atk_name'] = self.attacker.rob_name
        if hasattr(self.defender, 'rob_name'):
            self.m_dMsg['init']['dfd_name'] = self.defender.rob_name

        # 初始化爆击数值
        # self._initCrit()

        # print self.m_dMsg['init']
        # 战斗前初始化数据
        self._initHistorySubSpeed()

        for i in range(10):
            if self.m_tAtkArray[i] != 0:
                self.startSetMembers(i)
            if self.m_tDfdArray[i] != 0:
                self.startSetMembers(i + 100)

        # 纪录所有历史数据
        self.m_tHistoryDataAll = {}
        for i in xrange(5):
            self.m_tHistoryDataAll[i] = copy.deepcopy(self.m_tAtkArray[i])
            self.m_tHistoryDataAll[i + 100] = copy.deepcopy(self.m_tDfdArray[i])

        # 记录已经攻击的角色位置id
        self.m_tHadAttackedId = []

# --------------------------------------- this is a little cut of line --------------------------------------

    def get_equip_forge_values(self, c_id, key_key_dict, data):
        """
        获取装备锻造减少对方的值
        :param c_id:
        :param data: 这件装备的属性值
        :param card: 卡牌属性
        :return:
        """
        # for attr, rate in card_data.iteritems():
            # new_attr = key_key_dict.get(attr)
            # add_dict(result, new_attr, rate * card[new_attr])
        card_data = data.get(c_id, {})
        all_data = data.get(-1, {})
        result = {}

        for attr, attr_value in card_data.iteritems():
            new_attr = key_key_dict.get(attr)
            add_dict(result, new_attr, attr_value/10.0)

        for attr, attr_value in all_data.iteritems():
            new_attr = key_key_dict.get(attr)
            add_dict(result, new_attr, attr_value/10.0)

        return result

    def updateMsg(self, flag, param):
        """
        更新消息数据
        flag:   动作标记 anger怒气
        param:  参数
        """
        self.m_dMsg['battle'][self.m_nRecord] = {FLAGKEY: flag, PARAMETERKEY: param}
        if MyDebug:
            tempLog = {}
            for i in range(5):
                tempLog[i] = copy.deepcopy(self.getMembers(i))
                tempLog[i + 100] = copy.deepcopy(self.getMembers(i + 100))
            self.m_nRecord += 1
            self.m_dMsg['battle'][self.m_nRecord] = {FLAGKEY: 'logMsg', PARAMETERKEY: tempLog}
            self.m_nRecord += 1
            self.m_dMsg['battle'][self.m_nRecord] = {FLAGKEY: 'logSort', PARAMETERKEY: copy.copy(self.m_tSortArray)}    # 出手顺序
        self.m_nRecord += 1

    def start(self):
        """
        战斗开始
        """
        # # 战斗前初始化数据
        # self.m_nRoundNum = 0
        # self._initHistorySubSpeed()
        #
        # for i in range(5):
        #     if self.m_tAtkArray[i] != 0:
        #         self.startSetMembers(i)
        #     if self.m_tDfdArray[i] != 0:
        #         self.startSetMembers(i + 100)
        #
        # # 纪录所有历史数据
        # self.m_tHistoryDataAll = {}
        # for i in xrange(5):
        #     self.m_tHistoryDataAll[i] = copy.deepcopy(self.m_tAtkArray[i])
        #     self.m_tHistoryDataAll[i + 100] = copy.deepcopy(self.m_tDfdArray[i])
        #
        # # 记录已经攻击的角色位置id
        # self.m_tHadAttackedId = []

        self.addAnger(0, 50)            # 战斗前攻击方给每个英雄增加50点怒气
        self.addAnger(1, 50)            # 战斗前防守方给每个英雄增加50点怒气

        # 触发战前技能脚本
        skill.battle_skill_tregger(self, self.all_battle_skill)

        # 战斗前触发英雄技能初始化脚本
        for i in range(2):
            if self.m_tHeroSkill[i] != 0:
                hero_skill.heroSkillInit(self.m_tHeroSkill[i], self, i)
                self.checkDeath()

        if self.checkOver():            # 检查是否有敌人
            self.depart_pre_battle()
            return self.m_dMsg

    def checkDeath(self):
        """
        检查双方队列里是否有死亡
        """
        # 同步前端数据
        self.HistoryChangeMsg()

    def HistoryChangeMsg(self):
        """
        历史数据变化消息
        """
        tempMsg = {}
        for i in xrange(5):
            tempData = self.getMembers(i)
            tempData2 = self.getMembers(i + 100)
            tempHData = self.m_tHistoryDataAll[i]
            tempHData2 = self.m_tHistoryDataAll[i + 100]
            # if tempData != 0:
            #     if self.m_tHistoryHp[tempData['id']] != tempData['tempHp']:
            #         tempDH = tempData['tempHp']
            #         tempMsg[i] = tempDH
            # if tempData2 != 0:
            #     if self.m_tHistoryHp[tempData2['id']] != tempData2['tempHp']:
            #         tempDH = tempData2['tempHp']
            #         tempMsg[i + 100] = tempDH
            temp1 = {}
            if tempData != 0:
                for j, v in enumerate(tempHData):
                    if not ((v == "tempSpeed") and (i in self.m_tHadAttackedId)):
                        if tempHData[v] != tempData[v]:
                            pass

    def startSetMembers(self, positionId):
        """
        第一次启动战斗时初始化数据
        """
        if positionId < 10:
            tempMembers = self.m_tAtkArray[positionId]
        else:
            tempMembers = self.m_tDfdArray[positionId - 100]
        tempMembers['tempSpeed'] = tempMembers['speed']
        tempMembers['tempDfs'] = tempMembers['dfs']
        tempMembers['tempMgc'] = tempMembers['mgc']
        tempMembers['maxHp'] = tempMembers['hp']
        tempMembers['tempHp'] = tempMembers['hp']
        tempMembers['tempPhsc'] = tempMembers['phsc']
        # tempMembers['crit'] = 5

        # tempMembers['subhurt'] = 0
        # tempMembers['crit'] = 0
        # tempMembers['dr'] = 0
        # tempMembers['hr'] = 100

        tempMembers['tempCrit'] = tempMembers['crit']
        tempMembers['tempDr'] = tempMembers['dr']
        tempMembers['tempHr'] = tempMembers['hr']
        tempMembers['subHurt'] = tempMembers['subhurt']
        magic_sorts = ['fire', 'fire_dfs', 'wind', 'wind_dfs', 'water', 'water_dfs', 'earth', 'earth_dfs']
        for magic_sort in magic_sorts:
            tempMembers['temp' + magic_sort.capitalize()] = tempMembers[magic_sort]     # capitalize()首字母变大写

    def getMembers(self, positionid):
        """
        通过位置id获得在场队员的数据信息
        """
        # tempMembers = {}
        # # {id, phsc(物理攻), mgc(魔法攻), dfs(防御), hp(血), speed(速), lv(等级), crit(暴击率), dr(闪避率), hr(命中率),}
        # tempMembers['id'] = -1
        # tempMembers['phsc'] = -1
        # tempMembers['mgc'] = -1
        # tempMembers['dfs'] = -1
        # tempMembers['hp'] = -1
        # tempMembers['speed'] = -1
        # tempMembers['lv'] = -1
        # tempMembers['crit'] = -1
        # tempMembers['dr'] = -1
        # tempMembers['hr'] = -1
        # tempMembers['tempSpeed'] = tempMembers['speed']
        # tempMembers['tempPhsc'] = tempMembers['phsc']
        # tempMembers['tempMgc'] = tempMembers['mgc']
        # tempMembers['tempDfs'] = tempMembers['dfs']
        # if 'tempHp' not in tempMembers:
        #     tempMembers['tempHp'] = tempMembers['hp']
        #     tempMembers['subHurt'] = -1
        #     tempMembers['crit'] = -1
        #     tempMembers['dr'] = -1
        #     tempMembers['hr'] = -1
        # tempMembers['tempCrit'] = tempMembers['crit']
        # tempMembers['tempDr'] = tempMembers['dr']
        # tempMembers['tempHr'] = tempMembers['hr']
        # tempMembers['subHurt'] = -1

        if 0 <= positionid < 8:
            if self.m_tAtkArray[positionid] != 0:
                return self.m_tAtkArray[positionid]
            else:
                # return tempMembers
                return 0
        elif 100 <= positionid < 108:
            if self.m_tDfdArray[positionid - 100]:
                return self.m_tDfdArray[positionid - 100]
            else:
                # return tempMembers
                return 0
        else:
            return 0

    def addAnger(self, id, value):
        """
        增加怒气
        id 0为攻方,1为守方
        value 50数值
        """
        if id < 0 or id > 1:
            # print "----------------ghou log------------battle addAnger hero_id", id
            return
        if self.m_tHeroSkill[id] == 0:
            # print "----------------ghou log------------battle addAnger hero not have skill", id
            return
        self.m_tAnger[id] += value      # 英雄怒气
        if self.m_tAnger[id] < 0:       # 怒气太小
            self.m_tAnger[id] = 0
        elif self.m_tAnger[id] > 100:   # 怒气最大
            self.m_tAnger[id] = 100
        self.updateMsg('anger', {'src': id, 'value': self.m_tAnger[id]})

    def getCampAllLife(self, positionid):
        """
        得到与positionid相同阵营的全部位置
        """
        if positionid < 5:
            tempArray = self.m_tAtkArray
            tempOffset = 0
        else:
            tempArray = self.m_tDfdArray
            tempOffset = 100
        tempList = []
        for i in range(5):
            if tempArray[i] != 0:
                tempList.append(i + tempOffset)
        return tempList

    def _initCrit(self):
        """
        初始化爆击率,
        此方法已经弃用
        :return:
        """
        for i in range(10):
            tempData = self.m_tAtkArray[i]
            if tempData != 0:
                tempDataLv = max(tempData['lv'], 1)
                tempData['crit'] = int((tempData['speed'] / tempDataLv / 1500) * 100)

            tempData = self.m_tDfdArray[i]
            if tempData != 0:
                tempDataLv = max(tempData['lv'], 1)
                tempData['crit'] = int((tempData['speed'] / tempDataLv / 1500) * 100)

    def _initHistorySubSpeed(self):
        """
        初始化历史扣速度总值
        """
        for i in xrange(5):
            self.m_tHistorySubSpeed[i] = 0
            self.m_tHistorySubSpeed[i + 100] = 0


def merge_dict(source, target):
    """合并字典
    :param source: 源字典 {'k', v}
    :param target: 目标字典 {'k', v}
    :return:
    """
    for k in target:
        if k in source:
            source[k] += target[k]
        else:
            source[k] = target[k]