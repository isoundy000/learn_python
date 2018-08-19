# -*- coding: utf-8 -*-

import time
import traceback

from table.t_role import t_role
from table.t_mail3 import t_mail3
from table.t_ktv import t_ktv
from table.t_worldboss1 import t_worldboss1
from table.t_worldboss2 import t_worldboss2
from table.Log.t_log_getgold import t_log_getgold
from table.Log.t_log_usegold import t_log_usegold
import gc

class UtilsMerge(object):
    def __init__(self, config):
        self.config = config

        self.mail_increment = 0
        self.orm_objects = []

    def __del__(self):
        self.config = None
        self.orm_objects.clear()

    def run(self):
        # # 合服后邮件主键索引
        # self._init_increment()
        # # 合服后发送邮件
        # self._dispose_rename_mail()
        # 成长计划统计/限时红装
        self._dispose_ktv()
        try:
            # 世界BOSS统计
            self._dispose_worldboss()
        except Exception, e:
            traceback.print_exc()
        try:
            # 元宝消耗统计
            self._dispose_log()
        except Exception, e:
            traceback.print_exc()

    def _init_increment(self):
        for status in self.config.dst_database.session.execute("""SHOW TABLE STATUS;"""):
            table_name = status[0]
            table_increment = status[10]
            if table_name == 't_mail3':
                self.mail_increment = table_increment

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

    def _dispose_rename_mail(self):
        def send_rename_card_mail(rid):
            mail = t_mail3()
            self.mail_increment += 1
            mail.id = self.mail_increment
            mail.rid = rid
            mail.source = 0
            mail.type = "system"
            mail.status = "no"
            # mail.title = "合服奖励"
            # mail.content = "为了让您合服后更好的体验游戏，特奖励改名卡一张，请查收！"
            mail.title = "Cross Server Reward"
            mail.content = "Get 1 Rename card after cross server"
            mail.attachment = """{"20018":1}"""
            self.orm_objects.append(mail)

        roles = self.config.dst_database.session.query(t_role).all()
        for role in roles:
            rid = role.id
            send_rename_card_mail(rid)
                
        self._dump_orm_objects()
        gc.collect()
    def _dispose_ktv(self):

        # 限时红装
        turntable_list = []

        recharge_growplan_total = 0
        recharge_growplan_total_2 = 0
        for src_database in self.config.src_databases + [self.config.dst_database]:
            ktv_recharge_growplan_total = src_database.session.query(t_ktv).filter(t_ktv.key == 'recharge_growplan_total').first()
            ktv_recharge_growplan_total_2 = src_database.session.query(t_ktv).filter(t_ktv.key == 'recharge_growplan_total_2').first()
            # if ktv_recharge_growplan_total and ktv_recharge_growplan_total_2 and ktv_recharge_growplan_total.value and ktv_recharge_growplan_total_2.value:
            #     recharge_growplan_total += max(int(ktv_recharge_growplan_total.value), int(ktv_recharge_growplan_total_2.value))
            #     recharge_growplan_total_2 += min(int(ktv_recharge_growplan_total.value), int(ktv_recharge_growplan_total_2.value))
            value = 0
            value2 = 0
            if ktv_recharge_growplan_total and ktv_recharge_growplan_total.value:
                value = int(ktv_recharge_growplan_total.value)
            if ktv_recharge_growplan_total_2 and ktv_recharge_growplan_total_2.value:
                value2 = int(ktv_recharge_growplan_total_2.value)
            recharge_growplan_total += max(value, value2)
            recharge_growplan_total_2 += min(value, value2)
            # value = 0
            # value2 = 0
            # if ktv_recharge_growplan_total and ktv_recharge_growplan_total.value:
            #     value = int(ktv_recharge_growplan_total.value)
            # if ktv_recharge_growplan_total_2 and ktv_recharge_growplan_total_2.value:
            #     value = int(ktv_recharge_growplan_total_2.value)
            # if value2 == 0:
            #     value2 = value
            # recharge_growplan_total += max(value, value2)
            # recharge_growplan_total_2 += min(value, value2)

            # 限时红装
            turntableData = src_database.session.query(t_ktv).filter(t_ktv.key == 'turntable').first()
            if turntableData and turntableData.value:
                turntable_list.append(turntableData.value)

        new_ktv_recharge_growplan_total = t_ktv()
        new_ktv_recharge_growplan_total.type = 'int'
        new_ktv_recharge_growplan_total.key = 'recharge_growplan_total'
        new_ktv_recharge_growplan_total.value = recharge_growplan_total
        new_ktv_recharge_growplan_total.value = min(new_ktv_recharge_growplan_total.value, 9999)
        self.config.dst_database.session.merge(new_ktv_recharge_growplan_total)

        new_ktv_recharge_growplan_total_2 = t_ktv()
        new_ktv_recharge_growplan_total_2.type = 'int'
        new_ktv_recharge_growplan_total_2.key = 'recharge_growplan_total_2'
        new_ktv_recharge_growplan_total_2.value = recharge_growplan_total_2
        new_ktv_recharge_growplan_total_2.value = min(new_ktv_recharge_growplan_total_2.value, 9999)
        self.config.dst_database.session.merge(new_ktv_recharge_growplan_total_2)

        if turntable_list:
            new_ktv_turntable = t_ktv()
            new_ktv_turntable.type = 'int'
            new_ktv_turntable.key = 'turntable'
            new_ktv_turntable.value = max(turntable_list)
            self.config.dst_database.session.merge(new_ktv_turntable)

        self.config.dst_database.session.commit()
        gc.collect()

    def _dispose_worldboss(self):
        new_worldboss1 = None
        for src_database in self.config.src_databases + [self.config.dst_database]:
            worldboss1 = src_database.session.query(t_worldboss1).first()
            if new_worldboss1 and worldboss1:
                if worldboss1.level <= new_worldboss1.level:
                    new_worldboss1 = worldboss1.new_from(worldboss1)
            if not new_worldboss1 and worldboss1:
                new_worldboss1 = t_worldboss1.new_from(worldboss1)
        if new_worldboss1:
            self.config.dst_database.session.merge(new_worldboss1)
            self.config.dst_database.session.commit()
        gc.collect()
        new_worldboss2 = None
        for src_database in self.config.src_databases + [self.config.dst_database]:
            worldboss2 = src_database.session.query(t_worldboss2).first()
            if new_worldboss2 and worldboss2:
                if worldboss2.level <= new_worldboss2.level:
                    new_worldboss2 = worldboss2.new_from(worldboss2)
            if not new_worldboss2 and worldboss2:
                new_worldboss2 = t_worldboss2.new_from(worldboss2)
        if new_worldboss2:
            self.config.dst_database.session.merge(new_worldboss2)
            self.config.dst_database.session.commit()
        gc.collect()

    def _dispose_log(self):
        print(u"_dispose_log")
        for src_database in self.config.src_databases:
            log_getgolds = src_database.session.query(t_log_getgold).all()
            for log_getgold in log_getgolds:
                new_log_getgold = t_log_getgold.new_from(log_getgold)
                new_log_getgold.rid = self.config.role_merge_maps.get_new_id(src_database.identifier, log_getgold.rid)
                if new_log_getgold.rid:
                    self.orm_objects.append(new_log_getgold)

            log_usegolds = src_database.session.query(t_log_usegold).all()
            for log_usegold in log_usegolds:
                new_log_usegold = t_log_usegold.new_from(log_usegold)
                new_log_usegold.rid = self.config.role_merge_maps.get_new_id(src_database.identifier, log_usegold.rid)
                if new_log_usegold.rid:
                    self.orm_objects.append(new_log_usegold)

        self._dump_orm_objects()
        gc.collect()
