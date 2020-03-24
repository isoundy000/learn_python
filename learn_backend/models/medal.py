#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time

from lib.db import ModelBase, ModelTools
import game_config
import settings


class Medal(ModelBase):
    """
    勋章系统 记录在每个用户身上
    """
    _need_diff = ('_medal',)

    ATTR_DICT = {
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

    MATERIAL_GIFT_ID = 29  # 勋章材料的标识
    MEDAL_GIFT_ID = 30  # 勋章的标识

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            # 'train': {
            #     1 : {
            #         'is_finish': 0,   # 是否可以领取
            #         'material_id': '',# 训练的材料
            #         'start_time': 0,  # 炼制的时间
            #     },
            #     2 : {
            #         'is_finish': 0,   # 是否可以领取
            #         'material_id': '',# 训练的材料
            #         'start_time': 0,  # 炼制的时间
            #     },
            #     3 : {
            #         'is_finish': 0,   # 是否可以领取
            #         'material_id': '',# 训练的材料
            #         'start_time': 0,  # 炼制的时间
            #     },
            #     4 : {
            #         'is_finish': 0,   # 是否可以领取
            #         'material_id': '',# 训练的材料
            #         'start_time': 0,  # 炼制的时间
            #     },
            # },
            'free_times': 1,  # 免费加速炼制勋章的次数
            'quick_train_times': 0,  # 加速炼制勋章的次数
            'refresh_time': 0,  # 刷新的时间
            'train_medal': {},  # {1: {'time': 'medel_id': }, 2:{}, 3:{}}
            'synthesis_medal_time': 0,  # 合成勋章的时间
            'exchange_rate': 30,  # 变卡的概率
            'material': {},  # 勋章的材料 material_id : num表示数量
            '_medal': {},  # 勋章的背包 medal_id: num 功勋的数量
            'medal_pos': {
                0: ['0', '0', '0', '0', '0', '0'],  # 阵型的勋章
            },
        }
        for i in range(10):
            self._attrs['medal_pos'][i] = ['0'] * 6
        super(Medal, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server_name='', need_init=True):
        o = super(Medal, cls).get(uid, server_name=server_name, need_init=need_init)
        # o.refresh_day()
        return o

    # def refresh_day(self):
    #     """
    #     每日刷新
    #     :return:
    #     """
    #     now = time.strftime('%Y-%m-%d')
    #     if self.refresh_time != now:
    #         self.free_times = 1
    #         self.quick_train_times = 0
    #         self.refresh_time = now
    #         self.save()

    # def clear_train_pos(self, pos, save=True):
    #     """
    #     清理炼制位置信息
    #     :param pos:
    #     :return:
    #     """
    #     pos_info = self.train[pos]
    #     pos_info['is_finish'] = 0
    #     pos_info['material_id'] = ''
    #     pos_info['start_time'] = 0
    #     if save:
    #         self.save()

    def get_medal_num(self, medal_id):
        """ 获取勋章的数量
        :return:
        """
        return self._medal.get(medal_id, 0)

    def remover_material(self, material_id, num=1):
        """
        :param material_id: 材料的id
        :param num: 材料的数量
        :return:
        """
        if material_id not in self.material:
            return False
        cur_num = self.material.get(material_id, 0)
        if cur_num < num:
            return False
        cur_num -= num
        if cur_num <= 0:
            del self.material[material_id]
        else:
            self.material[material_id] = cur_num
        return True

    def add_material(self, material_id, num=1):
        """
        :param material_id: 材料的id
        :param num: 材料的数量
        :return:
        """
        if material_id not in self.material:
            self.material[material_id] = num
        else:
            self.material[material_id] += num
        return self.material[material_id]

    def remover_medal(self, medal_id, num=1):
        """
        :param medal_id: 勋章的id
        :param num: 勋章的数量
        :return:
        """
        if medal_id not in self._medal:
            return False
        cur_num = self._medal.get(medal_id, 0)
        if cur_num < num:
            return False
        cur_num -= num
        if cur_num <= 0:
            del self._medal[medal_id]
        else:
            self._medal[medal_id] = cur_num
        return True

    def add_medal(self, medal_id, num=1):
        """ 新建一个勋章
        :param medal_id: 勋章的id
        """
        if medal_id not in self._medal:
            self._medal[medal_id] = num
        else:
            self._medal[medal_id] += num
        return self._medal[medal_id]

    def get_all_medal_pos(self):
        """ 获取所有位置上的勋章的id
        :return [medal_id, medal_id]
        """
        all_medal = []
        for medal_ids in self.medal_pos.itervalues():
            for medal_id in medal_ids:
                if medal_id != '0':
                    all_medal.append(medal_id)
        return all_medal

    def position_medal_info(self, medal_position):
        """ 计算某个位置的勋章效果
        medal_position    : int, 1~9, 代表勋章的位置
        return          : dict, 如{'fire':1400, 'wind_dfs':1000}, 其中key值只可能为attr_dict中的八种
        """
        result_dict = {}
        # 传入的位置错误或该位置没有勋章
        if medal_position not in range(10) or self.medal_pos[medal_position] == ['0', '0', '0', '0', '0', '0']:
            return result_dict
        medal_config = game_config.medal
        for medal_id in self.medal_pos[medal_position]:
            if medal_id == '0' or medal_id not in medal_config:
                continue
            else:
                effects = medal_config[medal_id].get('effect')
                if effects:
                    for effect in effects:
                        attr_type = self.ATTR_DICT[effect[0]]
                        if attr_type not in result_dict:
                            result_dict[attr_type] = effect[1]
                        else:
                            result_dict[attr_type] += effect[1]
        return result_dict


class FirstReceiveMedal(ModelTools):
    """
    首次合成勋章的人的纪录
    """
    FIRST_RECEIVE_MEDAL = 'first_receive_medal'

    def __init__(self, server_name):
        """
        :return:
        """
        father_server_name = settings.get_father_server(server_name)
        self._father_server_name = father_server_name
        self.first_receive_key = {}
        self.redis = self.get_redis_client(self.__class__.__name__, father_server_name)

    def make_first_receive_medal(self, medal_id):
        """
        生成一个key
        :param medal_id:
        :return:
        """
        if medal_id not in self.first_receive_key:
            first_receive_medal_key = '%s_%s' % (medal_id, self.FIRST_RECEIVE_MEDAL)
            self.first_receive_key[medal_id] = ModelTools.make_key_cls(first_receive_medal_key, self._father_server_name)
        return self.first_receive_key[medal_id]

    def set_first_receive_medal(self, medal_id, uid):
        """
        设置首次合成勋章的人
        """
        self.redis.setnx(self.make_first_receive_medal(medal_id), uid)

    def get_first_receive_medal(self, medal_id):
        """
        获取首次合成勋章的人
        :param num:
        :return:
        """
        return self.redis.get(self.make_first_receive_medal(medal_id))

    def delete_first_receive_medal(self, medal_id):
        """
        删除一个首次合成勋章的人
        :return:
        """
        self.redis.delete(self.make_first_receive_medal(medal_id))