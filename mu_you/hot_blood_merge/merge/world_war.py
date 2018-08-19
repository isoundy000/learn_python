# -*- coding: utf-8 -*-

import time

from table.WorldWar.t_world_war_sign_role import t_world_war_sign_role
from table.WorldWar.t_world_war_sign_slot import t_world_war_sign_slot
from table.WorldWar.t_world_war_sign_general import t_world_war_sign_general
from table.WorldWar.t_world_war_role import t_world_war_role
from table.WorldWar.t_world_war_slot import t_world_war_slot
from table.WorldWar.t_world_war_general import t_world_war_general
from table.WorldWar.t_world_war_battle import t_world_war_battle
from table.WorldWar.t_world_war_weed_info import t_world_war_weed_info
import gc

class WorldWarMerge(object):
    def __init__(self, config):
        self.config = config

        self.sign_role_increment = 0

        self.orm_objects = []

    def __del__(self):
        self.config = None
        self.orm_objects.clear()

    def run(self):
        self._init_increment()
        self._merge()

    def _init_increment(self):
        for status in self.config.dst_database.session.execute("""SHOW TABLE STATUS;"""):
            table_name = status[0]
            table_increment = status[10]
            if table_name == 't_world_war_sign_role':
                self.sign_role_increment = table_increment

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

    def _merge(self):
        dst_roles = self.config.dst_database.session.query(t_world_war_role).all()
        dst_battles = self.config.dst_database.session.query(t_world_war_battle).all()
        dst_weed_infos = self.config.dst_database.session.query(t_world_war_weed_info).all()

        dst_role_map = {}
        dst_battle_map = {}
        dst_weed_info_map = {}
        gc.collect()
        for dst_role in dst_roles:
            dst_role_map[dst_role.id] = dst_role
        for dst_battle in dst_battles:
            dst_battle_map[dst_battle.id] = dst_battle
        for dst_weed_info in dst_weed_infos:
            dst_weed_info_map[dst_weed_info.id] = dst_weed_infos

        for src_database in self.config.src_databases:
            sign_roles = src_database.session.query(t_world_war_sign_role).all()
            sign_slots = src_database.session.query(t_world_war_sign_slot).all()
            sign_generals = src_database.session.query(t_world_war_sign_general).all()

            sign_role_map = {}
            sign_slot_map = {}
            sign_general_map = {}

            for sign_role in sign_roles:
                sign_role_map[sign_role.id] = sign_role
            for sign_slot in sign_slots:
                sign_slot_map[sign_slot.id] = sign_slot
            for sign_general in sign_generals:
                if sign_general.id not in sign_general_map:
                    sign_general_map[sign_general.id] = {}
                sign_general_map[sign_general.id][sign_general.gid] = sign_general

            for sign_role in sign_roles:
                sign_id = sign_role.id
                new_sign_id = self.sign_role_increment

                new_sign_role = t_world_war_sign_role.new_from(sign_role)
                new_sign_role.rid = self.config.role_merge_maps.get_new_id(src_database.identifier, sign_role.rid)
                new_sign_role.id = new_sign_id
                self.orm_objects.append(new_sign_role)

                sign_slot = sign_slot_map[sign_id]
                new_sign_slot = t_world_war_sign_slot.new_from(sign_slot)
                new_sign_slot.id = new_sign_id
                self.orm_objects.append(new_sign_slot)

                sign_generals = sign_general_map[sign_id]
                for sign_general in sign_generals.values():
                    new_sign_general = t_world_war_sign_general.new_from(sign_general)
                    new_sign_general.id = new_sign_id
                    self.orm_objects.append(new_sign_general)

                self.sign_role_increment += 1

        for src_database in self.config.src_databases:
            roles = src_database.session.query(t_world_war_role).all()
            slots = src_database.session.query(t_world_war_slot).all()
            generals = src_database.session.query(t_world_war_general).all()

            role_map = {}
            slot_map = {}
            general_map = {}

            for role in roles:
                role_map[role.id] = role
            for slot in slots:
                slot_map[slot.id] = slot
            for general in generals:
                if general.id not in general_map:
                    general_map[general.id] = {}
                general_map[general.id][general.gid] = general

            for role in roles:
                if role.id in dst_role_map:
                    continue
                dst_role_map[role.id] = role
                new_role = t_world_war_role.new_from(role)
                self.orm_objects.append(new_role)

                slot = slot_map.get(role.id)
                if slot:
                    new_slot = t_world_war_slot.new_from(slot)
                    self.orm_objects.append(new_slot)

                generals = general_map.get(role.id)
                if generals:
                    for general in generals.values():
                        new_general = t_world_war_general.new_from(general)
                        self.orm_objects.append(new_general)

        for src_database in self.config.src_databases:
            battles = src_database.session.query(t_world_war_battle).all()
            for battle in battles:
                if battle.id in dst_battle_map:
                    continue
                dst_battle_map[battle.id] = battle
                new_battle = t_world_war_battle.new_from(battle)
                self.orm_objects.append(new_battle)

        for src_database in self.config.src_databases:
            weed_infos = src_database.session.query(t_world_war_weed_info).all()
            for weed_info in weed_infos:
                if weed_info.id in dst_weed_info_map:
                    continue
                dst_weed_info_map[weed_info.id] = weed_info
                new_weed_info = t_world_war_weed_info.new_from(weed_info)
                self.orm_objects.append(new_weed_info)

        self._dump_orm_objects()
