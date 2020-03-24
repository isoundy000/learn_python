#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import copy
import time
import itertools

from lib import utils
from lib.utils.debug import print_log
from lib.db import ModelBase
import game_config
from lib.utils import salt_generator


class Pets(ModelBase):
    """# Pets: 宠物

    """
    _need_diff = ('_pets', 'pet_pos', 'pet_follow_pos')

    LOCK_TYPE = ['sys', 'user', 'train']

    BASE_ATTRS = ['patk', 'matk', 'def', 'speed', 'hp']

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


    def __init__(self, uid=None):
        self.uid = uid
        total_acount = len(game_config.pet_corral)
        acount = len([k for k, v in game_config.pet_corral.iteritems() if v['is_open']])
        total_follow_num = len(game_config.pet_follow) or 8
        self._attrs = {
            '_pets': {

            },
            'pet_pos': ['0'] * acount + ['-1'] * (total_acount - acount),   # -1标示未解锁 0标示已经解锁
            'pet_follow_pos': ['-1'] * total_follow_num,    # -1标示未解锁 0标示已经解锁
        }
        self._cache = {}
        super(Pets, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server=''):
        o = super(Pets, cls).get(uid, server)
        return o

    def _client_cache_update(self):
        """# _client_cache_update: 卡牌的变化，不能仅仅把数据库记录的数据交给前端，还需要用single_pet_info处理一下
        args:
            :    ---    arg
        returns:
            0    ---
        """
        if '_pets' in self._diff:
            d = {}
            for k, v in self._diff['_pets']['update'].iteritems():
                d[k] = self.single_pet_info(v)
            self._diff['pets'] = {
                'update': d,
                'remove': self._diff['_pets']['remove'],
            }
            del self._diff['_pets']
        return self._diff

    @classmethod
    def _make_id(cls, config_id):
        """ 生成宠物的id

        :param config_id: 宠物id
        :return:
        """
        return '%s-%s-%s' % (config_id, int(time.time()), salt_generator())

    def crystal_effect(self, crystal_type, level):
        """ 强化效果

        :param crystal_type: 强化属性类型
        :param level: 宠物强化等级
        :return:
        """
        config = game_config.pet_strengthen
        crystal_type = 'add_%s' % crystal_type
        return config[level][crystal_type] if level in config else 0

    def single_pet_info(self, pet_dict):
        """ 包含了一个卡牌各个数值的比较完整的info

        :param pet_dict:
        :return:
        """
        if not isinstance(pet_dict, dict):
            pet_dict = self._pets[pet_dict]

        pet_key = pet_dict['id']
        cache_pet = self._cache.get(pet_key)
        if cache_pet is not None:
            return cache_pet

        lv = pet_dict['lv']

        pet_config = game_config.pet_detail[int(pet_dict['c_id'])]

        pet = copy.deepcopy(pet_dict)

        for s in self.BASE_ATTRS:
            growth_value = pet_config['growth_%s' % s]
            sbase = (lv - 1) * growth_value + pet['base_%s' % s]
            pet[s] = sbase + self.crystal_effect(s, pet['%s_crystal' % s])

        pet['quality'] = pet_config['quality']
        pet['race'] = pet_config['race']
        pet['career'] = pet_config['career']
        pet['animation'] = pet_config['animation']
        pet['rgb_sort'] = pet_config['rgb_sort']

        self._cache[pet_key] = pet

        return pet

    def remove_cache(self, pet_key):
        """ 删除cache中得数据

        :param pet_key:
        :return:
        """
        if pet_key in self._cache:
            del self._cache[pet_key]

    def remove(self, pet_key):
        """ 删除宠物

        :param pet_key: 宠物key
        :return:
        """
        if self.is_remove_able(pet_key):
            del self._pets[pet_key]
            return True
        else:
            return False

    def is_remove_able(self, pet_key):
        """ 能否删除

        :param pet_key: 宠物key
        :return:
        """
        return not self._pets[pet_key]['remove_avail']

    def lock_pet(self, pet_key, lock_type):
        """ 由程序主动锁定一只宠物，此宠物不能删除

        :param pet_key: 宠物key
        :param lock_type: 锁的类型
        :return:
        """
        if lock_type not in self.LOCK_TYPE:
            raise
        if lock_type not in self._pets[pet_key]['remove_avail']:
            self._pets[pet_key]['remove_avail'].append(lock_type)
        else:
            return 1

    def release_card(self, pet_key, lock_type):
        """ 释放(解锁)宠物

        :param pet_key: 宠物key
        :param lock_type: 锁的类型
        :return:
        """
        if lock_type not in self.LOCK_TYPE:
            raise
        if lock_type in self._pets[pet_key]['remove_avail']:
            self._pets[pet_key]['remove_avail'].remove(lock_type)
        else:
            return 1

    def get_lock_status(self, pet_key):
        """ 获取锁的状态

        :param pet_key:
        :return:
        """
        st = self._pets[pet_key]['remove_avail']
        if 'user' in st:
            return 10002
        elif 'train' in st:
            return 10003
        elif 'sys' in st:
            return 10001

    def new(self, config_id, s_1=(), s_2=(), lv=1, **kwargs):
        """ 创建一只宠物

        :param config_id: 宠物id
        :param s_1: 技能1(技能key, 技能等级)
        :param s_2: 技能2(技能key, 技能等级)
        :param lv: 宠物等级
        :param kwargs:
        :return:
        pet = {
            'id': pet_key,      # 宠物key
            'c_id': config_id,  # 宠物配置id
            'lv': lv,           # 宠物等级
            'level_max': min(lv, pet_config['level_max']),  # 宠物最大等级
            'exp': 0,               # 宠物经验
            'pre_exp': 0,     # 宠物之前总经验
            'star': 0,              # 进阶升星

            'base_patk': 0,
            'base_matk': 0,
            'base_def': 0,
            'base_speed': 0,
            'base_hp': 0,

            'patk_crystal': 0,      # 强化
            'matk_crystal': 0,
            'def_crystal': 0,
            'speed_crystal': 0,
            'hp_crystal': 0,

            's_1': {
                'lv': 1,
                'exp': 0,
                'avail': 2,    # 0 - 不可用，1 - 可以激活，2 - 已经激活
                's': 0,        # 技能的id  根据技能的id可以在pet_skill_detail中可以取到最大等级max_lv
            },
            's_2': {'lv': 1, 'exp': 0, 'avail': 0, 's': 0,},

            'remove_avail': [],    # 是否可以被删除, []表示可以删除
        }
        """
        config_id = int(config_id)
        pet_config = game_config.pet_detail[config_id]

        if config_id in self.get_pos_config_id() or len([pos for pos in self.pet_pos if pos == '0']) <= 0:
            '''宠物存在|没有解锁宠物位置'''
            resolve_id = pet_config['resolve_id']
            resolve_num = pet_config['resolve_num']
            self.weak_user.item.add_item(resolve_id, resolve_num, immediate=True)
        else:
            pet_key = self._make_id(config_id)
            pet_type = pet_config['type']

            pet_dict = {
                'id': pet_key,          # 宠物key
                'c_id': config_id,      # 宠物配置id
                'lv': lv,               # 宠物等级
                'level_max': pet_config['level_max'],       # 宠物最大等级
                'exp': 0,               # 宠物经验
                'pre_exp': 0,           # 宠物之前总经验
                'star': pet_config['star'],     # 进阶升星
                'remove_avail': [],     # 是否可以被删除, []表示可以删除
                'is_refresh': False,    # 是否刷新属性
            }

            # 添加基础属性 和 强化属性
            for attr in self.BASE_ATTRS:
                base_attr = 'base_%s' % attr
                pet_dict[base_attr] = pet_config[base_attr]
                crystal_attr = '%s_crystal' % attr
                pet_dict[crystal_attr] = 0

            for i in '12':
                if locals()['s_' + i] != ():
                    s, s_lv = locals()['s_' + i]
                    avail = 2
                else:
                    skill_source = pet_config['skill_%s_source' % i]
                    s = utils.weight_choice(skill_source, 1)[0] if skill_source else 0
                    s_lv = 1
                    avail = 0 if i != '1' else 2
                pet_dict['s_%s' % i] = {'lv': int(s_lv), 'exp': 0, 'avail': avail, 's': int(s)}

            pet_dict['star'] = 1
            star = pet_config['star'] - 1

            for i in range(star):
                self.evolution(pet_key, pet_dict, pet_config)

            pet_dict['pre_exp'] = sum([int(game_config.pet_base[level]['exp']) for level in xrange(1, lv)])

            self._pets[pet_key] = pet_dict

            # for index, pos in enumerate(self.pet_pos):
            #     if pos == '0':
            #         self.pet_pos[index] = pet_key
            #         break

            return pet_key

    def evolution(self, pet_key, raw_pet_info=None, pet_config=None):
        """ 进化

        :param pet_key: 宠物key
        :param raw_pet_info: 宠物数据
        :param pet_config: 宠物配置数据
        :return:
        """
        raw_pet_info = raw_pet_info or self._pets[pet_key]
        pet_config = pet_config or game_config.pet_detail[raw_pet_info['c_id']]
        evo_config = game_config.pet_evolution

        cur_star = raw_pet_info['star']
        next_star = cur_star + 1
        pre_config = evo_config.get(next_star)
        if not pre_config:
            return False

        cur_pet_config = evo_config.get(cur_star)
        raw_pet_info['lv'] = max(1, raw_pet_info['lv'] - pre_config['level_off'])
        # 降等级 重新计算pre_exp
        if pre_config['level_off']:
            raw_pet_info['pre_exp'] = sum([int(game_config.pet_base[level]['exp']) for level in xrange(1, raw_pet_info['lv'])])

        if pet_config['is_evo']:
            raw_pet_info['level_max'] = pet_config['maxlv']

        for idx, v in enumerate(pre_config['skill']):                       # 进化影响宠物技能
            skill = raw_pet_info['s_%s' % (idx + 1)]
            pre_v = cur_pet_config['skill'][idx] if cur_pet_config else 0
            if pre_v != v and skill['s'] > 0:
                if v == 1:
                    skill['avail'] = 2
                elif v > 1:
                    skill_config = game_config.pet_skill_detail[skill['s']]
                    next_skill_key = skill_config['is_evolution']
                    if next_skill_key:
                        skill['avail'] = 2
                        skill['s'] = next_skill_key

        raw_pet_info['star'] = next_star
        self.calc_base_attrs_value(pet_key, raw_pet_info, pet_config)
        self.remove_cache(pet_key)

        return raw_pet_info

    def calc_base_attrs_value(self, pet_key, pet_info=None, pet_config=None):
        """ 重新计算宠物五项属性的值,加上evo的效果

        :param pet_key: 宠物key
        :param pet_info: 宠物数据
        :param pet_config: 宠物配置数据
        :return:
        """
        raw_pet_info = pet_info or self._pets[pet_key]
        pet_config = pet_config or game_config.pet_detail[raw_pet_info['c_id']]
        evo_config = game_config.pet_evolution

        cur_star = raw_pet_info['star']
        _config = evo_config.get(cur_star)
        if not _config:
            return

        for attr, value in itertools.izip(self.BASE_ATTRS, _config['type%s' % pet_config['race']]):
            attr_str = 'base_%s' % attr
            all_rate = _config['all']
            raw_pet_info[attr_str] = (value + pet_config[attr_str]) * (1 + all_rate)

    def calc_base_attrs_diff_value(self, pet_key, start_evo=0, end_evo=1, pet_info=None, pet_config=None):
        """ 计算宠物五项属性的差值, 加上evo的效果

        :param pet_key:
        :param start_evo:
        :param end_evo:
        :param pet_info:
        :param pet_config:
        :return:
        """
        raw_pet_info = pet_info or self._pets[pet_key]
        pet_config = pet_config or game_config.pet_detail[raw_pet_info['c_id']]
        evo_config = game_config.pet_evolution

        start_evo_config = evo_config.get(start_evo)
        end_evo_config = evo_config.get(end_evo)
        if not start_evo_config or not end_evo_config or start_evo >= end_evo:
            return {}

        diff_data = {}

        for attr, s_value, e_value in itertools.izip(self.BASE_ATTRS,
                                                     start_evo_config['type%s' % pet_config['race']],
                                                     end_evo_config['type%s' % pet_config['race']]):
            end_all_rate = end_evo_config['all']
            start_all_rate = start_evo_config['all']
            diff_data[attr] = e_value * (1 + end_all_rate) - s_value * (1 + start_all_rate)

        return diff_data

    def get_all_cards(self):
        """# get_all_cards: 获得所有宠物卡牌所有信息
        args:
            :    ---    arg
        returns:
            0    ---
        """
        _pets_temp = {}
        for k, v in self._pets.iteritems():
            info = self.single_pet_info(v)
            info['id'] = k
            _pets_temp[k] = info
        return _pets_temp

    def get_pos_config_id(self):
        """ 获取位置上的config_id

        :return:
        """
        return [v['c_id'] for v in self._pets.itervalues()]

    def add_exp(self, pet_key, exp_add):
        """ 给某宠物加经验

        :param pet_key: 宠物key
        :param exp_add: 增加的经验
        :return:
        """
        raw_pet_info = self._pets[pet_key]
        pet_config = game_config.pet_detail[raw_pet_info['c_id']]
        evo_config = game_config.pet_evolution
        _evo_config = evo_config.get(raw_pet_info['star'])

        # 策划又新开放了等级上限，还是在这里每次都判断上限更新吧
        if pet_config['is_evo'] and _evo_config:
            level_max = _evo_config['maxlv']
        else:
            level_max = pet_config['level_max']

        raw_pet_info['level_max'] = level_max
        level = raw_pet_info['lv']
        if level_max <= level:
            return [(level, 0)]

        level_config = game_config.pet_base

        exp = self._pets[pet_key]['exp'] + int(exp_add)

        next_level_exp_need = int(level_config[level]['exp'])

        level_change = [(level, next_level_exp_need)]
        while next_level_exp_need <= exp:
            exp -= next_level_exp_need
            level += 1
            if level_max < level:
                level = level_max
                exp = 0  # next_level_exp_need
                level_change.append((level, next_level_exp_need))
                break
            self._pets[pet_key]['pre_exp'] += next_level_exp_need
            next_level_exp_need = int(level_config[level]['exp'])
            level_change.append((level, next_level_exp_need))
        self._pets[pet_key]['exp'] = exp
        self._pets[pet_key]['lv'] = level
        self.remove_cache(pet_key)

        return level_change

    def get_max_level_need_exp(self, pet_key):
        """ 获取满级需要的经验

        :param pet_key:
        :return:
        """
        c_id = self._pets[pet_key]['c_id']
        level = self._pets[pet_key]['lv']
        level_max = self._pets[pet_key].get('level_max') or game_config.pet_detail[c_id]['level_max']

        if level_max <= level:
            return 0

        level_config = game_config.pet_base

        # 需要到达满级的总经验
        total_exp = sum([int(level_config[i]['exp']) for i in xrange(level, level_max)])

        # 需要减去当前经验
        diff_exp = total_exp - self._pets[pet_key]['exp']

        return diff_exp

    def get_need_exp_for_level(self, start_level, end_level):
        """ 通过等级获取经验

        :param start_level:
        :param end_level:
        :return:
        """
        level_config = game_config.pet_base

        # 需要到达满级的总经验
        total_exp = sum([int(level_config[i]['exp']) for i in xrange(start_level, end_level)])

        return total_exp

    def add_skill_exp(self, pet_key, skill_id):
        """ 升级宠物中对应技能经验

        :param pet_key:
        :param skill_id:
        :return:
        """
        raw_pet_info = self._pets[pet_key]
        pet_skill = None
        for i in '12':
            pet_skill = raw_pet_info['s_%s' % i]
            if pet_skill['avail'] != 0 and pet_skill['s'] == skill_id:
                break
            else:
                pet_skill = None

        if pet_skill is None:
            return 3

        skill_detail = game_config.pet_skill_detail[pet_skill['s']]
        skill_quality = skill_detail['skill_quality']

        lv = pet_skill['lv']

        skill_levelup = game_config.pet_skill_levelup[lv]
        stone_cost = skill_levelup['stone_cost'][skill_quality]

        if self.weak_user.pet_skill_stone < stone_cost:
            return 4

        exp = pet_skill['exp'] + stone_cost

        max_lv = skill_detail['max_lv']

        if lv >= max_lv:
            return 'error_11'

        next_lv_exp = skill_levelup['skill_exp'][skill_quality]

        while exp >= next_lv_exp:
            lv += 1
            exp -= next_lv_exp
            if lv >= max_lv:
                lv = max_lv
                exp = 0
                break
            next_lv_exp = game_config.pet_skill_levelup[lv]['skill_exp'][skill_quality]
        pet_skill['lv'] = lv
        pet_skill['exp'] = exp
        self.remove_cache(pet_key)

        self.weak_user.pet_skill_stone -= stone_cost

    def check_skill_used_exp(self, pet_key, skill_pos):
        """ 检查升级技能需要的经验

        :param pet_key:
        :param skill_pos:
        :return:
        """
        need_exp = 0
        pet_info = self._pets[pet_key]
        skill_info = pet_info[skill_pos]
        if skill_info['avail'] == 2:
            quality = game_config.pet_skill_detail[skill_info['s']]['skill_quality']
            need_exp = sum([game_config.pet_skill_levelup[lv]['skill_exp'][quality]
                            for lv in xrange(1, skill_info['lv'])])
        return need_exp + skill_info['exp']

    def has_pet(self, pet_key):
        """ 检查是否有卡牌

        :param pet_key:
        :return:
        """
        return pet_key in self._pets

    def get_card_data(self, pet_key):
        """ 得到卡牌当前的宠物数据的拷贝

        :param pet_key:
        :return:
        """
        if pet_key in self._pets:
            return copy.deepcopy(self._pets[pet_key])
        else:
            return None

    def get_base_attr(self, pet_key, attribute):
        """ 根据key（attribute）得到指定值

        :param pet_key:
        :param attribute:
        :return:
        """
        return self._pets[pet_key][str(attribute)]

    def check_pet_used_crystal(self, pet_key, pet_info=None):
        """ 返回宠物能晶
        :param pet_key:
        :param pet_info:
        :return:
        """
        pet_info = pet_info or self._pets[pet_key]
        need_crystal = 0
        for tp in self.BASE_ATTRS:
            _tp = '%s_crystal' % tp
            lvs = pet_info[_tp]
            for lv in xrange(1, lvs + 1):
                lv_config = game_config.pet_strengthen[lv]
                need_crystal_list = lv_config['need_crstal_' + tp]
                if need_crystal_list[0] == 3:
                    need_crystal += need_crystal_list[1]
        return need_crystal

    def pet_follow_effect(self, card_id):
        """
        跟谁宠物的效果
        :return:
        """
        result_dict = {}
        if card_id != '-1':     # 这个位置有卡牌
            # 基础值10
            pos_min = min(game_config.position)
            position_config = game_config.position.get(pos_min)
            value = position_config.get('value', 10)

            for pet_follow_id in self.pet_follow_pos:
                if pet_follow_id in ('-1', '0'):
                    continue
                pet_follow = self.single_pet_info(pet_follow_id)
                follow_data = copy.deepcopy(pet_follow)
                # 刷新的数值
                refresh_num = 0
                if follow_data.get('is_refresh', False):
                    refresh_num += follow_data.get('refresh_num')

                for attr_type in self.BASE_ATTRS:
                    effect = follow_data[attr_type]
                    pet_follow_effect = effect * (value / 100.0 + refresh_num)
                    if attr_type not in result_dict:
                        result_dict[attr_type] = pet_follow_effect
                    else:
                        result_dict[attr_type] += pet_follow_effect
        return result_dict