#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import datetime
import weakref
import re

from lib import utils
from lib.utils import encoding
from lib.utils.debug import print_log
from lib.utils.time_tools import is_open_from_week
from lib.utils.encoding import force_unicode
from lib.db import ModelBase, ModelTools
import settings
import game_config
from models.user import User as UserM
from lib.utils import salt_generator
from lib.utils import round_float_or_str, generate_rank_score
from return_msg_config import i18n_msg


class AllAssociation(ModelBase):
    """
    工会全部id记录

    @CHANGE LOG:
        assid里工会的id由纯数字改为servername-assid
    """
    ALLASSOCIAATION_ID = 'global_association_id'

    def __init__(self, uid=None):
        """
        记录id
        """
        self.uid = 'global_association_id'
        self._attrs = {
            'ass_id': [],
            'remove_id': [],
            'combined_servers': [],     # 合在一起的服务器server_name列表
        }
        super(AllAssociation, self).__init__(self.uid)

    @staticmethod
    def get(cls, uid="", server_name=""):
        """
        重载父类get
        """
        if not server_name:
            raise TypeError('ERROR, NEED SERVER_NAME')

        father_server_name = settings.get_father_server(server_name)
        if settings.is_combined(server_name):
            # 该服有合服
            # if is_combined_server_changed(father_server_name):
            pass

        return cls.get_obj(server_name=father_server_name)




class Association(ModelBase):

    def __init__(self, uid):
        self.uid = uid
        self._attrs = {

        }
        super(Association, self).__init__(self.uid)

    @classmethod
    def get(cls, a_id, server_name=""):
        if is_new_format(a_id):
            server_name, _ = a_id.split("-")
        else:
            a_id = int(a_id)

        return super(cls, Association).get(a_id, server_name=server_name)


class AssociationLog(ModelBase):
    """# AssociationLog: 公会日志，用于升级记录, uid为工会id"""
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'shop_update_log': {
                # item_id: update_timestamp,
            },
            'levelup_log': {
                # type: [(uid, timestamp)],
            }
        }

        super(AssociationLog, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server_name):
        if is_new_format(uid):
            server_name, _ = uid.split("-")
        return super(cls, AssociationLog).get(uid, server_name)


class AssociationBuyLog(ModelTools):
    """# AssociationLog: 工会日志，主要用于记录各个物品的剩余数量, uid为公会id"""
    def __init__(self, uid, server_name):
        if is_new_format(uid):
            server_name, _ = uid.split("-")

        self.uid = uid      # 工会id
        self._server_name = server_name
        self.redis = self.get_redis_client(uid, server_name)
        super(AssociationBuyLog, self).__init__()


class AssociationUser(ModelBase):
    """# AssociationUser: 用户的工会数据，主要用于购买记录等等"""
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'buy_log': {},  # item_key: buy_amount
            'last_dedicate': 0
        }
        super(AssociationUser, self).__init__(self.uid)

    @classmethod
    def get(cls, uid, server_name=""):
        server_name = cls.get_server_name(uid)
        return super(cls, AssociationUser).get(uid, server_name)


def is_new_format(id):
    '''
    是否是工会id的新格式
    :param id:
    :return:
    '''
    return bool(re.match(r'[a-zA-Z0-9]+\d+-\d+', str(id)))