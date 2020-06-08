#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from UserDataConfig import UserDataPrepareMap, UserDataMap, UserDataNewUserActivity
from Source.GameOperation.Time.ComputeTimedeltaSeconds import ComputeTimedeltaSeconds
# from UserLastResponse import *
from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.GameData import GameData
from datetime import datetime
from Source.Log.Write import Log
from Source.DataBase.Table.t_role import t_role

RESPONSE_CACHE_NOT_SET = {999990, 999988, 999989, 999904, 999905, 999907}


class UserDataObj(dict):

    def __init__(self):
        dict.__init__(self)
        self["_change"] = []
        self["_changenum"] = 0
        self["_changenum2"] = 0
        self["_delete"] = []
        self["_ext"] = {
            "firstin": True,            # 第一次
            "friend_recommend": {},     # 好友推荐
            "friend_request": {},       # 好友申请
        }
        self["_change_log"] = {}
        self["_delete_log"] = {}
        self["_lastlogin"] = None
        self["_systemtip"] = {"_timer": {}}
        self["_response"] = {}
        self["_response_id_lst"] = []   # 为了限制缓存回应
        self["_session"] = None
        self["__create"] = datetime.now()
        self["__abnormal_num"] = 0
        self["__error_num"] = 0
        self["__lastreq_tick"] = -2
        self["__30tick_req_count"] = 0
        self["__favorite_sum"] = 0
        self["__basic_sync_tick"] = 0
        self["__role_change_num"] = 0
        self["__role_change_num2"] = 0
        self["__visit_num"] = 0
        self["__visit_tick"] = -1
        self["__item_visit_time"] = {}  # 处理在线玩家缓存多余数据
        self["__tag_online"] = False
        self._max_intent_tid = None
        self._liveness_pd = None

    def LoadFirst(self, userid=None, roleid=None):
        '''
        加载数据
        :param userid:
        :param roleid:
        :return:
        '''
        # Log.Write("UserDataObj.LoadFirst", userid, roleid)
        role = None
        if userid:
            role = t_role.LoadUserData(userid)
            Log.Write("from uid userid:", userid, "roleid:", role.id, role)
        if roleid:
            role = t_role.LoadRoleData(roleid)
            if role:
                Log.Write("from rid userid:", role.uid, "roleid:", roleid, "power:", role.power)
        if not role:
            return False
        self["role"] = role
        # if role.profile <= 10100 or role.profile > 10115:   # 头像
        #     role.profile = 10101
        # self.NewUserActivity()
        if role.power == -1:
            role.power = 0
            self.LoadSecond()
            for i in range(1, 8):
                general = self.slot.slot[i]
                if general:
                    role.power += general.power
        return True

    def NewUserActivity(self):
        '''
        新玩家的建角活动
        :return:
        '''
        sec = ComputeTimedeltaSeconds(datetime.now(), self.role.createtime)
        for key, info in UserDataNewUserActivity.iteritems():
            if sec > info[0]:
                continue
            table = info[1]
            self[key] = table.LoadRoleData(self.rid)

    def LoadSecond(self):
        '''二次加载'''
        # Log.Write("UserDataObj.LoadSecond", self.rid)
        # for (key, table) in UserDataPrepareMap.iteritems():
        #     self[key] = table.LoadRoleData(self.rid)
        self.LoadCriticalFromDB()
        self.pet_passive.LoadData(self)
        self.slot_gem.LoadData(self)


    def LoadCriticalFromDB(self):
        '''
        加载重要的数据从数据库中
        :return:
        '''
        Log.Write("[NewCacheM]LoadKeyFromDB", self["__tag_online"])
        if self["__tag_online"]:
            for key, table in UserDataPrepareMap.iteritems():
                self[key] = table.LoadRoleData(self.rid)
        else:
            for (key, table) in UserDataPrepareMap.iteritems():
                if key not in {"general", "equip", "soul"}:
                    self[key] = table.LoadRoleData(self.rid)

            self["general"] = {}
            self["equip"] = {}
            self["soul"] = {}

            general_ids = []
            equip_ids = []
            soul_ids = []

            slot = self["slot"]
            for i in xrange(1, 8):                  # 主战
                gid = slot["s" + str(i)]
                if gid:
                    general_ids.append(gid)

            for i in xrange(1, 9):                  # 助威
                gid = slot["c" + str(i)]
                if gid:
                    general_ids.append(gid)

            self["general"] = UserDataPrepareMap["general"].LoadInIds(general_ids)
            for general in self['general'].values():
                if general:
                    if general.rid == self.rid:
                        if general.weapon:
                            equip_ids.append(general.weapon)
                        if general.armor:
                            equip_ids.append(general.armor)
                        if general.accessory:
                            equip_ids.append(general.accessory)
                        if general.head:
                            equip_ids.append(general.head)
                        if general.treasure:
                            equip_ids.append(general.treasure)
                        if general.horse:
                            equip_ids.append(general.horse)

                        for i in xrange(1, 9):              # 武魂
                            sid = general["s" + str(i)]
                            if sid:
                                soul_ids.append(sid)

            self["equip"] = UserDataPrepareMap["equip"].LoadInIds(equip_ids)
            self["soul"] = UserDataPrepareMap["soul"].LoadInIds(soul_ids)

            # for gid in general_ids:
            #     general = UserDataPrepareMap["general"].LoadByIid(gid)
            #     if general:
            #         if general.rid == self.rid:
            #             if general.weapon:
            #                 equip_ids.append(general.weapon)
            #             if general.armor:
            #                 equip_ids.append(general.armor)
            #             if general.accessory:
            #                 equip_ids.append(general.accessory)
            #             if general.head:
            #                 equip_ids.append(general.head)
            #             if general.treasure:
            #                 equip_ids.append(general.treasure)
            #             if general.horse:
            #                 equip_ids.append(general.horse)
            #
            #             for i in xrange(1, 9):
            #                 sid = general["s" + str(i)]
            #                 if sid:
            #                     soul_ids.append(sid)
            #
            #             self["general"][gid] = general

            # for eid in equip_ids:
            #     equip = UserDataPrepareMap["equip"].LoadByIid(eid)
            #     if equip:
            #         self["equip"][eid] = equip
            #
            # for sid in soul_ids:
            #     soul = UserDataPrepareMap["soul"].LoadByIid(eid)
            #     if soul:
            #         self["soul"][sid] = soul