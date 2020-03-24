#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import datetime
from lib.db import ModelBase
from logics import notice
import copy
import game_config
from lib.utils import generate_rank_score
from logics.share import refresh_cyc
from lib.utils import weight_choice
from lib.utils.debug import print_log


class Equip(ModelBase):
    """# Equip: 装备"""
    _need_diff = ('_equip',)

    # 根据品质计算排行积分
    QUALITY_RANK_RATE = {
        1: 1,
        2: 1.3,
        3: 2.3,
        4: 4.6,
        5: 6.9,
        6: 9.2,
        7: 12.3,  # 暂时不用
        8: 16.5,  # 暂时不用
    }
    ENCHANT_LIMIT_TIME = 60 * 10    # 初始附魔超过10分钟未保存，取消附魔效果
    EXCHANGE_REFRESH_TIME = [0, 12]
    # 适配战斗里的字段命名
    KEY_MAPPING = {
        'patk': 'phsc',
        'matk': 'mgc',
        'def': 'dfs',
        'speed': 'speed',
        'hp': 'hp',
        'crit': 'crit',
        'hr': 'hr',
        'subhurt': 'subhurt',
        'dr': 'dr',
        'fire': 'fire',
        'water': 'water',
        'wind': 'wind',
        'earth': 'earth',
        'fire_dfs': 'fire_dfs',
        'water_dfs': 'water_dfs',
        'wind_dfs': 'wind_dfs',
        'earth_dfs': 'earth_dfs',
    }

    def __init__(self, uid=None):
        """
        _equip: {
            1: {                        # 背包id
                id: 1,                  # 对应的背包id
                c_id: 1,                # 配置id
                lv: 3,                  # 物品等级
                pos: 1,                 # 对应卡牌对阵位置,-1为没有装备，0～4为主力位置，5～9为替补位置，为装备相应位置
                is_enchant: False,      # 是否初始附魔过
                enchant_times: 0,       # 附魔次数
                enchant_time: 0,        # 初始附魔时间
                atts: {}                # 附魔属性字典{属性:值}
            }
            3: {
                'id': 3,
                'c_id': 10205,
                'lv': 1,
                'pos': -1,
                'is_enchant': False,
                'enchant_times': 0,
                'enchant_time': 0,
                'atts': {},

                'equip_forge': {
                    6: {'patk': 0.0},
                    16: {'patk': 0.0},
                    26: {'matk': 0.0}
                },

                'equip_forge_level': {'exp': 10, 'lv': 0, 'used_exp': 0},
                'equip_forge_temp': {},

                'is_equip_forge': True,
                'is_equip_refine': False,
                'st_lv': 0,
                'ts': 1439458155
            }
        }

        equip_pos: {
            0: []           # key为对应对阵位置0～4为主力位置，5～9为替补位置
                            # 数组[]:为0:武器(sort 1)，1:饰品(sort 2)，2:防具(sort 3)，3:鞋子(sort 4)
                            # 数组中的值为卡牌背包id，0为没有装备
        }
        :param uid:
        """
        self.uid = uid
        self._attrs = {
            '_equip': {},                       # 装备背包
            'bag_extend': 0,                    # 背包扩展
            'equip_pos': {                      # 主战和替补
                0: [0, 0, 0, 0],
            },
            'ass_equip_pos': {                  # 助威
            },
            'equip_pos_1': {                    # 神域1
            },
            'equip_pos_2': {                    # 神域1
            },
            'equip_pos_3': {
            },
            'exchange_equip_shop': {},          # 装备打造商店数据
            'exchange_equip_refresh_time': 0,   # 装备打造刷新时间
            'exchange_equip_count': {},         # 装备融合次数
        }
        for i in range(10):
            self._attrs['equip_pos'][i] = [0] * 4
        for i in range(10):
            self._attrs['ass_equip_pos'][100 + i] = [0] * 4

        # 神域第一阵型的装备
        for i in range(10):
            self._attrs['equip_pos_1'][i] = [0] * 4
        # 神域第二阵型的装备
        for i in range(10):
            self._attrs['equip_pos_2'][i] = [0] * 4
        # 神域第三阵型的装备
        for i in range(10):
            self._attrs['equip_pos_3'][i] = [0] * 4
        super(Equip, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server=''):
        o = super(Equip, cls).get(uid, server)
        o.refresh()
        return o

    def refresh(self):
        """
        检查不存在的equip
        """
        for pos, v in self.equip_pos.iteritems():
            for idx, equip_id in enumerate(v):
                if equip_id != 0:
                    equip_info = self._equip.get(equip_id)
                    if equip_info is None:
                        v[idx] = 0
                    elif equip_info['pos'] != pos:              # 装备的位置
                        equip_info['pos'] = pos

        for pos, v in self.ass_equip_pos.iteritems():
            for idx, equip_id in enumerate(v):
                if equip_id != 0:
                    equip_info = self._equip.get(equip_id)
                    if equip_info is None:
                        v[idx] = 0
                    elif equip_info['pos'] != pos:
                        equip_info['pos'] = pos

        # 神域的第一个阵型的装备
        for pos, v in self.equip_pos_1.iteritems():
            for idx, equip_id in enumerate(v):
                if equip_id != 0:
                    equip_info = self._equip.get(equip_id)
                    if equip_info is None:
                        v[idx] = 0

        # 神域的第二个阵型的装备
        for pos, v in self.equip_pos_2.iteritems():
            for idx, equip_id in enumerate(v):
                if equip_id != 0:
                    equip_info = self._equip.get(equip_id)
                    if equip_info is None:
                        v[idx] = 0

        # 神域的第三个阵型的装备
        for pos, v in self.equip_pos_3.iteritems():
            for idx, equip_id in enumerate(v):
                if equip_id != 0:
                    equip_info = self._equip.get(equip_id)
                    if equip_info is None:
                        v[idx] = 0

    def _make_id(self):
        """# make_id: 生成一个装备 的id
        args:
            :    ---    arg
        returns:
            0    ---
        """
        ids = self._equip.keys()
        if not ids:
            return 1
        else:
            return max(ids) + 1

    def new(self, config_id):
        """# new: docstring
        args:
            config_id:    ---    arg
        returns:
            0    ---
        """
        equip_id = self._make_id()
        self._equip[equip_id] = {
            'id': equip_id,
            'c_id': config_id,
            'lv': 1,
            'pos': -1,
            'st_lv': 0,                 # 精炼级别
            'st': int(time.time()),
            'is_enchant_tims': 0,
            'enchant_time': 0,
            'atts': {},
            'is_equip_refine': False,   # 装备是否洗炼
            'is_equip_forge': False,    # 装备是否锻造
        }
        notice.notice_4_get_equip(self.weak_user, config_id=config_id)
        self.add_equip_book(config_id)
        return equip_id

    def add_equip_book(self, config_id):
        '''
        增加图鉴
        :param config_id:
        :return:
        '''
        if self.weak_user and config_id in game_config.equip_book_sort \
                and config_id not in self.weak_user.handbook.equip_books:
            self.weak_user.handbook.equip_books[config_id] = int(time.time())
            self.weak_user.handbook.save()

    def data_update_func_1(self):
        '''
        增加 精炼级别
        :return:
        '''
        for v in self._equip.itervalues():
            if 'st_lv' not in v:
                v['st_lv'] = 0

    def data_update_func_2(self):
        '''

        :return:
        '''
        for v in self._equip.itervalues():
            if 'is_enchant' not in v:
                v['is_enchant'] = False
                v['enchant_times'] = 0
                v['enchant_time'] = 0
                v['atts'] = {}

    def data_update_func_4(self):
        """
        修复一件装备洗炼的数据
        :return:
        """
        for v in self._equip.itervalues():
            if 'is_equip_refine' in v and v['c_id'] == 32001 and v['is_equip_refine']:
                # 装备洗炼的数据
                if 'def' in v['equip_refine']:
                    if v['equip_refine'].get('def', 0):
                        if v['equip_refine'].get('matk', 0):
                            v['equip_refine']['matk'] += v['equip_refine']['def']
                        else:
                            v['equip_refine']['matk'] = v['equip_refine']['def']
                    else:
                        if not v['equip_refine'].get('matk', 0):
                            v['equip_refine']['matk'] = 0
                    del v['equip_refine']['def']
                # 装备最后一次洗炼的缓存数据
                if 'def' in v['equip_refine_temp']:
                    if v['equip_refine_temp'].get('def', 0):
                        if v['equip_refine_temp'].get('matk', 0):
                            v['equip_refine_temp']['matk'] += v['equip_refine_temp']['def']
                        else:
                            v['equip_refine_temp']['matk'] = v['equip_refine_temp']['def']
                    else:
                        if not v['equip_refine_temp'].get('matk', 0):
                            v['equip_refine_temp']['matk'] = 0
                    del v['equip_refine_temp']['def']

    def extend_bag(self, amount):
        """# extend_bag: 扩大包裹
        args:
            amount:    ---    arg
        returns:
            0    ---
        """
        self.bag_extend += amount

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

    def single_info(self, equip_id, combat=False):      # 计算战斗值判断是否执行精炼的标记
        """# single_info: docstring
        args:
            equip_dict:    ---    arg
        returns:
            0    ---
        """
        temp = copy.copy(self._equip[equip_id])

        # 属性用0初始化
        for i in self.CHAIN_EFFECT_NUM_NAME_DICT.itervalues():
            if not i: continue
            temp[i] = 0

        e_config = game_config.equip[temp['c_id']]

        # 装备的等级加成
        for i in '12':                          # 用game_config.equip中的数据计算当前level属性值
            ability = e_config['ability' + i]
            value = e_config['value' + i]
            temp[self.CHAIN_EFFECT_NUM_NAME_DICT[ability]] = value + e_config['level_add' + i] * (temp['lv'] - 1)

        # 准备精炼的效果
        if not combat:
            tempSort = e_config['sort']
            tempFlag = ['', 'patk', 'matk', 'def', 'speed']
            if tempSort < 5 and tempSort > 0:
                if temp['st_lv'] > 0:
                    config_st = game_config.equip_st[temp['st_lv']]
                    ability, value = config_st[tempFlag[tempSort]]
                    temp[self.CHAIN_EFFECT_NUM_NAME_DICT[ability]] += value

        # 附魔属性加入单张卡牌信息
        if self._equip[equip_id].get('is_enchant', False) == True:
            for key, value in self._equip[equip_id]['atts'].iteritems():
                if key in temp:
                    temp[key] += value
                else:
                    temp[key] = value

        # 是否洗炼 属性加入单张卡牌信息
        if self._equip[equip_id].get('is_equip_refine', False) == True:
            for key, value in self._equip[equip_id]['equip_refine'].iteritems():
                if key in temp and key not in ['extra_break_1', 'extra_break_2']:
                    if key in temp:
                        temp[key] += value
                    else:
                        temp[key] = value

        # 是否锻造 属性加入单张卡牌信息
        if self._equip[equip_id].get('is_equip_forge', False) == True:
            for value in self._equip[equip_id]['equip_forge'].itervalues():
                for key, val in value.iteritems():
                    if key in temp:
                        temp[key] += val
                    else:
                        temp[key] = val

        for k, v in self.KEY_MAPPING.iteritems():
            temp[v] = temp.setdefault(k, 0)
        return temp

    def attack_and_defender_attr_point(self, equip_id, equip_forge_temp=None):
        """
        返回每件装备的减少的值
        :param equip_id:
        :return:
        """
        equip_forge_temp = equip_forge_temp or {}
        equip_info = self._equip[equip_id]
        # 是否锻造 属性加入单张卡牌信息
        if equip_info.get('is_equip_forge', False) == True:
            for _id, value in equip_info['equip_forge'].iteritems():
                set_config = game_config.equip_set_random.get(_id)
                attr_id = set_config['sort']
                enemy_list = set_config['enemy']
                if not enemy_list:
                    continue
                attr = self.CHAIN_EFFECT_NUM_NAME_DICT.get(attr_id)
                if enemy_list[0] == -1:
                    if -1 not in equip_forge_temp:
                        equip_forge_temp[-1] = {attr: value[attr]}
                    else:
                        if attr not in equip_forge_temp[-1]:
                            equip_forge_temp[-1][attr] = value[attr]
                        else:
                            equip_forge_temp[-1][attr] += value[attr]
                else:
                    for c_id in enemy_list:
                        if c_id not in equip_forge_temp:
                            equip_forge_temp[c_id] = {attr: value[attr]}
                        else:
                            if attr not in equip_forge_temp[c_id]:
                                equip_forge_temp[c_id][attr] = value[attr]
                            else:
                                equip_forge_temp[c_id][attr] += value[attr]
        return equip_forge_temp

    def suit_effect(self, pos, equip_pos=None, god_formation=None):
        # 套装增幅
        temp = {}
        for i in self.CHAIN_EFFECT_NUM_NAME_DICT.itervalues():  # 属性用0初始化
            if not i: continue
            temp[i] = 0
        if not god_formation:
            if 0 <= pos <= 9:
                # 阵型上 出战和替补
                if equip_pos is None:
                    equip_pos = self.equip_pos[pos]
            else:
                # 助威的装备
                if equip_pos is None:
                    equip_pos = self.ass_equip_pos[pos]
        # 神域阵型上 出战和替补
        elif god_formation == 1:
            # 阵型上 出战和替补
            if equip_pos is None:
                equip_pos = self.equip_pos_1[pos]
        elif god_formation == 2:
            # 阵型上 出战和替补
            if equip_pos is None:
                equip_pos = self.equip_pos_2[pos]
        elif god_formation == 3:
            # 阵型上 出战和替补
            if equip_pos is None:
                equip_pos = self.equip_pos_3[pos]

        suit_ids = {}
        own_suit = set()

        for equip_id in equip_pos:
            if equip_id:
                e_config = game_config.equip[self._equip[equip_id]['c_id']]
                suit_id = e_config['suit']
                # 自己的装备
                own_suit.add(e_config['equip_id'])
                if suit_id:
                    suit_config = game_config.suit[suit_id]
                    part = suit_config['part']
                    suit_equip_ids = set()
                    for p in part:
                        # 套装装备的id
                        suit_equip_ids.add(game_config.equip[p]['equip_id'])
                    # 套装的装备id
                    suit_ids[suit_id] = suit_equip_ids
        # 套装效果
        for suit_id, suit_equip_ids in suit_ids.iteritems():
            num = len(own_suit & suit_equip_ids)
            if num >= 2:
                for i in xrange(2, num + 1):
                    effect = game_config.suit[suit_id]['effect_%d' % i]
                    for ef in effect:
                        temp[self.CHAIN_EFFECT_NUM_NAME_DICT[ef[0]]] += ef[1]

        for k, v in self.KEY_MAPPING.iteritems():
            temp[v] = temp.setdefault(k, 0)
        return temp

    def suit_effects(self):
        """ 获取所有的套装效果, 不包括助威的

        :return: {0: temp, 1: temp}
        """
        equip_data = {}
        for pos, equip_ids in self.equip_pos.iteritems():
            temp = self.suit_effect(pos, equip_ids)
            equip_data[pos] = temp
        return equip_data

    def get_all(self):
        """
        得到全部的卡包
        """
        return self._equip

    def remove(self, equip_id):
        """
        从背包里去掉一个指定装备（equip_id）
        """
        tempPos = -1
        if equip_id in self._equip:
            tempPos = self._equip[equip_id]['pos']
            del self._equip[equip_id]

        if 0 <= tempPos <= 9:
            tempIndex = self.equip_pos[tempPos].index(equip_id)
            self.equip_pos[tempPos][tempIndex] = 0
            # 更新装备强度排行榜
            self.update_equipment_rank()
        elif 100 <= tempPos <= 109:
            tempIndex = self.ass_equip_pos[tempPos].index(equip_id)
            self.ass_equip_pos[tempPos][tempIndex] = 0
            # 更新装备强度排行榜
            self.update_equipment_rank()

        # 删除神域阵型1上的装备
        for equip_ids in self.equip_pos_1.itervalues():
            for equip_id in equip_ids:
                index = equip_ids.index(equip_id)
                if index >= 0:
                    equip_ids[index] = 0
                    self.update_equipment_rank()

        # 删除神域阵型2上的装备
        for equip_ids in self.equip_pos_2.itervalues():
            if equip_id in equip_ids:
                index = equip_ids.index(equip_id)
                if index >= 0:
                    equip_ids[index] = 0
                    self.update_equipment_rank()

        # 删除神域阵型3上的装备
        for equip_ids in self.equip_pos_3.itervalues():
            if equip_id in equip_ids:
                index = equip_ids.index(equip_id)
                if index >= 0:
                    equip_ids[index] = 0
                    self.update_equipment_rank()

    def check_used_metal_and_metalcore(self, equip_id, equip_info):
        equip_info - equip_info or self._equip[equip_id]
        config = game_config.equip[equip_info['c_id']]
        need_metal, need_metalcore, need_enchant = 0, 0, 0

        quality = config['quality']
        for lv in range(1, equip_info['lv']):
            tempStrongthen = game_config.equip_strongthen[lv]
            need_metal += tempStrongthen['metal'] * tempStrongthen['quality' + str(quality)] / 100

        for lv in range(1, equip_info['st_lv'] + 1):
            if lv not in game_config.equip_st:
                continue
            st_config = game_config.equip_st[lv]
            need_metal += st_config['metal']
            need_metalcore += st_config['metalcore']

        # need_enchant += equip_info['enchant_times'] * game_config.enchant[quality]['piece']
        count = 0
        for v in equip_info['atts'].values():
            need_enchant += v
            count += 1
        if count:
            need_enchant = int(need_enchant / count * 0.8)

        return need_metal, need_metalcore, need_enchant

    def get_all_equip_pos(self, is_formation=True):
        """ 获取所有位置上的装备id

        :return [equip_id, equip_id]
        """
        all_equip = []
        for equip_ids in self.equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id != 0:
                    all_equip.append(equip_id)

        for equip_ids in self.ass_equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id != 0:
                    all_equip.append(equip_id)

        if is_formation:
            # 神域的三套装备
            for equip_ids in self.equip_pos_1.itervalues():
                for equip_id in equip_ids:
                    if equip_id != 0:
                        all_equip.append(equip_id)

            for equip_ids in self.equip_pos_2.itervalues():
                for equip_id in equip_ids:
                    if equip_id != 0:
                        all_equip.append(equip_id)

            for equip_ids in self.equip_pos_3.itervalues():
                for equip_id in equip_ids:
                    if equip_id != 0:
                        all_equip.append(equip_id)

        return all_equip

    def get_equip_pos(self):
        """ 获取阵容中得装备id

        :return:
        """
        equip = []
        for equip_ids in self.equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id != 0:
                    equip.append(equip_id)
        return equip

    def get_ass_equip_pos(self):
        """ 获取助威中得装备id

        :return:
        """
        equip = []
        for equip_ids in self.ass_equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id != 0:
                    equip.append(equip_id)
        return equip

    def update_equipment_rank(self):
        """ 装备强度排行榜

        :return:
        """
        equipment_score = 0

        for equip_ids in self.equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id > 0:
                    equip = self._equip[equip_id]
                    config = game_config.equip[equip['c_id']]
                    equipment_score += int(equip['lv'] * self.QUALITY_RANK_RATE.get(config['quality'], 1) +
                                           equip['st_lv'] * 10)

        for equip_ids in self.ass_equip_pos.itervalues():
            for equip_id in equip_ids:
                if equip_id > 0:
                    equip = self._equip[equip_id]
                    config = game_config.equip[equip['c_id']]
                    equipment_score += int(equip['lv'] * self.QUALITY_RANK_RATE.get(config['quality'], 1) +
                                           equip['st_lv'] * 10)

        if equipment_score:
            rank_key = self.weak_user.user_m.get_equipment_rank_key()
            redis = self.get_father_redis(rank_key)
            redis.zadd(rank_key, self.uid, generate_rank_score(equipment_score))

    def check_exchange_equip_time(self, save=True):
        """ 检查装备打造刷新时间
        i [0, 12]   刷新时间
        :return:
        """
        for i in self.EXCHANGE_REFRESH_TIME:
            status = refresh_cyc(self, 'exchange_equip_refresh_time', i, self.refresh_exchange_equip_shop, save=save)
            if status:
                break

    def refresh_exchange_equip_shop(self):
        """ 刷新装备打造数据

        :return:
        """
        data = []
        for k, v in game_config.exchange_equip_shop.iteritems():
            start_level, end_level = v['show_level']
            if start_level <= self.weak_user.level <= end_level:
                data.append((k, v['weight']))

        shop = {}
        for i in xrange(6):
            if data:
                shop_id, _ = weight_choice(data)
                shop[shop_id] = 0
                data.remove((shop_id, _))

        self.exchange_equip_shop = shop             # 装备打造商店

    def get_exchange_equip_remain_time(self):
        """ 获取装备打造剩余时间

        :return:
        """
        now = datetime.datetime.now()
        cur_hour = now.hour
        index = None
        for i, hour in enumerate(self.EXCHANGE_REFRESH_TIME):
            if hour <= cur_hour:
                index = i

        if index is None or index == len(self.EXCHANGE_REFRESH_TIME) - 1:
            cal_now = datetime.datetime(now.year, now.month, now.day, self.EXCHANGE_REFRESH_TIME[0]) + \
                      datetime.timedelta(days=1)
        else:
            index += 1
            if index >= len(self.EXCHANGE_REFRESH_TIME):
                index = 0
            cal_now = datetime.datetime(now.year, now.month, now.day, self.EXCHANGE_REFRESH_TIME[index])

        return int(time.mktime(cal_now.timetuple()) - time.time())