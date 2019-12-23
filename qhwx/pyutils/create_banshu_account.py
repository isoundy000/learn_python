# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os
import random
import string
import sys
from jpzmg_init import project_init
project_init()
from app.models.stage import Stage

# Create your tests here.
from gm_manage.views.player_info.edit_user_info import modify_user
from gm_manage.views.player_info.finish_stage import skip
from django.conf.global_settings import SECRET_KEY
from account.views import _generate_token
from app.models.account import Account
from app.models.account_mapping import AccountMapping

from rklib.utils.guuid import get_uuid

import arrow
from app.models.user_mapping import UserMapping
from app.models.user import User
from app.action.card_package import add_cards
from app.action.wing_room import add_confidants
from config import game_config

guest = 'guest'
if __name__ == "__main__":
    ctime = arrow.utcnow().timestamp
    # openid = '%s_%s' % (guest, 0)
    # openkey = openid
    # user_mapping = UserMapping.get(openid)
    # if not isinstance(user_mapping, UserMapping):
    #     user_mapping = UserMapping._install(openid, openkey, 4)
    pwd = '123456'
    account_number = 'test10'
    openid = get_uuid()
    openkey = _generate_token(SECRET_KEY)
    pwd_md = hashlib.md5()
    pwd_md.update(pwd)
    Account._install(account_number, pwd_md.hexdigest(), openid)
    AccountMapping._install(openid, account_number, openkey)
    user_mapping = UserMapping.get(openid)
    if not isinstance(user_mapping, UserMapping):
        user_mapping = UserMapping._install(openid, openkey, 4)
    uid = user_mapping.uid
    rk_user = User.get(uid)
    if not isinstance(rk_user, User):
        rk_user = User._install_new_user(uid, openid)
    rk_user.stage._install(uid)
    charpter = map(int, game_config.chapter[10]['pve'].split(","))[-1]  # 关卡编号
    skip(rk_user, 10, charpter)  # 关卡
    # need_lv = game_config.exp.keys()[rk_user.user_lv_manage.ulv - 1: 10]
    # total_exp = []
    # for i in need_lv:
    #     total_exp.append(game_config.exp[i]['exp'])
    # level_config = sum(total_exp)

    # modify_user(rk_user, '1', level_config, 1, 10)
    # rk_user =User.get(1000000004)
    # rk_user.guide.finish_guide()  # 跳过新手引导
    # num = 10000000
    # for i in range(3, 7, 1):  # 3-银两 4-元宝 5-士兵 6-粮草
    #     modify_user(rk_user, str(i), num, 0, 0)


    #
    # for i in xrange(1, 31):
    #     # openid = '%s_%s' % (guest, i)
    #     openid = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #
    #     openkey = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #     user_mapping = UserMapping.get(openid)
    #     if not isinstance(user_mapping, UserMapping):
    #         user_mapping = UserMapping._install(openid, openkey, 4)
    #
    #     uid = user_mapping.uid
    #     rk_user = User.get(uid)
    #     if not isinstance(rk_user, User):
    #         user = User._install_new_user(uid, openid)
    #     # user.item_package.add_items(add_items, is_put=True)
    #
    # for i in xrange(31, 61):
    #     # openid = '%s_%s' % (guest, i)
    #     openid = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #
    #     openkey = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #     user_mapping = UserMapping.get(openid)
    #     if not isinstance(user_mapping, UserMapping):
    #         user_mapping = UserMapping._install(openid, openkey, 4)
    #     uid = user_mapping.uid
    #     rk_user = User.get(uid)
    #     if not isinstance(rk_user, User):
    #         rk_user = User._install_new_user(uid, openid)
    #     rk_user.card_package._install(uid)
    #     rk_user.wing_room._install(uid)
    #
    #     rk_user.guide.finish_guide()  # 跳过新手引导
    #     need_lv = game_config.exp.keys()[rk_user.user_lv_manage.ulv - 1: 2]
    #     total_exp = []
    #     for i in need_lv:
    #         total_exp.append(game_config.exp[i]['exp'])
    #     level_config = sum(total_exp)
    #     modify_user(rk_user, '1', level_config, 1, 2)
    #     rk_user.sites_dress_up.init_building_for_lv(lv=2)  # 裝扮
    #     num = 10000
    #     for i in range(3, 7, 1):  # 3-银两 4-元宝 5-士兵 6-粮草
    #         modify_user(rk_user, str(i), num, 0, 0)
    #     charpter = map(int, game_config.chapter[1]['pve'].split(","))[-1]  # 关卡编号
    #     skip(rk_user, 1, charpter)  # 关卡
    #     continue
    # for i in xrange(61, 101):
    #     # openid = '%s_%s' % (guest, i)
    #     openid = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #
    #     openkey = string.join(
    #         random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
    #                       50)).replace(" ", "")
    #     user_mapping = UserMapping.get(openid)
    #     if not isinstance(user_mapping, UserMapping):
    #         user_mapping = UserMapping._install(openid, openkey, 4)
    #     uid = user_mapping.uid
    #     rk_user = User.get(uid)
    #     if not isinstance(rk_user, User):
    #         rk_user = User._install_new_user(uid, openid)
    #     rk_user.guide.finish_guide()  # 跳过新手引导
    #
    #     rk_user.card_package._install(uid)
    #     rk_user.wing_room._install(uid)
    #
    #     need_lv = game_config.exp.keys()[rk_user.user_lv_manage.ulv - 1: 2]
    #     total_exp = []
    #     for i in need_lv:
    #         total_exp.append(game_config.exp[i]['exp'])
    #     level_config = sum(total_exp)
    #     modify_user(rk_user, '1', level_config, 1, 16)  # 修改用户等级
    #     rk_user.sites_dress_up.init_building_for_lv(lv=15)  # 裝扮
    #     num = 100000000
    #     for i in range(3, 7, 1):  # 3-银两 4-元宝 5-士兵
    #         modify_user(rk_user, str(i), num, 0, 0)
    #     charpter = map(int, game_config.chapter[20]['pve'].split(","))[-1]  # 关卡编号
    #     skip(rk_user, 20, charpter)  # 关卡
    #     continue
