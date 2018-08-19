# -*- coding: utf-8 -*-

from config import wrapper_database_info

from table.t_gang2 import t_gang2
from table.t_gang2_role import t_gang2_role
from table.t_gang2_fishpond import t_gang2_fishpond
import gc

class GangMerge(object):
    def __init__(self, config):
        self.config = config

        self.gang_increment = 0

        self.name_map = {}

    def run(self):
        self._init_increment()
        dst_gangs = self.config.dst_database.session.query(t_gang2).all()
        for dst_gang in dst_gangs:
            self.name_map[dst_gang.name] = dst_gang.gid

        database_gangs = get_database_gangs(self.config.src_databases)
        for database_gang in database_gangs:
            self._dispose(database_gang)

        self.config.dst_database.session.commit()
        gc.collect()

    def _init_increment(self):
        for status in self.config.dst_database.session.execute("""SHOW TABLE STATUS;"""):
            table_name = status[0]
            table_increment = status[10]
            if table_name == 't_gang2':
                self.gang_increment = table_increment

    def _dispose(self, database_gang):
        database = database_gang.database
        gang = database_gang.data
        new_gang = t_gang2.new_from(gang)
        for attr_name in ('rid', 'rid1', 'rid2', 'rid3', 'optparam'):
            rid = getattr(gang, attr_name)
            if rid:
                setattr(new_gang, attr_name, self.config.role_merge_maps.get_new_id(database.identifier, rid))
        self.gang_increment += 1
        new_gang.gid = self.gang_increment
        if new_gang.name in self.name_map:
            rename_gang_id = self.name_map[new_gang.name]
            rename_gang = self.config.dst_database.session.query(t_gang2).filter(t_gang2.gid == rename_gang_id).first()
            rename_gang.name = '%s%s%d' % (rename_gang.name, self.config.rename_postfix, int(rename_gang.rid / self.config.server_id_step))
            self.config.dst_database.session.merge(rename_gang)
            new_gang.name = '%s%s%d' % (new_gang.name, self.config.rename_postfix, int(new_gang.rid / self.config.server_id_step))

            self.name_map[rename_gang.name] = rename_gang_id
            print('rename gid:%d' % rename_gang.gid)
            print('rename gid:%d' % new_gang.gid)
        self.name_map[new_gang.name] = new_gang.gid

        self.config.dst_database.session.add(new_gang)
        self.config.gang_merge_maps.add(database.identifier, gang.gid, new_gang.gid)

        gang_fishpond = database.session.query(t_gang2_fishpond).filter(t_gang2_fishpond.gid == gang.gid).first()
        if gang_fishpond:
            new_gang_fishpond = t_gang2_fishpond.new_from(gang_fishpond)
            new_gang_fishpond.gid = new_gang.gid
            self.config.dst_database.session.add(new_gang_fishpond)

        print('%s | %d -> %d' % (database.identifier, gang.gid, new_gang.gid))
        gang_roles = database.session.query(t_gang2_role) \
            .filter(t_gang2_role.gid == gang.gid) \
            .all()
        for gang_role in gang_roles:
            new_rid = self.config.role_merge_maps.get_new_id(database.identifier, gang_role.rid)
            if not new_rid:
                continue
            new_gang_role = self.config.dst_database.session.query(t_gang2_role)\
                .filter(t_gang2_role.rid == new_rid)\
                .first()
            if not new_gang_role:
                continue
            new_gang_role.gid = new_gang.gid
            self.config.dst_database.session.merge(new_gang_role)


def get_database_gangs(databases):
    database_gangs = []
    for database in databases:
        for gang in database.session.query(t_gang2).all():
            database_gangs.append(wrapper_database_info(database, gang))
    print("all gangs %d" % len(database_gangs))
    return database_gangs
