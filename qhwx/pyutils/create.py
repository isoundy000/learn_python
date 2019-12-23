# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import random
import string
import sys
from jpzmg_init import project_init
project_init()
# Create your tests here.
from gm_manage.views.player_info.edit_user_info import modify_user
from gm_manage.views.player_info.finish_stage import skip


import arrow
from app.models.user_mapping import UserMapping
from app.models.user import User
from app.action.card_package import add_cards
from app.action.wing_room import add_confidants
from config import game_config
guest = 'guest'

ctime = arrow.utcnow().timestamp

for i in xrange(1, 91):
    # openid = '%s_%s' % (guest, i)
    openid = string.join(
        random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                      10)).replace(" ", "")

    openkey = string.join(
        random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                      10)).replace(" ", "")
    user_mapping = UserMapping.get(openid)
    if not isinstance(user_mapping, UserMapping):
        user_mapping = UserMapping._install(openid, openkey, 4)
    uid = user_mapping.uid
    user = User.get(uid)
    if not isinstance(user, User):
        user = User._install_new_user(uid, openid)
    if i <= 50:
        continue
    cnos = [10006, 10007, 10008, 10009, 10010, 10011]
    womens = [20002]
    add_items = {}
    for item_no in game_config.item.keys():
        add_items[int(item_no)] = 10
    pct = 3000              # 1
    gold = 5000000          # 2
    provender = 5000000     # 3
    soldiers = 5000000      # 4
    orank = 7

    if i > 100:
        cnos += [10012, 10013, 10014, 10015, 10016]
        womens += [20003]
        add_items = {}
        for item_no in game_config.item.keys():
            add_items[int(item_no)] = 100
        pct = 10000  # 1
        gold = 50000000  # 2
        provender = 50000000  # 3
        soldiers = 50000000  # 4
        orank = 12

    add_cards(user, cnos)
    add_confidants(user, womens)

    user.game_info.pct = pct
    user.game_info.gold = gold
    user.game_info.provender = provender
    user.game_info.soldiers = soldiers
    user.game_info.orank = orank
    user.game_info.put()
    user.item_package.add_items(add_items, is_put=True)
    continue








