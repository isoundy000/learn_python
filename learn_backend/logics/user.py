#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime
import weakref
import itertools
import traceback

from lib import utils
from lib.utils.debug import print_log_maker
from lib.utils.debug import print_log as debug_print
import settings
import game_config
from models.user import User as UserM
from models.user import UidServer
from lib.utils import round_float_or_str, generate_rank_score
from lib.utils import get_local_ip


class User(object):
    """# User: 用户类，现在当作所有model的数据容器"""
    @classmethod
    def print_log(cls, *args, **kwargs):
        print_log_maker(2)(*args, **kwargs)

    def __init__(self, uid, user_m_obj=None):
        self.uid = uid
        if user_m_obj is not None:
            self.user_m = user_m_obj
        else:
            self.user_m = UserM.get(uid)
        self._server_name = self.user_m._server_name

        super(User, self).__init__()

    @classmethod
    def get(cls, uid, server_name=''):
        if server_name == 'master' or settings.SERVICE_NAME == 'master':
            # server = UidServer.get(uid).server
            if uid != 'test':
                server = uid[:-7]
            else:
                server = server_name
            user_m = UserM.get(uid, server)
        elif server_name:
            user_m = UserM.get(uid, server_name)
        else:
            user_m = UserM.get(uid)

        o = cls(uid, user_m_obj=user_m)
        # o.countdown()
        return o

    def is_cards_full(self):
        """# is_cards_full: 卡牌包裹是否已满
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return len(self.cards._cards) >= game_config.role[self.level]['character_max'] + self.cards.bag_extend

    def is_equip_full(self):
        """# is_equip_full: 装备包裹是否已满
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return len(self.equip._equip) >= game_config.role[self.level]['equip_max'] + self.equip.bag_extend

    def update_session_and_expired(self, sid, expired):
        """ 更新session和过期时间

        :return:
        """
        if self.sid == sid and self.expired == expired:
            return False

        self.sid = sid
        self.expired = expired
        return True

    def session_expired(self, session):
        """ 检查session是否过期

        :param session:
        :return:
        """
        if self.expired:
            if self.expired < time.time():
                return True
            elif self.sid != session:
                return True
            else:
                return False
        else:
            return True
