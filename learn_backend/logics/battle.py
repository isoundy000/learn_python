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
        self.pre_skill = {}                                                 # 战斗前释放的技能
        
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
        self.m_nDeathSpeed = -1         # 死亡速度
        self.m_nHistoryAttack = 0       # 得到当前攻击者的id
        self.m_bNextLoop = False        # 是否跳过当前出手者
        self.m_nRoundNum = 0            # 战斗回合数
        self.m_bBeHurting = False       # 是否在伤害中
        self.m_bHeroSkilling = False    # 英雄是否正在施放技能
        self.m_bBuffSkilling = False    # buff技能
        # 用来加在战前技能后的msg
        self.tmp_m_dMsg = []

        self.m_tBuffList = [[], [], [], [], [], [], [], [], [], []]         # 前5个是攻击方buff 后5个是防守方buff

        # 出手排序
        self.m_tSortArray = [0] * 10    # 卡牌索引 [0, 100, 1, 2, 3, 101, 102, 103, 4, 104]

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

    def setWiner(self, positionid):
        """
        设置胜利方, <5 attacker获胜
        """
        self.m_dMsg['winer'] = positionid
        if positionid > 5:
            self.checkDrama(2, 1)
        else:
            self.checkDrama(2, 0)
            if self.drama != None:
                self.attacker.drama.completionFight(self.defender.uid)

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

        # 宠物战斗前触发技能
        for i in xrange(2):
            skill_object = self.m_tPetSkill[i]
            if skill_object:
                pet_skill.petTregger(skill_object, skill_tregger_def.KBEFOREBATTLE, self, i)
                self.checkDeath()
                if self.checkOver():
                    self.depart_pre_battle()
                    return self.m_dMsg

        # 角色出战卡牌战斗前触发技能
        for i in range(5):              # 战前触发器
            if self.m_tAtkArray[i] != 0:
                self.add_pre_skill(i, self.m_tAtkArray, self.m_tSkillMap)
                skill.skillTregger(self.m_tSkillMap[self.m_tAtkArray[i]['id']], skill_tregger_def.KBEFOREBATTLE, self, i)
                self.checkDeath()
                if self.checkOver():
                    self.depart_pre_battle()
                    return self.m_dMsg

            if self.m_tDfdArray[i] != 0:
                self.add_pre_skill(i + 100, self.m_tDfdArray, self.m_tSkillMap)
                skill.skillTregger(self.m_tSkillMap[self.m_tDfdArray[i]['id']], skill_tregger_def.KBEFOREBATTLE, self, i + 100)
                self.checkDeath()
                if self.checkOver():
                    self.depart_pre_battle()
                    return self.m_dMsg

        # 战前技能处理()
        self.depart_pre_battle()

        self.checkDrama(1)
        self.beforeBattle()                 # 战斗前调整战场

        tempi = 0
        while tempi < 30:                   # 循环30次
            self.m_nCurtIndex = 9           # 当前出手索引
            self.createSpeedArray()         # 初始化出手顺序和、合前buff触发器、触发buff效果持续加持
            self.m_tHadAttackedId = []      # 记录已经攻击的角色位置id

            self.m_bNextLoop = False        # 判断是否要跳过本次循环
            self.checkDrama(3, tempi)       # 剧情

            self.checkDeath()               # 检查死亡，其中有死亡触发器
            if self.checkOver():            # 检查是否战斗结束
                return self.m_dMsg

            # 宠物战斗前触发技能               回合排序前触发技能
            for i in xrange(2):
                skill_object = self.m_tPetSkill[i]
                if skill_object:
                    pet_skill.petTregger(skill_object, skill_tregger_def.KBEFOREROUND, self, i)
                    self.checkDeath()
                    if self.checkOver():
                        self.depart_pre_battle()
                        return self.m_dMsg

            # 角色回合排序前触发技能
            for i in range(5):              # 回合前触发器
                if self.m_tAtkArray[i] != 0:
                    skill.skillTregger(self.m_tSkillMap[self.m_tAtkArray[i]['id']], skill_tregger_def.KBEFOREROUND, self, i)
                if self.m_tDfdArray[i] != 0:
                    skill.skillTregger(self.m_tSkillMap[self.m_tDfdArray[i]['id']], skill_tregger_def.KBEFOREROUND, self, i + 100)

            while self.m_nCurtIndex >= 0:
                self.checkDeath()           # 检查死亡，其中有死亡触发器
                if self.checkOver():        # 检查是否战斗结束
                    return self.m_dMsg

                tempPositionid = self.m_tSortArray[self.m_nCurtIndex]
                if self.checkHaveValue(tempPositionid):
                    self.m_nHistoryAttack = tempPositionid          # 记录当前攻击者id
                    tempEnim = self.selectEnim(tempPositionid)      # 选择攻击的目标 敌人
                    if tempEnim < 0:
                        self.updateMsg(BATTLEFLAG['winer'], tempPositionid)     # 攻击者胜利
                        self.setWiner(tempPositionid)
                        return self.m_dMsg

                    self.buffTregger(tempPositionid, skill_tregger_def.KBUFFATTACK)  # 增加攻击前buff触发器
                    self.checkDeath()
                    if not self.checkHaveValue(tempPositionid):     # 攻击完毕
                        self.m_nCurtIndex -= 1
                        self.updateMsg('attack_over', {"src": tempPositionid})
                        # self.updateMsg("log", {"msg": "next loop", "src": tempPositionid})
                        continue

                    if self.m_bNextLoop:    # 判断是否要跳过本次循环
                        self.m_nCurtIndex -= 1
                        self.m_bNextLoop = False
                        self.updateMsg('attack_over', {"src": tempPositionid})
                        self.m_tHadAttackedId.append(tempPositionid)
                        # self.updateMsg("log", {"msg": "next loop", "src": tempPositionid})
                        continue

                    if not self.attack(tempPositionid):     # 攻击
                        return self.m_dMsg

                    self.checkDeath()       # 检查死亡，其中有死亡触发器
                    if self.checkOver():
                        return self.m_dMsg

                    for tempj in range(5):  # 被攻击触发器  被攻击之后触发的技能
                        if self.SynHp(tempj):
                            if self.m_tAtkArray[tempj]:
                                skill.skillTregger(self.m_tSkillMap[self.m_tAtkArray[tempj]['id']], skill_tregger_def.KAFTERHURT, self, tempj)      # 受伤后触发器
                        if self.SynHp(tempj + 100):
                            if self.m_tDfdArray[tempj]:
                                skill.skillTregger(self.m_tSkillMap[self.m_tDfdArray[tempj]['id']], skill_tregger_def.KAFTERHURT, self, tempj + 100)

                    self.checkDeath()       # 检查死亡，其中有死亡触发器
                    if self.checkOver():
                        return self.m_dMsg

                    self.updateMsg("attack_over", {"src": tempPositionid})      # 攻击卡牌出手结束
                    self.m_tHadAttackedId.append(tempPositionid)                # 添加已经出手的卡牌
                    self.checkAnger(tempPositionid)                             # 检查英雄怒气
                    tempMem = self.getMembers(tempPositionid)
                    if tempMem != 0:
                        tempMem["tempSpeed"] = 999999999    # 出手卡牌的速度

                    self.checkBuffEffect()      # 检查buff触发次数

                    self.resetMembersAll()      # 重置所有数据，重置keepbuff
                    self.HistoryChangeMsg()     # 历史数据变化消息

                self.m_nCurtIndex -= 1

            tempi += 1
            self.m_nRoundNum = tempi
            self.checkBuffRound()
            self.checkAbandon()
            self.changedHeroSkillCd()           # TODO 临时做法
            for i in self.m_tSkillMap:
                skill.cardSkillCdChange(self.m_tSkillMap[i])    # 更新卡牌技能当前cd
            for skillObject in self.m_tPetSkill:
                pet_skill.petSkillCdChange(skillObject)
            # 重新计算出手顺序
            self.sortSpeedArray()

        self.updateMsg(BATTLEFLAG['winer'], 100)
        self.setWiner(100)

        return self.m_dMsg

    def changedHeroSkillCd(self):
        """
        geng新CD
        """
        hero_skill.heroChangedCd(self.m_tHeroSkill[0])
        hero_skill.heroChangedCd(self.m_tHeroSkill[1])

    def checkAbandon(self):
        """
        检查buff当前是否被废弃
        """
        j = 0
        for buffs in self.m_tBuffList:
            i = 0
            while i < len(buffs):
                if buffs[i] == None:
                    del buffs[i]
                    continue
                i += 1
            j += 1

    def checkBuffRound(self):
        """
        检查buff时效
        """
        j = 0
        for buffs in self.m_tBuffList:
            i = 0
            while i < len(buffs):
                if buffs[i] != None:
                    buffs[i].m_record -= 1
                    if buffs[i].m_record <= 0:
                        if j < 5:
                            positionId = j
                        else:
                            positionId = j + 100 - 5
                        self.removeBuffWithIndex(positionId, i)
                i += 1
            j += 1

    def resetMembersAll(self):
        """
        重置所有活着的卡牌数据
        """
        for i in range(5):
            if self.getMembers(i) != 0:
                self.setMembers(i)
                self.buffTregger(i, skill_tregger_def.KBUFFKEEP, False)
            if self.getMembers(i + 100) != 0:
                self.setMembers(i + 100)
                self.buffTregger(i + 100, skill_tregger_def.KBUFFKEEP, False)
        self.updateMsg("log", "resetMembersAll")
        self.HistoryChangeMsg()

    def checkBuffEffect(self):
        """
        检查buff的次数效果
        """
        j = 0
        for buffs in self.m_tBuffList:          # 前5个是攻击方buff 后5个是防守方buff
            i = 0
            while i < len(buffs):
                if buffs[i] != None:
                    if buffs[i].m_effect <= 0:
                        if j < 5:
                            positionId = j
                        else:
                            positionId = j + 100 - 5
                        self.removeBuffWithIndex(positionId, i)
                i += 1
            j += 1

    def removeBuffWithIndex(self, positionid, index):
        '''
        删除指定buff
        :param positionid: 位置0-4    100-104
        :param index: 技能索引
        :return:
        '''
        if positionid < 5:
            buffsIndex = positionid
        else:
            buffsIndex = positionid - 100 + 5
        if self.m_tBuffList[buffsIndex][index] is None:
            return

        tempbuff = self.m_tBuffList[buffsIndex][index]
        if tempbuff is None:
            return

        self.updateMsg('remove_buff', {'name': self.m_tBuffList[buffsIndex][index].m_name, 'src': positionid})
        # del self.m_tBuffList[buffsIndex][index]

        self.m_tBuffList[buffsIndex][index] = None
        del tempbuff

        tempMembers = self.getMembers(positionid)
        if tempMembers == 0:
            return
        self.setMembers(positionid)                                 # 恢复初始数值
        self.buffTregger(positionid, skill_tregger_def.KBUFFKEEP)   # 触发buff效果持续加持
        tempMembers["tempSpeed"] = max(tempMembers["tempSpeed"] - self.m_tHistorySubSpeed[positionid], 0)
        if tempMembers['tempHp'] > tempMembers['maxHp']:
            tempMembers['tempHp'] = tempMembers['maxHp']

    def checkAnger(self, positionId):
        """
        检查怒气
        positionid： 本轮出手者id
        """
        if positionId < 5:
            tempList = [0, 1]                   # 出手者的英雄技能顺序
        else:
            tempList = [1, 0]
        for i in tempList:
            if self.m_tAnger[i] < 100:
                continue
            if self.m_tHeroSkill[i] != 0:       # 英雄技能
                self.m_bHeroSkilling = True
                tempValue = hero_skill.heroTregger(self.m_tHeroSkill[i], self, i)
                self.m_bHeroSkilling = False
            else:
                tempValue = (False, 0)

            if tempValue[0]:
                self.m_tAnger[i] -= min(tempValue[1], 100)  # 英雄怒气
                # 触发减怒气后触发脚本
                hero_skill.heroSkillEnd(self.m_tHeroSkill[i], self, i)
                self.updateMsg('test', {'sub_anger': i, 'value': tempValue[1]})     # 减少怒气
                self.addAnger(i, 0)             # i 0为攻方,1为守方

    def SynHp(self, positionid):
        """
        同步历史血量
        positionid < 5 攻击  > 5防守
        """
        if positionid < 5:
            tempData = self.m_tAtkArray[positionid]
        else:
            tempData = self.m_tDfdArray[positionid - 100]

        if tempData == 0:
            return False
        # print '------------------synHp-------------------', positionid
        # print tempData
        if self.m_tHistoryHp[tempData['id']] <= tempData['tempHp']:     # 同步失败
            self.m_tHistoryHp[tempData['id']] = tempData['tempHp']
            return False
        else:
            self.m_tHistoryHp[tempData['id']] = tempData['tempHp']      # 同步成功
            return True

    def attack(self, positionid):
        """
        攻击
        positionid:     攻击者位置
        """
        # 这里会有释放技能
        if skill.skillTregger(self.m_tSkillMap[self.getMembers(positionid)['id']], skill_tregger_def.KBEFOREATTACK,
                              self, positionid) == 0:   # 攻击前触发，如果返回1则继续触发普通攻击
            return True
        # 这里是普通攻击
        # tempDic = {}    # 返回字符串
        # tempTk = 0      # 攻击者数据
        # tempFd = 0      # 被攻击者数据

        # 获得攻击者数据
        if positionid < 5:
            tempTk = self.m_tAtkArray[positionid]
        else:
            tempTk = self.m_tDfdArray[positionid - 100]

        # 获得被攻击者id
        tempDid = self.selectEnim(positionid)
        if tempDid < 0:
            self.updateMsg(BATTLEFLAG['winer'], positionid)
            self.setWiner(positionid)
            return False

        # 获得被攻击者数据
        if tempDid < 5:
            tempFd = self.m_tAtkArray[tempDid]
        else:
            tempFd = self.m_tDfdArray[tempDid]

        # 计算伤害值
        temphurt = max((tempTk['tempPhsc'] + tempTk['tempMgc']) / 2 - tempFd['tempDfs'], 1)

        # 计算速度减少值
        tempSpeedIndex = self.m_tSortArray.index(tempDid)
        if tempSpeedIndex >= self.m_nCurtIndex:
            tempspc = 0
        else:
            # tempspc = tempFd['speed'] / 10
            tempspc = 0

        self.addAnger(0, 10)        # 攻击方添加怒气
        self.addAnger(1, 10)        # 防守方添加怒气

        temphurt = self.realHurt(tempDid, temphurt)     # 被攻击者掉血 返回掉血量
        # temphurt = temphurt * (100 - tempFd['subHurt']) / 100.0     # 计算免伤系数
        # tempDic['hurt'] = temphurt
        tempDic = {
            'src': positionid,      # 出手位置id
            'des': tempDid,         # 挨揍位置id
            'act': 0,               # 动作编号
            'hurt': temphurt,       # 受伤值
            'spc': tempspc,         # 速度损失值
            # 'type': tempRand,       # 攻击种类
        }

        attr_type, tempattrhurt = 0, 0

        for indx, att in enumerate(self.ATT_ATTRS):     # 攻击者属性伤害 'tempEarth', 'tempWater', 'tempFire', 'tempWind'
            attr_hurt = tempTk[att]     # 攻击者属性伤害
            if tempFd['tempHp'] <= 0:   # 防守方血量
                break
            if attr_hurt > 0:
                attr_type = indx + 1
                tempattrhurt = max(attr_hurt - tempFd[self.DEF_ATTRS[indx]], 1)
                break

        if attr_type:
            tempattrhurt = self.realattrHurt(tempDid, tempattrhurt)
            tempDic['attr_type'] = attr_type            # 属性伤害类型
            tempDic['attr_hurt'] = tempattrhurt         # 属性伤害

        self.updateMsg(BATTLEFLAG['attack'], tempDic)
        # self.HistoryChangeMsg()

        if tempDid < 5:                 # 受伤的卡牌
            # self.m_tAtkArray[tempDid]['tempHp'] -= temphurt
            self.m_tHistorySubSpeed[tempDid] += tempspc     # 记录速度减少的值
            if self.m_tAtkArray[tempDid]['tempSpeed'] > 0:
                self.m_tAtkArray[tempDid]['tempSpeed'] = max(self.m_tAtkArray[tempDid]['tempSpeed'] - tempspc, 0)   # 挨揍的卡减速
        else:
            Did = tempDid - 100
            # self.m_tDfdArray[Did]['tempHp'] -= temphurt
            self.m_tHistorySubSpeed[Did] += tempspc
            if self.m_tDfdArray[Did]['tempSpeed'] > 0:
                self.m_tDfdArray[Did]['tempSpeed'] = max(self.m_tDfdArray[Did]['tempSpeed'] - tempspc, 0)

        skill.skillTregger(self.m_tSkillMap[self.getMembers(positionid)['id']], skill_tregger_def.KATTACK, self, positionid)    # 普攻触发器
        return True

    def realattrHurt(self, positionid, attr_hurt):
        """
        得到指定位置（positionid），指定属性伤害（attr_hurt）, 同时减血
        :param positionid: 受伤的位置
        :param attr_hurt: 受到属性伤害
        :return:
        """
        attr_hurt = int(attr_hurt)
        if attr_hurt <= 0:
            return 0

        tempEnem = self.getMembers(positionid)
        if tempEnem == 0:
            return 0

        tempEnem['tempHp'] -= attr_hurt
        return attr_hurt

    def realHurt(self, positionid, hurt):
        """
        得到指定位置（positionid），指定伤害（hurt）计算免伤后的伤害,同时减血
        """
        # if positionid < 5:
        #     tempIndex = positionid
        #     tempArray = self.m_tAtkArray
        # else:
        #     tempIndex = positionid - 100
        #     tempArray = self.m_tDfdArray
        tempEnem = self.getMembers(positionid)      # 敌人信息
        if tempEnem == 0:
            return 0
        if hurt <= 0:
            hurt = 10       # 伤害为mess

        # 受伤前触发技能
        if not self.m_bBeHurting and not self.m_bHeroSkilling and not self.m_bBuffSkilling:
            self.m_bBeHurting = True
            skill.skillTregger(self.m_tSkillMap[tempEnem['id']], skill_tregger_def.KBEATTACK, self, positionid)     # KBEATTACK 被攻击触发器标志
            self.buffTregger(positionid, skill_tregger_def.KBUFFBEATTACK)   # buff被攻击前触发效果  # ???????????????????????????buff被攻击触发器

            if self.getMembers(self.m_nHistoryAttack) != 0:     # 记录当前攻击者id
                if self.hit_1(self.m_nHistoryAttack, positionid):
                    if self.doubleKill_1(self.m_nHistoryAttack):
                        hurt *= 1.5
                else:
                    hurt = 0
            self.m_bBeHurting = False

        subHurt = tempEnem['subHurt']       # 减伤率
        if hurt > 0:
            tempHurt = max(hurt * max(0, (100 - subHurt)) / 100.0, 10)
        else:
            tempHurt = 0
        tempHurt = int(tempHurt)
        # tempHurt = max(1, tempHurt)
        tempEnem['tempHp'] -= tempHurt      # 敌人掉血
        return tempHurt                     # 掉血量

    def doubleKill(self, positionid):
        """
        双倍攻击 不使用
        """
        return False

    def doubleKill_1(self, positionid):
        """
        双倍攻击
        :param positionid: 攻击方id
        :return:
        """
        tempRand = real_rand.myRand()
        tempMember = self.getMembers(positionid)
        if tempRand < tempMember['tempCrit']:       # 暴击率
            return True
        return False

    def hit(self, APositionId, DPositionId):
        """
        命中 不使用
        """
        return True

    def hit_1(self, APositionId, DPositionId):
        '''
        是否命中
        :param APositionId: 攻击id
        :param DPositionId: 防守id
        :return:
        '''
        # return True    # 去掉闪避
        tempRand = real_rand.myRand()
        tempA = self.getMembers(APositionId)
        tempD = self.getMembers(DPositionId)
        tempHit = tempA['tempHr'] - tempD['tempDr']     # 攻击方命中 - 防守方闪避
        if tempRand <= tempHit:
            return True
        return False

    def selectEnim(self, positionid):
        """
        选择默认目标敌人
        :param positionid: 攻击者位置
        :return:
        """
        if positionid < 5:
            tempAI = self.m_tASelectEnim[positionid + 1][self.m_tDfdFormation]
            for i in tempAI:
                if self.m_tDfdArray[i - 1] != 0:
                    return i - 1 + 100
            return -1       # 对方无可攻击目标
        else:
            tempAI = self.m_tDSelectEnim[positionid - 100 + 1][self.m_tAtkFormation]
            for i in tempAI:
                if self.m_tAtkArray[i - 1] != 0:
                    return i - 1
            return -1       # 对方无可攻击目标

    def checkHaveValue(self, positionid):
        """
        检查是否有角色数据
        """
        if positionid < 5:
            return self.m_tAtkArray[positionid] != 0
        else:
            return self.m_tDfdArray[positionid - 100] != 0

    def createSpeedArray(self):
        '''
        初始化排序
        :return:
        '''
        self._initHistorySubSpeed()         # 初始化历史扣速度总值
        for i in [0, 1, 2, 3, 4]:
            self.m_tSortArray[i] = i        # 出手排序
            if self.m_tAtkArray[i] != 0:
                # self.m_tAtkArray[i]['tempSpeed'] = self.m_tAtkArray[i]['speed']
                # if 'tempHp' not in self.m_tAtkArray[i]:
                #     self.m_tAtkArray[i]['tempHp'] = self.m_tAtkArray[i]['hp']
                self.setMembers(i)
                tempA = self.getMembers(i)
                tempA["tempSpeed"] = tempA["speed"]
                self.buffTregger(i, skill_tregger_def.KBUFFBEFOREROUND)     # 回合前buff触发器
                self.buffTregger(i, skill_tregger_def.KBUFFKEEP)        # 触发buff效果持续加持

            self.m_tSortArray[i + 5] = 100 + i
            if self.m_tDfdArray[i] != 0:
                # self.m_tDfdArray[i]['tempSpeed'] = self.m_tDfdArray[i]['speed']
                # if 'tempHp' not in self.m_tDfdArray[i]:
                #     self.m_tDfdArray[i]['tempHp'] = self.m_tDfdArray[i]['hp']
                self.setMembers(i + 100)
                tempD = self.getMembers(i + 100)
                tempD["tempSpeed"] = tempD["speed"]
                self.buffTregger(i + 100, skill_tregger_def.KBUFFBEFOREROUND)  # ????????????????????????增加回合前buff触发器
                self.buffTregger(i + 100, skill_tregger_def.KBUFFKEEP)  # 触发buff效果持续加持

        self.m_nDeathSpeed = -1
        self.sortSpeedArray()       # 根据速度排列出手顺序
        # tempSort = {}
        # for i, v in enumerate(self.m_tSortArray):
        #     tempSort[v] = i
        # self.updateMsg(BATTLEFLAG['sort'], tempSort)        # 输出出手顺序
        self.updateMsg(BATTLEFLAG['sort'], self.m_tSortArray[:])    # 更新消息 创建排序队列
        self.m_dMsg['init']['sort_array'].append(self.m_tSortArray[:])

    def sortSpeedArray(self):
        """
        重新排序队列
        """
        def f(x):
            if x < 5:                           # 攻击方速度排序
                if self.m_tAtkArray[x] == 0:
                    return 0
                return self.m_tAtkArray[x]['tempSpeed']
            else:                               # 防守方速度排序
                if self.m_tDfdArray[x - 100] == 0:
                    return 0
                return self.m_tDfdArray[x - 100]['tempSpeed']
        self.m_tSortArray.sort(key=f)

    def beforeBattle(self):
        """
        战前调整战场
        主战卡牌没有人，但是有替补的位置，让替补上场
        """
        for i in range(5):
            if self.getMembers(i) == 0:
                self.substitution(i)
            if self.getMembers(i + 100) == 0:
                self.substitution(i + 100)

    def add_pre_skill(self, pos, card_array, skill_map):
        """
        添加战斗前释放的技能
        :param pos: 位置
        :param card_array: 出战卡牌组
        :param skill_map: 技能包
        :return:
        """
        if pos >= 100:
            real_pos = pos - 100
        else:
            real_pos = pos

        card_id = card_array[real_pos]['id']
        skill_obj = skill_map[card_id]

        preskill_id = 0
        for i in range(len(skill_obj.m_tTreggerFlag)):
            if skill_obj.m_tTreggerFlag[i] == skill_tregger_def.KBEFOREBATTLE:
                preskill_id = skill_obj.m_tSkillid[i]
                break

        if preskill_id:
            self.pre_skill[pos] = preskill_id

    def depart_pre_battle(self):
        """战前技能要和常规战斗数据分离
        """
        user_toggle = getattr(self.attacker, 'pre_battle', 0)
        if not user_toggle:
            return None

        pre_battle = copy.copy(self.m_dMsg['battle'])
        self.m_dMsg['battle'] = {}      # 清空
        self.m_nRecord = 1              # 回合数

        pre_battle = self.format_pre_battle(pre_battle)
        if pre_battle:
            self.updateMsg('pre_battle', pre_battle)

        self.updateMsg('cur_data', self.get_current_data())
        self.add_tail_msg()

    def format_pre_battle(self, steps):
        """战前技能数据格式整理
        """
        if len(steps) < 1:
            return {}

        pre_battle = {
            'skill': {},
            'hurt': {},
            'health': {},
            'buff': {},
            'attr_hurt': {},
        }

        for i in range(1, len(steps) + 1):
            step = steps[i]
            flag = step['flag']
            param = step['param']
            if flag == 'skill':
                self.process_skill_data(param, pre_battle)
                self.process_attr_hurt(param, pre_battle)
            elif flag == 'add_buff':
                src = param['src']
                buffname = param['name']
                pre_battle['buff'][src] = buffname
            elif flag == 'anger':
                self.updateMsg('anger', param)
            else:
                self.stash_msg(step)

        pre_battle['skill'] = self.get_pre_skill()

        if not self.is_pre_skill_null(pre_battle):
            return {}

        return pre_battle

    def is_pre_skill_null(self, pre_battle):
        '''
        战前技能数据是空
        :param pre_battle:
        :return:
        '''
        flag = False
        for k in pre_battle:
            if pre_battle[k]:
                flag = True
                break

        return flag

    def get_pre_skill(self):
        """获取英雄战前释放的技能
        """
        return self.pre_skill

    def process_skill_data(self, param, pre_battle):
        """战前的技能伤害数据整理
        """
        if not param.get('des'):
            return None

        des = param.get('des')
        health = param.get('health')
        hurt = param.get('hurt')
        tmp_health = {}
        tmp_hurt = {}

        if isinstance(des, list):
            for i, d in enumerate(des):
                if health:
                    h = 0
                    if isinstance(health, list):
                        if i < len(health):
                            h = health[i]
                    else:
                        h = health
                    tmp_health[d] = h
                if hurt and i < len(hurt):
                    tmp_hurt[d] = hurt[i]
        else:
            if health:
                tmp_health[des] = health
            if hurt:
                tmp_health[des] = hurt

        if health:
            merge_dict(pre_battle['health'], tmp_health)
        if hurt:
            merge_dict(pre_battle['hurt'], tmp_hurt)

    def process_attr_hurt(self, param, pre_battle):
        """属性伤害数据整理

           @des: pre_battle['attr_hur']:
                attr_hurt: {
                    pos: {‘attr_type’: hurt ’attr_type’: hurt}
                }
        """
        attr_type = param.get('attr_type')
        if not attr_type:
            return None

        attr_hurt = param.get('attr_hurt', [])
        if not isinstance(attr_hurt, list):
            attr_hurt = [attr_hurt]

        for i, d in enumerate(attr_hurt):
            des_attr_hurt = pre_battle['attr_hurt'].get(d, {})
            if des_attr_hurt.get(attr_type):
                des_attr_hurt[attr_type] += attr_hurt[i]
            else:
                des_attr_hurt[attr_type] = attr_hurt[i]

            pre_battle['attr_hurt'][d] = des_attr_hurt

    def add_tail_msg(self):
        """把如death和winer信息加入到m_dMsg后边
        """
        for step in self.tmp_m_dMsg:
            self.updateMsg(step['flag'], step['param'])

        self.tmp_m_dMsg = []

    def stash_msg(self, step):
        """暂存信息
        """
        self.tmp_m_dMsg.append(step)

    def get_current_data(self):
        """获取当前血量和最大血量
        """
        cur_data = {}
        for i in range(len(self.m_tAtkArray)):
            m_tmp = self.m_tAtkArray[i]
            if not m_tmp:
                continue
            tmp_data = {}
            tmp_data['tempHp'] = m_tmp['tempHp']
            tmp_data['maxHp'] = m_tmp['maxHp']
            pos = i

            cur_data[pos] = tmp_data

        for i in range(len(self.m_tDfdArray)):
            m_tmp = self.m_tDfdArray[i]
            if not m_tmp:
                continue
            tmp_data = {}
            tmp_data['tempHp'] = m_tmp['tempHp']
            tmp_data['maxHp'] = m_tmp['maxHp']
            pos = 100 + i
            cur_data[pos] = tmp_data

        return cur_data

    def checkDrama(self, flag, round=0):
        """
        检查剧情
        :param flag: 1、3
        :param round: 回合
        :return:
        """
        if self.drama is None:
            return
        for i in self.drama:
            tempDrama = game_config.drama[i]
            if tempDrama['start_sort'] == flag:
                if flag == 3 and tempDrama['data'] == round:
                    self.updateMsg('drama', i)
                elif flag == 2 and tempDrama['data'] == round:
                    self.updateMsg('drama', i)
                elif flag == 1:
                    self.updateMsg('drama', i)

    def checkOver(self):
        """
        检查战斗是否结束
        """
        winflag_l = False               # 攻击方获胜
        winflag_r = False               # 防守方获胜
        for i in range(5):
            if self.getMembers(i) != 0:
                winflag_l = True
            if self.getMembers(i + 100) != 0:
                winflag_r = True
        if not winflag_l or not winflag_r:
            if winflag_l:
                self.updateMsg(BATTLEFLAG['winer'], 0)
                self.setWiner(0)
            else:
                self.updateMsg(BATTLEFLAG['winer'], 101)
                self.setWiner(101)
            return True
        return False

    def checkDeath(self):
        """
        检查双方队列里是否有死亡
        """
        # 同步前端数据
        self.HistoryChangeMsg()         # changed by ghou on 2014,1,24
        # 检查死亡，以及死亡触发器
        deathArray = []
        for i in xrange(5):
            if self.m_tAtkArray[i] != 0 and self.m_tAtkArray[i]['tempHp'] <= 0:
                # self.updateMsg(BATTLEFLAG['death'], i)      # 更新消息 死亡
                self.buffTregger(i, skill_tregger_def.KBUFFDEAD)    # ???????????????????????死亡buff效果触发
                skill.skillTregger(self.m_tSkillMap[self.m_tAtkArray[i]['id']], skill_tregger_def.KDEAD, self, i)   # 死亡触发器
                if self.m_tAtkArray[i]['tempHp'] <= 0:
                    deathArray.append(i)
                    # self.updateMsg(BATTLEFLAG['death'], i)  # 更新消息 死亡
                    # self.__removeAllBuff(i)
                    # self.substitution(i)
            if self.m_tDfdArray[i] != 0 and self.m_tDfdArray[i]['tempHp'] <= 0:
                # self.updateMsg(BATTLEFLAG['death'], i + 100)    # 更新消息 死亡
                self.buffTregger(i + 100, skill_tregger_def.KBUFFDEAD)  # ???????????????????????死亡buff效果触发
                skill.skillTregger(self.m_tSkillMap[self.m_tDfdArray[i]['id']], skill_tregger_def.KDEAD, self, i + 100)     # 死亡触发器
                if self.m_tDfdArray[i]['tempHp'] <= 0:
                    deathArray.append(i + 100)
                    # self.updateMsg(BATTLEFLAG['death'], i + 100)    # 更新消息 死亡
                    # self.__removeAllBuff(i + 100)
                    # self.substitution(i + 100)

        for j in deathArray:
            self.updateMsg(BATTLEFLAG['death'], j)
            self.__removeAllBuff(j)
            self.substitution(j)

    def substitution(self, positionid):
        """
        替补上场
        positionid: 需要替换队员位置序号
        """
        # 插入排序队列？
        tempindex = 0
        while tempindex < 10:
            if positionid == self.m_tSortArray[tempindex]:      # 出手排序
                break
            tempindex += 1
        if tempindex < self.m_nCurtIndex and tempindex > 0:
            tempi = tempindex - 1
            while tempi >= 0:
                self.m_tSortArray[tempi], self.m_tSortArray[tempi + 1] = self.m_tSortArray[tempi + 1], self.m_tSortArray[tempi]
                tempi -= 1

        if positionid < 5:
            # 攻击方替补
            tempSubId = self.m_tAAlternate[positionid] - 1 + 5
            if self.m_tAtkArray[tempSubId] != 0:
                self.m_tAtkArray[positionid] = self.m_tAtkArray[tempSubId]      # 把替补放在死亡的卡牌位置
                self.m_tAtkArray[tempSubId] = 0                                 # 替补清零
                self.setMembers(positionid)
                self.m_tAtkArray[positionid]["tempSpeed"] = self.m_nDeathSpeed  # 死亡出手速度
                self.m_nDeathSpeed -= 1                                         # 出手速度减掉一点
                self.m_tHistoryDataAll[positionid] = copy.deepcopy(self.m_tAtkArray[positionid])    # 替补的数据 每次同步所有数据一次
                self.updateMsg(BATTLEFLAG['substitution'], {'a': positionid, 'b': tempSubId})       # 更新消息 替补上场
                return True
            else:
                self.m_tAtkArray[positionid] = 0                                # 攻击卡牌置成0
                return False
        else:
            # 守方替补
            tempid = positionid - 100                                           # 防守方索引
            tempSubId = self.m_tDAlternate[tempid] - 1 + 5                      # 替补索引
            if self.m_tDfdArray[tempSubId] != 0:
                self.m_tDfdArray[tempid] = self.m_tDfdArray[tempSubId]
                self.m_tDfdArray[tempSubId] = 0
                self.setMembers(positionid)
                self.m_tDfdArray[tempid]["tempSpeed"] = self.m_nDeathSpeed
                self.m_nDeathSpeed -= 1
                self.m_tHistoryDataAll[positionid] = copy.deepcopy(self.m_tDfdArray[tempid])
                self.updateMsg(BATTLEFLAG['substitution'], {'a': positionid, 'b': tempSubId + 100})  # 更新消息 替补上场
                return True
            else:
                self.m_tDfdArray[tempid] = 0
                return False

    def setMembers(self, positionid):
        '''
        设置成员
        :param positionid: 位置
        初始化临时数据，除血量以外
        {
            id,
            phsc(物理攻),
            mgc(魔法攻),
            dfs(防御),
            hp(血),
            speed(速),
            lv(等级),
            tempSpeed(上场队员当前速度),
            tempPhsc(物攻临时),
            tempMgc,
            tempDfs,
            subHurt,
            crit(暴击率),
            dr(闪避率),
            hr(命中率),
            tempcrit(暴击临时),
            tempdr(闪避率临时),
            temphr(命中率临时)
        }
        :return:
        '''
        if positionid < 5:
            tempMembers = self.m_tAtkArray[positionid]
        else:
            tempMembers = self.m_tDfdArray[positionid - 100]
        tempMembers['tempPhsc'] = tempMembers['phsc']
        tempMembers['tempMgc'] = tempMembers['mgc']
        tempMembers['tempDfs'] = tempMembers['dfs']
        tempMembers['maxHp'] = tempMembers['hp']
        if 'tempHp' not in tempMembers:
            tempMembers['tempHp'] = tempMembers['hp']
            # tempMembers['subhurt'] = 0
            # tempMembers['crit'] = 0
            # tempMembers['dr'] = 0
            # tempMembers['hr'] = 100

        tempMembers['tempSpeed'] = tempMembers['speed']
        tempMembers['tempCrit'] = tempMembers['crit']
        tempMembers['tempDr'] = tempMembers['dr']
        tempMembers['tempHr'] = tempMembers['hr']
        tempMembers['subHurt'] = tempMembers['subhurt']
        magic_sorts = ['fire', 'fire_dfs', 'wind', 'wind_dfs', 'water', 'water_dfs', 'earth', 'earth_dfs']
        for magic_sort in magic_sorts:
            tempMembers['temp' + magic_sort.capitalize()] = tempMembers[magic_sort]

    def __removeAllBuff(self, positionid):
        '''
        去掉指定位置上的所有buff
        :param positionid:
        :return:
        '''
        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5
        self.m_tBuffList[tempIndex] = []

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
                    # if not ((v == "tempSpeed") and (i in self.m_tHadAttackedId)):
                        if tempHData[v] != tempData[v]:
                            temp1[v] = tempData[v]
                            tempHData = tempData[v]
            if len(temp1) > 0:
                tempMsg[i] = temp1
            temp2 = {}
            if tempData2 != 0:
                for j, v in enumerate(tempHData2):
                    # if not((v == "tempSpeed") and ((i + 100) in self.m_tHadAttackedId)):
                        if tempHData2[v] != tempData2[v]:
                            temp2[v] = tempData2[v]
                            tempHData2[v] = tempData2[v]
            if len(temp2) > 0:
                tempMsg[i + 100] = temp2
        
        if len(tempMsg) > 0:
            self.updateMsg('cur_data', tempMsg)

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

    def buffTregger(self, positionid, tregger, synchro=True):
        """
        buff 效果触发器
        :param positionid: 卡牌位置
        :param tregger: 触发类型
        :param synchro:
        :return:
        """
        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5

        tempTrgs = self.m_tBuffList[tempIndex]

        i = 0
        templen = len(tempTrgs)
        while i < templen:
            if tempTrgs[i] is None or tempTrgs[i].m_tregger != tregger:
                i += 1
                continue
            else:
                tempFunc = tempTrgs[i].m_func
                # tempTrgs[i].m_effect -= 1
                if tempTrgs[i].m_effect > 0:
                #     self.removeBuffWithIndex(positionid, i)
                #     templen = len(tempTrgs)
                #     tempFunc(self, positionid)
                #     continue
                # else:
                    self.m_bBuffSkilling = True
                    tempFunc(self, positionid)
                    self.m_bBuffSkilling = False
                    # if synchro:
                    #     self.HistoryChangeMsg()       # changed by zhangchen on 2014,1,24
                    tempTrgs[i].m_effect -= 1
                    templen1 = len(tempTrgs)
                    if templen != templen1:
                        templen = templen1
                        continue
            i += 1

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

    #######################################start end所用的方法############################################

    def get_attacker_last_hp_rate(self):
        """获取攻击方剩余血量百分比 6%  6/100 * 100 6就是6%"""
        all_hp = 0
        last_hp = 0
        for init_card, finished_card in itertools.izip(self.m_dMsg['init']['atk'], self.m_tAtkArray):
            if finished_card:
                all_hp += finished_card['maxHp'] if 'maxHp' in finished_card else finished_card['hp']
                last_hp += finished_card['tempHp'] if 'tempHp' in finished_card else finished_card['hp']
            elif init_card:
                all_hp += init_card['hp']
        return last_hp * 100.0 / all_hp if last_hp else 0

    def get_defender_last_hp_rate(self):
        """获取防守方剩余血量百分比"""
        all_hp = 0
        last_hp = 0
        for init_card, finished_card in itertools.izip(self.m_dMsg['init']['dfd'], self.m_tDfdArray):
            if finished_card:
                all_hp += finished_card['maxHp'] if 'maxHp' in finished_card else finished_card['hp']
                last_hp += finished_card['tempHp'] if 'tempHp' in finished_card else finished_card['hp']
            elif init_card:
                all_hp += init_card['hp']
        return last_hp * 100.0 / all_hp if last_hp else 0

    def get_defender_total_hp(self):
        """获取防守方当前总血量
        每个成员的血量之和
        """
        total_hp = 0
        for i in self.m_tDfdArray:
            if i:
                total_hp += i['tempHp']
        return total_hp

    def get_defender_hp(self):
        """# 世界boss战 玩家失败后 查看boss剩余血量
        """
        for i in self.m_tDfdArray:
            if i:
                return i['tempHp']
        else:
            return 0

    def getPets(self, positionid):
        """
        通过id获得宠物的数据信息 id 0为攻击方 1为防守方
        """
        if positionid not in (0, 1):
            return 0

        pet = self.m_tPet[positionid]
        if not pet:
            return 0

        return pet

    def getAttacker(self):
        """
        得到当前攻击者的id
        """
        return self.m_nHistoryAttack

    def getAnger(self, id):
        """
        获得英雄当前怒气值
        id 0为攻方,1为守方
        """
        return self.m_tAnger[id]

    def addBuff(self, buff, positionid, msg={}):
        """
        给指定角色添加buff
        buff： buff节点
        positionid：位置id
        """
        tempBuff = copy.deepcopy(buff)
        tempdes = self.getMembers(positionid)
        if tempdes == 0 or tempdes["tempHp"] <= 0:
            return

        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5

        i = 0
        for it in self.m_tBuffList[tempIndex]:                  # 前5个是攻击方buff 后5个是防守方buff
            if it != None and it.m_flag == tempBuff.m_flag:     # m_flag buff类型标记，同样类型的buff不能叠加
                # self.m_tBuffList[tempIndex][i] = buff
                self.removeBuffWithIndex(positionid, i)
                break
            i += 1

        # self.m_tBuffList[tempIndex].insert(0, tempBuff)
        self.m_tBuffList[tempIndex].append(tempBuff)
        self.updateMsg('add_buff', {'name': buff.m_name, 'src': positionid, 'msg': msg})

        self.buffTregger(positionid, skill_tregger_def.KBUFFADDBUFF)        # 触发buff效果，增加buff触发器
        if tempBuff.m_tregger == skill_tregger_def.KBUFFKEEP:               # buff持续生效
            self.buffTreggerCur(positionid, tempBuff)                       # 持续buff第一次触发，不做触发计数器减

    def getHeroSkillAll(self, positionid, heroSkillId):
        """
        获得英雄指定技能所有数据
        positionid 0为攻方英雄技能树，1为守方英雄技能树
        heroSkillId 英雄技能id
        """
        if positionid < 0 or positionid > 1 or self.m_tHeroSkill[positionid] == 0:
            return 0
        tempSkillMap = self.m_tHeroSkillTree[positionid]
        tempSkillAll = copy.deepcopy(game_config.leader_skill[heroSkillId])
        if heroSkillId in tempSkillMap['skill']:        # heroSkillId {433: 3} 用户已经学会的主角技能，对应等级
            tempSkillLv = tempSkillMap['skill'][heroSkillId]
        else:
            tempSkillLv = 0
        tempSkillAll['lv'] = tempSkillLv
        return tempSkillAll

    def getHeroSuperSkillAll(self, positionid, heroSkillId):
        """
        获得英雄指定技能所有数据 高级的英雄技能
        """
        if positionid < 0 or positionid > 1 or self.m_tHeroSkill[positionid] == 0:
            return 0
        tempSkillMap = self.m_tHeroSkillTree[positionid]
        tempSkillAll = copy.deepcopy(game_config.leader_skill_advanced[heroSkillId])
        if heroSkillId in tempSkillMap.get('super_skill', {}):
            tempSkillLv = tempSkillMap['super_skill'][heroSkillId]
        else:
            tempSkillLv = 0
        tempSkillAll['lv'] = tempSkillLv
        return tempSkillAll

    def isHaveBuffTerm(self, positionid, teamId):
        """
        检查指定位置上的人是否有指定的buff类型
        :param positionid: 指定位置
        :param teamId: 组的id
        :return:
        """
        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5
        if len(self.m_tBuffList[tempIndex]) <= 0:
            return False
        for buff in self.m_tBuffList[tempIndex]:
            if buff != None and buff.m_team == teamId:
                return True
        return False

    def isHaveBuffTeams(self, positionid, teamStart, teamEnd):
        """
        检查指定位置（positionid）上的人是否有指定的一些buff类型（teamStart到teamEnd）
        """
        for teamid in range(teamStart, teamEnd + 1):
            if self.isHaveBuffTerm(positionid, teamid):
                return True
        return False

    def buffTreggerCur(self, positionid, buffbag):
        """
        根据buff包触发一个指定buff,不减触发器，专为keep触发器做
        """
        tempFunc = buffbag.m_func
        buffbag.m_effect -= 1

        self.m_bBuffSkilling = True
        tempFunc(self, positionid)
        self.m_bBuffSkilling = False

        self.updateMsg("log", "buffTreggerCur")
        self.HistoryChangeMsg()                     # changed by zhangchen on 2014,1,24

    def removeBuff(self, positionid, name):
        """
        删除指定位置上的指定名字的buff
        """
        if positionid < 5:
            buffsIndex = positionid
        else:
            buffsIndex = positionid - 100 + 5
        i = 0
        for buff in self.m_tBuffList[buffsIndex]:
            if buff != None and cmp(buff.m_name, name):
                self.removeBuffWithIndex(positionid, i)
                return
            i += 1

    def removeBuffWithTeam(self, positionid, teamId):
        """
        移除指定位置（positionid）上的指定team（teamId）的buff
        """
        if positionid < 5:
            buffsIndex = positionid
        else:
            buffsIndex = positionid - 100 + 5
        i = 0
        while i < len(self.m_tBuffList[buffsIndex]):
            if self.m_tBuffList[buffsIndex][i] != None and teamId == self.m_tBuffList[buffsIndex][i].m_team:
                self.removeBuffWithIndex(positionid, i)
            i += 1

    def removeBuffWithTeams(self, positionId, teamStart, teamEnd):
        """
        移除指定位置（positionid）上的指定team范围（teamStart，teamEnd）的buff
        """
        if positionId < 5:
            buffsIndex = positionId
        else:
            buffsIndex = positionId
        for teamId in range(teamStart, teamEnd + 1):
            self.removeBuffWithTeam(positionId, teamId)

    def removeAllBuff(self, positionid):
        """
        去掉指定位置上人物的所有
        """
        self.__removeAllBuff(positionid)
        self.updateMsg('remove_buff', {'name': 'all', 'src': positionid})

    def removeOtherAllBuff(self, positionid, name):
        """
        删除除指定buff之外的所有buff
        """
        if positionid < 5:
            buffsIndex = positionid
        else:
            buffsIndex = positionid - 100 + 5
        i = 0
        for buff in self.m_tBuffList[buffsIndex]:
            if buff != None and cmp(buff.m_name, name):
                i += 1
                continue
            self.removeBuffWithIndex(positionid, i)
            i += 1

    def checkRemoveBuff(self):
        """
        检查所有的buff是否要释放
        """
        j = 0
        for buffs in self.m_tBuffList:
            i = 0
            templen = len(buffs)
            if j < 5:
                positionid = j
            else:
                positionid = j - 5 + 100
            while i < templen:
                if buffs[i] != None:
                    buffs[i].m_record -= 1
                    if buffs[i].m_record <= 0 or buffs[i].m_effect <= 0:
                        self.updateMsg('remove_buff', {'name': buffs[i].m_name, 'src': positionid})
                        del buffs[i]
                        continue
                i += 1
            j += 1

    def nextAction(self):
        """
        跳过当前出手者
        """
        self.m_bNextLoop = True

    def getBuffName(self, positionid):
        """
        得到指定位置上角色所有buff的名字
        """
        tempNameList = []
        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5

        tempbuffs = self.m_tBuffList[tempIndex]
        for buff in tempbuffs:
            if buff == None:
                continue
            tempNameList.insert(0, buff.m_name)
        return tempNameList

    def getItemCount(self, positionid):
        """
        返回与位置id同队伍的在场人数
        """
        if positionid < 5:
            tempTeam = self.m_tAtkArray
        else:
            tempTeam = self.m_tDfdArray

        tempCount = 0
        for i in [0, 1, 2, 3, 4]:
            if tempTeam[i] != 0:
                tempCount += 1
        return tempCount

    def subHeroSkillCd(self, heroPositionId, skillName, subCd):
        """
        减少指定英雄的指定技能的当前Cd时间
        :param heroPositionId: 0攻击 1防守
        :param skillName: 技能名称
        :param subCd: 减少的cd时间
        :return:
        """
        self.m_tHeroSkill[heroPositionId].subCurtCd(skillName, subCd)

    def getMoreEnem(self, positionId, count):
        """
        得到更多的敌人没有重复
        :param positionId: 攻击方[0-4]|防守方[100-104]
        :param count: 获取敌人的数量 5
        :return:
        """
        randlist = []
        if positionId < 5:
            templist = range(100, 105)
            tempArray = self.m_tDfdArray
        else:
            templist = range(0, 5)
            tempArray = self.m_tAtkArray

        for i in range(0, 5):
            if tempArray[i] != 0:
                randlist.insert(0, templist[i])

        tempDid = self.selectEnim(positionId)       # 获取默认的攻击目标
        if tempDid in randlist:
            randlist.remove(tempDid)
        random.shuffle(randlist)                    # 打乱顺序
        randlist.insert(0, tempDid)                 # 插回默认的敌人
        realcount = min(count, len(randlist))       # 获取人数
        return randlist[:realcount]                 # 返回敌人的索引 0-4, 100-105

    def getMaybeMoreEnem(self, positionId, count):
        """
        得到更多的敌人，有可能重复
        :param positionId: 攻击者位置
        :param count: 获取数量
        :return:
        """
        randlist = []
        if positionId < 5:
            templist = range(100, 105)
            tempArray = self.m_tDfdArray
        else:
            templist = range(0, 5)
            tempArray = self.m_tAtkArray

        for i in range(0, 5):
            if tempArray[i] != 0:
                randlist.append(templist[i])

        tempDid = self.selectEnim(positionId)
        random.shuffle(randlist)                # 敌人打乱顺序

        wantlist = []
        wantlist.append(tempDid)                # 添加默认的敌人

        for i in range(count - 1):              # 去掉一个可获取的敌人
            wantlist.append(random.choice(randlist))    # 可能会获取重复的敌人

        return wantlist

    def getMoreEnemHaventNormal(self, heroId, count):
        """
        得到更多的敌人，忽略对位，一般用于英雄，heroId可直接传递英雄id，0：取右边敌人count个
                                                                1：取左边敌人count个
        所取敌人不会重复，可能少于count个
        :param heroId:
        :param count:
        :return:
        """
        if heroId == 0:                     # 攻击方英雄
            tempList = range(100, 105)
            tempArray = self.m_tDfdArray
        else:
            tempList = range(0, 5)
            tempArray = self.m_tAtkArray

        randlist = []
        for i in range(0, 5):
            if tempArray[i] != 0:
                randlist.append(tempList[i])

        random.shuffle(randlist)
        realcount = min(count, len(randlist))
        return randlist[:realcount]

    def getMaybeMoreEnemHaventNomal(self, heroId, count):
        """
        得到更多的敌人，忽落对位，同上
        所取得敌人可能会重复，不少于count个
        """
        if heroId == 0:
            tempList = range(100, 105)
            tempArray = self.m_tDfdArray
        else:
            tempList = range(0, 5)
            tempArray = self.m_tAtkArray

        randlist = []
        for i in range(0, 5):
            if tempArray[i] != 0:
                randlist.append(tempList[i])
        random.shuffle(randlist)

        wantlist = []
        for i in range(count - 1):
            wantlist.append(random.choice(randlist))
        return wantlist

    def setSkillProba(self, positionid, skillname, proba):
        """
        设置指定位置上指定技能的触发几率
        """
        if not self.checkHaveValue(positionid):
            return None
        # if positionid < 5:
        #     tempIndex = positionid
        # else:
        #     tempIndex = positionid - 100 + 5
        tempId = self.getMembers(positionid)['id']
        self.m_tSkillMap[tempId].setProba(skillname, proba)

    def setSkillCd(self, positionid, skillname, cd):
        """
        设置指定位置上指定技能的cd时间
        """
        if not self.checkHaveValue(positionid):
            return None
        if positionid < 5:
            tempIndex = positionid
        else:
            tempIndex = positionid - 100 + 5
        tempId = self.getMembers(positionid)['id']
        self.m_tSkillMap[tempId].setCurCd(skillname, cd)

    def realPetHurt(self, positionid, pet_hurt):
        """
        得到指定位置（positionid），指定属性伤害（pet_hurt）,同时减血
        """
        pet_hurt = int(pet_hurt)
        if pet_hurt <= 0:
            return 0

        tempEnem = self.getMembers(positionid)
        if tempEnem == 0:
            return 0

        tempEnem['temHp'] -= pet_hurt
        return pet_hurt

    def getAllLife(self):
        """
        得到在场所有存活的
        """
        tempList = []
        for i in range(5):
            if self.m_tAtkArray[i] != 0:
                tempList.append(i)
            if self.m_tDfdArray[i] != 0:
                tempList.append(i + 100)
        return tempList

    def getCampAssistantLife(self, position_id):
        """ 获取position_id相同阵营的替补位置

        :param position_id: 5、6、7攻击替补 105、106、107
        :return:
        """
        if position_id < 8:
            tempArray = self.m_tAtkArray
            tempOffset = 0
        else:
            tempArray = self.m_tDfdArray
            tempOffset = 100

        tempList = []
        for i in range(5, 8):
            if tempArray[i] != 0:
                tempList.append(i + tempOffset)
        return tempList

    def getCampAssistantAndAllLife(self, position_id):
        """ 获取position_id相同的阵容的替补与上阵位置

        :param position_id:
        :return:
        """
        if position_id < 8:
            tempArray = self.m_tAtkArray
            tempOffset = 0
        else:
            tempArray = self.m_tDfdArray
            tempOffset = 100

        tempList = []
        for i in xrange(8):
            if tempArray[i] != 0:
                tempList.append(i + tempOffset)
        return tempList

    def getRowAll(self, positionid, row):
        """
        得到指定整排
        :param positionid: 攻击|防守
        :param row:
        :return:
        """
        if positionid < 5:
            tempPosition = self.m_tDPosition        # 防守
        else:
            tempPosition = self.m_tAPosition

        temp = []
        if row == 1:
            for i in range(3):                      # 0、1、2
                if tempPosition[i] < 0:             # -1空位
                    continue
                tempData = self.getMembers(tempPosition[i])
                if tempData != 0:
                    temp.append(tempPosition[i])
            if len(temp) > 0:
                return temp
            for i in range(3, 6):
                if tempPosition[i] < 0:
                    continue
                tempData = self.getMembers(tempPosition[i])
                if tempData != 0:
                    temp.append(tempPosition[i])
            return temp
        elif row == 2:
            for i in range(3, 6):
                if tempPosition[i] < 0:
                    continue
                tempData = self.getMembers(tempPosition[i])
                if tempData != 0:
                    temp.append(tempPosition[i])
            if len(temp) > 0:
                return temp
            for i in range(3):
                if tempPosition[i] < 0:
                    continue
                tempData = self.getMembers(tempPosition[i])
                if tempData != 0:
                    temp.append(tempPosition[i])
            return temp

    def getFrontRowAll(self, positionid):
        """
        得到前排所有人，如果没有，得到后排所有人
        """
        return self.getRowAll(positionid, 1)

    def getBackRowAll(self, positionid):
        """
        得到后排所有人，如果没有，得到前排所有人
        """
        return self.getRowAll(positionid, 2)

    def getVerAll(self, positionid):
        """
        得到一列敌人
        """
        if positionid < 5:
            tempPosition = self.m_tDPosition
        else:
            tempPosition = self.m_tAPosition

        temp = []
        tempEnim = self.selectEnim(positionid)
        temp.append(tempEnim)
        tempEnimIndex = tempPosition.index(tempEnim)
        if tempEnimIndex < 3:           # 只有前排有人的时候，后排才会有人
            tempNextEnim = tempPosition[tempEnimIndex + 3]
            if self.getMembers(tempNextEnim) != 0:
                temp.append(tempNextEnim)
        return temp

    def addHp(self, positionid, value):
        """
        给某一个单位加血，不大于血量最大值
        """
        tempH = self.getMembers(positionid)
        if tempH == 0:
            return
        tempMaxHp = tempH['maxHp']

        tempHpR = int(value)
        if tempH['tempHp'] >= 0:
            tempH['tempHp'] += tempHpR
        else:
            tempH['tempHp'] = tempHpR

        if tempH['tempHp'] > tempMaxHp:
            # tempHpR = tempHpR - (tempH['tempHp'] - tempMaxHp)
            tempH['tempHp'] = tempMaxHp
        return int(value)

    def getRoundNum(self):
        """
        得到回合数字
        """
        return self.m_nRoundNum

    ###################################################################

    @classmethod
    def world_boss_enemy_info_generator(cls, enemy_id):
        """# 世界boss信息生成
           返回的数据结构 与logics.battle.Battle.monster_enemy_info_generator 方法返回的内容相同
        """
        return {
            'alternate1': 0,                # 替补
            'alternate2': 0,
            'alternate3': 0,
            'alternate4': 0,
            'alternate5': 0,
            'enemy_rage': 0,                #
            'formation_id': 1,              # 出战阵型
            'position1': 0,                 # 主战的卡牌
            'position2': str(enemy_id),     # 怪的位置
            'position3': 0,
            'position4': 0,
            'position5': 0,
            'reward_exp_character': 0,      # 卡牌加经验
            'reward_exp_role': 0,           # 主角加经验
            'team_rage': 0
        }

    @classmethod
    def monster_enemy_info_generator(cls, fight_key):
        """# monster_enemy_info_generator: 生成一个包含了怪物的数据结构
        args:
            fight_key:    ---    arg
        returns:
            0    ---
        """
        d = {}
        raw_config = game_config.map_fight[str(fight_key)]
        for k, v in raw_config.iteritems():
            if 'position' in k or 'alternate' in k:
                if len(v) == 0:
                    d[k] = 0                        # 位置放卡牌
                elif len(v) != 1:
                    d[k] = weight_choice(v, 1)[0]   # 位置放卡牌
                else:
                    d[k] = int(v[0])
            else:
                d[k] = v
        return d

    def battle_reward(self, fight_info, sort=1):
        """# battle_reward: 打怪的时候战斗掉落 *** 此函数执行完后必须执行user.save()来保存 ***
        args:
            fight_info:    ---    arg
        returns:
            0    ---
        """
        card_obj = self.attacker.cards
        battle_rewards = {
            'reward_exp_player': (),        # 玩家经验
            'reward_exp_character': {},     # 卡牌经验
            'reward_character': {},         # 卡牌奖励
            'reward_item': {}               # 道具奖励
        }

        # 给攻击者送经验
        reward_exp_player = fight_info['reward_exp_role']       # 战斗掉落的角色经验
        if reward_exp_player:
            old_exp = self.attacker.exp
            self.attacker.exp += reward_exp_player
            battle_rewards['reward_exp_player'] = (
                reward_exp_player, old_exp, self.attacker.level_change   # 奖励经验、之前的经验、角色等级变化
            )

        # 给每张在阵卡牌送经验
        reward_card_exp = fight_info['reward_exp_character']
        if reward_card_exp:                 # 主战阵型 card_obj.alignment[0]
            for card_set, add_exp in [(card_obj.alignment[0], reward_card_exp), (card_obj.alignment[1], reward_card_exp / 2),]:
                for card_id in card_set:
                    if card_id == card_obj.NONE_CARD_ID_FLAG:
                        continue
                    old_exp = card_obj._cards[card_id]['exp']
                    level_change = card_obj.add_exp(card_id, add_exp)
                    battle_rewards['reward_exp_character'][card_id] = (
                        add_exp, old_exp, level_change
                    )
            self.attacker.user_m._add_model_save(card_obj)

        for p in [
            'position1', 'position2', 'position3', 'position4', 'position5',
            'alternate1', 'alternate2', 'alternate3', 'alternate4', 'alternate5'
        ]:
            enemy = fight_info['p']
            if not enemy:
                continue
            if sort == 1:
                enemy_config = game_config.enemy_all[str(enemy)]            # 获取默认的敌人
            else:
                enemy_config = game_config.afterlife_enemy[str(enemy)]      # 获取其他敌人
            enemy_reward_config = [enemy_config['loot_non']]
            for c in ['loot_character', 'loot_item']:                       # 掉落
                for i in enemy_config[c]:
                    enemy_reward_config.append([i[0], i[1], c])

            # 只有loot_non, 没有奖励
            if len(enemy_reward_config) == 1:
                continue
            rbl = utils.weight_choice(enemy_reward_config, 1)

            if rbl[0] == -1:
                continue
            if rbl[2] == 'loot_character':
                card_id = card_obj.now(rbl[0])
                # card_obj._cards[card_id]['lv'] = rbl[1]
                battle_rewards['reward_character'][card_id] = card_obj.single_card_info(card_id)
                self.attacker.user_m._add_model_save(card_obj)

            if rbl[2] == 'loot_item':
                self.attacker.item.add_item(rbl[0], 1, immediate=True)
                battle_rewards['reward_item'][rbl[0]] = 1
                self.attacker.user_m._add_model_save(self.attacker.item)
        return battle_rewards

    def merge_battle_reward(self, all_rewards, _battle_reward):
        """# 合成多场战斗的战斗奖励
        args:
            all_rewards: merge之前总共的奖励
            _battle_reward: 单场奖励
        """
        battle_rewards = {
            'reward_exp_player': [],
            'reward_exp_character': {},
            'reward_character': {},
            'reward_item': {}
        }
        battle_rewards.update(all_rewards)
        if _battle_reward['reward_exp_player']:
            if not battle_rewards['reward_exp_player']:     # reward_exp_player: (add_exp, old_exp, level_change)
                battle_rewards['reward_exp_player'] = list(_battle_reward['reward_exp_player'])
            else:
                battle_rewards['reward_exp_player'][0] += _battle_reward['reward_exp_player'][0]
                battle_rewards['reward_exp_player'][-1] = battle_rewards['reward_exp_player'][-1]

        for k, v in _battle_reward['reward_exp_character'].iteritems():     # k是card_id
            if k not in battle_rewards['reward_exp_character']:     # reward_exp_character: (add_exp, old_exp, level_change)
                battle_rewards['reward_exp_character'][k] = list(v)
            else:
                battle_rewards['reward_exp_character'][k][0] += v[0]
                for i in v[-1]:
                    if i not in battle_rewards['reward_exp_character'][k][-1]:
                        battle_rewards['reward_exp_character'][k][-1].append(i)

        for k, v in _battle_reward['reward_character'].iteritems():
            battle_rewards['reward_character'][k] = v
        for k, v in _battle_reward['reward_item'].iteritems():
            if k in battle_rewards['reward_item']:
                battle_rewards['reward_item'][k] += v
            else:
                battle_rewards['reward_item'][k] = v
        return battle_rewards

    def getAllCardHp(self):
        """
        获得战场中全部卡牌剩余血量
        """
        tempCardHp = []
        for i in range(10):
            tempMem = self.m_tAtkArray[i]
            if tempMem != 0:
                if "tempHp" in tempMem:
                    tempCurHp = tempMem["tempHp"]
                else:
                    tempCurHp = tempMem["hp"]
                tempCardHp.append((i, tempCurHp))
            tempMem = self.m_tDfdArray[i]
            if tempMem != 0:
                if "tempHp" in tempMem:
                    tempCurHp = tempMem["tempHp"]
                else:
                    tempCurHp = tempMem["hp"]
                tempCardHp.append((i + 100, tempCurHp))
        return tempCardHp

    def getAttackCardHP(self):
        """# getAttackCardHP: 获得攻击方当前血量
        args:
            :    ---    arg
        returns:
            0    ---
        """
        tempCardHp = []
        for i in range(10):
            tempMem = self.m_tAtkArray[i]
            if tempMem != 0:
                if "tempHp" in tempMem:
                    tempCurHp = tempMem["tempHp"]
                else:
                    tempCurHp = tempMem["hp"]
                tempCardHp.append((i, tempCurHp))
        return tempCardHp

    def getDefendCardHP(self,):
        """# getDefendCardHP: 获得防守方当前血量
        args:
            :    ---    arg
        returns:
            0    ---
        """
        tempCardHp = []
        for i in range(10):
            tempMem = self.m_tDfdArray[i]
            if tempMem != 0:
                if "tempHp" in tempMem:
                    tempCurHp = tempMem["tempHp"]
                else:
                    tempCurHp = tempMem["hp"]
                tempCardHp.append((i + 100, tempCurHp))
        return tempCardHp

    def setCardHp(self, positionid, hp):
        """
        设置某个位置上的卡牌血量
        """
        if positionid < 10:
            tempCard = self.m_tAtkArray[positionid]
        else:
            tempCard = self.m_tDfdArray[positionid - 100]

        if tempCard == 0:
            return 0
        if hp > tempCard["maxHp"]:
            hp = tempCard["maxHp"]

        tempCard['tempHp'] = hp
        self.HistoryChangeMsg()
        return hp

    def getAtkDie(self):
        """ 获取攻击方死亡卡牌

        :return:
        """
        life = set()                        # 存活的卡牌
        for i in xrange(10):
            tempMem = self.m_tAtkArray[i]
            if tempMem != 0 and tempMem['tempHp'] > 0:
                life.add(tempMem['id'].split('_')[-1])

        all_atk = set([i.split('_')[-1] for i in self.card_att.keys()])     # self.card_att传输给前端的所有卡牌

        return list(all_atk - life)         # 所有卡牌 - 存活的卡牌

    def get_attacker_hurt_hp(self):
        """ 获取攻击方伤害总血量

        :return:
        """
        remainder_hp = sum([min(i['tempHp'], self.attacker_hp.get(i['id'], 0)) for i in self.m_tAtkArray if i])  # attacker_hp 攻击方初始化血量

        total_hp = sum([i for i in self.attacker_hp.itervalues()])

        return max(0, total_hp - remainder_hp)

    def get_defender_hurt_hp(self):
        """ 获取防守方伤害总血量

        :return:
        """
        remainder_hp = sum([min(i['tempHp'], self.defender_hp.get(i['id'], 0)) for i in self.m_tDfdArray if i])

        total_hp = sum([i for i in self.defender_hp.itervalues()])

        return max(0, total_hp - remainder_hp)

    def get_attacker_left_hp_percent(self):
        """ 获取攻击方剩余血量百分比

        :return:
        """
        remainder_hp = sum([min(i['tempHp'], self.attacker_hp.get(i['id'], 0)) for i in self.m_tAtkArray if i])

        total_hp = sum([i for i in self.attacker_hp.itervalues()])

        return float(remainder_hp) / total_hp


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