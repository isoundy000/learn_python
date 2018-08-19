# -*- coding: utf-8 -*-

import time
import os
from sqlalchemy import *

from config import wrapper_database_info

from table.t_gang2 import t_gang2
from table.t_role import t_role
from table.t_role_status import t_role_status
from table.t_role_ext import t_role_ext
from table.Count.t_role_count import t_role_count
from table.t_count import t_count
from table.t_cdkey import t_cdkey
from table.t_vip import t_vip
from table.t_guide import t_guide
from table.t_protagonist import t_protagonist
from table.t_general4 import t_general4
from table.t_equip4 import t_equip4
from table.t_equip_collect import t_equip_collect
from table.t_equip_fragment import t_equip_fragment
from table.t_slot2 import t_slot2
from table.t_pet3 import t_pet3
from table.t_pet_fragment import t_pet_fragment
from table.t_soul2 import t_soul2
from table.t_soul_role import t_soul_role
from table.t_props import t_props
from table.t_general_collect import t_general_collect
from table.t_mail3 import t_mail3
from table.t_recruit_counter import t_recruit_counter
from table.t_recruit_priority import t_recruit_priority
from table.t_shop import t_shop
from table.Log.t_log_giftbag import t_log_giftbag
from table.t_map import t_map
from table.t_copy import t_copy
from table.t_mieshendian import t_mieshendian
from table.t_signin2 import t_signin2
from table.t_invitecode import t_invitecode
from table.Recharge.t_recharge_monthcard import t_recharge_monthcard
from table.Recharge.t_recharge_growplan import t_recharge_growplan
from table.Recharge.t_recharge_growplan_global import t_recharge_growplan_global
from table.t_favorite_general4 import t_favorite_general4
from table.t_favorite_task2 import t_favorite_task2
from table.t_friendcopy import t_friendcopy
from table.t_friendcopy_role import t_friendcopy_role
from table.t_gem import t_gem
from table.t_slot_gem import t_slot_gem
from table.t_general_map import t_general_map
from table.t_general_copy import t_general_copy
from table.t_instrument import t_instrument
from table.t_kingman import t_kingman
from table.t_magicstone import t_magicstone
from table.t_mysteryshop import t_mysteryshop
from table.t_pet3_passiveskill import t_pet3_passiveskill
from table.t_pet3_passiveskill_bag import t_pet3_passiveskill_bag
from table.t_quickslot import t_quickslot
from table.t_recommend import t_recommend
from table.t_task import t_task
from table.t_chat_status import t_chat_status
from table.t_activity_daydaygift import t_activity_daydaygift
from table.t_activity_daydaygift_x1 import t_activity_daydaygift_x1
from table.t_activity_daydaygift_x2 import t_activity_daydaygift_x2
from table.t_activity_rechargegift import t_activity_rechargegift
from table.t_activity_rechargegift_x1 import t_activity_rechargegift_x1
from table.t_activity_rechargegift_x2 import t_activity_rechargegift_x2
from table.t_activity_consumegift import t_activity_consumegift
from table.t_activity_consumegiftx1 import t_activity_consumegiftx1
from table.t_activity_consumegiftx2 import t_activity_consumegiftx2
from table.t_activity_monthfund import t_activity_monthfund
from table.t_activity_mammon import t_activity_mammon
from table.t_activity_mammon_x1 import t_activity_mammon_x1
from table.t_cup2_sign import t_cup2_sign
from table.t_cup2_sign_pet3 import t_cup2_sign_pet3
from table.t_cup2_sign_general import t_cup2_sign_general
from table.t_overpass import t_overpass
from table.t_trial_role import t_trial_role
from table.t_chat_blacklst import t_chat_blacklst
from table.t_spinampwin import t_spinampwin
from table.t_budokai_role import t_budokai_role
from table.t_budokai_ladder import t_budokai_ladder
from table.t_protagonist_fashion import t_protagonist_fashion
from table.t_slot_spirit import t_slot_spirit
from table.t_god_down import t_god_down
from table.t_protagonist_game import t_protagonist_game
from table.t_activity_q import t_activity_q
from table.t_olddriver import t_olddriver
from table.t_gang2_role import t_gang2_role
from table.t_gang2_skill import t_gang2_skill
from table.t_patrol import t_patrol
from table.t_slot_cover import t_slot_cover
from table.t_activity_singlerechargegift1 import t_activity_singlerechargegift1
from table.t_activity_singlerechargegift_new import t_activity_singlerechargegift_new
from table.t_olduser_login import t_olduser_login
from table.t_olduser_mycode import t_olduser_mycode
from table.t_olduser_return import t_olduser_return
from table.WorldWar.t_world_war import t_world_war
from table.WorldWar.t_world_war_battle_reward import t_world_war_battle_reward
from table.WorldWar.t_world_war_weed_reward import t_world_war_weed_reward
from table.WorldWar.t_world_war_bet import t_world_war_bet
from table.WorldWar.t_world_war_sign_role import t_world_war_sign_role
from table.t_cup_point import t_cup_point
from table.t_dividestallcarnival import t_dividestallcarnival
from table.t_general_best import t_general_best
from table.t_time_gift import t_time_gift
from table.t_achievement_limittime import t_achievement_limittime
from table.t_achievement_limittime_c import t_achievement_limittime_c
from table.t_trigger_gift import t_trigger_gift
from table.t_watchstar import t_watchstar
from table.t_turntable import t_turntable
from table.t_integralturntable import t_integralturntable
from table.t_manor import t_manor
from table.t_manor_shop import t_manor_shop
from table.t_activity_totalrecharge import t_activity_totalrecharge
from table.t_rechargerebate import t_rechargerebate
from table.t_recyclebin import t_recyclebin
from table.Recharge.t_recharge_double import t_recharge_double
from table.Recharge.t_recharge_double_rota import t_recharge_double_rota
from table.t_dragonwishing import t_dragonwishing
from table.t_groundhog import t_groundhog
from table.t_role_groundhog import t_role_groundhog
from table.t_october1st import t_october1st
from table.t_october1st_exchange import t_october1st_exchange
from table.t_continue7 import t_continue7
from table.t_limittime_shop import t_limittime_shop
from table.t_activity_recharge_lifetime import t_activity_recharge_lifetime
from table.t_copy_star import t_copy_star
import gc
from table.t_activity_may_first import t_activity_may_first
from table.t_activity_share1 import t_activity_share1
from table.t_activity_startgift import t_activity_startgift
from table.t_baokam import t_baokam
from table.t_begin28days_role import t_begin28days_role
from table.t_begin28days_role_count import t_begin28days_role_count
from table.t_begin28days_exchange import t_begin28days_exchange
from table.t_blackmarket import t_blackmarket
from table.t_brave_copy import t_brave_copy
from table.t_brave_map import t_brave_map
from table.t_checkerboard import t_checkerboard
from table.t_christmas import t_christmas
from table.t_cornucopia import t_cornucopia
from table.t_deep_map import t_deep_map
from table.t_deep_copy import t_deep_copy
from table.t_deep_copy_star import t_deep_copy_star
from table.t_exchange_sys import t_exchange_sys
from table.t_expedition2 import t_expedition2
from table.t_favor2_buf import t_favor2_buf
from table.t_gemdiscount_shop import t_gemdiscount_shop
from table.t_gemdiscount_shop1 import t_gemdiscount_shop1
from table.t_gemdiscount_shop2 import t_gemdiscount_shop2
from table.t_gemdiscount_shop3 import t_gemdiscount_shop3
from table.t_god_down_x6 import t_god_down_x6
from table.t_god_general import t_god_general
from table.t_intent import t_intent
from table.t_legendary import t_legendary
from table.t_limittimeexchange import t_limittimeexchange
from table.t_limittimeexchange_itemcount import t_limittimeexchange_itemcount
from table.t_limittimeexchangenew import t_limittimeexchangenew
from table.t_mid_autumn import t_mid_autumn
from table.t_olddriverx1 import t_olddriverx1
from table.t_protagonist_wingcolor import t_protagonist_wingcolor
from table.t_recharge_rebate_st import t_recharge_rebate_st
from table.t_resourcesrec import t_resourcesrec
from table.t_resourcesrec_count import t_resourcesrec_count
from table.t_role_avatar import t_role_avatar
from table.t_top_of_world_role import t_top_of_world_role
from table.t_top_of_world_role_count import t_top_of_world_role_count
from table.t_top_of_world_role_exchange import t_top_of_world_role_exchange
from table.t_zodiac_new import t_zodiac_new
from table.t_activity_dragon_ball_shop import *
from table.t_activity_wish_tree import t_activity_wish_tree
from table.t_activity_wish_tree_shop import t_activity_wish_tree_shop
from table.t_activity_wish_tree_shop_w import t_activity_wish_tree_shop_w
from table.t_activity_wish_tree_w import t_activity_wish_tree_w
from table.t_facebook import t_facebook
from table.t_firsthint import t_firsthint
from table.t_task_lately import t_task_lately


