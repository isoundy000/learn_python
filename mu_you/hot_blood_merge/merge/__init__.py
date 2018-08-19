# -*- coding: utf-8 -*-

from table.t_merge_log import t_merge_log


class MergeMap(object):
    def __init__(self, identifier, old_id, new_id, is_new):
        self.identifier = identifier
        self.old_id = old_id
        self.new_id = new_id
        self.is_new = is_new


class MergeMaps(object):
    def __init__(self, table_name):
        self.table_name = table_name
        self.maps = []

        self.new_map = {
            #identifier: {
            #    old_id: new_id
            #}
        }
        self.old_map = {}

    def add(self, identifier, old_id, new_id, is_new=True):
        merge_map = MergeMap(identifier, old_id, new_id, is_new=is_new)
        self.maps.append(merge_map)
        if identifier not in self.new_map:
            self.new_map[identifier] = {}
        if identifier not in self.old_map:
            self.old_map[identifier] = {}

        self.new_map[identifier][old_id] = new_id
        self.old_map[identifier][new_id] = old_id

    def get_old_id(self, identifier, new_id):
        #for m in self.maps:
        #    if m.identifier == identifier and m.new_id == new_id:
        #        return m.old_id
        return self.old_map.get(identifier, {}).get(new_id)

    def get_new_id(self, identifier, old_id):
        #for m in self.maps:
        #    if m.identifier == identifier and m.old_id == old_id:
        #        return m.new_id
        return self.new_map.get(identifier, {}).get(old_id)

    def load_merge_log(self, session):
        for merge_log in session.query(t_merge_log).filter(t_merge_log.table_name == self.table_name).all():
            self.add(merge_log.identifier, merge_log.old_id, merge_log.new_id, is_new=False)

    def dump_merge_log(self, session):
        for merge_map in self.maps:
            if merge_map.is_new is False:
                continue
            merge_log = t_merge_log(
                table_name=self.table_name,
                identifier=merge_map.identifier,
                old_id=merge_map.old_id,
                new_id=merge_map.new_id
            )
            session.add(merge_log)
        session.commit()


def init_merge_log(database_info, is_delete):
    t_merge_log.metadata.create_all(bind=database_info.engine)
    if is_delete:
        database_info.session.query(t_merge_log).delete()
    database_info.session.commit()
