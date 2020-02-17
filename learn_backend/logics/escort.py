#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lib.db import ModelTools


class Escort(object):

    def __init__(self, user=None):
        if user:
            self.user = user
            self.uid = user.uid
            self.escort = self.user.escort
            self.world_id = user.world_id

    @classmethod
    def can_escort_timer(cls):
        pass


class EscortVehicle(ModelTools):
    """运镖车信息"""
    SERVER_NAME = 'master'

    def __init__(self, captain_uid):
        """
        :param:镖车队长uid
        """
        super(EscortVehicle, self).__init__()
        self.uid = captain_uid
        self._key = self.make_key(captain_uid, server_name=self.SERVER_NAME)
        self.redis = self.get_redis_client(self._key, self.SERVER_NAME)


class LEscortVehicle(object):
    """镖车相关逻辑"""

    def __init__(self, user):
        self.user = user
        self.uid = user.uid
        self.world_id = self.user.world_id
        self.escort = self.user.escort
        self.judge_vehicle_info(self.escort.captain)


    @classmethod
    def timer_arrive(cls, world_id):
        """定时检查是否有飞船抵达"""
        if not Escort.can_escort_timer():
            return


    def judge_vehicle_info(self, captain_uid):
        """判断飞船信息是否存在，不存在就把信息置空
        """
        vehicle_redis = EscortVehicle(captain_uid)
        vehicle_dic = vehicle_redis.get(captain_uid)
        if not vehicle_dic:
            self.escort.captain = ''
            self.escort.save()