class RoleMerge(object):
    def __init__(self, config):
        self.config = config

        self.execute_count = 0

        self.general_increment = 0
        self.equip_increment = 0
        self.soul_increment = 0
        self.pet_increment = 0
        self.mail_increment = 0
        self.gem_increment = 0

        self.orm_objects = []


    def __del__(self):
        self.config = None
        self.orm_objects.clear()

    def run(self):
        # 读取有自增长id数据表的自增长达到数值
        self._init_increment()

        # total_role = 0
        # for database in self.config.src_databases:
        #     total_role += len(self.get_role_ids(database))

        count = 0
        for database in self.config.src_databases:
            for role_id in self.get_role_ids(database):
                count += 1
                self._dispose(database, role_id)
                if count % 100 == 0:
                    self._dump_orm_objects()

                    # # 推送合服进度
                    # pre = int(count*1.0/total_role*100)
                    # if pre == 100:
                    #     pre = 99
                    # print ("[Speed of progress]_______:%s%%" % pre)
                    # try:
                    #     url = self.config.status_url + str(pre)
                    #     os.system("curl \"%s\"" % url)
                    # except:
                    #     print "[Error] url is Error"

        self._dump_orm_objects()

        for database in self.config.src_databases:
            for role_id in self.get_role_ids(database):
                self._merge_chat_blacklst(database, role_id)
        self._dump_orm_objects()

    def _init_increment(self):
        for status in self.config.dst_database.session.execute("""SHOW TABLE STATUS;"""):
            table_name = status[0]
            table_increment = status[10]
            if table_name == 't_general4':
                self.general_increment = table_increment
            elif table_name == 't_equip4':
                self.equip_increment = table_increment
            elif table_name == 't_soul':
                self.soul_increment = table_increment
            elif table_name == 't_pet3':
                self.pet_increment = table_increment
            elif table_name == 't_mail3':
                self.mail_increment = table_increment
            elif table_name == 't_gem':
                self.gem_increment = table_increment

    def _dump_orm_objects(self):
        print("clear orm objects start: %d" % len(self.orm_objects))
        t1 = time.time()
        for orm_object in self.orm_objects:
            self.config.dst_database.session.add(orm_object)
        self.config.dst_database.session.commit()
        self.orm_objects = []
        del self.orm_objects
        self.orm_objects = []
        gc.collect()
        t2 = time.time()
        print("clear orm objects end: %ds" % (t2 - t1))

    def get_role_ids(self, database):
        ids = set()
        session = database.session

        # 筛选出符合要求的合服rid
        dt = self.config.role_filter_login_datetime
        role_ids = set(filter(lambda r: r > 0, map(lambda r: r[0],
                                                   session.execute(
                                                       """select r.id from t_role r, t_vip v where r.uid > 0 and r.id = v.rid and (r.level >= %d or v.rmb > 3000 or r.lastlogin > '%s');""" % (
                                                       self.config.role_filter_level, dt))
                                                   )))
        ids.update(role_ids)
        # ids.update(list(role_ids)[:1])
        # ids.update([23001521])

        # 筛选出未会长或副会长的rid
        gang_ids = set(filter(lambda r: r > 0, map(lambda r: r[0], session
                                                   .query(t_role.id)
                                                   .filter(or_(t_gang2.rid == t_role.id,
                                                               t_gang2.rid1 == t_role.id,
                                                               t_gang2.rid2 == t_role.id,
                                                               t_gang2.rid3 == t_role.id,
                                                               t_gang2.optparam == t_role.id))
                                                   .all())))
        ids.update(gang_ids)

        # 筛选出跨服战报名的rid
        world_sign_ids = set(
            filter(lambda r: r > 0, map(lambda r: r[0], session.query(t_world_war_sign_role.rid).all())))
        ids.update(world_sign_ids)

        # TODO筛选出竞拍的rid
        # pass

        print('%s roles %d' % (database.identifier, len(ids)))
        return ids

    def _dispose(self, database, role_id):
        role = database.session.query(t_role).filter(t_role.id == role_id).first()
        self._merge(wrapper_database_info(database, role))

    def _merge_chat_blacklst(self, database, rid):
        chat_blacklsts = database.session.query(t_chat_blacklst).filter(t_chat_blacklst.rid == rid).all()

        new_rid = self.config.role_merge_maps.get_new_id(database.identifier, rid)
        # 聊天黑名单
        for chat_blacklst in chat_blacklsts:
            new_oid = self.config.role_merge_maps.get_new_id(database.identifier, chat_blacklst.oid)
            if not new_oid:
                continue
            new_chat_blacklst = t_chat_blacklst.new_from(chat_blacklst)
            new_chat_blacklst.rid = new_rid
            new_chat_blacklst.oid = new_oid
            self.orm_objects.append(new_chat_blacklst)

    def _merge(self, database_role):
        t1 = time.time()

        self.execute_count += 1
        database = database_role.database
        role = database_role.data
        # 将久的玩家对象赋值到一个新的玩家对象
        new_role = t_role.new_from(role)

        # 重赋值一个新的rid
        new_role_id = role.id
        if database.server_id != 0:
            new_role_id += database.server_id * self.config.server_id_step
        new_role.id = new_role_id

        # 查询rid关联表格
        protagonist = database.session.query(t_protagonist).filter(t_protagonist.id == role.id).first()
        generals = database.session.query(t_general4).filter(t_general4.rid == role.id).all()
        equips = database.session.query(t_equip4).filter(t_equip4.rid == role.id).all()
        souls = database.session.query(t_soul2).filter(t_soul2.rid == role.id).all()
        pets = database.session.query(t_pet3).filter(t_pet3.rid == role.id).all()
        passiveskill_bags = database.session.query(t_pet3_passiveskill_bag).filter(t_pet3_passiveskill_bag.rid == role.id).all()
        slot = database.session.query(t_slot2).filter(t_slot2.rid == role.id).first()
        mails = database.session.query(t_mail3).filter(and_(t_mail3.rid == role.id, t_mail3.status != "get")).all()
        gems = database.session.query(t_gem).filter(t_gem.rid == role.id).all()
        slot_gem = database.session.query(t_slot_gem).filter(t_slot_gem.rid == role.id).first()
        quickslots = database.session.query(t_quickslot).filter(t_quickslot.rid == role.id).all()
        cup2_sign = database.session.query(t_cup2_sign).filter(t_cup2_sign.rid == role.id).first()
        cup2_sign_generals = database.session.query(t_cup2_sign_general).filter(
            t_cup2_sign_general.rid == role.id).all()
        cup2_sign_pet3s = database.session.query(t_cup2_sign_pet3).filter(t_cup2_sign_pet3.rid == role.id).all()

        # 用户状态记录
        self._single_merge(database, t_role_status, role, new_role)
        # 用户扩展信息
        self._single_merge(database, t_role_ext, role, new_role)
        self._single_merge(database, t_role_count, role, new_role)
        self._single_merge(database, t_count, role, new_role)
        # cdkey领取
        self._single_merge(database, t_cdkey, role, new_role)
        # vip
        self._single_merge(database, t_vip, role, new_role)
        # 引导
        self._multi_merge(database, t_guide, role, new_role)
        # 装备
        for equip in equips:
            new_equip = t_equip4.new_from(equip)
            self.equip_increment += 1
            new_equip.id = self.equip_increment
            new_equip.rid = new_role.id
            self.orm_objects.append(new_equip)
            self.config.equip_merge_maps.add(database.identifier, equip.id, new_equip.id)
        # 装备图鉴
        self._multi_merge(database, t_equip_collect, role, new_role)
        # 装备碎片
        self._multi_merge(database, t_equip_fragment, role, new_role)
        # 命格
        for soul in souls:
            new_soul = t_soul2.new_from(soul)
            self.soul_increment += 1
            new_soul.id = self.soul_increment
            new_soul.rid = new_role.id
            self.orm_objects.append(new_soul)
            self.config.soul_merge_maps.add(database.identifier, soul.id, new_soul.id)
        # 命格属性
        self._single_merge(database, t_soul_role, role, new_role)
        # 角色
        for general in generals:
            new_general = t_general4.new_from(general)
            self.general_increment += 1
            new_general.id = self.general_increment
            new_general.rid = new_role.id
            self.orm_objects.append(new_general)
            self.config.general_merge_maps.add(database.identifier, general.id, new_general.id)
            # 主角
            if protagonist and protagonist.iid == general.id:
                new_protagonist = t_protagonist.new_from(protagonist)
                new_protagonist.id = new_role.id
                new_protagonist.iid = new_general.id
                self.orm_objects.append(new_protagonist)
            # 关联的装备
            for i in ['weapon', 'armor', 'accessory', 'head', 'treasure', 'horse']:
                if getattr(general, i):
                    setattr(new_general, i,
                            self.config.equip_merge_maps.get_new_id(database.identifier, getattr(general, i)))
            # 关联的命格
            for i in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']:
                if getattr(general, i):
                    setattr(new_general, i,
                            self.config.soul_merge_maps.get_new_id(database.identifier, getattr(general, i)))
        # 武将魂魄
        self._multi_merge(database, t_general_collect, role, new_role)
        # 宠物
        for pet in pets:
            new_pet = t_pet3.new_from(pet)
            self.pet_increment += 1
            new_pet.id = self.pet_increment
            new_pet.rid = new_role.id
            self.orm_objects.append(new_pet)
            self.config.pet_merge_maps.add(database.identifier, pet.id, new_pet.id)
        # 宠物魂魄
        self._multi_merge(database, t_pet_fragment, role, new_role)
        # 阵容
        if slot:
            new_slot = t_slot2.new_from(slot)
            new_slot.rid = new_role.id
            self.orm_objects.append(new_slot)
            for i in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']:
                if getattr(slot, i):
                    setattr(new_slot, i,
                            self.config.general_merge_maps.get_new_id(database.identifier, getattr(slot, i)))
            if slot.p1:
                new_slot.p1 = self.config.pet_merge_maps.get_new_id(database.identifier, slot.p1)

        for passiveskill_bag in passiveskill_bags:
            new_passiveskill_bag = t_pet3_passiveskill_bag.new_from(passiveskill_bag)
            new_passiveskill_bag.rid = new_role.id
            new_passiveskill_bag.petid = self.config.pet_merge_maps.get_new_id(database.identifier, passiveskill_bag.petid)
            self.orm_objects.append(new_passiveskill_bag)

        # 道具
        self._multi_merge(database, t_props, role, new_role)
        # 邮件
        for mail in mails:
            if not mail.attachment or mail.status == "get":
                continue
            new_mail = t_mail3.new_from(mail)
            self.mail_increment += 1
            new_mail.id = self.mail_increment
            new_mail.rid = new_role.id
            self.orm_objects.append(new_mail)
            self.config.mail_merge_maps.add(database.identifier, mail.id, new_mail.id)
        # 武将招募计数器
        self._multi_merge(database, t_recruit_counter, role, new_role)
        # 武将招募计数权重
        self._multi_merge(database, t_recruit_priority, role, new_role)
        # 商城
        self._single_merge(database, t_shop, role, new_role)
        # 礼包
        self._multi_merge(database, t_log_giftbag, role, new_role)
        # 普通副本地图
        self._multi_merge(database, t_map, role, new_role)
        # 普通副本据点
        self._multi_merge(database, t_copy, role, new_role)
        # 竞技场角色信息
        # 灭神殿
        self._single_merge(database, t_mieshendian, role, new_role)
        # 签到
        self._single_merge(database, t_signin2, role, new_role)
        # 邀请码
        self._single_merge(database, t_invitecode, role, new_role)
        # 月卡
        self._single_merge(database, t_recharge_monthcard, role, new_role)
        # 成长计划
        self._single_merge(database, t_recharge_growplan, role, new_role)
        self._single_merge(database, t_recharge_growplan_global, role, new_role)
        # 客栈
        self._multi_merge(database, t_favorite_general4, role, new_role)
        # 客栈成就
        self._multi_merge(database, t_favorite_task2, role, new_role)
        # 好友副本
        self._multi_merge(database, t_friendcopy, role, new_role)
        # 好友副本计数
        self._single_merge(database, t_friendcopy_role, role, new_role)
        # 魔符
        for gem in gems:
            new_gem = t_gem.new_from(gem)
            self.gem_increment += 1
            new_gem.id = self.gem_increment
            new_gem.rid = new_role.id
            self.orm_objects.append(new_gem)
            self.config.gem_merge_maps.add(database.identifier, gem.id, new_gem.id)

        # 魔符阵位信息
        if slot_gem:
            new_slot = t_slot_gem.new_from(slot_gem)
            new_slot.rid = new_role.id
            for i in range(1, 9):
                for j in range(1, 5):
                    attr_name = 's%d%d' % (i, j)
                    old_gem_id = getattr(slot_gem, attr_name)
                    if not old_gem_id:
                        continue
                    new_gem_id = self.config.gem_merge_maps.get_new_id(database.identifier, old_gem_id)
                    setattr(new_slot, attr_name, new_gem_id)
            self.orm_objects.append(new_slot)

        # 名将副本地图
        self._multi_merge(database, t_general_map, role, new_role)
        # 名将副本据点
        self._multi_merge(database, t_general_copy, role, new_role)
        # 法宝
        self._multi_merge(database, t_instrument, role, new_role)
        # 王的男人
        self._multi_merge(database, t_kingman, role, new_role)
        # 神石
        self._multi_merge(database, t_magicstone, role, new_role)
        # 神魂商店
        self._single_merge(database, t_mysteryshop, role, new_role)
        # 神魂商店限制购买次数
        # self._multi_merge(database, t_mysteryshop_itemcount, role, new_role)
        # 魔宠被动技能
        self._single_merge(database, t_pet3_passiveskill, role, new_role)
        # 王的男人布阵
        for quickslot in quickslots:
            if quickslot:
                new_quickslot = t_quickslot.new_from(quickslot)
                new_quickslot.rid = new_role.id
                for i in ['s1', 's2', 's3', 's4', 's5', 's6', 's7']:
                    if getattr(quickslot, i):
                        setattr(new_quickslot, i,
                                self.config.general_merge_maps.get_new_id(database.identifier, getattr(quickslot, i)))
                if slot.p1:
                    new_quickslot.p1 = self.config.pet_merge_maps.get_new_id(database.identifier, quickslot.p1)
                self.orm_objects.append(new_quickslot)
        # 阵容推荐
        self._single_merge(database, t_recommend, role, new_role)
        # 成就
        self._multi_merge(database, t_task, role, new_role)
        self._multi_merge(database, t_task_lately, role, new_role)

        # 禁言
        self._single_merge(database, t_chat_status, role, new_role)
        # 天天好礼
        self._single_merge(database, t_activity_daydaygift, role, new_role)
        self._single_merge(database, t_activity_daydaygift_x1, role, new_role)
        self._single_merge(database, t_activity_daydaygift_x2, role, new_role)
        # 累计充值
        self._single_merge(database, t_activity_rechargegift, role, new_role)
        self._single_merge(database, t_activity_rechargegift_x1, role, new_role)
        self._single_merge(database, t_activity_rechargegift_x2, role, new_role)
        # 消费有礼
        self._single_merge(database, t_activity_consumegift, role, new_role)
        self._single_merge(database, t_activity_consumegiftx1, role, new_role)
        self._single_merge(database, t_activity_consumegiftx2, role, new_role)
        # 月基金 基金福利
        self._single_merge(database, t_activity_monthfund, role, new_role)
        # 迎财神
        self._single_merge(database, t_activity_mammon, role, new_role)
        self._single_merge(database, t_activity_mammon_x1, role, new_role)
        # 杯赛
        cup2_orm_objects = []
        cup2_is_ok = True
        if cup2_is_ok:
            for cup2_sign_general in cup2_sign_generals:
                new_cup2_sign_general = t_cup2_sign_general.new_from(cup2_sign_general)
                new_general_id = self.config.general_merge_maps.get_new_id(database.identifier, cup2_sign_general.id)
                if not new_general_id:
                    cup2_is_ok = False
                    break
                new_cup2_sign_general.id = new_general_id
                new_cup2_sign_general.rid = new_role.id
                cup2_orm_objects.append(new_cup2_sign_general)
                self.config.cup2_general_merge_maps.add(database.identifier, cup2_sign_general.id,
                                                        new_cup2_sign_general.id)
        if cup2_is_ok:
            for cup2_sign_pet3 in cup2_sign_pet3s:
                new_cup2_sign_pet3 = t_cup2_sign_pet3.new_from(cup2_sign_pet3)
                new_pet_id = self.config.pet_merge_maps.get_new_id(database.identifier, cup2_sign_pet3.id)
                if not new_pet_id:
                    cup2_is_ok = False
                    break
                new_cup2_sign_pet3.id = new_pet_id
                new_cup2_sign_pet3.rid = new_role.id
                cup2_orm_objects.append(new_cup2_sign_pet3)
                self.config.cup2_pet3_merge_maps.add(database.identifier, cup2_sign_pet3.id, new_cup2_sign_pet3.id)
        if cup2_is_ok and cup2_sign:
            new_cup2_sign = t_cup2_sign.new_from(cup2_sign)
            new_cup2_sign.rid = new_role.id
            for i in xrange(1, 8):
                for j in ['s', 'c']:
                    attr_name = '%s%d' % (j, i)
                    if getattr(cup2_sign, attr_name):
                        setattr(new_cup2_sign, attr_name,
                                self.config.cup2_general_merge_maps.get_new_id(database.identifier,
                                                                               getattr(cup2_sign, attr_name)))
            if cup2_sign.p1:
                new_cup2_sign.p1 = self.config.cup2_pet3_merge_maps.get_new_id(database.identifier, cup2_sign.p1)
                cup2_orm_objects.append(new_cup2_sign)
        if cup2_is_ok:
            self.orm_objects.extend(cup2_orm_objects)
        else:
            print('rid:%d: give up cup' % new_role.id)
        # 过关斩将
        self._single_merge(database, t_overpass, role, new_role)
        # 冠军试炼
        self._single_merge(database, t_trial_role, role, new_role)
        # 老虎机
        self._single_merge(database, t_spinampwin, role, new_role)

        # 武道会
        self._single_merge(database, t_budokai_role, role, new_role)
        # 武道会段位奖励
        self._single_merge(database, t_budokai_ladder, role, new_role)
        # 时装
        self._multi_merge(database, t_protagonist_fashion, role, new_role)
        # 灵阵图
        self._single_merge(database, t_slot_spirit, role, new_role)
        # 天神下凡(八戒美梦)
        self._single_merge(database, t_god_down, role, new_role)
        # 魔王游戏厅
        self._single_merge(database, t_protagonist_game, role, new_role)
        # 喷他Q商店
        self._single_merge(database, t_activity_q, role, new_role)
        # 老司机
        self._single_merge(database, t_olddriver, role, new_role)
        # 工会信息
        self._single_merge(database, t_gang2_role, role, new_role)
        # 工会技能
        self._single_merge(database, t_gang2_skill, role, new_role)
        # 天庭银座
        patrols = database.session.query(t_patrol).filter(t_patrol.rid == role.id).all()
        for patrol in patrols:
            new_patrol = patrol.new_from(patrol)
            new_patrol.rid = new_role.id
            new_patrol.gid = self.config.general_merge_maps.get_new_id(database.identifier, patrol.gid)
            self.orm_objects.append(new_patrol)
        # 魔罩
        self._single_merge(database, t_slot_cover, role, new_role)
        # 单笔充值
        self._single_merge(database, t_activity_singlerechargegift1, role, new_role)
        self._single_merge(database, t_activity_singlerechargegift_new, role, new_role)


        # 老用户回归
        self._single_merge(database, t_olduser_login, role, new_role)
        self._single_merge(database, t_olduser_mycode, role, new_role)
        self._single_merge(database, t_olduser_return, role, new_role)
        # 杯赛积分
        self._single_merge(database, t_cup_point, role, new_role)
        # 跨服战
        self._single_merge(database, t_world_war, role, new_role)
        self._multi_merge(database, t_world_war_battle_reward, role, new_role)
        self._multi_merge(database, t_world_war_weed_reward, role, new_role)
        self._multi_merge(database, t_world_war_bet, role, new_role)
        # 武将精华
        self._multi_merge(database, t_general_best, role, new_role)
        # 周礼包 月礼包
        self._single_merge(database, t_time_gift, role, new_role)
        # 限时成就
        self._single_merge(database, t_achievement_limittime, role, new_role)
        self._single_merge(database, t_achievement_limittime_c, role, new_role)
        # 触发礼包
        self._multi_merge(database, t_trigger_gift, role, new_role)
        # 观星台
        self._single_merge(database, t_watchstar, role, new_role)
        # 限时红装
        self._single_merge(database, t_turntable, role, new_role)
        # 分档大转盘
        self._single_merge(database, t_dividestallcarnival, role, new_role)
        # # 积分抽奖
        self._single_merge(database, t_integralturntable, role, new_role)
        # 庄园
        self._single_merge(database, t_manor, role, new_role)
        # 庄园商店
        self._single_merge(database, t_manor_shop, role, new_role)
        # 累充2
        self._single_merge(database, t_activity_totalrecharge, role, new_role)
        # 充值消费返利
        self._single_merge(database, t_rechargerebate, role, new_role)
        # 乾坤炉默认品质
        self._single_merge(database, t_recyclebin, role, new_role)
        # 多倍充值、复制多倍充值
        self._single_merge(database, t_recharge_double, role, new_role)
        self._single_merge(database, t_recharge_double_rota, role, new_role)
        # 神龙许愿
        self._single_merge(database, t_dragonwishing, role, new_role)
        # 打地鼠
        self._single_merge(database, t_groundhog, role, new_role)
        self._single_merge(database, t_role_groundhog, role, new_role)
        # 十一狂欢
        self._single_merge(database, t_october1st, role, new_role)
        self._single_merge(database, t_october1st_exchange, role, new_role)
        # 连续登陆
        self._single_merge(database, t_continue7, role, new_role)
        # 限时商店
        self._single_merge(database, t_limittime_shop, role, new_role)
        # 永久充值
        self._single_merge(database, t_activity_recharge_lifetime, role, new_role)
        # 副本星数排行榜
        self._single_merge(database, t_copy_star, role, new_role)
        # 五一活动
        self._single_merge(database, t_activity_may_first, role, new_role)
        # 分享活动
        self._single_merge(database, t_activity_share1, role, new_role)
        # 风月宝鉴
        self._single_merge(database, t_baokam, role, new_role)
        # 创角28日活动
        self._multi_merge(database, t_begin28days_role, role, new_role)
        self._single_merge(database, t_begin28days_role_count, role, new_role)
        self._single_merge(database, t_begin28days_exchange, role, new_role)
        # 黑市
        self._single_merge(database, t_blackmarket, role, new_role)
        # brave_copy
        self._multi_merge(database, t_brave_copy, role, new_role)
        self._multi_merge(database, t_brave_map, role, new_role)
        # 棋盘
        self._single_merge(database, t_checkerboard, role, new_role)
        # 圣诞节
        self._single_merge(database, t_christmas, role, new_role)
        # cornucopia
        self._single_merge(database, t_cornucopia, role, new_role)
        # 深渊副本
        self._multi_merge(database, t_deep_map, role, new_role)
        self._multi_merge(database, t_deep_copy, role, new_role)
        self._single_merge(database, t_deep_copy_star, role, new_role)
        # exchange_sys
        self._single_merge(database, t_exchange_sys, role, new_role)
        # expedition2
        self._multi_merge(database, t_expedition2, role, new_role)
        # 花坊
        self._multi_merge(database, t_favor2_buf, role, new_role)
        # gemdiscount_shop
        self._single_merge(database, t_gemdiscount_shop, role, new_role)
        self._single_merge(database, t_gemdiscount_shop1, role, new_role)
        self._single_merge(database, t_gemdiscount_shop2, role, new_role)
        self._single_merge(database, t_gemdiscount_shop3, role, new_role)
        # 三档八戒圆梦
        self._single_merge(database, t_god_down_x6, role, new_role)
        # 限时神将
        # self._single_merge(database, t_god_general, role, new_role)
        # 目标
        self._multi_merge(database, t_intent, role, new_role)
        # 一拳超神
        # self._single_merge(database, t_legendary, role, new_role)
        # 限时兑换
        self._single_merge(database, t_limittimeexchange, role, new_role)
        self._multi_merge(database, t_limittimeexchange_itemcount, role, new_role)
        self._single_merge(database, t_limittimeexchangenew, role, new_role)
        # 中秋
        self._single_merge(database, t_mid_autumn, role, new_role)
        # 老司机
        self._single_merge(database, t_olddriverx1, role, new_role)
        # 主角翅膀颜色
        self._single_merge(database, t_protagonist_wingcolor, role, new_role)
        # 充值消费返利
        self._single_merge(database, t_recharge_rebate_st, role, new_role)
        # 资源找回
        self._multi_merge(database, t_resourcesrec, role, new_role)
        self._multi_merge(database, t_resourcesrec_count, role, new_role)
        # 玩家头像
        self._multi_merge(database, t_role_avatar, role, new_role)
        # 走向巅峰
        self._multi_merge(database, t_top_of_world_role, role, new_role)
        self._single_merge(database, t_top_of_world_role_count, role, new_role)
        self._single_merge(database, t_top_of_world_role_exchange, role, new_role)
        # 十二生肖
        self._multi_merge(database, t_zodiac_new, role, new_role)
        # 未知活动
        self._single_merge(database, t_activity_startgift, role, new_role)

        # 龙珠兑换
        self._single_merge(database, t_activity_dragon_ball_shop, role, new_role)

        # 许愿树
        self._single_merge(database, t_activity_wish_tree, role, new_role)
        self._single_merge(database, t_activity_wish_tree_shop, role, new_role)
        self._single_merge(database, t_activity_wish_tree_shop_w, role, new_role)
        self._single_merge(database, t_activity_wish_tree_w, role, new_role)

        # facebook
        self._single_merge(database, t_facebook, role, new_role)

        # t_firsthint
        self._single_merge(database, t_firsthint, role, new_role)



        # 空名处理
        if not new_role.name or not new_role.name.strip():
            new_role.name = str(new_role.id)
            print('none name rid:%d' % new_role.id)

        self.orm_objects.append(new_role)
        self.config.role_merge_maps.add(database.identifier, role.id, new_role.id)

        self.config.dst_database.session.commit()

        t2 = time.time()
        print("%d time:%f database:%s uid:%d old_rid:%d new_rid:%d" % (self.execute_count, (t2 - t1), database.identifier, role.uid, role.id, new_role.id))

    # 处理单一对应套路模式数据表
    def _single_merge(self, database, table, role, new_role):
        obj = database.session.query(table).filter(table.rid == role.id).first()
        if obj:
            new_obj = table.new_from(obj)
            new_obj.rid = new_role.id
            self.orm_objects.append(new_obj)

    # 处理多条对应套路模式数据表
    def _multi_merge(self, database, table, role, new_role):
        objs = database.session.query(table).filter(table.rid == role.id).all()
        for obj in objs:
            new_obj = table.new_from(obj)
            new_obj.rid = new_role.id
            self.orm_objects.append(new_obj)
