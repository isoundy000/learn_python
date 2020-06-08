#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import random
import game_config
from lib.utils import weight_choice
from logics.gift import add_gift


class Item(object):

    def __init__(self, user):
        """
        道具类
        """
        self.user = user

    def sell(self, item_id, num):
        pass

    def exchange(self, exchange_id, count):
        """#
        args:
            exchange_id: 兑换id
        """
        exchange_config = game_config.exchange[exchange_id]




def try_replace_box_reward_by_count(user, box_id):
    '''
    开启指定box_id，记录次数，到指定次数给予指定奖励
    :param user:
    :param box_id:
    :return:
    '''
    box_reward_new_config = getattr(game_config, 'box_reward_new', {})
    box_reward = None
    if box_reward_new_config:
        box_reward = box_reward_new_config.get(box_id)
    else:
        if box_id in game_config.BOX_REWARD_BOX_IDS:  # 开宝箱会触发特殊效果的box_id们
            config_key = 'box_reward_%s' % box_id
            box_reward = getattr(game_config, config_key, game_config.box_reward)

    if box_reward:
        new_count = user.item.add_box_use_count(box_id)
        for box_reward_id, data in sorted(box_reward.iteritems()):
            min_count, max_count = data[0]['nums']
            # 比最小的次数还少，直接跳出
            if new_count < min_count:
                break
            # 次数命中
            if min_count <= new_count <= max_count:
                # 记录替换情况
                if box_reward_id not in user.item.get_box_replace_counts(box_id):
                    # 在区间内随机一个值命中
                    rand_count = random.randint(min_count, max_count)
                    if new_count >= rand_count:
                        user.item.add_box_replace_count(box_id, box_reward_id, new_count)
                        return data
                break

    return game_config.box[box_id]
