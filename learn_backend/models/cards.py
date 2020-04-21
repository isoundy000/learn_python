#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import copy
import time
import datetime
import itertools
import settings

from lib import utils
from lib.utils.debug import print_log
from lib.db import ModelBase
import game_config
from logics import notice
from lib.utils import salt_generator
from lib.utils import generate_rank_score
from lib.utils import weight_choice


class CardRemoveError(Exception):
    """# CardRmoveError: docstring"""
    def __init__(self, message, Errors):
        """# __init__: docstring
        """
        super(CardRemoveError, self).__init__(message)
        self.Errors = Errors


'''
pos: 
    alignment_1: 1,2,3,4,5
    alignment_2: 11,12,13,14,15
'''
class Cards(ModelBase):
    """# Cards: 卡片包裹
    self.cards 动态生成，显示的是self._cards 和 game_config.character_detail 组合而成的 card的完整数据
    self.alignment 动态生成，显示的是 战斗队伍中的卡牌，数据结构：
        [
            [1,2,3],
            [5,6,7]
        ]
    self._cards 数据库中的用户的卡牌记录，数据结构：
        {
            1: {               # 卡牌的储存id
                c_id: '',      # 配置id
                lv: 1,         # 卡的等级
                exp: 0,        # 卡的经验
                pos: 0,        # 战斗位，0表示不在战斗队伍中，小于10表示在第一阵列，大于10表示在第二阵列
                s_1: {         # 卡牌的技能1
                    lv: 1,     # 技能1等级
                    exp: 0,    # 技能1经验
                    s: '1',    # 技能的配置key
                },
                s_2: {lv,
                    exp,
                    s,},
                s_3: {lv,
                    exp,
                    s,},
                    }
                s_4: {lv,
                    exp,
                    s,},
                    }
                s_5: {lv,
                    exp,
                    s,},
                    }
                'patk_crystal': 0, 'matk_crystal': 0, 'def_crystal': 0, 'speed_crystal': 0, 'hp_crystal': 0, # 使用各种能晶所升到的等级
            }
        }

    self.formation 数据库中关于阵型的记录, 数据结构
        {
            'own': [1, ],   # 已经开启的阵型列表
            'current': 1,   # 当前使用的阵型
        }

    self.card_rank = {
        'flag': 0,      # 0代表没有检查过, 1代表检查过了
        'card': {
            3: (),      # 紫卡, ('card_id': combat)
            4: (),      # 橙卡, ('card_id': combat)
        },
    }
    """
    # 卡牌 开启新的站位 阵型 主战卡出战个数 替补卡出战个数 助威 阵型上的configid 助威效果
    _need_diff = ('_cards', 'open_position', 'formation', 'position_num',
                  'alternate_num', 'assistant', 'destiny', 'assistant_effect')

    NONE_CARD_ID_FLAG = '-1'

    DIRT_SHOP_REFRESH_TIME = 4 * 3600  # dirt shop更新周期
    DIRT_SHOP_NUM = 8  # 可看到的dirt_shop数量

    DEFAULT_EXP_INHERIT = 0.7  # 默认经验传承系数

    ORANGE_CARD_RANK_KEY_PREFIX = 'orange_card_rank'
    PURPLE_CARD_RANK_KEY_PREFIX = 'purple_card_rank'    # 紫色

    SETTINGS_LIST_FOR_UPDATA_FUNC_4_5 = ['dev', 'test', 'cloud_ios']

    REPLACE_ATTR = ['lv', 'evo', 'step', 'bre', 'pos', 'exp', 'pre_exp', 'super_step',
                    'def_crystal', 'hp_crystal', 'matk_crystal', 'patk_crystal', 'speed_crystal',
                    'evo_metals', 'super_soul', 'remove_avail']

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            '_cards': {},
            'bag_extend': 0,                 # 卡牌背包的扩展
            'formation': {
                'own': range(1, 7),        # 已经开启的阵型列表  [1,2,3,4,5,6]
                'current': 1,              # 当前使用的阵型      6
            },
            'open_position': range(1, 9),  # 当前已开启站位 [1, 2, 3, 4, 5, 6, 7, 8]
            'dirt_shop': {},               # 可看到的 dirt shop列表
            'dirt_refresh_ts': 0,          # dirt 上次更新时间
            'dirt_refresh_times': 0,       # dirt shop 手工刷新次数
            'position_num': 1,             # 主战卡出战个数
            'alternate_num': 0,            # 替补卡出战个数
            'last_date': '',
            'assistant': ['-1'] * 9,       # -1为未开通, 0表示没有 助威卡牌
            'destiny': ['-1'] * 9,         # -1为未开通, 0表示没有 命运卡牌
            'assistant_effect': ['-1'] * 9,  # -1为标志着没有初始化数据
            'max_combat': 0,                # 历史最大战力
            'exp_ball': 0,                  # 卡牌经验球
            'card_rank': {                  # 卡牌排行
                'flag': 0,
                'card': {
                    3: (),
                    4: (),
                },
            },
            'card_exchange_reward': [],  # 卡牌合成的特定奖励
            'exchange_card_times': {},  # {exchange_id : cishu} 每类 兑换的次数
            'ingorne_update_func': 0,  # 第一版func_4 升级错误 如果未被第一版func_4影响的用户 就直接跳过func_5
            # 'god_field_ids': {1: [], 2: [], 3: []},  # 神域战斗的卡牌阵型。1:[card_id,.....,card_id], 2:[card_id,.....], 3:[card_id,.....]
            'role_attri_level': 0,  # 英雄属性等级
        }
        self.orange_card_rank_key = None
        self.purple_card_rank_key = None
        super(Cards, self).__init__(self.uid)

    def data_update_func_1(self):
        """# 记录升级到当前级别总共需要的经验"""
        level_config = game_config.character_base
        for v in self._cards.itervalues():
            if 'pre_exp' not in v:
                v['pre_exp'] = 0
                for level in range(1, v['lv']):
                    card_type = game_config.character_detail[v['c_id']]['type']
                    rate = game_config.character_base_rate[card_type]['exp_rate']
                    v['pre_exp'] += int(level_config[level]['exp'] * rate)

    def data_update_func_2(self):
        """# evo配置调整，重新计算下卡牌数值"""
        for k in self._cards:
            self.calc_base_attrs_value(k)

    def data_update_func_3(self):
        """# evo配置调整，重新计算下卡牌数值"""
        for k in self._cards:
            self.calc_base_attrs_value(k)

    def data_update_func_4(self):
        """# 死神2200 技能配置出错，重走一次进阶以更正技能数据"""
        if settings.ENV_NAME not in self.SETTINGS_LIST_FOR_UPDATA_FUNC_4_5:
            return

        self.ingorne_update_func = 5
        for k, v in self._cards.iteritems():
            if v['c_id'] == 2200:
                card_config = game_config.character_detail[v['c_id']]
                lv = v['lv']
                pre_exp = v['pre_exp']
                for i in '12345':
                    if 's_' + i not in v:
                        continue
                    skill_source = card_config.get('skill_%s_source' % i)
                    if skill_source:
                        s = utils.weight_choice(skill_source, 1)[0]
                    else:
                        s = 0
                    s_lv = 1
                    avail = 0 if i != '1' else 2
                    v['s_' + i].update({'s': int(s), 'avail': avail})
                evo = v['evo']
                v['evo'] = 0
                for i in range(evo):
                    self.evolution(k)

                v['lv'] = lv
                v['pre_exp'] = pre_exp

    def data_update_func_5(self):
        """# func_4把卡牌等级和技能等级给搞错了，找补回来
        """
        if settings.ENV_NAME not in self.SETTINGS_LIST_FOR_UPDATA_FUNC_4_5:
            return

        # 未走第一次错误func4的 不走func5
        if self.ingorne_update_func == 5:
            return
        for k, v in self._cards.iteritems():
            if v['c_id'] == 2200:
                card_config = game_config.character_detail[v['c_id']]
                for i in '12345':
                    if 's_' + i not in v:
                        continue
                    skill_source = card_config.get('skill_%s_source' % i)
                    if skill_source:
                        s = utils.weight_choice(skill_source, 1)[0]
                    else:
                        s = 0
                    s_lv = 1
                    avail = 0 if i != '1' else 2
                    v['s_' + i].update({'s': int(s), 'avail': avail})

                lv = v['lv']
                evo = v['evo']
                v['evo'] = 0
                level_off = 0
                evo_config = self.get_evolution_config(k, v, card_config)
                for i in range(evo):
                    cur_evo = v['evo']
                    next_evo = cur_evo + 1
                    _config = evo_config.get(next_evo)
                    if _config:
                        # 加回被降的等级 重新计算pre_exp
                        level_off += _config['level_off']
                    self.evolution(k)

                level_config = game_config.character_base
                v['pre_exp'] = 0
                v['lv'] = min(v['level_max'], lv + level_off)
                for level in range(1, v['lv']):
                    card_type = card_config['type']
                    rate = game_config.character_base_rate[card_type]['exp_rate']
                    v['pre_exp'] += int(level_config[level]['exp'] * rate)

                # 技能等级直接开到最大
                for i in '12345':
                    skill = v.get('s_' + i)
                    if skill and skill['avail']:
                        skill['lv'] = 30

    def data_update_func_6(self):
        """# 增加助威+1数据
        """
        pass

    def data_update_func_7(self):
        """# 增加助威+1数据
        """
        pass

    def data_update_func_8(self):
        """# evo配置调整，重新计算下卡牌数值"""
        for k in self._cards:
            self.calc_base_attrs_value(k)

    def data_update_func_9(self):
        """# 死神2200 技能配置又又出错，再次重走一次进阶以更正技能数据"""
        if settings.ENV_NAME not in self.SETTINGS_LIST_FOR_UPDATA_FUNC_4_5:
            return

        for k, v in self._cards.iteritems():
            if v['c_id'] == 2200:
                card_config = game_config.character_detail[v['c_id']]
                lv = v['lv']
                pre_exp = v['pre_exp']
                for i in '12345':
                    if 's_' + i not in v:
                        continue
                    skill_source = card_config.get('skill_%s_source' % i)
                    if skill_source:
                        s = utils.weight_choice(skill_source, 1)[0]
                    else:
                        s = 0
                    s_lv = 1
                    avail = 0 if i != '1' else 2
                    v['s_' + i].update({'s': int(s), 'avail': avail})
                evo = v['evo']
                v['evo'] = 0
                for i in range(evo):
                    self.evolution(k)

                v['lv'] = lv
                v['pre_exp'] = pre_exp

    def data_update_func_10(self):
        """# 增加助威+1数据
        """
        self.refesh_assistant_effect()

    def data_update_func_11(self):
        """# 增加助威+1数据
        """
        for index, ass in enumerate(self.assistant_effect):
            if ass.get('active_status') != '-1':
                self.assistant_effect[index]['base_value'] = game_config.assistant[index + 1]['att_value']

    def data_update_func_12(self):
        """# 更新图鉴, 图鉴需要在图鉴模块中更新
        """
        pass
        # for k, v in self._cards.iteritems():
        #     if v['c_id'] in [7900, 32000, 32100]:
        #         self.add_card_book(v['c_id'])

    def data_update_func_13(self):
        """# evo配置调整，重新计算下卡牌数值"""
        for k in self._cards:
            self.calc_base_attrs_value(k)
        self.save()

    def data_update_func_14(self):
        """增加技能4和5"""
        for k, v in self._cards.iteritems():
            card_config = game_config.character_detail[v['c_id']]
            for i, s in enumerate(('s_4', 's_5')):
                if s not in v:
                    skill_source = card_config.get('skill_%s_source' % (i + 4))
                    if skill_source:
                        skill = utils.weight_choice(skill_source, 1)[0]
                    else:
                        skill = 0
                    v[s] = {'lv': 1, 'exp': 0, 'avail': 0, 's': skill}
                elif not v[s]['s']:
                    skill_source = card_config.get('skill_%s_source' % (i + 4))
                    if skill_source:
                        skill = utils.weight_choice(skill_source, 1)[0]
                    else:
                        skill = 0
                    v[s]['s'] = skill
        self.save()

    def data_update_func_15(self):
        """增加技能4和5"""
        for k, v in self._cards.iteritems():
            card_config = game_config.character_detail[v['c_id']]
            for i, s in enumerate(('s_4', 's_5')):
                if s not in v:
                    skill_source = card_config.get('skill_%s_source' % (i + 4))
                    if skill_source:
                        skill = utils.weight_choice(skill_source, 1)[0]
                    else:
                        skill = 0
                    v[s] = {'lv': 1, 'exp': 0, 'avail': 0, 's': skill}
                elif not v[s]['s']:
                    skill_source = card_config.get('skill_%s_source' % (i + 4))
                    if skill_source:
                        skill = utils.weight_choice(skill_source, 1)[0]
                    else:
                        skill = 0
                    v[s]['s'] = skill
        self.save()

    def data_update_func_16(self):
        """ 清理战力排行榜

        :return:
        """
        self.max_combat = 0

    def data_update_func_17(self):
        """ 修改卡牌8800技能

        :return:
        """
        for k, v in self._cards.iteritems():
            if v['c_id'] == 8800:
                card_config = game_config.character_detail[v['c_id']]
                lv = v['lv']
                pre_exp = v['pre_exp']
                for i in '2':
                    if 's_' + i not in v:
                        continue
                    skill_source = card_config.get('skill_%s_source' % i)
                    if skill_source:
                        s = utils.weight_choice(skill_source, 1)[0]
                    else:
                        s = 0
                    v['s_' + i].update({'s': int(s)})
                evo = v['evo']
                v['evo'] = 0
                for i in range(evo):
                    self.evolution(k)

                v['lv'] = lv
                v['pre_exp'] = pre_exp

    def data_update_func_18(self):
        """ 修改卡牌8800技能

        :return:
        """
        for k, v in self._cards.iteritems():
            if v['c_id'] == 9800:
                card_config = game_config.character_detail[v['c_id']]
                lv = v['lv']
                pre_exp = v['pre_exp']
                for i in '12345':
                    if 's_' + i not in v:
                        continue
                    skill_source = card_config.get('skill_%s_source' % i)
                    if skill_source:
                        s = utils.weight_choice(skill_source, 1)[0]
                    else:
                        s = 0
                    v['s_' + i].update({'s': int(s)})
                evo = v['evo']
                v['evo'] = 0
                for i in range(evo):
                    self.evolution(k)

                v['lv'] = lv
                v['pre_exp'] = pre_exp

    def data_update_func_19(self):
        """ 修改转世卡牌技能
            32300  圣の齐天大圣
            32400  圣の霸王丸
            32500  圣の奥丁
            32600  圣の贝吉特
            60500  圣の哈迪斯
            60600  圣の波塞冬
            60700  圣の宙斯
            60800  圣の雅典娜
        :return:
        """
        for k, v in self._cards.iteritems():
            if v['c_id'] in [32300, 32400, 32500, 32600, 60500, 60600, 60700, 60800]:
                for i in '12345':
                    old_suffix = v['s_' + i]['s'] % 100
                    new_s_id = v['c_id'] + old_suffix
                    v['s_' + i].update({'s': new_s_id})

    @classmethod
    def get(cls, uid, server=''):
        o = super(Cards, cls).get(uid, server)
        fredis = o.get_father_redis()
        setattr(o, "fredis", fredis)
        return o

    def refesh_assistant_effect(self):
        """ 助威+1数据

        :return:
        """
        for index, ass in enumerate(self.assistant_effect):
            if ass == '-1':
                init_data = {
                    'active_status': '-1',  # 状态 -1未激活 0已激活

                    'base_value': 0,    # 基础数值, 可变, 无用
                    'ass_random_id': 0,     # assistant_random的id, 通过ability1

                    'limit_character_id': 0,    # 限定伙伴
                    # 'limit_value': 0,   # 限定数值, 固定, 无用

                    'two_switch': 0,    # 第二属性开关
                    # 'base_level': 0,    # 基础等级
                    'two_value': 0,    # 限定开启第二个属性配置id, 可变
                    'refresh': {        # 刷新临时数据
                        'ability1': 0,
                        'card': 0,
                        'ability2': 0,
                    }
                }
                self.assistant_effect[index] = init_data
            elif 'refresh' not in ass:
                self.assistant_effect[index]['refresh'] = {     # 刷新临时数据
                    'ability1': 0,
                    'card': 0,
                    'ability2': 0,
                }
                self.assistant_effect[index]['ass_random_id'] = 0
            if 'active_status' not in self.assistant_effect[index]:
                self.assistant_effect[index]['active_status'] = '-1'
            if self.assistant_effect[index]['active_status'] != '-1' and \
                self.assistant_effect[index]['limit_character_id'] == 0:
                assistant_config = game_config.assistant[index + 1]
                self.assistant_effect[index]['limit_character_id'] = \
                    self.generate_assistant_random(assistant_config['card'])
            if 'two_switch' not in ass:
                self.assistant_effect[index]['two_switch'] = 0
        self.save()

    def refresh_dirt_shop(self, refresh_by_coin=False):
        flag = False
        now = datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')
        if today != self.last_date:
            self.last_date = today
            self.dirt_refresh_times = 0
            flag = True

        t = int(time.time())
        if t - self.dirt_refresh_ts > self.DIRT_SHOP_REFRESH_TIME or refresh_by_coin:
            shops = []
            for k, v in game_config.dirt_shop.iteritems():
                if not v['is_positive'] or refresh_by_coin:
                    # 添加条件判断，若指定了等级范围，则只有在这个等级范围内才可刷新
                    show_level = v.get('show_level')
                    if not show_level or show_level[0] <= self.weak_user.level <= show_level[1]:
                        shops.append([k, v['weight']])

            d = []
            for i in range(min(self.DIRT_SHOP_NUM, len(shops))):
                rs = utils.weight_choice(shops)
                shops.remove(rs)
                d.append(rs[0])

            d.sort()
            if not refresh_by_coin:
                self.dirt_refresh_ts = t
            self.dirt_shop = dict.fromkeys(d, 0)
            flag = True

        if flag:
            self.save()

    def dirt_shop_expire(self):
        return self.DIRT_SHOP_REFRESH_TIME - int(time.time()) + self.dirt_refresh_ts

    def _client_cache_update(self):
        """# _client_cache_update: 卡牌的变化，不能仅仅把数据库记录的数据交给前端，还需要用single_card_info处理一下
        args:
            :    ---    arg
        returns:
            0    ---
        """
        if '_cards' in self._diff:
            d = {}
            for k, v in self._diff['_cards']['update'].iteritems():
                d[k] = self.single_card_info(v)
            self._diff['cards'] = {
                'update': d,
                'remove': self._diff['_cards']['remove']
            }
            del self._diff['_cards']
        return self._diff

    @classmethod
    def _make_id(cls, config_id):
        """# make_id: 生成一个卡片的id
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return '%s-%s-%s' % (config_id, int(time.time()), salt_generator())

    def crystal_effect(self, crystal_type, level):
        """# crystal_effect: docstring
        args:
            crystal_type, level:    ---    arg
        returns:
            0    ---
        """
        config = game_config.character_strengthen
        crystal_type = 'add_' + crystal_type
        if level in config:
            return config[level][crystal_type]
        else:
            return 0

    CHAIN_EFFECT_NUM_NAME_ARRAY = [
        'patk', 'matk', 'def', 'speed', 'hp',
    ]

    GEM_CHAIN_EFFECT_NUM_NAME_ARRAY = [
        '', 'patk', 'matk', 'def', 'speed', 'hp', 'crit', 'hr', 'subhurt', 'dr'
    ]

    CHAIN_EFFECT_NUM_NAME_DICT = {
        1: 'patk',
        2: 'matk',
        3: 'def',
        4: 'speed',
        5: 'hp',
        6: 'crit',
        7: 'hr',
        8: 'subhurt',
        9: 'dr',
        201: 'fire',
        202: 'water',
        203: 'wind',
        204: 'earth',
        301: 'fire_dfs',
        302: 'water_dfs',
        303: 'wind_dfs',
        304: 'earth_dfs',
    }

    def commander_effect(self, tp, level):
        config = game_config.commander_type
        tp = 'add_%s' % tp
        if level in config:
            return config[level].get(tp, 0)
        else:
            return 0

    def single_card_info(self, card_dict, for_battle=False, is_assistant=False, assistant_config=None, god_formation=None):
        """# single_card_info: 包含了一个卡牌各个数值的比较完整的info
        args:
            card_dict:    ---    arg
        returns:
            0    ---
        """
        if not isinstance(card_dict, dict):
            card_dict = self._cards[card_dict]
        card_config = game_config.character_detail[int(card_dict['c_id'])]

        lv = card_dict['lv']
        card_id = card_dict['id']

        # 关于卡牌间联携和卡牌＋道具联携
        chain_add = {}
        if ((for_battle or is_assistant) and (card_dict['pos'] != 0 or card_id in self.assistant)) or god_formation:
            for chain_id in card_config['chain']:
                chain_config = game_config.chain[chain_id]
                # 卡牌联携
                if int(chain_config['condition_sort']) == 0:
                    chain_character_id = set()
                    for cid in chain_config['data']:
                        chain_character_id.add(game_config.character_detail[cid]['character_ID'])
                    # [1, 2, 3].issubset(set([1, 2, 3, 4, 5])) = True
                    if not god_formation and not chain_character_id.issubset(self.card_config_id_on_alignment):
                        continue
                    if god_formation and not chain_character_id.issubset(self.card_id_on_alignment(god_formation=god_formation)):
                        continue
                else:
                    # 装备联携
                    if card_id not in self.assistant:
                        # 出战的卡牌和替补的装备id [0,1,2,3,4,5,6,7,8,9]
                        if not god_formation:
                            _pos_for_equip = card_dict['pos'] - 1 if card_dict['pos'] < 10 else card_dict['pos'] - 6
                            equips = self.weak_user.equip.equip_pos[_pos_for_equip]
                        elif god_formation == 1:
                            _index = self.weak_user.god_field.god_field_ids.get(god_formation).index(card_id)
                            equips = self.weak_user.equip.equip_pos_1[_index]
                        elif god_formation == 2:
                            _index = self.weak_user.god_field.god_field_ids.get(god_formation).index(card_id)
                            equips = self.weak_user.equip.equip_pos_2[_index]
                        elif god_formation == 3:
                            _index = self.weak_user.god_field.god_field_ids.get(god_formation).index(card_id)
                            equips = self.weak_user.equip.equip_pos_3[_index]
                    else:
                        # 助威卡牌的装备id [100,101,.......,109]
                        index = self.assistant.index(card_id)
                        equips = self.weak_user.equip.ass_equip_pos[index + 100]

                    is_chain = True

                    for i in chain_config['data']:
                        # 联携表中装备id
                        equip_config = game_config.equip[i]
                        sort = equip_config['sort']
                        equip_id = equips[sort - 1]     # [1, 2, 3, 4] 相应的位置放置相应的装备
                        if not equip_id:
                            is_chain = False
                            continue

                        # 卡牌阵型上的装备
                        config = game_config.equip[self.weak_user.equip._equip[equip_id]['c_id']]
                        if 'chain_id' in config:
                            c_id = config['chain_id']
                        else:
                            c_id = config['equip_id']

                        if 'chain_id' in equip_config:
                            e_c_id = equip_config['chain_id']
                        else:
                            e_c_id = equip_config['equip_id']

                        # 相应的位置放置相应的装备
                        if not (e_c_id == c_id or c_id == sort):
                            is_chain = False
                            continue

                    if not is_chain:
                        continue

                for chain_effect in chain_config['effect']:
                    if self.CHAIN_EFFECT_NUM_NAME_ARRAY[chain_effect[0]] in chain_add:
                        chain_add[self.CHAIN_EFFECT_NUM_NAME_ARRAY[chain_effect[0]]] += chain_effect[1]
                    else:
                        chain_add[self.CHAIN_EFFECT_NUM_NAME_ARRAY[chain_effect[0]]] = chain_effect[1]

        r = copy.deepcopy(card_dict)
        # 初始化属性伤害和属性防御
        r['fire'] = 0
        r['water'] = 0
        r['wind'] = 0
        r['earth'] = 0
        r['fire_dfs'] = 0
        r['water_dfs'] = 0
        r['wind_dfs'] = 0
        r['earth_dfs'] = 0

        assistant_info = {}
        if is_assistant and not god_formation:
            # 助威
            end_evo = assistant_config.get('cardlimit', 25)
            card_evo = card_dict.get('evo', 0)
            if end_evo < card_evo:
                assistant_info = self.calc_base_attrs_diff_value(card_id, start_evo=end_evo, end_evo=card_evo,
                                                                 card_info=card_dict, card_config=card_config)

        for s in self.CHAIN_EFFECT_NUM_NAME_ARRAY:
            # calc_base_attrs_value()增长了growth_s的比率
            growth_value = card_config['growth_' + s]
            sbase = (lv - 1) * growth_value + self.get_base_attr(card_id, 'base_' + s) + self.get_base_attr(card_id, s + '_afterlife')

            sbase -= assistant_info.get(s, 0)

            r[s] = (
                (
                    sbase + self.crystal_effect(s, card_dict[s + '_crystal'])
                    # + gem_addition
                ) * (1000 + chain_add.get(s, 0)) * 0.001
            )
            if for_battle:
                # 加上统帅效果
                r[s] += self.commander_effect(s, self.weak_user.commander.attrs[s]['lv'])

        # 转生
        if 'bre' not in r:
            r['bre'] = 0

        r['hr'] = 100
        r['dr'] = 0
        r['crit'] = 10
        r['subhurt'] = 0

        # break4, break5属性更新
        for i in xrange(4, r['bre'] + 1):
            break_config = card_config.get('break%s' % i, None)
            if break_config:
                k, v = break_config
                r[self.GEM_CHAIN_EFFECT_NUM_NAME_ARRAY[k]] += v

        if for_battle and not god_formation:
            # 星魂百分比的效果
            soul_effect = self.weak_user.soul.calc_soul_attrs(r)
            if soul_effect:
                for attr, count in soul_effect.iteritems():
                    r[attr] += count

        if for_battle:
            # 额外的 统帅能力
            for tp in ['hp2', 'hp3']:
                r['hp'] += self.commander_effect(tp, self.weak_user.commander.attrs[tp]['lv'])

        if 'level_max' not in r:
            r['level_max'] = card_config['level_max']
        # 进阶
        if 'evo' not in r:
            r['evo'] = 0

        r['quality'] = card_config['quality']
        r['star'] = card_config['star']
        r['race'] = card_config['race']         # 职业
        r['is_boss'] = 0
        r['career'] = card_config['career']
        r['exp'] = self._cards[card_id]['exp']
        r['animation'] = card_config['animation']
        r['rgb_sort'] = card_config['rgb_sort']

        add_attrs = self.get_cards_evolution_attr(card_id, card_dict, card_config)

        for attr, count in add_attrs.iteritems():
            r[attr] += count

        super_attr_plus = self.super_attr_plus(card_dict, card_config)
        for attr, count in super_attr_plus.iteritems():
            if attr not in r:
                r[attr] = count
            else:
                r[attr] += count

        add_break_attrs = self.get_cards_break_attr(card_dict)

        for attr, count in add_break_attrs.iteritems():
            r[attr] += count

        rate = game_config.character_base_rate[card_config['type']]['exp_rate']
        next_level_exp_need = int(game_config.character_base[lv]['exp'] * rate)
        r['exp_max'] = next_level_exp_need

        for attr in self.CHAIN_EFFECT_NUM_NAME_DICT.itervalues():
            r[attr] = int(r[attr])

        return r

    def back_card_pos(self, card_id, god_formation):
        """
        返回神域卡牌的索引
        :param card_id:
        :param god_formation:
        :return:
        """
        if card_id in ['-1', '0']:
            return -1
        god_formation_list = self.weak_user.god_field.god_field_ids.get(god_formation, [])
        if card_id in god_formation_list:
            pos_for_card = god_formation_list.index(card_id)
        else:
            pos_for_card = -1
        return pos_for_card

    def super_attr_plus(self, card_dict, card_config=None):
        """
        增加超进阶的 6 暴击 7 命中 8 减伤 9 闪避 和属性加成(201 火攻 202 水攻 203 风攻 204 地攻 301 火防 302 水防 303 风防 304 地防)
        (501: 改变外框，后面填1和1..1   502: 品质增加 # 超进阶 同一品质的变化 橙-->橙1-->橙2-->橙3  不同品质的变化 橙-->红-->金)
        :param card_dict: 卡牌信息
        :param card_config: 卡牌配置
        :return:
        """
        super_effect = {
            6: 'crit',
            7: 'hr',
            8: 'subhurt',
            9: 'dr',
            201: 'fire',
            202: 'water',
            203: 'wind',
            204: 'earth',
            301: 'fire_dfs',
            302: 'water_dfs',
            303: 'wind_dfs',
            304: 'earth_dfs',
            501: 'super_quality_1',  # super_step [501, 1] [501, 1] 品质也是累加的所以都配置成1就ok了  501从1到9  502没用
            502: 'super_quality_2',
        }
        card_config = card_config or game_config.character_detail[card_dict['c_id']]

        add_attrs = self.calc_super_attrs(super_effect, card_dict, card_config)

        return add_attrs

    def get_cards_evolution_attr(self, card_id, card_dict, card_config=None):
        """ 获取卡牌进化的属性加成

        :param card_dict:
        :return:
        """
        attrs = ('fire', 'water', 'wind', 'earth', 'fire_dfs', 'water_dfs', 'wind_dfs', 'earth_dfs')
        card_config = card_config or game_config.character_detail[card_dict['c_id']]

        evo_config = self.get_evolution_config(card_id, card_dict, card_config)
        cur_evo = card_dict['evo']
        _config = evo_config.get(cur_evo)
        if not _config:
            return {}

        race = card_config['race']
        attr_config = _config.get('attr%s' % race)
        if not attr_config:
            return {}

        add_attrs = {}

        for attr, value in itertools.izip(attrs, attr_config):
            if value:
                add_attrs[attr] = value

        return add_attrs

    def get_cards_break_attr(self, card_dict):
        """ 获取卡牌转生的属性加成

        :param card_id: 卡牌id
        :param card_dict: 卡牌信息
        :param card_config: 配置信息
        :return:
        """
        attrs = ('fire', 'water', 'wind', 'earth')
        attr_defs = ('fire_dfs', 'water_dfs', 'wind_dfs', 'earth_dfs')
        bre = card_dict.get('bre', 0)
        bre_config = game_config.break_control.get(bre, 0)
        if not bre_config:
            return {}

        add_attrs = {}

        if bre_config.get('ability_sort', 0) == 1:
            need_attrs = attrs
        elif bre_config.get('ability_sort', 0) == 2:
            need_attrs = attr_defs
        else:
            return {}

        ability_add = bre_config.get('ability_add', 0)

        if not ability_add:
            return {}

        for attr in need_attrs:
            add_attrs[attr] = ability_add

        return add_attrs

    def calc_assistant_effect(self, card_id):
        """ 计算助威效果

        :param card_id: 卡牌id
        :return:
        """
        effect = {}

        if not game_config.assistant:
            return effect

        for index, ass in enumerate(self.assistant_effect):
            if ass != '-1' and ass.get('active_status', '-1') != '-1' and \
                self.assistant[index] not in {'-1', '0', card_id}:
                pos = index + 1
                config = game_config.assistant[pos]
                att_type_config = config.get('att_type')

                add_atts = []

                # 基础
                att_type = self.CHAIN_EFFECT_NUM_NAME_DICT.get(att_type_config)
                if ass['ass_random_id'] > 0:
                    assistant_random_config = game_config.assistant_random[ass['ass_random_id']]
                    att_value = assistant_random_config['ability']
                else:
                    att_value = config.get('att_value', 0)

                add_atts.append((att_type, att_value))

                # 卡牌
                if ass['limit_character_id'] > 0:
                    card_id = self.assistant[index]
                    c_id = self._cards[card_id]['c_id']
                    assistant_random_config = game_config.assistant_random[ass['limit_character_id']]
                    config_c_id = int(assistant_random_config['ability'])
                    character_ID = game_config.character_detail[config_c_id]['character_ID']
                    card_character_ID = game_config.character_detail[c_id]['character_ID']
                    if character_ID == card_character_ID:
                        att_type = config['card_ability']
                        att_value = config['card_value']
                        att_type = self.CHAIN_EFFECT_NUM_NAME_DICT.get(att_type)
                        if att_type:
                            add_atts.append((att_type, att_value))

        return effect

    def extend_bag(self, amount):
        """# extend_bag: 扩大包裹
        args:
            amount:    ---    arg
        returns:
            0    ---
        """
        self.bag_extend += amount

    def remove(self, card_id):
        """# del: 删除一张卡牌
        args:
            card_dict:    ---    arg
        returns:
            0    ---
        """
        # 删除神域上的卡牌
        self.remove_god_card(card_id)
        if self.is_remove_able(card_id):
            self.update_remove_card_rank(card_id)
            del self._cards[card_id]
        else:
            raise CardRemoveError('the card is in stove')

    def remove_god_card(self, card_id):
        """
        删除神域上的卡牌
        :param card_id:
        :return:
        """
        is_save = False
        if card_id not in self.alignment[0] or card_id not in self.alignment[1]:
            for god_formation, val in self.weak_user.god_field.god_field_ids.iteritems():
                if card_id in val:
                    for idx, card_id_new in enumerate(val):
                        if card_id_new in ['-1', '0']:
                            continue
                        if card_id_new != card_id:
                            continue
                        self.weak_user.god_field.god_field_ids[god_formation][idx] = '-1'
                    is_save = True
                # 检查主战卡牌是否都删除了
                if list(set(val[:6])) in [['-1', '0'], ['0', '-1']]:
                    self.weak_user.god_field.is_formation = False
                    is_save = True
                if list(set(val[:6])) in ['-1']:
                    self.weak_user.god_field.god_field_ids[god_formation][1] = '0'
                    self.weak_user.god_field.is_formation = False
                    is_save = True
        # 是否保存神域阵型
        if is_save:
            self.weak_user.god_field.save()

    LOCK_TYPE = ['sys', 'user', 'train']

    def lock_card(self, card_id, lock_type):
        """# lock_card: 由程序主动锁定一张卡，此卡不能删除
        lock_type in
        args:
            card_id:    ---    arg
        returns:
            0    ---
        """
        if lock_type not in self.LOCK_TYPE:
            raise
        if lock_type not in self._cards[card_id]['remove_avail']:
            self._cards[card_id]['remove_avail'].append(lock_type)
        else:
            return 1

    def release_card(self, card_id, lock_type):
        """# release_card: docstring
        args:
            card_id, lock_type:    ---    arg
        returns:
            0    ---
        """
        if lock_type not in self.LOCK_TYPE:
            raise
        if lock_type in self._cards[card_id]['remove_avail']:
            self._cards[card_id]['remove_avail'].remove(lock_type)
        else:
            return 1

    def get_lock_status(self, card_id):
        '''
        获取卡牌的锁状态
        :param card_id: 卡牌id
        :return:
        '''
        st = self._cards[card_id]['remove_avail']
        if 'user' in st:
            return 10002
        elif 'train' in st:
            return 10003
        elif 'sys' in st:
            return 10001

    def is_remove_able(self, card_id):
        """# is_remove_able: docstring
        args:
            card_id:    ---    arg
            如果没有锁, 就能删除
            有锁, 不能删除
        returns:
            0    ---
        """
        return not self._cards[card_id]['remove_avail']

    def new(self, config_id, s_1=(), s_2=(), s_3=(), s_4=(), s_5=(), lv=1, evo=0, **kwargs):
        """# new: 新建一张卡牌，外部使用
        args:
            config_id:    ---    卡牌的配置id
            s_1, s_2, s_3: (1, 2), (技能key，技能等级)
            lv: 卡牌等级
        returns:
            0    ---
        """
        card_id = self._make_id(config_id)
        config_id = int(config_id)
        card_config = game_config.character_detail[config_id]

        # 橙卡 放入gacha伪随机池
        if card_config['quality'] == 4:
            if self.weak_user:
                if config_id in self.weak_user.gacha.loot_log:
                    self.weak_user.gacha.loot_log[config_id] += 1
                else:
                    self.weak_user.gacha.loot_log[config_id] = 1
                if kwargs.get('gacha_save', True):
                    self.weak_user.gacha.save()

        pre_exp = 0
        card_type = card_config['type']
        rate = game_config.character_base_rate[card_type]['exp_rate']

        card_dict = {
            'id': card_id,
            'c_id': config_id,
            'lv': lv,
            'level_max': card_config['level_max'],
            'exp': 0,
            'pre_exp': pre_exp,
            'pos': 0,             # 出战位置[1,2,3,4,5] 替补的位置位[11,12,13], 这两个省略[14, 15] 助威assistant位置为0
                                  # 命运user.cards.destiny激活为0 有card_id表示放上了卡牌
            'evo': 0,
            'step': 0,
            'super_step': 0,      # 超进阶的等级
            'super_soul': [],     # 超进阶铸魂的卡牌
            # 'super_quality_1': 0, # 同一品质的变化 橙-->橙1-->橙2-->橙3
            # 'super_quality_2': 0, # 不同品质的变化 橙-->红-->金
            'bre': 0,

            'base_patk'     : card_config['base_patk'],
            'base_matk'     : card_config['base_matk'],
            'base_def'      : card_config['base_def'],
            'base_speed'    : card_config['base_speed'],
            'base_hp'       : card_config['base_hp'],

            'patk_history'  : 0,    # 无用
            'matk_history'  : 0,    # 无用
            'def_history'   : 0,    # 无用
            'speed_history' : 0,    # 无用
            'hp_history'    : 0,    # 无用

            'patk_crystal'  : 0,
            'matk_crystal'  : 0,
            'def_crystal'   : 0,
            'speed_crystal' : 0,
            'hp_crystal'    : 0,

            'patk_afterlife'  : 0,
            'matk_afterlife'  : 0,
            'def_afterlife'   : 0,
            'speed_afterlife' : 0,
            'hp_afterlife'    : 0,

            's_1': {
                'lv': 1,
                'exp': 0,
                'avail': 2,    # 0 - 不可用，1 - 可以激活，2 - 已经激活
                's': 0,        # 技能的id  根据技能的id可以在skill_detail中可以取到最大等级max_lv
            },
            's_2': {'lv': 1, 'exp': 0, 'avail': 0, 's': 0},
            's_3': {'lv': 1, 'exp': 0, 'avail': 0, 's': 0},
            's_4': {'lv': 1, 'exp': 0, 'avail': 0, 's': 0},
            's_5': {'lv': 1, 'exp': 0, 'avail': 0, 's': 0},

            'remove_avail': [],         # 是否可以被删除, []表示可以删除
            'evo_metals': {},           # 所有进阶消耗的卡牌
            'is_world': False,          # 卡牌是否转世过了
            'card_world_task': 0,       # 卡牌转世的任务
            'card_world_step': 0,       # 卡牌转世的阶段

            'after_world_point': 0,     # 转世能量点槽
        }

        for i in '12345':
            if locals()['s_' + i] != ():
                s, s_lv = locals()['s_' + i]
                avail = 2
            else:
                skill_source = card_config.get('skill_%s_source' % i)
                if skill_source:
                    s = utils.weight_choice(skill_source, 1)[0]
                else:
                    s = 0
                s_lv = 1
                avail = 0 if i != '1' else 2
            card_dict['s_' + i]['s'] = int(s)
            card_dict['s_' + i]['lv'] = int(s_lv)
            card_dict['s_' + i]['avail'] = avail

        self._cards[card_id] = card_dict    # 卡牌背包
        if getattr(self, '_cards_temp', ''):
            self._cards_temp[card_id] = self.single_card_info(card_dict)

        for i in range(evo):        # 卡牌进阶
            self.evolution(card_id, card_dict, card_config)

        lv = min(lv, card_dict['level_max'])
        for level in range(1, lv):
            pre_exp += int(game_config.character_base[level]['exp'] * rate)
        card_dict['pre_exp'] = pre_exp
        card_dict['lv'] = lv
        self.add_card_book(config_id)
        # 获得卡牌广播
        notice.notice_4_get_card(self.weak_user, config_id=config_id, card_config=card_config)
        # 更新最强卡牌排行
        self.update_card_rank(card_id)
        return card_id

    def replace_card(self, card_id, config_id, save=True):
        """ 替换卡牌

        :param card_id:
        :param config_id:
        :return:
        """
        if not self.has_card(card_id):
            return False

        evo_config = self.get_evolution_config(card_id)

        new_card_id = self.new(config_id)
        value = self._cards.pop(card_id)
        new_value = self._cards[new_card_id]
        for attr in self.REPLACE_ATTR:          # 卡牌属性
            v = value.get(attr)
            if v:
                new_value[attr] = v
        # 更新技能
        for i in '12345':
            skill = 's_%s' % i
            if skill not in value:
                continue
            for sattr in ['avail', 'exp', 'lv']:
                new_value[skill][sattr] = value[skill][sattr]
        # 在加速中
        if 'train' in value['remove_avail']:
            school = self.weak_user.school
            for stove_key in school._attrs:
                stove = getattr(school, stove_key)
                if stove['card_id'] == card_id:
                    stove['card_id'] = new_card_id
                    school.save()
                    break
        # 进阶提升最大等级
        max_lv = evo_config.get(value['evo'], {}).get('maxlv', 0)
        if max_lv:
            new_value['level_max'] = max_lv
        self.calc_base_attrs_value(new_card_id)
        if save:
            self.save()

        return new_card_id

    def add_card_book(self, config_id):
        '''
        增加卡牌图鉴
        :param config_id:
        :return:
        '''
        if self.weak_user and config_id in game_config.character_book_sort \
                and config_id not in self.weak_user.handbook.books:
            self.weak_user.handbook.books[config_id] = int(time.time())
            self.weak_user.handbook.save()

    def get_evolution_config(self, card_id, raw_card_info=None, card_config=None):
        '''
        获取进阶的配置
        :param card_id:
        :param raw_card_info:
        :param card_config:
        :return:
        '''
        if card_config is None:
            raw_card_info = raw_card_info or self._cards[card_id]
            card_config = card_config or game_config.character_detail[raw_card_info['c_id']]

        if 'evo_kind' in card_config:
            quality = card_config['evo_kind']
        else:
            quality = card_config['quality']

        if quality < 3:
            evo_config = game_config.evolution
        elif quality == 3:
            evo_config = game_config.evolution_3
        elif quality == 4:
            evo_config = game_config.evolution_4
        else:
            evo_config = game_config.evolution_5

        return evo_config

    def evolution(self, card_id, raw_card_info=None, card_config=None):
        attrs = ['base_patk', 'base_matk', 'base_def', 'base_speed', 'base_hp']
        raw_card_info = raw_card_info or self._cards[card_id]
        card_config = card_config or game_config.character_detail[raw_card_info['c_id']]
        evo_config = self.get_evolution_config(card_id, raw_card_info, card_config)

        cur_evo = raw_card_info['evo']
        next_evo = cur_evo + 1
        _config = evo_config.get(next_evo)
        if not _config:
            return False

        pre_config = evo_config.get(cur_evo)
        raw_card_info['lv'] = max(1, raw_card_info['lv'] - _config['level_off'])
        # 降等级 重新计算pre_exp
        if _config['level_off']:
            rate = game_config.character_base_rate[card_config['type']]['exp_rate']
            pre_exp = 0
            for level in range(1, raw_card_info['lv']):
                pre_exp += int(game_config.character_base[level]['exp'] * rate)
            raw_card_info['pre_exp'] = pre_exp

        raw_card_info['level_max'] = _config['maxlv']
        raw_card_info['step'] = _config['step']

        for idx, v in enumerate(_config['skill']):
            skill = raw_card_info['s_%s' % (idx + 1)]
            pre_v = pre_config['skill'][idx] if pre_config else 0
            if pre_v != v and skill['s'] > 0:
                if v == 1:
                    skill['avail'] = 2
                elif v > 1:
                    skill_config = game_config.skill_detail[skill['s']]
                    next_skill_key = skill_config['is_evolution']
                    if next_skill_key:
                        raw_card_info['s_%s' % (idx + 1)] = {'lv': skill['lv'], 'avail': 2, 'exp': skill['exp'], 's': next_skill_key}

        raw_card_info['evo'] = next_evo
        self.calc_base_attrs_value(card_id, raw_card_info, card_config)
        # for attr, value in itertools.izip(attrs, _config['type%s' % card_config['race']]):
        #     raw_card_info[attr] = int((value + card_config[attr]) * (1 + _config['all']))
        return raw_card_info

    def calc_base_attrs_value(self, card_id, card_info=None, card_config=None):
        """重新计算卡牌五项属性的值,加上evo、break的效果
        """

        attrs = ['base_patk', 'base_matk', 'base_def', 'base_speed', 'base_hp']
        raw_card_info = card_info or self._cards[card_id]
        card_config = card_config or game_config.character_detail[raw_card_info['c_id']]

        evo_config = self.get_evolution_config(card_id, raw_card_info, card_config)
        cur_evo = raw_card_info['evo']
        _config = evo_config.get(cur_evo)
        if not _config:
            return

        super_base_attr = {
            1: 'base_patk',
            2: 'base_matk',
            3: 'base_def',
            4: 'base_speed',
            5: 'base_hp',
        }

        add_attrs = self.calc_super_attrs(super_base_attr, raw_card_info, card_config)

        cur_bre = raw_card_info.get('bre', 0)
        break_hp_add_rate = game_config.break_control.get(cur_bre, {}).get('hp_add', 0)
        for attr, value in itertools.izip(attrs, _config['type%s' % card_config['race']]):
            all_rate = _config['all']
            if attr == 'base_hp':
                all_rate += break_hp_add_rate
            raw_card_info[attr] = (value + card_config[attr] + add_attrs.get(attr, 0)) * (1 + all_rate)

    def calc_base_attrs_diff_value(self, card_id, start_evo=0, end_evo=1, card_info=None, card_config=None):
        """ 计算卡牌五项属性的差值, 加上evo、break的效果
        """
        attrs = ('patk', 'matk', 'def', 'speed', 'hp')
        raw_card_info = card_info or self._cards[card_id]
        card_config = card_config or game_config.character_detail[raw_card_info['c_id']]

        evo_config = self.get_evolution_config(card_id, raw_card_info, card_config)
        start_evo_config = evo_config.get(start_evo)
        end_evo_config = evo_config.get(end_evo)
        if not start_evo_config or not end_evo_config or start_evo >= end_evo:
            return {}

        cur_bre = raw_card_info.get('bre', 0)
        break_hp_add_rate = game_config.break_control.get(cur_bre, {}).get('hp_add', 0)

        diff_data = {}
        # listone = ['a','b','c']  listtwo = ['11','22','abc']   ('a', '11') ('b', '22') ('c', 'abc')
        for attr, s_value, e_value in itertools.izip(attrs,
                                                     start_evo_config['type%s' % card_config['race']],
                                                     end_evo_config['type%s' % card_config['race']]):
            if attr == 'hp':
                break_rate = break_hp_add_rate
            else:
                break_rate = 0

            end_all_rate = end_evo_config['all']
            start_all_rate = start_evo_config['all']
            end = e_value * (1 + end_all_rate + break_rate)
            start = s_value * (1 + start_all_rate + break_rate)
            diff_data[attr] = end - start

        return diff_data

    def calc_super_attrs(self, super_base_attr, card_info, card_config):
        """ 计算超进阶

        :param super_base_attr:
        :return:
        """
        add_attrs = {}
        super_id = card_config.get('super_evo', 0)
        if super_id:
            # 超进阶的等级
            super_step = card_info.get('super_step', 0)
            # 铸魂的材料
            super_soul = card_info.get('super_soul', [])
            super_config = game_config.super_evolution.get(super_id)

            if super_step:
                for super_level in xrange(1, super_step + 1):
                    level_add = super_config.get('level_%s_add' % super_level)
                    # 增加超进阶的属性
                    for add in level_add:
                        attr_name = super_base_attr.get(add[0])
                        if attr_name:
                            if attr_name not in add_attrs:
                                add_attrs[attr_name] = add[1]
                            else:
                                add_attrs[attr_name] += add[1]

                for super_level in xrange(1, super_step + 1):
                    level_need = super_config.get('level_%s_need' % super_level)
                    for team_id in level_need:
                        super_evo_team_config = game_config.super_evo_team.get(team_id)
                        if super_evo_team_config:
                            ability_add = super_evo_team_config.get('ability_add')
                            # 增加铸魂的属性
                            for add in ability_add:
                                attr_name = super_base_attr.get(add[0])
                                if attr_name:
                                    if attr_name not in add_attrs:
                                        add_attrs[attr_name] = add[1]
                                    else:
                                        add_attrs[attr_name] += add[1]

            if super_soul:
                level_need = super_config.get('level_%s_need' % (super_step + 1))
                for index, team_id in enumerate(level_need):
                    if super_soul[index]:
                        super_evo_team_config = game_config.super_evo_team.get(team_id)
                        if super_evo_team_config:
                            ability_add = super_evo_team_config.get('ability_add')
                            # 增加铸魂的属性
                            for add in ability_add:
                                attr_name = super_base_attr.get(add[0])
                                if attr_name:
                                    if attr_name not in add_attrs:
                                        add_attrs[attr_name] = add[1]
                                    else:
                                        add_attrs[attr_name] += add[1]

        return add_attrs

    def get_all_cards(self):
        """# get_all_cards: 获得所有卡牌所有信息
        args:
            :    ---    arg
        returns:
            0    ---
        """
        _cards_temp = {}
        for k, v in self._cards.iteritems():
            info = self.single_card_info(v)
            info['id'] = k
            _cards_temp[k] = info
        return _cards_temp

    def alignment():
        '''
        阵型
        :return:
        '''
        doc = "The alignment property."
        def fget(self):
            if getattr(self, '_card_config_id_on_alignment', None):
                del self._card_config_id_on_alignment
            alignment_1 = ['-1'] * 5
            alignment_2 = ['-1'] * 5
            for v in self._cards.itervalues():
                if not v['pos']:
                    continue
                elif v['pos'] < 10:
                    pos = v['pos'] - 1
                    alignment_1[pos] = v['id']
                elif v['pos'] > 10:
                    pos = v['pos'] % 10 - 1
                    alignment_2[pos] = v['id']
            self._alignment = [alignment_1, alignment_2]
            return self._alignment

        def fset(self, value):
            raise ValueError, 'readonly, use set_alignment to change value'

        def fdel(self):
            del self._alignment

        return locals()

    alignment = property(**alignment())

    def card_num_in_alignment(self):
        '''
        阵型上的卡牌数量
        :return:
        '''
        num = 0
        for v in self.alignment:
            for vv in v:
                if vv != self.NONE_CARD_ID_FLAG:
                    num += 1
        return num

    def card_config_id_on_alignment():
        '''
        在阵型上的config_id cid 出战、替补、助威、命运
        :return:
        '''
        doc = "阵型上的configid"
        def fget(self):
            if not getattr(self, "_card_config_id_on_alignment", None):
                _card_config_id_on_alignment = set()
                for o in [self.alignment[0], self.alignment[1], self.assistant, self.destiny]:
                    for v in o:                 # 卡牌id
                        if v not in (self.NONE_CARD_ID_FLAG, '0'):  # 没有卡牌、没激活
                            if v not in self._cards:
                                if v in self.assistant:
                                    self.assistant[self.assistant.index(v)] = '0'
                                    if v not in self.destiny:
                                        continue
                                if v in self.destiny:
                                    self.destiny[self.destiny.index(v)] = '0'
                                    continue

                            _card_config_id_on_alignment.add(game_config.character_detail[self._cards[v]['c_id']]['character_ID'])
                            # _card_config_id_on_alignment.add(self._cards[vv]['c_id'])

                setattr(self, "_card_config_id_on_alignment", _card_config_id_on_alignment)
            return self._card_config_id_on_alignment

        def fdel(self):
            del self._card_config_id_on_alignment

        return locals()

    card_config_id_on_alignment = property(**card_config_id_on_alignment())

    def card_id_on_alignment(self, god_formation=None):
        '''
        神域阵型的卡牌联携
        :param god_formation:
        :return:
        '''
        card_alignment = set()
        if not god_formation:
            return card_alignment
        # 神域阵型上卡牌的联携
        cards_list = self.weak_user.god_field.god_field_ids.get(god_formation)
        for card_id in cards_list:
            if card_id in ['-1', '0']: continue
            card_alignment.add(game_config.character_detail[self._cards[card_id]['c_id']]['character_ID'])
        return card_alignment

    def add_exp(self, card_id, exp_add):
        """# add_exp: 给某一张卡牌加经验
        args:
            card_id ---   卡牌数据库id
        returns:
            0    ---
        """
        raw_card_info = self._cards[card_id]
        card_config = game_config.character_detail[raw_card_info['c_id']]
        evo_config = self.get_evolution_config(card_id, raw_card_info, card_config)
        _evo_config = evo_config.get(raw_card_info['evo'])

        # 策划又新开放了等级上限，还是在这里每次都判断上限更新吧
        if card_config['is_evo'] and _evo_config:
            level_max = _evo_config['maxlv']
        else:
            level_max = card_config['level_max']

        raw_card_info['level_max'] = level_max
        level = raw_card_info['lv']
        if level_max <= level:
            return [(level, 0)]

        level_config = game_config.character_base

        card_type = card_config['type']
        rate = game_config.character_base_rate[card_type]['exp_rate']
        exp = self._cards[card_id]['exp'] + int(exp_add)

        next_level_exp_need = int(level_config[level]['exp'] * rate)
        # if level_max == level and next_level_exp_need == exp:
        #     return [(0, 0)]

        update_rank = False

        level_change = [(level, next_level_exp_need)]
        while next_level_exp_need <= exp:
            update_rank = True
            exp -= next_level_exp_need
            level += 1
            if level_max < level:
                level = level_max
                exp = 0     # next_level_exp_need
                level_change.append((level, next_level_exp_need))
                break
            self._cards[card_id]['pre_exp'] += next_level_exp_need
            next_level_exp_need = int(level_config[level]['exp'] * rate)
            level_change.append((level, next_level_exp_need))
        self._cards[card_id]['exp'] = exp
        self._cards[card_id]['lv'] = level

        if update_rank:
            # 更新最强卡牌排行
            self.update_card_rank(card_id)

        return level_change

    def get_max_level_need_exp(self, card_id):
        """ 获取满级需要的经验

        :param card_id:
        :return:
        """
        c_id = self._cards[card_id]['c_id']
        level = self._cards[card_id]['lv']
        level_max = self._cards[card_id].get('level_max') or game_config.character_detail[c_id]['level_max']

        if level_max <= level:
            return 0

        level_config = game_config.character_base

        card_type = game_config.character_detail[c_id]['type']
        rate = game_config.character_base_rate[card_type]['exp_rate']

        # 需要到达满级的总经验
        total_exp = 0

        # 从当前等级循环, 上限为最大等级
        for i in xrange(level, level_max):
            # 需要到达每级需要的经验
            total_exp += int(level_config[i]['exp'] * rate)

        # 需要减去当前经验
        diff_exp = total_exp - self._cards[card_id]['exp']

        return diff_exp

    def get_need_exp_for_level(self, c_id, start_level, end_level):
        """ 通过等级获取经验

        :return:
        """
        level_config = game_config.character_base

        card_type = game_config.character_detail[c_id]['type']
        rate = game_config.character_base_rate[card_type]['exp_rate']
        # 需要到达满级的总经验
        total_exp = 0

        # 从当前等级循环, 上限为最大等级
        for i in xrange(start_level, end_level):
            # 需要到达每级需要的经验
            total_exp += int(level_config[i]['exp'] * rate)

        return total_exp

    def set_alignment(self, card_id, pos):
        """# set_alignment: 将一个卡牌放到阵型中
        args:
            card_id ---   卡牌数据库id
            pos:    ---   卡牌的位置
                    alignment_1: 1,2,3,4,5
                    alignment_2: 11,12,13,14,15
        returns:
            0    ---
        """
        if pos < 10:
            _pos = pos - 1
            card_id_pos = self.alignment[0][_pos]
            if str(card_id_pos) != self.NONE_CARD_ID_FLAG:
                self._cards[card_id_pos]['pos'] = 0
                self.release_card(card_id_pos, 'sys')
        elif pos < 20:
            _pos = pos % 10 - 1
            card_id_pos = self.alignment[1][_pos]
            if str(card_id_pos) != self.NONE_CARD_ID_FLAG:
                self._cards[card_id_pos]['pos'] = 0
                self.release_card(card_id_pos, 'sys')
        if card_id != self.NONE_CARD_ID_FLAG:
            self._cards[card_id]['pos'] = pos
            self.lock_card(card_id, 'sys')

    def add_skill_exp(self, card_id, skill_id, exp_add):
        """
        升级卡牌中对应技能经验
        card_id:    user表卡牌id
        skill_id:   技能keyid
        exp_add:    要增加的经验
        """
        tempCard = self._cards[card_id]
        for i in range(1, 6):
            tempSkill = tempCard.get('s_' + str(i))
            if tempSkill and tempSkill['s'] == skill_id:
                break
        tempExp = tempSkill['exp'] + int(exp_add)       # get skill exp
        tempLv = tempSkill['lv']        # skill current level
        tempMaxLv = game_config.skill_detail[tempSkill['s']]['max_lv']
        if tempLv >= tempMaxLv:
            return 'error_11'
        tempQlt = game_config.skill_detail[tempSkill['s']]['skill_quality']     # get skill quality
        tempNextLvNeed = game_config.skill_levelup[tempLv][tempQlt]

        while tempExp >= tempNextLvNeed:
            tempLv += 1
            tempExp -= tempNextLvNeed
            if tempLv >= tempMaxLv:
                tempLv = tempMaxLv
                tempExp = 0
                break
            tempNextLvNeed = game_config.skill_levelup[tempLv][tempQlt]
        tempSkill['lv'] = tempLv
        tempSkill['exp'] = tempExp

    def check_skill_used_exp(self, card_id, skill_pos):
        """
        args:
            card_id: 卡牌id
            skill_pos： 技能 s_1, s_2, s_3
        """
        need_exp = 0
        card_info = self._cards[card_id]
        skill_info = card_info[skill_pos]
        if skill_info['avail'] == 2:
            quality = game_config.skill_detail[skill_info['s']]['skill_quality']
            for lv in range(1, skill_info['lv']):
                need_exp += game_config.skill_levelup[lv][quality]
        return need_exp + skill_info['exp']

    def has_card(self, card_id):
        """
        检查是否有卡牌
        """
        return card_id in self._cards

    def get_card_data(self, card_id):
        """
        得到卡牌当前的user数据的拷贝
        """
        if self.has_card(card_id):
            return copy.deepcopy(self._cards[card_id])
        return None

    def has_card_by_c_id(self, c_id):
        """ 根据c_id是否有卡牌

        :param c_id:
        :return:
        """
        for key, value in self._cards.iteritems():
            card_config = game_config.character_detail[value['c_id']]
            if card_config['character_ID'] == c_id:
                return True
        return False

    def eaten_card(self, major, metal, pos=1):
        """
        主卡(major)吃材料卡(metal)，获得技能经验，(pos)指定id技能

            -1  # 卡包里没有主卡
            -2  # 主卡没有技能
            -3   # 材料卡不能被吃
            -4  # 材料卡片不存在
        """
        tempMajorId = major
        if not self.has_card(tempMajorId):
            return 'error_21'    # 卡包里没有主卡
        tempMajor = self._cards[tempMajorId]
        skillCount = 0
        max_lv_skills = 0
        tempSkill = tempMajor.get('s_%s' % pos)
        if tempSkill and tempSkill['s'] > 0 and tempSkill['avail'] == 2:
            # 主卡技能激活的个数
            skillCount += 1
            tempLv = tempSkill['lv']    # skill current level
            tempMaxLv = game_config.skill_detail[tempSkill['s']]['max_lv']
            if tempLv >= tempMaxLv:
                max_lv_skills += 1
        else:
            return 2    # 技能未开放

        if skillCount <= 0:
            return -2    # 主卡没有技能

        # 卡牌当前技能等级超过30, 只能使用蓝色品质的卡牌增加经验
        if pos in (4, 5):
            if isinstance(metal, list):
                for card_id in metal:
                    if not self.has_card(card_id):
                        return 'error_21'
                    tempCard = self._cards[card_id]
                    if not self.is_remove_able(card_id):
                        return self.get_lock_status(card_id)
                    quality = game_config.character_detail[tempCard['c_id']].get('quality')
                    if quality <= 2:
                        return 3    # 你所选择的材料伙伴中，品质不符合要求

        if max_lv_skills == skillCount:
            return 'error_11'

        if isinstance(metal, list):
            for cardid in metal:
                tempCardId = cardid
                if not self.has_card(tempCardId):
                    return 'error_21'
                tempCard = self._cards[tempCardId]
                if not self.is_remove_able(tempCardId):
                    return self.get_lock_status(tempCardId)

                if tempCard['pos'] != 0:        # this card in the battle team
                    continue
                tempCardType = game_config.character_detail[tempCard['c_id']]['type']       # get character type
                tempLv = tempCard['lv']     # get card current lv
                tempEatBace = game_config.character_base[tempLv]['eaten_skill_exp']
                tempRate = game_config.character_base_rate[tempCardType]['eaten_skill_exp_rate']    # 0.5
                tempReal = int(tempEatBace * tempRate)  # 50 * 0.5
                tempSkillList = []
                for j in range(1, 4):
                    skill = tempCard.get('s_' + str(j), {}).get('s')
                    if skill:
                        tempSkillList.append(skill)

                if skillCount == 2:
                    tempReal = int(tempReal * 1.2)
                elif skillCount == 3:
                    tempReal = int(tempReal * 1.5)

                tempReal /= skillCount
                tempSkillId = tempMajor['s_%s' % pos]['s']
                tempAvailFlag = tempMajor['s_%s' % pos]['avail']
                if tempSkillId > 0 and tempAvailFlag == 2:
                    error = self.add_skill_exp(tempMajorId, tempSkillId, tempReal)
                    if error:
                        continue
                    if tempSkillId in tempSkillList:
                        self.add_skill_exp(tempMajorId, tempSkillId, int(tempEatBace * tempRate))
                if self.weak_user:
                    used_crystal, used_adv_crystal = self.check_card_used_crystal(tempCardId, tempCard)
                    self.weak_user.crystal += used_crystal
                    self.weak_user.adv_crystal += used_adv_crystal
                self.remove(tempCardId)
        return 0

    def get_base_attr(self, card_id, attribute):
        """
        根据key（attribute）得到指定值

        """
        return self._cards[card_id].get(str(attribute), 0)
        # 2014.03.31 卡牌进阶功能修改，卡牌属性成长曲线固定了，无需下面代码了
        attribute = str(attribute)
        tempAttrKey = ['base_patk', 'base_matk', 'base_def', 'base_speed', 'base_hp']
        tempCId = self._cards[card_id]['c_id']
        tempConfigCard = game_config.character_detail[tempCId]

        if attribute in tempAttrKey:
            return self._cards[card_id][attribute] + tempConfigCard[attribute]
        else:
            return tempConfigCard[attribute]

    def set_base_attr(self, card_id, attribute, value):
        """
        根据key（attribute）设置指定值
        """
        attribute = str(attribute)
        tempAttrKey = ['base_patk', 'base_matk', 'base_def', 'base_speed', 'base_hp']
        tempHisKey = ['patk_history', 'matk_history', 'def_history', 'speed_history', 'hp_history']
        if attribute in tempAttrKey:
            tempIndex = tempAttrKey.index(attribute)
            tempCard = self._cards[card_id]
            tempCard[tempHisKey[tempIndex]] = tempCard[attribute]
            tempCard_cid = tempCard['c_id']
            card_config = game_config.character_detail[tempCard_cid]
            tempCard[attribute] = value - card_config[attribute]
            return True
        return False

    def add_new_formation(self, level):
        """# add_new_fo: 添加一个新的阵型
        args:
            arg:    ---    arg
        returns:
            0    ---
        """
        # ps: 2014.02.25 默认全开启站位，所以删除这个 配置参数了
        return
        config_value = game_config.role[level]['open_formation']
        if config_value and config_value not in self.formation['own']:
            self.formation['own'].append(config_value)

    def add_new_open_position(self, level):
        """# 开启新的站位
        """
        # ps: 2014.02.25 默认全开启站位，所以删除这个 配置参数了
        return
        config_value = game_config.role[level]['open_position']
        for i in config_value:
            if i not in self.open_position:             # 当前已开启站位
                self.open_position.append(int(i))

    def add_position_num(self, level):
        '''
        增加开启占位数量
        :param level:
        :return:
        '''
        config = game_config.role[level]
        if config['position_num']:
            self.position_num = config['position_num']
        if config['alternate_num']:
            self.alternate_num = config['alternate_num']

    def check_card_used_crystal(self, card_id, card_info=None):
        ''' # 以元组形式返回需要的 能晶，高级能晶 '''
        card_info = card_info or self._cards[card_id]
        need_crystal = 0
        need_adv_crystal = 0
        tps = ['patk', 'matk', 'def', 'speed', 'hp']
        for lvs in [card_info[_tp] for _tp in ['%s_crystal' % tp for tp in tps]]:
            for lv in range(1, lvs + 1):
                lv_config = game_config.character_strengthen[lv]
                need_crystal_list = lv_config['need_crstal_' + tp]
                if need_crystal_list[0] == 1:
                    need_crystal += need_crystal_list[1]
                if need_crystal_list[0] == 2:
                    need_adv_crystal += need_crystal_list[1]
        return need_crystal, need_adv_crystal

    def generate_assistant_random(self, config_list):
        """ 生成assistant_random

        :param config_list:
        :return:
        """
        random_data = [(aid, game_config.assistant_random[aid]['weight'])
                       for aid in config_list if aid in game_config.assistant_random]
        if not random_data:
            return 0

        data = weight_choice(random_data)
        return data[0]

    #####################################排行榜#####################################
    def get_orange_card_rank_key(self):
        """ 最强橙卡排行key

        :return:
        """
        if self.orange_card_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.orange_card_rank_key = self.make_key_cls(self.ORANGE_CARD_RANK_KEY_PREFIX, server_name)
        return self.orange_card_rank_key

    def get_purple_card_rank_key(self):
        """ 最强紫卡排行key

        :return:
        """
        if self.purple_card_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.purple_card_rank_key = self.make_key_cls(self.PURPLE_CARD_RANK_KEY_PREFIX, server_name)
        return self.purple_card_rank_key

    def generate_card_key(self, card_id):
        """ 生成紫|橙卡卡牌key

        :return:
        """
        return '%s_%s' % (self.uid, card_id)

    def update_card_rank(self, card_id):
        """ 更新最强卡牌排行

        :return:
        """
        # 把robot_值copy过来, 这样不用区arena实例
        if 'robot_' in self.uid:
            return False

        if card_id not in self._cards:
            return False

        card_dict = self._cards[card_id]
        quality = game_config.character_detail[card_dict['c_id']]['quality']
        if quality not in {3, 4}:
            return False

        combat = self.cal_one_combat(card_id)
        card_rank = self.card_rank['card']
        card = card_rank.get(quality)
        if not card or card[1] < combat:
            if quality == 3:
                # 紫卡
                rank_key = self.get_purple_card_rank_key()
            else:
                # 橙卡
                rank_key = self.get_orange_card_rank_key()
            if card:
                old_card_id = card[0]
                old_key = self.generate_card_key(old_card_id)
                self.fredis.zrem(rank_key, old_key)
            key = self.generate_card_key(card_id)
            self.fredis.zadd(rank_key, key, generate_rank_score(combat))
            self.card_rank['card'][quality] = (card_id, combat)
            return True

        return False

    def update_remove_card_rank(self, card_id):
        """ 更新删除的卡牌

        :param card_id:
        """
        if card_id in [value[0] for value in self.card_rank['card'].itervalues() if value]:
            quality = game_config.character_detail[self._cards[card_id]['c_id']]['quality']
            if quality in {3, 4}:
                if quality == 3:
                    # 紫卡
                    rank_key = self.get_purple_card_rank_key()
                else:
                    # 橙卡
                    rank_key = self.get_orange_card_rank_key()
                old_key = self.generate_card_key(card_id)
                self.fredis.zrem(rank_key, old_key)                 # 删除数据库数据
                self.card_rank['card'][quality] = ()                # 删除卡牌排行缓存

    def check_card_rank(self):
        """ 检查卡牌排行, 用于第一次玩家录入排行数据

        :return:
        """
        if self.card_rank.get('flag', 0) != 1:
            self.card_rank['flag'] = 1
            card_3 = ''
            card_3_combat = 0
            card_4 = ''
            card_4_combat = 0
            for card_id, value in self._cards.iteritems():
                config = game_config.character_detail.get(value['c_id'])
                if config:
                    if config['quality'] == 3:
                        # 紫色卡
                        combat = self.cal_one_combat(card_id)
                        if combat > card_3_combat:
                            card_3 = card_id
                            card_3_combat = combat
                    elif config['quality'] == 4:
                        # 橙色卡
                        combat = self.cal_one_combat(card_id)
                        if combat > card_4_combat:
                            card_4 = card_id
                            card_4_combat = combat

            if 'card' not in self.card_rank:
                self.card_rank['card'] = {}

            save = False

            if card_3:
                rank_key = self.get_purple_card_rank_key()
                key = self.generate_card_key(card_3)
                self.fredis.zadd(rank_key, key, generate_rank_score(card_3_combat))
                self.card_rank['card'][3] = (card_3, card_3_combat)
                save = True

            if card_4:
                rank_key = self.get_orange_card_rank_key()
                key = self.generate_card_key(card_4)
                self.fredis.zadd(rank_key, key, generate_rank_score(card_4_combat))
                self.card_rank['card'][4] = (card_4, card_4_combat)
                save = True

            if save:
                self.save()

            return True
        else:
            return False

    def cal_one_combat(self, card_id):
        """ 计算一个卡牌的战斗力

        :param card_id:
        :return:
        """
        card_dict = self._cards[card_id]
        info = self.single_card_info(card_dict)
        combat = self.weak_user.calc_combat(info, is_user=False)
        evo_num = 100000 + card_dict['evo'] * 1000
        skill_num = sum([card_dict['s_%s' % i]['lv'] for i in xrange(1, 4)])
        num = evo_num + skill_num
        return int(combat) + num / 1000000.0

    #####################################排行榜#####################################


class Handbook(ModelBase):

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'books': {},
            'equip_books': {}
        }
        super(Handbook, self).__init__(self.uid)

    def has_card_by_c_id(self, c_id):
        """ 根据c_id是否有卡牌

        :param c_id:
        :return:
        """
        for key, value in self.books.iteritems():
            card_config = game_config.character_detail[key]
            if card_config['character_ID'] == c_id:
                return True
        return False