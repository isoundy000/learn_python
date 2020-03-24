#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

MESSAGES_LEN = 50

import time
from lib.db import ModelBase

import game_config
from return_msg_config import i18n_msg


class Notify(ModelBase):
    """ 各种邮件通知
    """

    ADD_FRIEND_SORT = 'add_friend'
    SYS_SORT = 'common'

    def __init__(self, uid=None):
        """
        mail = {
            'send_uid': '',
            'send_name': '',
            'send_role': 1,
            'send_level': 1,
            'ts': time.time(),
            'content': u'hello world',
            'sort': 'add_friend',
            'gift': [],
            'icon': '',
            'title': '',
        }
        """
        self.uid = uid
        self._attrs = {
            'messages': {},             # 各种信息
            'charge_log': {},           # 首充奖励信息 记录
            'level_log': {},            # 升级奖励 记录
            'charge_active_log': {}     # 充值奖励 记录
        }
        super(Notify, self).__init__(uid)

    def _generate_custom_notify(self, title, content, gift=None):
        '''
        生成个人邮件
        :param title: 标题
        :param content: 内容
        :param gift: 奖励
        :return:
        '''
        message = {
            'send_uid': 'sys',
            'send_name': 'sys',
            'send_role': 1,
            'send_level': 1,
            'content': content,
            'sort': self.SYS_SORT,
            'gift': [] if gift is None else gift,
            'icon': '',
            'title': title,
        }
        return message

    def add_message(self, message, save=False):
        """添加消息
        args:
            message: 消息内容
            save: 是否保存数据
        """
        if len(self.messages) > MESSAGES_LEN:
            d = sorted(self.messages.iteritems(), key=lambda x: x[1]['ts'])
            for k, v in d[:-MESSAGES_LEN]:
                if v['sort'] != self.SYS_SORT:      # 系统奖励消息还是留着用户手动删除吧
                    self.messages.pop(k)

        ts = int(time.time())
        if message['gift']:
            # 最多取前20个奖励拼接key,以防奖励过多导致key超长
            gift_info = '_'.join(['-'.join(map(str, i)) for i in message['gift'][:20]])
            _id = '%s_%s_%s' % (ts, len(self.messages), gift_info)
        else:
            _id = '%s_%s' % (ts, len(self.messages))
        message['ts'] = ts
        message['id'] = _id
        self.messages[_id] = message
        if save:
            self.save()

    def del_message(self, message_id_list=[], message_id_all=False, save=False):
        """删除消息
        args:
            message_id_list: 消息ID列表
            message_id_all: 是否删除全部
            save: 是否保存数据
        """
        if message_id_all:
            self.messages.clear()
        else:
            for _id in message_id_list:
                self.messages.pop(_id, '')
        if save:
            self.save()

    def send_level_up_gift(self, save=True):
        '''
        发送等级提升奖励邮件
        :param save:
        :return:
        '''
        if not self.weak_user:
            return False
        flag = False
        for v in game_config.level_reward.itervalues():
            if v['need_level'] in self.level_log:
                continue
            if self.weak_user.level >= v['need_level']:
                message = {
                    'send_uid': 'sys',
                    'send_name': 'sys',
                    'send_role': 1,
                    'send_level': 1,
                    'content': v['des'],
                    'sort': self.SYS_SORT,
                    'gift': v['reward'],
                    'icon': v['icon'],
                    'title': v['title'],
                }
                self.level_log[v['need_level']] = int(time.time())
                self.add_message(message, save)
                flag = True
        return flag

    def send_charge_reward(self, save=True):
        '''
        发送充值奖励
        :param save:
        :return:
        '''
        if not self.weak_user:
            return False
        flag = False
        for v in game_config.chargereward.itervalues():
            if v['need_charge'] in self.charge_log:
                continue
            if self.weak_user.vip_exp >= v['need_charge']:
                message = {
                    'send_uid': 'sys',
                    'send_name': 'sys',
                    'send_role': 1,
                    'send_level': 1,
                    'content': v['des'],
                    'sort': self.SYS_SORT,
                    'gift': v['reward'],
                    'icon': v['icon'],
                    'title': v['title'],
                }
                self.charge_log[v['need_charge']] = int(time.time())
                self.add_message(message, save)
                flag = True
        return flag