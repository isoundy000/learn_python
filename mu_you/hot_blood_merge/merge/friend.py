# -*- coding: utf-8 -*-

from table.t_friend import t_friend
import gc

class FriendMerge(object):
    def __init__(self, config):
        self.config = config

    def __del__(self):
        self.config = None

    def run(self):
        for merge_map in self.config.role_merge_maps.maps:
            for database in self.config.src_databases:
                if merge_map.identifier == database.identifier:
                    self._dispose(database, merge_map.old_id, merge_map.new_id)
                    break
        self.config.dst_database.session.commit()
        gc.collect()
    def _dispose(self, database, old_rid, new_rid):
        friends = database.session.query(t_friend).filter(t_friend.rid == old_rid).all()
        for friend in friends:
            fid = friend.fid
            if fid in database.npc_friend_ids:
                continue
            new_fid = self.config.role_merge_maps.get_new_id(database.identifier, fid)
            if not new_fid:
                continue
            new_friend = t_friend.new_from(friend)
            new_friend.rid = new_rid
            new_friend.fid = new_fid
            self.config.dst_database.session.add(new_friend)
