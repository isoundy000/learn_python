#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import traceback
import bisect
import sys
import time
import datetime
import copy
import urllib2
import json
import cPickle as pickle

import tornado

import settings
import game_config
import auth
import admin_config
from models.config import ConfigManager, ServerConfig
import upload as upup
from lib.utils.debug import print_log
from models.config import config_types, ConfigRefresh, ResourceVersion
from logics.user import User
from logics.arena import Arena as ArenaLogic
from models.user import User as User_m
from models.user import UnameUid, UidServer

import cPickle
import cStringIO
import re
import itertools
from lib.utils import change_time
from models.config import ChangeTime
from logics.item import try_replace_box_reward_by_count
from lib.utils import weight_choice
from admin.decorators import Logging as AdminLogging
from decorators import ApprovalPayment
from admin_models import Admin
from logics.gacha import Gacha
from logics.payment import virtual_pay_by_admin
from models.payment import ModelPayment, MySQLConnect
from models.notify import Notify
from models.logging import Logging
from decorators import require_permission
from models.gacha import RewardGacha
from models.super_active import SuperActive


def render(req, template_file, **kwargs):
    """# render: docstring
    args:
        req, template_file, **kwargs:    ---    arg
    returns:
        0    ---
    """
    kwargs['url_partition'] = settings.URL_PARTITION
    kwargs['PLATFORM'] = settings.PLATFORM or settings.ENV_NAME
    return tornado.web.RequestHandler.render(req, template_file, **kwargs)


def change_password(req):
    msgs = []
    d = {'msgs': msgs}
    if req.request.method == 'GET':
        return render(req, 'admin/change_password.html', **d)
    else:
        old = req.get_argument('old_password', 'old_password').strip()
        pwd1 = req.get_argument('password1', 'password1').strip()
        pwd2 = req.get_argument('password2', 'password2').strip()

        if not (pwd1 and pwd2):
            msgs.append(u'密码不能为空')
        elif pwd1 != pwd2:
            msgs.append(u'两次输入密码不同')
        else:
            admin = auth.get_admin_by_request(req)
            if admin:
                if not admin.check_password(old):
                    msgs.append(u'原始密码错误')
                else:
                    msgs.append(u'success')
                    admin.set_password(pwd1)
                    admin.save()

        return render(req, 'admin/change_password.html', **d)


def login(req):
    msgs = []
    d = {'msgs': msgs}
    if req.request.method == 'POST':
        username = req.get_argument('username', '')
        password = req.get_argument('password', '')
        if not username or not password:
            msgs.append(u'用户名或密码错误')
            return render(req, 'admin/login.html', **d)

        admin = Admin.get(username)
        if not admin:
            msgs.append(u'用户不存在')
            return render(req, 'admin/login.html', **d)
        elif not admin.check_password(password):
            msgs.append(u'密码错误')
            return render(req, 'admin/login.html', **d)

        auth.login(req, admin)
        return req.redirect('/%s/admin/index/' % settings.URL_PARTITION)
    return render(req, 'admin/login.html', **d)


def logout(req):
    auth.logout(req)
    return render(req, 'admin/login.html', **{'msgs': []})


@require_permission
def add_admin(req):
    """
     新建管理员
    """
    result = {
        'menu': None,
        'message': '',
        'user_exist': False,
    }

    menu = auth.get_menu()
    if menu:
        for value, name in menu:
            if value == 'all':
                result['all_v'] = value
                result['all_n'] = name
                menu.remove((value, name))
        result['menu'] = menu
        result['right_links'] = admin_config.secondary_links

    if req.request.method == "POST":
        username = req.get_argument("username", '').strip()
        password = req.get_argument("password", '').strip()
        password1 = req.get_argument("password1", '').strip()
        email = req.get_argument("email", '').strip()

        admin = Admin.get(username)
        if admin:
            result['message'] = u'帐号已存在'
            return render(req, "admin/add_admin.html", **result)
        elif password != password1:
            result['message'] = u'两次密码输入不同'
            return render(req, "admin/add_admin.html", **result)
        else:
            admin = Admin()
            admin.username = username
            admin.password = password
            admin.email = email
            admin.last_login = datetime.datetime.now()
            # 如果有全部勾选这一项
            if req.get_argument('all', ''):
                admin.left_href_list = admin_config.get_all_href_key()
            else:
                link_list = []
                # 提取勾选的权限
                for item_name in admin_config.left_href:
                    name = req.get_argument(item_name, '')
                    if name:
                        link_list.append(name)
                admin.left_href_list = link_list

            right_links = []
            for element_key in admin_config.secondary_links:
                if req.get_argument(element_key, ''):
                    if element_key not in right_links:
                        right_links.append(element_key)
            if right_links:
                admin.right_links = right_links
            # 这步是存储了
            admin.save()
            return req.finish('添加成功')
    else:
        username = req.get_argument("username", '').strip()
        all_user = Admin.get_all_user()
        result['all_user'] = all_user
        result['username'] = username
        if username in all_user:
            result['user_exist'] = True
            a = Admin.get(username)
            result['checked_user_left_href_list'] = lambda href: 'checked=checked' if href in a.left_href_list else ''
            result['checked_user_right_links'] = lambda href: 'checked=checked' if href in a.right_links else ''
        elif username:  # 如果用户名不为空但不在用户列表中
            return req.finish(u'用户不存在')
        return render(req, "admin/add_admin.html", **result)


@require_permission
def modify_admin(req):
    """修改管理员权限"""
    if req.request.method == "POST":
        username = req.get_argument("username", '').strip()
        all_user = Admin.get_all_user()
        if username not in all_user:
            return req.finish(u'用户不存在')
        admin = Admin.get(username)
        # 如果有全部勾选这一项
        if req.get_argument('all', ''):
            admin.left_href_list = admin_config.get_all_href_key()
        else:
            link_list = []
            # 提取勾选的权限
            for item_name in admin_config.left_href:
                name = req.get_argument(item_name, '')
                if name:
                    link_list.append(name)
            admin.left_href_list = link_list
        right_links = []
        for element_key in admin_config.secondary_links:
            if req.get_argument(element_key, ''):
                if element_key not in right_links:
                    right_links.append(element_key)
        if right_links:
            admin.right_links = right_links
        # 这步是存储了
        admin.save()
        return req.finish(u'修改成功')


@require_permission
def index(req):
    """# index: docstring
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    return render(req, 'admin/main.html', **{})

@require_permission
def left(req):
    """# left: docstring
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    left_href_list = []
    admin = auth.get_admin_by_request(req)
    # 开发环境不做权限验证
    href_lists = admin.left_href_list if admin else admin_config.left_href
    for i in href_lists:
        info = admin_config.left_href.get(i)
        if info:
            left_href_list.append(info)
    return render(req, 'admin/left.html', **{'left_href_list': left_href_list})


def sets(req):
    """# left: docstring
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    method = req.get_argument('page', 'info_view')
    return render(req, 'admin/info_view.html', **{'method': method})


@require_permission
def config(req, **msg):
    '''
    游戏配置
    :param req:
    :param msg:
    :return:
    '''
    """# config: docstring
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    server_id = req.get_argument('server_id', '')
    if server_id:
        config_name_list = sorted([i for i in game_config.config_name_list if i[2] and not i[6]], key=lambda x: x[4])
    else:
        config_name_list = sorted([i for i in game_config.config_name_list if i[2] and i[6]], key=lambda x: x[4])

    config_name_list_new = []
    l_len = len(config_name_list)
    line_n = l_len / 5
    i = 0
    while i <= line_n:
        left = i * 5
        right = (i + 1) * 5
        if right < l_len:
            config_name_list_new.append(config_name_list[left:right])
        else:
            config_name_list_new.append(config_name_list[left:])
        i += 1

    config_type = req.get_argument('config_type', 2)
    config_type = int(config_type) if config_type else 1

    config_key = req.get_argument('config_key', config_name_list[0][0])
    config_tuple = [i for i in config_name_list if i[0] == config_key][0]
    config_cn = i[4]
    config_data = ConfigManager.get_config_obj(config_key, config_type=config_type).value
    if repr(config_data) == '{}':
        config_data = getattr(game_config, config_key, '{}')

    message = req.get_argument('config_refresh_text', '')
    flag = int(req.get_argument('config_refresh_flag', 0))
    if flag or message:
        ConfigRefresh.refresh(flag, message)
    res_flag = int(req.get_argument('test_res_version_flag', -1))
    if res_flag >= 0:
        ResourceVersion.set(res_flag)
    rvf = ResourceVersion.get()
    refresh_flag, refresh_text = ConfigRefresh.check()
    return render(req, 'admin/config/index.html', **{
        'config_name_list': config_name_list_new,
        'config_key': config_key,
        'config_cn': config_cn,
        'config_data': config_data,
        'msg': msg.get('msg', ''),
        'server_id': server_id,
        'config_types': config_types,
        'config_type': config_type,
        'config_refresh_flag': refresh_flag,
        'config_refresh_text': refresh_text,
        'test_res_version_flag': rvf,
    })

@require_permission
def get_all_config(req):
    '''下载测试用配置'''
    """# get_all_config: docstring
    args:
        req:    ---    arg
    returns:
        0    ---    
    """
    req.set_header('Content-Type', 'application/txt')
    req.set_header('Content-Disposition', 'attachment;filename=local_config.py')
    from test.get_all_configs import get_all_config
    file_name = get_all_config()
    file_obj = open(file_name, 'r')
    req.write(file_obj.read())

@require_permission
def upload(req):
    '''上传文件'''
    """
    args:
        req:    ---    arg
    returns:
        0    ---    
    """
    file_obj = req.request.files.get('xls', None)
    server_id = req.get_argument('server_id', '')

    if not file_obj:
        return render(req, 'admin/config/notice.html',
                      **{'msg': unicode('哥们, 求文件', 'utf-8')}
                      )

    file_name = file_obj[0]['filename']
    platform = settings.PLATFORM
    if not settings.DEBUG and platform and platform not in file_name:
        return render(req, 'admin/config/notice.html',
                      **{'msg': unicode('检查配置文件是否为 %s 平台的' % platform, 'utf-8')}
                      )
    config_type = req.get_argument('config_type', 1)
    config_type = int(config_type) if config_type else 1
    rc, done_list = upup.upload(file_obj, server_id, config_type=config_type)

    # 跨服活动配置有错误
    if rc == -99:
        bug_info = done_list
        return render(req, 'admin/config/notice.html', **{'msg': unicode('%s' % bug_info, 'utf-8')})

    if rc == 100:
        return config(req, **{'msg': done_list})

    if rc == 1:
        return render(req, 'admin/city_map_test.html', **{
            'tb': done_list[0],
            'local_dict': done_list[1],
        })
    ConfigRefresh.reset()
    return config(req, **{'msg': 'done: ' + ', '.join(done_list)})


@require_permission
def server_list(req, server_config_obj=None, msg=None, server_config_type=None):
    """# server_config: 分服方面的设置
    """
    if server_config_obj is None:
        from models.config import ServerConfig
        l = ServerConfig.get().server_list(need_filter=False)
    else:
        l = server_config_obj.server_list(need_filter=False)

    return render(req, 'admin/server_config.html', **{
        'server_list': l,
        'config_types': config_types,
        'server_config_type': server_config_type,
        'msg': msg if msg is not None else [],
    })


@require_permission
def give_card(req, card_give=None, uid=None):
    """# give_card: docstring 送卡牌
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    cards = game_config.character_detail
    # skill_detail = game_config.skill_detail

    c_r = []
    for k, v in cards.iteritems():
        # skill = {}
        # for st in ['skill_1_source', 'skill_2_source', 'skill_3_source']:
        #     skill[st] = []
        #     skill_source = v[st]
        #     for i, s in enumerate(skill_source):
        #         skill_data = skill_detail.get(s[0])
        #         if not skill_data:
        #             continue
        #         skill[st].append({
        #             'c_id': s[0],
        #             'level_max': skill_data['max_lv'],
        #             'name': skill_data['skill_name'],
        #             'cent': s[1]
        #         })
        c_r.append({
            'c_id': k,
            # 'level_max': v['level_max'],
            'name': v['name'],
            'name_after': '',
            # 'skill': skill,
        })

    c_r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/givecard.html', **{
        'c_r': c_r,
        'uid': uid if uid else 'test',
        'card_give': card_give if card_give else {}
    })


@require_permission
def give_card_commit(req):
    """# get_card_commit: docstring 卡牌提交页面
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    cards = game_config.character_detail
    card_give = {}
    u = None
    if params:
        u = User.get(params.get('user_id', ['test'])[0])
        for k in cards.iterkeys():
            card_num = int(params.get('card_num_%d' % k, ['0'])[0])
            if card_num:    # params.get('card_%d' % k) == ['on']:
                card_lv = int(params.get('card_lv_%d' % k, ['0'])[0])
                card_evolv = int(params.get('card_evolv_%d' % k, ['0'])[0])
                # skill_1 = int(params.get('card_skill_1_%d' % k    , ['0'])[0])
                # skill_1_lv = int(params.get('card_skill_1_lv_%d' % k , ['0'])[0])
                # skill_2 = int(params.get('card_skill_2_%d' % k    , ['0'])[0])
                # skill_2_lv = int(params.get('card_skill_2_lv_%d' % k , ['0'])[0])
                # skill_3 = int(params.get('card_skill_3_%d' % k    , ['0'])[0])
                # skill_3_lv = int(params.get('card_skill_3_lv_%d' % k , ['0'])[0])

                for i in range(card_num):
                    # s1 = (skill_1, skill_1_lv) if skill_1_lv else ()
                    # s2 = (skill_2, skill_2_lv) if skill_2_lv else ()
                    # s3 = (skill_3, skill_3_lv) if skill_3_lv else ()
                    card_id = u.cards.new(k, evo=card_evolv)
                    u.cards._cards[card_id]['lv'] = card_lv
                    card_give[k] = {
                        'lv': card_lv,
                        # 'skill_1': (skill_1, skill_1_lv),
                        # 'skill_2': (skill_2, skill_2_lv),
                        # 'skill_3': (skill_3, skill_3_lv),
                        'card_num': card_num,
                        'evolv': card_evolv,
                    }
        u.cards.save()
    return give_card(req, card_give, u.uid)


@require_permission
def user_cards(req):
    """# user_cards: docstring 用户卡牌
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    uid = req.get_argument('uid', 'test')
    import game_config

    user = User.get(uid, 'master')
    cards = []
    for k, v in user.cards.get_all_cards().iteritems():
        v['card_id'] = k
        card_config = game_config.character_detail[v['c_id']]
        v['name'] = card_config['name']
        v['birth_time'] = datetime.datetime.fromtimestamp(int(k.split('-')[1]))     # 获得卡牌的时间
        for i in ['s_1', 's_2', 's_3', 's_4', 's_5']:                               # 卡牌技能
            if i in v:
                if v[i]['s'] and v[i]['s'] in game_config.skill_detail:
                    s_1_config = game_config.skill_detail[v[i]['s']]
                    v[i]['name'] = s_1_config['skill_name']
                else:
                    v[i]['name'] = ''

        cards.append(v)

    return render(req, 'admin/user_cards.html', **{
        'uid': uid,
        'cards': sorted(cards, key=lambda x: x['card_id']),
        'debug': settings.DEBUG,
    })


@require_permission
def del_card(req):
    """# del_card: docstring  对卡牌进行 删除、修改、拷贝、替换等操作
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    uid = req.get_argument('uid', 'test')
    ids = req.get_argument('ids', '')

    school_flag = False
    u = user = User.get(uid)
    if 'remove' in req.request.arguments:
        card_info = user.cards._cards[ids]
        if 'train' in card_info['remove_avail']:                # 卡牌在训练中
            for stove_key in u.school._attrs:
                stove = getattr(u.school, stove_key)
                if stove['card_id'] == ids:
                    u.cards.release_card(ids, 'train')          # 解锁
                    u.school.reset_stove(stove_key)             # 重置解锁
                    school_flag = True
        card_info['remove_avail'] = []
        user.cards.remove(ids)
    elif 'modified' in req.request.arguments:
        card_info = user.cards._cards.get(ids)
        card_config = game_config.character_detail[card_info['c_id']]

        if card_info:
            card_level = abs(int(req.get_argument('card_level'))) or 1
            evo = abs(int(req.get_argument('evo', 0)))
            evo_config = user.cards.get_evolution_config(ids, card_info, card_config)

            level_max = card_info.get('level_max') or card_config[card_info['c_id']]['level_max']
            card_info['lv'] = min(card_level, level_max)
            card_info['level_max'] = level_max

            if settings.DEBUG:
                if evo in evo_config:
                    card_info['evo'] = 0
                    for _ in range(evo):
                        user.cards.evolution(card_info['id'], card_info, card_config)
                    card_info['lv'] = min(card_level, card_info['level_max'])
                card_info['pre_exp'] = user.cards.get_need_exp_for_level(card_info['c_id'], 1, card_info['lv'])

            for _s in ['s_1', 's_2', 's_3', 's_4', 's_5']:
                _s_level = abs(int(req.get_argument('%s_%s' % (_s, 'level')))) or 1
                if _s in card_info and card_info[_s]['s'] and card_info[_s]['s'] in game_config.skill_detail:
                    _s_level = min(_s_level, game_config.skill_detail[card_info[_s]['s']]['max_lv'])
                    card_info[_s]['lv'] = _s_level
    elif 'copy' in req.request.arguments:
        card_info = user.cards._cards.get(ids)
        if card_info:
            new_card_id = user.cards._make_id(card_info['c_id'])
            user.cards._cards[new_card_id] = copy.deepcopy(card_info)
            user.cards._cards[new_card_id]['id'] = new_card_id
            user.cards._cards[new_card_id]['pos'] = 0
    elif 'replace' in req.request.arguments:
        re_id = req.get_argument('re_id', '')
        if re_id:
            user.cards.replace_card(ids, re_id, save=False)
    user.cards.save()
    if school_flag:
        user.school.save()
    return user_cards(req)


@require_permission
def give_equip(req, msg=None):
    """# give_equip: 装备展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    equip = game_config.equip
    # equip_max_level = game_config.equip_max_strongthen
    r = []
    for k, v in equip.iteritems():
        # quality = v['quality']
        r.append({
            'c_id': k,
            'name': v['name'],
            'max_level': 10,  # equip_max_level[quality]['max_strongthen']
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/equip.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_equip_commit(req):
    """# give_equip_commit: 装备发送
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    equip = game_config.equip
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    for k, v in equip.iteritems():
        lv = int(params.get('equip_lv_%d' % k, ['0'])[0])
        num = int(params.get('equip_num_%d' % k, ['0'])[0])
        if num and lv:
            for _ in range(num):
                equip_id = u.equip.new(k)
                u.equip._equip[equip_id]['lv'] = lv
            r.append({
                'name': v['name'],
                'num': num,
                'lv': lv,
                'c_id': k
            })
    u.equip.save()
    return give_equip(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def give_gem(req, msg=None):
    """# give_gem: 觉醒宝石展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    gem = game_config.gem
    r = []
    for k, v in gem.iteritems():
        r.append({
            'c_id': k,
            'name': '%s%s' % (v['last_name'], v['first_name']),
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/gem.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_gem_commit(req):
    """# give_gem_commit: 觉醒宝石提交
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    gem = game_config.gem
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    for k, v in gem.iteritems():
        num = int(params.get('gem_num_%s' % k, ['0'])[0])
        if num:
            for _ in range(num):
                u.gem.add(k)
            r.append({
                'name': '%s%s' % (v['last_name'], v['first_name']),
                'num': num,
                'c_id': k
            })
    u.gem.save()
    return give_gem(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def give_pet(req, msg=None):
    """# give_pet: 宠物展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    pet_config = game_config.pet_detail
    r = []
    for k, v in pet_config.iteritems():
        r.append({
            'unique_pet_id': k,
            'name': v['name'],
        })
    r.sort(key=lambda x: x['unique_pet_id'])
    return render(req, 'admin/pet.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_pet_commit(req):
    """# give_pet_commit: 提交宠物
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    pet_config = game_config.pet_detail
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    save_item = False
    save_pets = False
    for k, v in pet_config.iteritems():
        num = int(params.get('pet_num_%s' % k, ['0'])[0])
        if num:
            for _ in range(num):
                tempid = u.pets.new(k)
                if isinstance(tempid, tuple):
                    save_item = True
                else:
                    save_pets = True
            r.append({
                'name': v['name'],
                'num': num,
                'unique_pet_id': k
            })
    if save_pets:
        u.pets.save()
    if save_item:
        u.item.save()
    return give_pet(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def give_seed(req, msg=None):
    """# give_seed: 无主之地种子的展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    seed = game_config.seed
    r = []
    for k, v in seed.iteritems():
        r.append({
            'c_id': k,
            'name': v['name'],
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/seed.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_seed_commit(req):
    """# give_seed_commit: 无主之地种子的提交
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    seed = game_config.seed
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    flag = False
    for k, v in seed.iteritems():
        num = int(params.get('seed_num_%s' % k, ['0'])[0])
        if num:
            u.public_land.add(k, num)
            flag = True
            r.append({'name': v['name'],
                      'num': num,
                      'c_id': k})
    if flag:
        u.public_land.save()
    return give_seed(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def give_material(req, msg=None):
    """# give_material: 勋章材料的展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    material = game_config.material
    r = []
    for k, v in material.iteritems():
        r.append({
            'c_id': k,
            'name': v['name'],
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/material.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_material_commit(req):
    """# give_material_commit: 勋章材料的提交
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    material = game_config.material
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    flag = False
    for k, v in material.iteritems():
        num = int(params.get('material_num_%s' % k, ['0'])[0])
        if num:
            u.medal.add_material(k, num)
            flag = True
            r.append({
                'name': v['name'],
                'num': num,
                'c_id': k
            })
    if flag:
        u.medal.save()
    return give_material(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def give_medal(req, msg=None):
    """# give_medal: 勋章的展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    medal = game_config.medal
    r = []
    for k, v in medal.iteritems():
        r.append({
            'c_id': k,
            'name': v['name'],
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/medal.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_medal_commit(req):
    """# give_medal_commit: 勋章的提交
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    medal = game_config.medal
    uid = params.get('user_id')[0]

    u = User.get(uid)
    r = []
    flag = False
    for k, v in medal.iteritems():
        num = int(params.get('medal_num_%s' % k, ['0'])[0])
        if num:
            u.medal.add_medal(k, num)
            flag = True
            r.append({
                'name': v['name'],
                'num': num,
                'c_id': k
            })
    if flag:
        u.medal.save()
    return give_medal(req, {
        'uid': uid,
        'msg': r
    })


@require_permission
def refresh_outlets(req):
    """# refresh_outlets: 刷新限购商城
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    from models.shop import Shop
    msg = ''
    if req.request.method == 'POST':
        servers = settings.get_new_server([2, 3])   # 2老服、3老老服、
        for server in servers:
            Shop.update_outlets(server)
        msg = 'success'

    return render(req, 'admin/outlets.html', **{
        'msg': msg if msg else {},
    })


@require_permission
def mv_account(req):
    """# mv_account: 移动账号 替换账号
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    msg = ''
    if req.request.method == 'POST':
        old_uid = req.get_argument('old_uid')
        new_uid = req.get_argument('new_uid')
        res_user = User.get(old_uid)
        tag_user = User.get(new_uid)
        if res_user.user_m.inited or tag_user.user_m.inited:
            msg = 'fail'
        else:
            res_account = res_user.account
            tag_account = tag_user.account

            # 移动User
            res_user.account = tag_account
            tag_user.account = res_account
            res_user.save()
            tag_user.save()

            # 移动UnameUid
            res_uu = UnameUid.get(res_account)
            tag_uu = UnameUid.get(tag_account)
            res_uu_data = {}
            for res_k in res_uu._attrs:
                res_uu_data[res_k] = getattr(res_uu, res_k)
            res_uu_data = pickle.loads(pickle.dumps(res_uu_data))

            tag_uu_data = {}
            for tag_k in tag_uu._attrs:
                tag_uu_data[tag_k] = getattr(tag_uu, tag_k)
            tag_uu_data = pickle.loads(pickle.dumps(tag_uu_data))

            res_uu.__dict__.update(tag_uu_data)
            tag_uu.__dict__.update(res_uu_data)
            res_uu.save()
            tag_uu.save()

            # 移动UidServer
            for uid in res_uu_data['servers'].itervalues():
                us = UidServer.get(uid)
                us.account = tag_account
                us.save()

            for uid in tag_uu_data['servers'].itervalues():
                us = UidServer.get(uid)
                us.account = res_account
                us.save()

            msg = 'success'

    return render(req, 'admin/mv_account.html', **{
        'msg': msg if msg else {},
    })


@require_permission
def skill(req, battle_msg=''):
    """# skill: 上传skill的页面, 同时展示skill
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    script_path = settings.BASE_ROOT + '/logics/skill_script/'
    root, dir, files = list(os.walk(script_path))[0]
    fls = [i for i in files if (i.endswith('.py') and i != '__init__.py')]
    fls.sort()
    return render(req, 'admin/skill.html', **{
        'own_file': fls,
        'battle_result': battle_msg
    })


@require_permission
def code_index(req, codes=[], history=[]):
    '''
    激活激活码页面
    :param req:
    :param codes: 生成的激活码
    :param history:
    :return:
    '''
    from logics.code import check_time
    from models.code import ActivationCode

    ac = ActivationCode()
    show_code_config = []
    show_code_status = {}
    for code_id, config in game_config.code.iteritems():
        if check_time(config):
            show_code_config.append(code_id)
            all_num = ac.count(code_id)
            non_num = ac.count(code_id, non_use=True)
            one_num = ac.count(code_id, history=True)

            show_code_status[code_id] = {
                'all_num': all_num,
                'non_num': non_num,
                'use_num': all_num - non_num,
                'one_num': one_num,
                'name': config['name'],
            }

    kwargs = dict(
        show_code_config=show_code_config,
        show_code_status=show_code_status,
        show_codes=codes,
        history=history,
    )

    return render(req, 'admin/code.html', **kwargs)


@require_permission
def code_create(req):
    """生成激活码
    """
    from models.code import ActivationCode

    code_id = int(req.get_argument('code_id'))
    num = int(req.get_argument('num'))

    ac = ActivationCode()
    codes = ac.create_code(code_id, num)

    return code_index(req, codes=codes)


def code_show(req):
    """显示部分激活码
    """
    from models.code import ActivationCode

    code_id = int(req.get_argument('code_id'))
    create = req.get_argument('create', '')
    code_non = req.get_argument('code_non', '')
    code_one = req.get_argument('code_one', '')
    ac = ActivationCode()
    if code_non:
        codes = ac.find_keys(code_id, subhistory=create)
    elif code_one:
        codes = ac.find_keys(code_id, history=create)
    else:
        codes = ac.find_keys(code_id, True)

    return code_index(req, codes=list(codes), history=ac.history_count(code_id))


def code_history(req):
    """历史生成激活码记录
    """
    from models.code import ActivationCode

    code_id = int(req.get_argument('code_id'))
    ac = ActivationCode()

    return code_index(req, history=ac.history_count(code_id))


@require_permission
def open_positions(req):
    '''
    开启所有站位
    :param req:
    :return:
    '''
    params = req.summary_params()
    uid = params.get('uid')[0]
    u = User.get(uid)
    for i in game_config.role:
        u.cards.add_new_open_position(i)
        u.cards.add_position_num(i)
    u.cards.save()
    return user(req, msgs=[u'站位全部开启'])


@require_permission
def open_leader_skill(req):
    '''
    开启所有主角技能
    :param req:
    :return:
    '''
    params = req.summary_params()
    uid = params.get('uid')[0]
    u = User.get(uid)
    u.skill.skill = {}
    for k, v in game_config.leader_skill.iteritems():
        u.skill.skill[k] = v['max_level']
    u.skill.save()
    return user(req, msgs=[u'获得所有主角技能'])


@require_permission
def open_formations(req):
    '''
    开启所有阵型
    :param req:
    :return:
    '''
    params = req.summary_params()
    uid = params.get('uid')[0]
    u = User.get(uid)
    for i in game_config.role:
        u.cards.add_new_formation(i)
    u.cards.save()
    return user(req, msgs=[u'阵型全部开启'])


@require_permission
def recapture_all_building(req):
    '''
    抢占所有城市
    :param req:
    :return:
    '''
    params = req.summary_params()
    uid = params.get('uid')[0]
    u = User.get(uid)
    # d = {}
    # for city, map in game_config.map.iteritems():
    #     buildings = set()
    #     for row in map:
    #         for cell in row:
    #             if cell > 0:
    #                 buildings.add(str(cell))
    #     d[city] = list(buildings)
    u.private_city.user_building = {}
    u.private_city.final_recapture = game_config.map_mapping.keys()
    u.private_city.finish_base = True
    u.private_city.finish_hell = True           # 英雄
    u.private_city.finish_purgatory = True      # 炼狱
    u.private_city.recapture_log = {}
    all_city_regain_percent = {}
    for k in game_config.map.iterkeys():
        if 400 < int(k) <= 420:
            continue
        all_city_regain_percent[k] = 100
    u.private_city.city_regain_percent = all_city_regain_percent
    u.private_city.world_level = max(game_config.integration_world)
    u.private_city.world_score = game_config.integration_world[u.private_city.world_level]['top']
    u.private_city.save()
    return user(req, msgs=[u'the world is YOURS'])


@require_permission
def finish_all_guide(req):
    '''
    跳过所有新手引导
    :param req:
    :return:
    '''
    uid = req.get_argument('uid')
    u = User.get(uid)
    u.guide.clear()
    for sort, v in game_config.guide.iteritems():
        step = max(v)
        u.user_m.do_guide(sort, step, save=False)
    u.save()
    return user(req, msgs=[u'finish all guide'])


@require_permission
def upload_skill(req):
    """# upload: 上传skill的处理
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    file_obj = req.request.files.get('script', None)
    is_leader_skill = req.get_arguments('is_leader_skill')
    file_name = settings.BASE_ROOT + 'logics/skill_script/' + file_obj[0]['filename']
    file_body = file_obj[0]['body']
    import sys
    try:
        exec (file_body)
    except Exception, e:
        lines = traceback.format_exc()
        return render(req, 'admin/skill_error.html', **{
            'error_name': e.__class__.__name__,
            'error_msg': lines,
        })
    hfile = open(file_name, 'wb')
    hfile.write(file_body)
    hfile.close()
    try:
        module_name = file_obj[0]['filename'].replace('.py', '')
        if module_name in sys.modules:
            del sys.modules[module_name]
        # del sys.modules['logics.skill_script']
        from logics.skill_script import all_skill, load_all
        load_all()
        if not is_leader_skill:
            battle_result = card_skill_test(module_name)
        else:
            battle_result = leader_skill_test(module_name)
    except Exception, e:
        lines = traceback.format_exc()
        return render(req, 'admin/skill_error.html', **{
            'error_name': e.__class__.__name__,
            'error_msg': lines,
        })
    return skill(req, battle_result)


def leader_skill_test(skill_script_test_name):
    """# skill_test: docstring 英雄主角技能
    args:
        skil:    ---    arg
    returns:
        0    ---
    """
    skill_script_test = skill_script_test_name.replace(' ', '').replace('.py', '')
    test_skill_config = {
        'name'             : unicode('''霍格罗伊～～沙发！！！''', 'utf-8'),
        'icon'             : 'longya',
        'story'            : unicode('''对敌方造成己方魔攻最高值%s的伤害''', 'utf-8'),
        'tree'             : 1,
        'xy'               : [1, 3],
        'ready_time'       : 0,
        'cd'               : 10,
        'pre_skill'        : [],
        'max_level'        : 5,
        'is_positive'      : 1,
        'base_effect1'     : 90,
        'base_effect2'     : 0,
        'add_effect1'      : 10,
        'add_effect2'      : 0,
        'script'           : skill_script_test,
        'action'           : '',
    }
    test_skill_cid = 99999999999999999999
    import game_config
    game_config.leader_skill[test_skill_cid] = test_skill_config
    from models import fake
    user_a = fake.robot_for_skill_test('user_a')
    user_d = fake.robot_for_skill_test('user_d')

    leader_skill = {}
    for k in game_config.leader_skill.iterkeys():
        leader_skill[k] = 5
    user_a.skill.skill = leader_skill
    user_a.skill.skill[test_skill_cid] = 5
    user_a.skill.skill_1 = test_skill_cid
    from logics.battle import Battle

    b = Battle(user_a, user_d)
    # 战斗前初始化数据
    for i in range(5):
        if b.m_tAtkArray[i] != 0:
            b.setMembers(i)
            if b.m_tDfdArray[i] != 0:
                b.setMembers(i + 100)

    from logics.skill_script import all_skill
    all_skill[skill_script_test].ZCRealSkill(b, 0, 5)
    for i, bl in enumerate(b.m_tBuffList):
        if bl:
            for bu in bl:
                bu.m_func(b, i if i < 5 else i - 5 + 100)

    battle_result = b.m_dMsg
    import json
    battle_result = json.dumps(
        battle_result,
        ensure_ascii=False,
        encoding="utf-8",
        indent=4,
    )
    return battle_result


def card_skill_test(skill_script_test_name):
    """# skill_test: docstring
    args:
        skil:    ---    arg
    returns:
        0    ---
    """
    skill_script_test = skill_script_test_name.replace(' ', '').replace('.py', '')

    test_skill_cid = -10099
    import game_config
    test_skill_config = copy.deepcopy(game_config.skill_detail.values()[0])
    test_skill_config.update({
        'skill_name': unicode('''好有根！！！''', 'utf-8'),
        'skill_story': '',
        'skill_icon': '',
        'skill_quality': 3,
        'max_lv': 99,
        'is_evolution': 111,
        'is_learn': 1,
        'action': 1,
        'sprite_py': skill_script_test,
        'resource_type': 1,
        'resource_count': 10000,
    })
    game_config.skill_detail[test_skill_cid] = test_skill_config
    from models import fake
    user_a = fake.robot_for_skill_test('user_a', test_skill_cid)
    user_d = fake.robot_for_skill_test('user_d')
    from logics.battle import Battle

    b = Battle(user_a, user_d)
    # 战斗前初始化数据
    for i in range(5):
        if b.m_tAtkArray[i] != 0:
            b.setMembers(i)
            if b.m_tDfdArray[i] != 0:
                b.setMembers(i + 100)

    from logics.skill_script import all_skill
    all_skill[skill_script_test].ZCRealSkill(b, 0, 20, 432)
    for i, bl in enumerate(b.m_tBuffList):
        if bl:
            for bu in bl:
                if bu:
                    bu.m_func(b, i if i < 5 else i - 5 + 100)

    battle_result = b.m_dMsg
    import json
    battle_result = json.dumps(
        battle_result,
        ensure_ascii=False,
        encoding="utf-8",
        indent=4,
    )
    return battle_result


@require_permission
def skill_test(req):
    """# card_skill_test: 测试卡牌的技能
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    try:
        skill_script_test = req.get_argument('script_name')
        is_leader_skill = req.get_arguments('is_leader_skill')
        if is_leader_skill:
            battle_result = leader_skill_test(skill_script_test)
        else:
            battle_result = card_skill_test(skill_script_test)
        return skill(req, battle_result)
    except Exception, e:
        lines = traceback.format_exc()
        return render(req, 'admin/skill_error.html', **{
            'error_name': e.__class__.__name__,
            'error_msg': lines,
        })


@require_permission
def del_skill_script(req):
    """# del_skill_script: 删除一个错误技能脚本
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    file_name = req.get_argument('del_file', None)
    file_name = file_name.strip('.py')
    file = settings.BASE_ROOT + '/logics/skill_script/' + file_name + '.py'
    os.system('rm %s' % file)
    return skill(req)


@require_permission
def server_config_type(req):
    '''
    服务器的类型 1新服 2老服 3老老服 4新区
    :param req:
    :return:
    '''
    server = req.get_argument('server')
    config_uri = '%s/config/?method=server_env' % settings.SERVERS[server]['server']
    try:
        f = urllib2.urlopen(config_uri)
        data_str = f.read()
        data = json.loads(data_str)
        server_config_type = {server: data.get('data', {}).get('config_type', -1)}
    except:
        server_config_type = {server: -2}
    return server_list(req, server_config_type=server_config_type)


@require_permission
def server_change(req):
    """# server_change: 修改一个服务的属性，name和是否开放
    """
    msg = []
    server_key = req.get_argument('server_key')
    sc = None
    if server_key == 'master':
        msg.append(u'master不能被修改')
    else:
        server_name = req.get_argument('server_name', u'')
        is_open = int(req.get_argument('is_open'))
        flag = int(req.get_argument('flag'))
        sort_id = int(req.get_argument('sort_id'))
        if is_open and not server_name:
            msg.append(u'赐名方可开放')
        else:
            from models.config import ServerConfig
            sc = ServerConfig.get()
            sc.config_value[server_key]['name'] = server_name
            if not sc.config_value[server_key]['is_open'] and bool(is_open):
                if sc.config_value[server_key]['open_time'] <= 0:
                    sc.config_value[server_key]['open_time'] = int(time.time())
            sc.config_value[server_key]['is_open'] = bool(is_open)
            sc.config_value[server_key]['flag'] = flag
            sc.config_value[server_key]['sort_id'] = sort_id

            msg.append(u'%s-%s changed' % (server_key, server_name))
            sc.save()

    return server_list(req, server_config_obj=sc, msg=msg)

@require_permission
def battle_index(req, battle_process=None, battle_result=None, **kwargs):
    """battle_test: 战斗模拟
    """
    team_pos = [1, 2, 3, 4, 5, 11, 12, 13]

    kwargs = dict(
        team_pos=team_pos, args=req.summary_params(),
        card_detail=game_config.character_detail,
        card_detail_sort=sorted(game_config.character_detail.iteritems(), key=lambda x: int(x[0])),
        skill_detail=game_config.skill_detail,
        skill_detail_sort=sorted(game_config.skill_detail.iteritems(), key=lambda x: int(x[0])),
        formation=game_config.formation,
        battle_process=battle_process,
        battle_result=battle_result, **kwargs
    )

    return render(req, 'admin/battle_test.html', **kwargs)


@require_permission
def battle_test(req):
    from logics.battle import Battle as BattleLogic
    from parse_battle import parse_battle_result

    team_pos = [1, 2, 3, 4, 5, 11, 12, 13]
    attacker = User('test')
    defender = User('test1')

    for p, user in (('a', attacker), ('d', defender)):
        user.cards.reset()
        formation = int(req.get_argument('%s-f_id' % p, 1))
        user.cards.formation['current'] = formation             # 当前的阵型

        for i in team_pos:
            c_id = int(req.get_argument('%s-c_id-%d' % (p, i), 0))
            c_lv = int(req.get_argument('%s-c_lv-%d' % (p, i), 1))
            s_id1 = int(req.get_argument('%s-s_id1-%d' % (p, i), 0))
            s_lv1 = int(req.get_argument('%s-s_lv1-%d' % (p, i), 1))
            s_id2 = int(req.get_argument('%s-s_id2-%d' % (p, i), 0))
            s_lv2 = int(req.get_argument('%s-s_lv2-%d' % (p, i), 1))
            s_id3 = int(req.get_argument('%s-s_id3-%d' % (p, i), 0))
            s_lv3 = int(req.get_argument('%s-s_lv3-%d' % (p, i), 1))
            s_id4 = int(req.get_argument('%s-s_id4-%d' % (p, i), 0))
            s_lv4 = int(req.get_argument('%s-s_lv4-%d' % (p, i), 1))
            s_id5 = int(req.get_argument('%s-s_id5-%d' % (p, i), 0))
            s_lv5 = int(req.get_argument('%s-s_lv5-%d' % (p, i), 1))

            if c_id in game_config.character_detail:
                card_id = user.cards.new(c_id, s_1=(s_id1, s_lv1), s_2=(s_id2, s_lv2), s_3=(s_id3, s_lv3), s_4=(s_id4, s_lv4), s_5=(s_id5, s_lv5))
                user.cards._cards[card_id]['lv'] = c_lv
                user.cards._cards[card_id]['pos'] = i

    tempBattle = BattleLogic(attacker, defender)
    battle_result = tempBattle.start()
    battle_process = parse_battle_result(battle_result, game_config)

    return battle_index(req, battle_process=battle_process, battle_result=battle_result)


@require_permission
def gacha_test(req):
    u = User.get('test')
    data = {
        'game_config': game_config,
        'rs': [],
        'times': 1,
        'g_id': '',
        'counts': [],
    }
    counts = {}
    if settings.DEBUG and req.request.method == 'POST':
        g_id = int(req.get_argument('g_id'))
        times = int(req.get_argument('times'))
        u.gacha.check_config(u.level, for_test=True)
        data['g_id'] = g_id
        data['times'] = times
        for i in xrange(times):
            g = Gacha(u, g_id)
            rc, d, item = g.using_gacha(for_test=True)
            for i in d:
                if i in counts:
                    counts[i] += 1
                else:
                    counts[i] = 1
                if len(data['rs']) < 100:
                    data['rs'].append((d, u.gacha.gacha[g_id]['point'], item))

            counts = [(card_id, count, game_config.character_detail[card_id]['quality']) for card_id, count in counts.iteritems()]
            data['counts'] = sorted(counts, key=lambda x: x[-1], reverse=True)

    return render(req, 'admin/gacha_test.html', **data)


def get_buy_coin_value():
    '''
    获取购买钻石
    :return:
    '''
    buy_coin_values = []
    # for production_id, scheme in game_config.charge_scheme.iteritems():
    #     buy_coin_values.append((production_id, game_config.charge[scheme]))
    for k, v in game_config.charge.iteritems():
        buy_coin_values.append((k, v))
    return sorted(buy_coin_values, key=lambda x: x[1]['price'])


@require_permission
def virtual_index(req):
    '''
    虚拟充值 充值详情
    :param req:
    :return:
    '''
    data = {'msg': '', 'user': None, 'buy_coin_values': []}
    if req.request.method == 'POST':
        uid = req.get_argument('user_id', '')
        u = User.get(uid)
        if not u.regist_time:
            data['msg'] = u'查无此人'
            return render(req, 'admin/payment/virtual_index.html', **data)
        else:
            data['user'] = u
            data['buy_coin_values'] = get_buy_coin_value()
            return render(req, 'admin/payment/virtual_pay.html', **data)
    return render(req, 'admin/payment/virtual_index.html', **data)


@require_permission
def virtual_pay(req):
    '''
    后台提交虚拟充值
    :param req:
    :return:
    '''
    uid = req.get_argument('user_id')
    goods_id = req.get_argument('goods_id')
    kcoin = int(req.get_argument('coin'))
    reason = req.get_argument('reason')
    times = req.get_argument('times', 1)

    if 'admin' in req.request.arguments:
        tp = 'admin'            # 后台代充  算真实收入
    elif 'admin_test' in req.request.arguments:
        tp = 'admin_test'       # 管理员测试用 不算真实收入
    else:
        tp = ''

    data = {'msg': '', 'user': None, 'buy_coin_values': get_buy_coin_value()}
    u = User.get(uid)
    if not u.regist_time:
        data['msg'] = u'查无此人'
        return render(req, 'admin/payment/virtual_index.html', **data)
    if not reason:
        data['msg'] = u'充值原因呢'
        return render(req, 'admin/payment/virtual_index.html', **data)

    approval_payment = ApprovalPayment()

    key = approval_payment.add_payment(req.uname, uid, goods_id, reason, times, tp)

    admin = auth.get_admin_by_request(req)

    if settings.DEBUG or (admin and 'for_approval' in admin.right_links):
        approval_payment.approval_payment(req.uname, key, refuse=False)
        data['msg'] = u"充值成功"
    else:
        data['msg'] = u"已经提交审批"
    data['user'] = u
    return render(req, 'admin/payment/virtual_index.html', **data)


@require_permission
def pay_index(req):
    """列表显示最近一个月的充值记录
    日期-充值次数-充值人数-充值总额-查看详细
    Args:
        start_day  -- 开始时间
        end_day    -- 结束时间
    Returns:
        st_list_0=[{},{},{},]
    """
    start_day = req.get_argument('start_day', None)
    end_day = req.get_argument('end_day', None)

    now = datetime.datetime.now()
    filter_admin_pay = getattr(settings, 'FILTER_ADMIN_PAY', True)  # FILTER_ADMIN_PAY
    day_interval = [(now - datetime.timedelta(days=i)).isoformat()[:10] for i in xrange(0, 31 if filter_admin_pay else 75)]

    if not start_day:
        start_day = day_interval[30]
    if not end_day:
        end_day = day_interval[0]

    payment = ModelPayment()
    data = {}

    s_day = '%s 00:00:00' % start_day
    e_day = '%s 23:59:59' % end_day

    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    for item in mysql_conn.find(s_day, e_day):
        key = item['order_time'][:10]
        data.setdefault(key, []).append(item)

    st_list_0 = []
    all_data = dict(all_pay_times=0, all_person_times=0, all_pay_coins=0, all_pay_rmbs=0, all_admin_pay_rmbs=0, all_platform_pay_rmbs=0)

    for day, item_list in data.iteritems():
        user_ids, pay_coins, pay_rmbs, admin_pay_rmbs, really_pay_rmbs = set(), 0, 0, 0, 0

        for item in item_list:
            user_ids.add(item['user_id'])
            pay_coins += item['order_coin']
            pay_rmbs += item['order_money']
            if 'admin_test' in item['platform']:
                admin_pay_rmbs += item['order_money']
            else:
                really_pay_rmbs += item['order_money']

        all_data['all_pay_times'] += len(item_list)         # 所有支付的次数            充值次数
        all_data['all_person_times'] += len(user_ids)       # 所有人充值的次数          充值人数
        all_data['all_pay_coins'] += pay_coins              # 所有的钻石               总额(钻石)
        all_data['all_pay_rmbs'] += pay_rmbs                # 所有的支付人民币          总额(人民币)
        all_data['all_admin_pay_rmbs'] += admin_pay_rmbs    # 所有测试真实的充值人民币    管理员测试
        all_data['all_platform_pay_rmbs'] += really_pay_rmbs    # 所有真实的充值人民币   平台充值&后台代充

        st_list_0.append({
            'day': day,                                     # 天
            'pay_coins': pay_coins,                         # 总额(钻石)
            'pay_times': len(item_list),                    # 充值次数
            'pay_rmbs': pay_rmbs,                           # 总额(人民币)
            'admin_pay_rmbs': admin_pay_rmbs,               # 管理员测试
            'really_pay_rmbs': really_pay_rmbs,             # 平台充值&后台代充
            'person_times': len(user_ids),                  # 充值人数
        })

    st_list_0.sort(key=lambda x: x['day'], reverse=True)

    return render(req, 'admin/payment/index.html', **{
        'st_list_0': st_list_0,
        'day_interval': day_interval,
        'start_day': start_day,
        'end_day': end_day,
        'environment': settings.SERVICE_NAME,
        'all_data': all_data,
        'filter_admin_pay': filter_admin_pay
    })


@require_permission
def pay_day(req):
    """ 按照天查询充值记录
    Args:
        year      -- 年
        month     -- 月
        day       -- 日
    Returns:
        st_list_0=[{},{},{},]
    """
    day_dt = req.get_argument('day', None)

    add_kcoins = pay_rmbs = 0
    s_day = '%s 00:00:00' % day_dt
    e_day = '%s 23:59:59' % day_dt

    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    st_list_0 = sorted(mysql_conn.find(s_day, e_day), key=lambda x: x['order_time'], reverse=True)

    names_cache = {}
    for x in st_list_0:
        x['pay_rmb'] = x['order_money'] * 1
        pay_rmbs += x['pay_rmb']                # 支付的人民币
        add_kcoins += x['order_coin']           # 支付的钻石
        if x['user_id'] not in names_cache:
            names_cache[x['user_id']] = User.get(x['user_id']).name
        x['name'] = names_cache[x['user_id']]

    return render(req, 'admin/payment/pay_day.html', **{
        'start_day': day_dt,
        'end_day': day_dt,
        'st_list_0': st_list_0,
        'add_kcoins': add_kcoins,
        'pay_rmbs': pay_rmbs,
        'environment': settings.SERVICE_NAME,
    })


@require_permission
def pay_person(req):
    '''
    查询某人的充值记录
    :param req:
    :return:
    '''
    user_id = req.get_argument('user_id')

    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    st_list_0 = sorted(mysql_conn.find_by_uid(user_id), key=lambda x: x['order_time'], reverse=True)

    add_kcoins, pay_rmbs, admin_pay_rmbs, really_pay_rmbs = 0, 0, 0, 0
    names_cache = {}
    for x in st_list_0:
        x['pay_rmb'] = x['order_money'] * 1
        pay_rmbs += x['pay_rmb']
        add_kcoins += x['order_coin']
        if x['user_id'] not in names_cache:
            names_cache[x['user_id']] = User.get(x['user_id']).name
        x['name'] = names_cache[x['user_id']]
        if 'admin_test' in x['platform']:
            admin_pay_rmbs += x['order_money']
        else:
            really_pay_rmbs += x['order_money']

    return render(req, 'admin/payment/pay_person.html', **{
        'admin_pay_rmbs': admin_pay_rmbs,
        'really_pay_rmbs': really_pay_rmbs,
        'st_list_0': st_list_0,
        'add_kcoins': add_kcoins,
        'pay_rmbs': pay_rmbs,
        'environment': settings.SERVICE_NAME,
        'user_id': user_id,
    })


@require_permission
def sys_time_index(req, msg=''):
    """显示系统时间
    """
    real_time = change_time.REAL_DATETIME_FUNC()
    sys_time = datetime.datetime.now()

    return render(req, 'admin/sys_time_index.html', **{
        'real_time': real_time,
        'sys_time': sys_time,
        'msg': msg,
    })


@require_permission
def send_notify(req):
    """
    发送系统邮件
    """
    msg = ''
    success = []
    error = []

    title = ''
    content = ''
    gifts = []
    str_uids = ''

    if req.request.method == 'POST':
        title = req.get_argument('title', '')
        content = req.get_argument('content', '')
        gifts = eval(req.get_argument('gifts'))
        str_uids = req.get_argument('uids', '')

        message = {
            'send_uid': 'sys',
            'send_name': 'sys',
            'send_role': 1,
            'send_level': 1,

            'content': content,
            'sort': Notify.SYS_SORT,
            'gift': [] if gifts is None else gifts,
            'icon': '',
            'title': title
        }

        # 获取所有区服的 ID
        server_ids = set()
        servers = ServerConfig.get().server_list()
        for srv in servers:
            server_ids.add(srv['server'])

        str_uids = str_uids.replace('\r', '')
        o_uids = str_uids.split("\n")

        # 除重 UIDS
        uids = set(o_uids)

        if len(uids) > 100:
            msg = u'一次发送的 UID 数不能大于 100'
        else:
            for user_id in uids:
                user_id = user_id.strip()

                # # 检查玩家 ID 的长度
                # if len(user_id) != 11:
                #     error.append(user_id)
                #     continue

                # 检查区服是否存在或者开启
                server_id = user_id[:-7]
                if server_id not in server_ids:
                    error.append(user_id)
                    continue

                # 检查是否有效的用户
                user = User.get(user_id, server_id)
                if user:
                    user.notify.add_message(message, True)
                    success.append(user_id)
                else:
                    error.append(user_id)
                    continue

    return render(req, 'admin/send_notify.html', **{
        'sub_menu': 'develop',
        'msg': msg,
        'success': success,
        'error': error,
        'title': title,
        'content': content,
        'gifts': gifts,
        'uids': str_uids,
    })


@require_permission
def status_inquiry(req):
    '''
    服务器状态
    :param req:
    :return:
    '''
    # return req.finish(u'记得去改')
    from fabric.context_managers import settings
    from fabfile import info

    # with settings(host_string='houguangdong@dev.kaiqigu.net'):
    with settings(host_string='1737785826.qq.com'):
        result = info()

    # result = [['1', 2, 4, 5, 6], [7, '2'], '3', '4', '5']
    return render(req, 'admin/status_inquiry.html', **{
        'result': result,
    })


@require_permission
def ad_activate_count(req):
    '''
    ad激活
    :param req:
    :return:
    '''
    from models.code import Adver
    data = Adver.watch_activate_count()
    return render(req, 'admin/ad_activate_count.html', **{'data': data})


@require_permission
def ad_youxiduo_count(req):
    """游戏多
    为此平台提供查询用户激活，充值情况
    """
    from models.code import Adver
    acttype = req.get_argument('acttype', '')

    today = datetime.date.today()
    start_day = today.replace(day=1).strftime('%F')     # '2020-04-01' 本月1号
    end_day = today.strftime('%F')                      # '2020-04-22'
    result_data = {}
    msg = ''
    admin = auth.get_admin_by_request(req)

    if req.request.method == 'POST':
        # 登录操作
        if acttype == 'login':
            username = req.get_argument('username', '')
            password = req.get_argument('password', '')
            admin = Admin.get(username)
            if not admin:
                msg = unicode('用户不存在', 'utf-8')
            elif not admin.check_password(password):
                msg = unicode('密码错误', 'utf-8')
            else:
                auth.login(req, admin)
        # 登录操作
        elif acttype == 'logout':
            auth.logout(req)
            admin = None
        # 查询操作
        elif acttype == 'query' and admin:
            start_day = req.get_argument('start_day', start_day)
            end_day = req.get_argument('end_day', end_day)
            all_data = Adver.query_youxiduo_count()
            result = {}
            for key, data in all_data.iteritems():
                if start_day <= key <= end_day and data:
                    result[key] = eval(data)

            result_data = sorted(result.iteritems(), reverse=True)

    return render(req, 'admin/ad_youxiduo_count.html', **{
        'result_data': result_data,
        'start_day': start_day,
        'end_day': end_day,
        'login_user': admin,
        'msg': msg,
    })


@require_permission
def server_overview(req):
    '''
    充值和在线总数
    :param req:
    :return:
    '''
    from models.config import ServerConfig

    r = {}
    uid = 'test'
    server_list = [x for x in settings.SERVERS if x != 'master']
    server_list.sort(key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
    cur_uid_per_server = {}
    cur_online_uids = 0
    today_online_users_count = 0

    server_list = ServerConfig.get().server_list()
    for _server_info in server_list:
        i = _server_info['server']
        um = User_m.get(uid, i)
        online_user_count = um.get_online_user_count()
        today_online = um.get_user_count_by_active_days(active_days=-1)     # 获取今天登录的用户
        cur_uid_per_server[i] = {
            'user_count': online_user_count,
            'pay_rmb': 0,
            'pay_users': set(),
            'server_name': _server_info['server_name'],
            'open_time': datetime.datetime.fromtimestamp(_server_info['open_time']).strftime('%F %T'),
            'newbie_count': um.get_today_new_uids(only_count=True),         # 获取当天新增用户
            'server_user_count': um.get_user_count_by_active_days(),
            'today_online': today_online,
            'redis_used_memory': um.get_redis_userd_memory(),
        }
        cur_online_uids += online_user_count                                # 获得在线用户总数
        today_online_users_count += today_online                            # 获取今天登录的用户

    formatter = '%F %T'
    now = datetime.datetime.now()
    s_dt = now.date().strftime(formatter)
    e_dt = now.strftime(formatter)

    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    user_pay = {}
    filter_admin_pay = getattr(settings, 'FILTER_ADMIN_PAY', True)          # 后台页面是否过滤 虚拟充值
    for x in mysql_conn.find(s_dt, e_dt):
        if filter_admin_pay and 'admin_test' in x['platform']:
            continue
        x['pay_rmb'] = x['order_money'] * 1
        server_id = x['user_id'][:-7]
        if server_id in cur_uid_per_server:
            cur_uid_per_server[server_id]['pay_rmb'] += x['pay_rmb']
            cur_uid_per_server[server_id]['pay_users'].add(x['user_id'])
        else:
            cur_uid_per_server[server_id] = {'pay_rmb': x['pay_rmb'], 'user_count': 0, 'pay_users': set(x['user_id'])}

        if x['user_id'] in user_pay:
            user_pay[x['user_id']] += x['pay_rmb']
        else:
            user_pay[x['user_id']] = x['pay_rmb']

    big_brother_uid, big_brother_pay, big_brother_server = '', 0, ''
    if user_pay:
        big_brother_uid, big_brother_pay = max(user_pay.iteritems(), key=lambda x: x[1])
        big_brother_server = cur_uid_per_server.get(big_brother_uid[:-7], {}).get('server_name', big_brother_server)

    r['big_brother_uid'] = big_brother_uid                              # 大佬
    r['big_brother_pay'] = big_brother_pay                              # 大佬充值的钱数
    r['big_brother_server'] = big_brother_server                        # 大佬所在的服务器
    r['today'] = now.strftime('%F')
    r['cur_online_uids'] = cur_online_uids
    r['cur_uid_per_server'] = cur_uid_per_server
    r['today_online_users_count'] = today_online_users_count
    r['user_pay'] = user_pay
    r['pay_top_server'] = 0
    r['ONLINE_USERS_TIME_RANGE'] = User_m.ONLINE_USERS_TIME_RANGE       # 判断用户在线的时间参考

    return render(req, 'admin/server_overview.html', **r)


@require_permission
def spend_person(req):
    '''
    用户消费查询
    :param req:
    :return:
    '''
    uid = req.get_argument('user_id')

    mysql_conn = MySQLConnect(settings.SPENDLOG_HOST)
    st_list_0 = sorted(mysql_conn.find_by_uid_spend(uid), key=lambda x: x['subtime'], reverse=True)

    names_cache = {}
    for x in st_list_0:
        if x['uid'] not in names_cache:
            names_cache[x['uid']] = User.get(x['uid']).name
        x['name'] = names_cache[x['uid']]

    # total = {{reduce(lambda x, y: x + y, [st['coin_num'] for st in st_list_0 if 'coin_num' in st.keys()], 0)}}
    total = sum([st['coin_num'] for st in st_list_0 if st['coin_num']])

    return render(req, 'admin/payment/spend_person.html', **{
        'st_list_0': st_list_0,
        'environment': settings.SERVICE_NAME,
        'user_id': uid,
        'total': total
    })


@require_permission
def user_logging(req):
    '''
    获取玩家的日志 获取一周之内玩家所有的日志记录
    :param req:
    :return:
    '''
    uid = req.get_argument('user_id')
    u = User.get(uid)
    l = Logging(u)
    st_list_0 = l.get_all_logging()         # 获取一周之内玩家所有的日志记录
    return render(req, 'admin/user_logging.html', **{
        'st_list_0': st_list_0,
        'environment': settings.SERVICE_NAME,
        'user_id': uid,
        'user': u,
    })


ALL_BAN_UIDS_KEY = 'all_ban_uids'


def ban_user(req):
    '''
    封号
    :param req:
    :return:
    '''
    uid = req.get_argument('user_id')
    is_ban = int(req.get_argument('is_ban'))
    global_redis = ModelPayment.redis           # 支付数据, 与用户数据分离
    u = User.get(uid)
    u.is_ban = is_ban
    u.save()
    if is_ban:
        global_redis.zadd(ALL_BAN_UIDS_KEY, **{u.uid: time.time()})
    else:
        global_redis.zrem(ALL_BAN_UIDS_KEY, u.uid)
    return user(req, msgs=['success'])


def watch_ban_uids(req):
    '''
    查看封号的玩家
    :param req:
    :return:
    '''
    global_redis = ModelPayment.redis
    uids = global_redis.zrange(ALL_BAN_UIDS_KEY, 0, -1)
    data = ','.join(uids) if uids else u'无'
    return req.finish(data)

@require_permission
def sys_time_modify(req):
    """修改系统时间
    """
    if not settings.DEBUG:
        return sys_time_index(req, msg='fail')

    sys_time = req.get_argument('sys_time', '').strip('')

    real_time = change_time.REAL_TIME_FUNC()
    if sys_time == '0' or not sys_time:
        new_time = 0
        delta_seconds = 0
    else:
        new_time = mktimestamp(sys_time, '%Y-%m-%d %H:%M:%S')
        delta_seconds = int(new_time - real_time)

    change_time.change_time(new_time)       # 更改系统时间
    ChangeTime.set(delta_seconds)

    return sys_time_index(req, msg='success')


def mktimestamp(timestr, fmt='%Y-%m-%d %H:%M:%S'):
    """转换时间字符串到时间戳
    Args:
        timestr: 时间字符串
        fmt: 对应的时间格式
    Returns:
        时间戳
    """
    struct_time = time.strptime(timestr, fmt)
    return int(time.mktime(struct_time))


@require_permission
def open_box_index(req, result=None):
    '''
    开宝箱页面
    :param req:
    :param result:
    :return:
    '''
    args = {
        'uid': '',
        'box_id': 10,
        'times': 1,
        'msg': '',
        'goods': {},
    }
    if result:
        args.update(result)
    return render(req, 'admin/open_box_index.html', **args)


@require_permission
def open_box(req):
    '''
    开宝箱
    :param req:
    :return:
    '''
    uid = req.get_argument('uid', '')
    box_id = int(req.get_argument('box_id'))
    times = int(req.get_argument('times'))
    args = {
        'uid': uid,
        'box_id': box_id,
        'times': times,
    }
    item_config =game_config.item.get(box_id)
    if item_config['is_use'] != 1:
        args['goods'] = {}
        args['msg'] = u'宝箱id不正确'
        return open_box_index(req, args)

    if not uid:
        args['goods'] = {}
        args['msg'] = u'输入uid'
        return open_box_index(req, args)

    user = User.get(uid)
    goods = []
    box_id = item_config['use_effect'][0]
    for i in range(times):
        # 开启指定box_id=13时到一定次数会触发特殊奖励
        box_config = try_replace_box_reward_by_count(user, box_id)
        for _cfg in box_config:
            if 'level' in _cfg:
                if not _cfg['num'] or not _cfg['reward'] or not _cfg['level']:
                    continue
                if not (_cfg['level'][0] <= user.level <= _cfg['level'][1]):
                    continue
            else:
                if not _cfg['num'] or not _cfg['reward']:
                    continue
            for j in range(_cfg['num']):
                goods.append(weight_choice(_cfg['reward']))

    reward = {}
    for g in goods:
        good_str = repr(g)
        if good_str not in reward:
            reward[good_str] = 1
        else:
            reward[good_str] += 1

    goods = sorted(reward.iteritems(), key=lambda x: x[1], reverse=True)
    # data =  {'food': 0,
    #         'coin': 0,
    #         'silver': 0,
    #         'metal': 0,
    #         'metalcore': 0,
    #         'energy': 0,
    #         'cards': {},
    #         'equip': {},
    #         'item': {},
    #         'exp':0,
    #         'crystal': 0,
    #         'dirt_silver': 0,
    #         'dirt_gold': 0,
    #         'action_point': 0,
    #         'arena_point': 0,
    #         'star': 0,
    #         'grace': 0,
    #         'grace_high': 0,
    #         'adv_crystal': 0,
    #         'gem': {},
    #         'enchant': 0,
    # }
    # for pkg in goods:
    #     if(pkg[0] == 1):
    #         """
    #         加食品
    #         """
    #         data['food'] += pkg[2]
    #     elif(pkg[0] == 2):
    #         """
    #         加金属(铁)
    #         """
    #         data['metal'] += pkg[2]
    #     elif(pkg[0] == 3):
    #         """
    #         加能源
    #         """
    #         data['energy'] += pkg[2]
    #     elif(pkg[0] == 4):
    #         """
    #         加能晶
    #         """
    #         data['crystal'] += pkg[2]
    #     elif(pkg[0] == 5):
    #         """
    #         加卡牌
    #         """
    #         if pkg[1] not in data['cards']:
    #             data['cards'][pkg[1]]=pkg[2]
    #         else:
    #             data['cards'][pkg[1]]+=pkg[2]
    #     elif pkg[0] == 6:
    #         """
    #         道具
    #         """
    #         if pkg[1] not in data['items']:
    #             data['items'][pkg[1]]=pkg[2]
    #         else:
    #             data['items'][pkg[1]]+=pkg[2]
    #     elif pkg[0] == 7:
    #         """装备"""
    #         if pkg[1] not in data['equip']:
    #             data['equip'][pkg[1]]=pkg[2]
    #         else:
    #             data['equip'][pkg[1]]+=pkg[2]
    #     elif pkg[0] == 8:
    #         """exp"""
    #         data['exp'] += pkg[2]
    #     elif pkg[0] == 9:
    #         """金币"""
    #         data['coin'] += pkg[2]
    #     elif pkg[0] == 10:
    #         """普通尘"""
    #         data['dirt_silver'] += pkg[2]
    #     elif pkg[0] == 11:
    #         """超能尘"""
    #         data['dirt_gold'] += pkg[2]
    #     elif pkg[0] == 13:
    #         """行动力"""
    #         data['action_point'] += pkg[2]
    #     elif pkg[0] == 14:
    #         """star"""
    #         data['star'] += pkg[2]
    #     elif pkg[0] == 15:
    #         """silver"""
    #         data['silver'] += pkg[2]
    #     elif pkg[0] == 16:
    #         """metalcore"""
    #         data['metalcore'] += pkg[2]
    #     elif pkg[0] == 17:
    #         """神恩"""
    #         data['grace'] += pkg[2]
    #     elif pkg[0] == 18:
    #         """高级神恩"""
    #         data['grace_high'] += pkg[2]
    #     elif pkg[0] == 20:
    #         """高级能晶"""
    #         data['adv_crystal'] += pkg[2]
    #     elif pkg[0] == 19:
    #         """觉醒宝石"""
    #         if pkg[1] not in data['gem']:
    #             data['gem'][pkg[1]]=pkg[2]
    #         else:
    #             data['gem'][pkg[1]]+=pkg[2]
    #     elif pkg[0] == 21:
    #         """魔光碎片"""
    #         data['enchant'] += pkg[2]
    #     elif pkg[0] == 100:
    #         """竞技场点数"""
    #         data['arena_point'] += pkg[2]
    args['goods'] = goods
    args['msg'] = u''
    args['count'] = sum(reward.itervalues())
    return open_box_index(req, args)


@require_permission
def adminlog_index(req, search_args=None, msg=None):
    '''
    管理后台的操作日志
    :param req:
    :param search_args:
    :param msg:
    :return:
    '''
    admin_logging = AdminLogging(None)
    if search_args:
        if isinstance(search_args, basestring):
            data = admin_logging.get_all_logging()
            logging_data = [i for i in data if i['admin'] == search_args]
        elif isinstance(search_args, dict) and 'search_time' in search_args:
            logging_data = admin_logging.get_logging(search_args['search_time'])
        else:
            logging_data = admin_logging.get_all_logging()
    else:
        logging_data = admin_logging.get_all_logging()
    args = {
        'logging_data': logging_data,
        'message': msg if msg else '',
    }
    return render(req, 'admin/adminlogs/index.html', **args)


@require_permission
def adminlog_search_by_name(req):
    """ 日志搜索按照玩家名称

    :param req:
    :return:
    """
    username = req.get_argument('username', '')
    if not username:
        return adminlog_index(req, msg=u"请输入账号")

    return adminlog_index(req, search_args=username)


@require_permission
def adminlog_search_by_time(req):
    """ 日志搜索

    :param req:
    :return:
    """
    search_time = req.get_argument('search_time', '')
    if not search_time:
        return adminlog_index(req, msg=u"请输入时间")

    try:
        datetime.datetime.strptime(search_time, '%Y-%m-%d')
    except:
        return adminlog_index(req, msg=u"请输入正确的时间, 例如:2015-03-28")

    return adminlog_index(req, search_args={'search_time': search_time})


@require_permission
def approval_index(req, msg=None):
    """ 审批首页

    :param req:
    :param msg:
    :return:
    """
    record = ApprovalPayment().get_all_payment()

    args = {
        'record': record,
        'message': msg if msg else '',
    }

    return render(req, 'admin/approval/index.html', **args)


@require_permission
def for_approval(req):
    """ 进行审批

    :param req:
    :param msg:
    :return:
    """
    checkbox_unrefuses = req.get_arguments('checkbox_unrefuse')
    checkbox_refuses = req.get_arguments('checkbox_refuse')

    approval_payment = ApprovalPayment()

    for key in checkbox_unrefuses:
        approval_payment.approval_payment(req.uname, key, refuse=False)     # 同意

    for key in checkbox_refuses:
        approval_payment.approval_payment(req.uname, key, refuse=True)

    return approval_index(req, msg=u'成功')


@require_permission
def search_approval(req, msg=None):
    """ 查询审批后的数据

    :param req:
    :return:
    """
    approval_payment = ApprovalPayment()

    record = approval_payment.get_all_approval_log()

    args = {
        'record': record,
        'message': msg if msg else '',
    }

    return render(req, 'admin/approval/search.html', **args)


@require_permission
def limit_hero_rank(req):
    """查询限时神将排名
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    user_id = req.get_argument('uid', '')
    date = req.get_argument('date', '')
    start = req.get_argument('start', '')
    start = int(start) if start else 1
    end = req.get_argument('end', '')
    end = int(end) if end else 20

    # 检查日期格式
    date = date.replace('/', '-')
    rank = []
    user_rank = 0
    if user_id:
        user = User.get(user_id)
        user_rank = user.reward_gacha.get_reward_gacha_rank()
        server_name = user.father_server_name
        reward = RewardGacha.get('%s1234567' % server_name, server_name)
        rank_key = reward.get_rank_key()
        backup_key = rank_key + date if date else '*'
        rank = reward.redis.zrevrange(backup_key, start-1, end-1, withscores=True)

    return render(req, 'admin/rank/limit_hero_rank.html', **{
        'sub_menu': 'user',
        'rank_list': rank,
        'user_rank': user_rank,
        'user_id': user_id,
        'date': date,
        'start': start,
        'end': end,
    })


@require_permission
def super_active_rank(req):
    """
    查询宇宙最强和神龙排名
    :param req:
    :return:
    """
    user_id = req.get_argument('uid', '')
    date = req.get_argument('date', '')
    time = req.get_argument('time', '')         # 时间段
    time = time if time else '12'
    start = req.get_argument('start', '')
    start = int(start) if start else 1
    end = req.get_argument('end', '')
    end = int(end) if end else 20

    # 检查日期格式
    date = date.replace('/', '-')
    rank = ''
    if time == '24' and date:
        year, month, day = date.split('-')
        d = datetime.datetime(int(year), int(month), int(day)) + datetime.timedelta(1)
        date_new = str(d).split()[0]        # str(d) == '2020-04-24 00:00:00'  str(d).split() ['2020-04-24', '00:00:00']
    else:
        date_new = date                     # 2020-04-23

    if user_id:
        user = User.get(user_id)
        server_name = user.father_server_name
        active = SuperActive.get('%s1234567' % server_name, server_name)
        rank_key = active.get_score_rank_key()
        rank_key_bak = '%s_%s' % (rank_key, time)
        rank_stats_key = rank_key_bak + '_stats_' + date_new
        rank = active.redis.zrevrange(rank_stats_key, start-1, end-1, withscores=True)

    return render(req, 'admin/rank/super_active_rank.html', **{
        'sub_menu': 'user',
        'rank_list': rank,
        'user_id': user_id,
        'date': date,
        'time': time,
        'start': start,
        'end': end,
    })


@require_permission
def refresh_enemy_uid(req):
    """
    刷新神域的敌人
    :param req:
    :return:
    """
    user_id = req.get_argument('uid', '')
    enemy_num = int(req.get_argument('enemy_num', 0))
    if user_id:
        user = User.get(user_id)
        from logics.god_field import GodField
        god_field = GodField(user)
        rs, data = god_field.refresh_enemy_uid(enemy_num)
        if rs:
            data['msg'] = u'没有刷新成功'

    return render(req, 'admin/god_refresh_enemy.html', **{
        'sub_menu': 'user',
        'user_id': user_id,
        'enemy_num': enemy_num if enemy_num else 0,
        'msg': data['msg'] if user_id else u'请输入uid',
    })


@require_permission
def modify_guild(req):
    """ 修改自身公会数据

    :param req:
    :return:
    """
    msg = ''
    if req.request.method == 'POST':
        uid = req.get_argument('uid')
        user = User.get(uid)
        if user.user_m.inited or user.user_m.inited:
            msg = 'player does not exist'
        else:
            ass = user.association
            if not user.association_id or ass.inited:
                msg = 'association not exist'
            elif uid in ass.player:
                msg = 'already exist'
            else:
                member_num = game_config.guild_level[ass.guild_lv]['member_num']
                if len(ass.player) >= member_num:       # 超过了工会的最大数量
                    user.association_id = 0
                    user.association_name = ''
                    user.join_association_date = 0      # 加入工会的时间
                    user.quit_ass_time = 0              # 退出工会时间
                    user.save()
                    msg = 'upper limit of the number of members'
                else:
                    ass.player.append(uid)
                    ass.save()
                    msg = 'success'

    return render(req, 'admin/modify_guild.html', **{
        'msg': msg if msg else {},
    })


user_attrs = {
    'subordinate': u'阵型下属',
    'map': u'地图详情',
    'skill': u'主角技能',
    'item': u'道具列表',
    'gacha': u'gacha活动列表',
    # 'pay': u'充值列表',
    # 'building': u'建筑行为',
    # 'friend': u'好友列表',
    'arena': u'竞技场',
    # 'active': u'活动情况',
    # 'log': u'操作日志统计',
    'equip': u'装备',
    'gem': u'宝石',
    'pet': u'宠物',
    'medal': u'勋章',
    'medal_material': u'勋章材料',
    'soul': u'英魂',
}

@require_permission
def user(req, reset_msg=None, msgs=None):
    """# user_value: 显示用户属性
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    uid = req.get_argument('uid', 'test')
    if uid == 'test':
        u = User.get(uid, 'master')
    else:
        u = User.get(uid)
    if reset_msg is None:
        reset_msg = []

    cur_date = time.localtime(u.regist_time)
    cur_date = time.strftime('%Y-%m-%d %H:%M', cur_date)
    return render(req, 'admin/user.html', **{
        'user': u,
        'reset_msg': reset_msg,
        'user_attrs': user_attrs,
        'msgs': msgs,
        'settings': settings,
        'cur_date': cur_date,
    })


@require_permission
def export(req, reset_msg=None, msgs=None):
    """# transfer user data 导出数据
    """
    uid1 = req.get_argument('export_uid', 'test')

    u = User.get(uid1)
    r = u.user_m.redis

    key_list = r.keys('*%s*' % uid1)

    l = ["""uid1 = '%s'\ndata=[""" % uid1]

    for key in key_list:
        if not 'BattleLog' in key:
            if r.type(key) == 'string':
                raw = r.get(key)
                l.append("(%r, %r)," % (key, raw))

    l.append(']')
    s = ''.join(l)
    req.set_header('Content-Type', 'application/txt')
    req.set_header('Content-Disposition', 'attachment;filename=%s.txt' % uid1)
    req.write(s)


@require_permission
def inject(req, reset_msg=None, msgs=None):
    '''
    导入数据
    :param req:
    :param reset_msg:
    :param msgs:
    :return:
    '''
    uid2 = req.get_argument('inject_uid', 'test')

    u = User.get(uid2)
    r = u.user_m.redis

    file_obj = req.request.files.get('user_file', None)
    content = file_obj[0]['body']

    f = open('%sadmin/my_value.py' % settings.BASE_ROOT, 'w+')     # A temp file to store HTTP body content, to facilitate the file reading process
    f.write(content)
    f.seek(0)

    l = []
    for i in f:
        l.append(i)

    for i in l:
        if 'uid' in i or 'data' in i:       # Simple condition selector to prevent misoperation.
            exec i

    for i in f:                             # for i in data:
        temp = i[0].split('||')
        temp[3] = uid2
        temp[2] = temp[3][:-7]              # Remove last 7 numbers of uid to get server id
        replaced_data = '||'.join(temp)

        if 'Friend' in replaced_data or 'association' in replaced_data:
            continue
        r.set(replaced_data, i[1])

    msgs = 'OK!'
    u = User.get(uid2)
    u.association_id = 0
    u._request_code['master'] = {}
    u._request_code['slave'] = {}
    u.save()
    if reset_msg is None:
        reset_msg = []

    cur_date = time.localtime(u.regist_time)
    cur_date = time.strftime('%Y-%m-%d %H:%M', cur_date)
    return render(req, 'admin/user.html', **{
        'user': u,
        'reset_msg': reset_msg,
        'user_attrs': user_attrs,
        'msgs': msgs,
        'settings': settings,
        'cur_date': cur_date
    })


@require_permission
def bulk_export(req, msgs=None):
    """# transfer user data 批量导出
    """
    server = req.get_argument('server', 'g6')
    uid_numbers = req.get_argument('uid_numbers', '50')
    uid_numbers = int(uid_numbers)
    if uid_numbers > 200 or uid_numbers < 0:
        uid_numbers = 50

    u = User.get('%s1234567' % server)           # Logic user here
    top_list = [i['uid'] for i in u.get_top(uid_numbers)['top']]    # 获取战力排行榜玩家

    r = u.user_m.redis
    result_list = []

    for uid in top_list:
        uid_info = {'uid': uid, 'origin_server': uid[:-7]}          #

        user_key = u.user_m.make_key_cls(uid, uid[:-7])
        user_data = r.get(user_key)
        uid_info[user_key] = user_data

        for item in u._model_property_candidate_list:
            if item[0] not in ['friend', 'association']:             # friend and association will cause error on testing server, so we didn't export it
                cls_instance = getattr(u, item[0])
                cls_key = cls_instance.make_key_cls(uid, uid[:-7])
                cls_data = r.get(cls_key)
                if not cls_data:
                    continue
                uid_info[cls_key] = cls_data

        result_list.append(uid_info)

    teleport_data = cPickle.dumps(result_list)

    req.set_header('Content-Type', 'application/txt')
    req.set_header('Content-Disposition', 'attachment;filename=%s.txt' % server)
    req.write(teleport_data)


@require_permission
def bulk_inject(req, reset_msg=None, msgs=None):
    '''
    批量导入
    :param req:
    :param reset_msg:
    :param msgs:
    :return:
    '''
    target_server = req.get_argument('server', 'gt1')

    if not (target_server.startswith('h') or target_server.startswith('gt') or target_server.startswith('at')): # prevent misuse
        msgs = u'禁止向外服批量导入数据!'
        return render(req, 'admin/bulk_uid_transfer.html', **{
            msgs: msgs,
        })

    u = User.get('%s1234567' % target_server)
    r = u.user_m.redis

    file_obj = req.request.files.get('user_file', None)             # 导出的源文件
    content = file_obj[0]['body']

    origin_file = cStringIO.StringIO()
    origin_file.write(content)
    origin_uid_list = cPickle.loads(origin_file.getvalue())         # 获取源uid集合

    uid_file_obj = req.request.files.get('target_uid_file', None)   # 导入的目标文件
    content2 = uid_file_obj[0]['body']

    uid_file = cStringIO.StringIO()
    uid_file.write(content2)
    target_uid_list = re.split('\r\n\s+|\r\n|\n\s+|\n', uid_file.getvalue())    # 导入的目标uid集合

    debug_flag = False
    debug_list = []

    for target_uid, origin_uid_data in itertools.izip(target_uid_list, origin_uid_list):
        origin_uid = origin_uid_data['uid']
        origin_server = origin_uid_data['origin_server']
        uid_server = target_uid[:-7]
        if uid_server != target_server:                             # 导出的服务器和导入的服务器不是同一个
            debug_flag = True
            debug_list.append(target_uid)
            continue

        for key in origin_uid_data:
            if key not in ['uid', 'origin_server']:
                origin_value = origin_uid_data[key]                 # 源数据
                temp_key = key.replace(origin_uid, target_uid)
                new_key = temp_key.replace(origin_server, target_server, 1)     # 生产新的key
                r.set(new_key, origin_value)

    for uid in target_uid_list:
        try:
            u = User.get(uid)
            u.association_id = 0
            u._request_code['master'] = {}                          # 邀请码奖励
            u._request_code['slave'] = {}
            u.save()
        except:
            continue

    msgs = u'帐号群已导入至服务器%s' % target_server

    if debug_flag == True:
        msgs = u'以下uid所在服务器与目标服务器不符，导入失败 %r' % debug_list

    return render(req, 'admin/bulk_uid_transfer.html', **{
        'msgs': msgs,
    })


@require_permission
def view_bulk_uid_transfer(req, msgs=None):
    '''
    批量账号转移
    :param req:
    :param msgs:
    :return:
    '''
    return render(req, 'admin/bulk_uid_transfer.html', **{
        'msgs': msgs,
    })


@require_permission
def user_attr(req):
    '''
    玩家属性
    :param req:
    :return:
    '''
    attr = ''
    name = ''
    for attr, tmp_name in user_attrs.iteritems():
        if attr in req.request.arguments:
            name = tmp_name
            break

    uid = req.get_argument('uid')
    u = User.get(uid)
    data = {'user': u, 'attr': attr, 'server': u'1服', 'user_attrs': user_attrs}

    if attr == 'subordinate':       # 阵型下属
        card_list = []
        _crystals = ['def', 'matk', 'patk', 'hp', 'speed']
        for k, v in u.cards._cards.iteritems():
            _cfg = game_config.character_detail[v['c_id']]
            card_list.append([
                v['id'], _cfg['name'], '%s/%s' % (v['lv'], v.get('level_max') or _cfg['level_max']),
                '/'.join([str(v['%s_crystal' % j]) for j in _crystals]), u'出战' if v['pos'] else u'未出战',
            ])
        data['card_list'] = card_list
        data['_crystals'] = '/'.join(_crystals)     # 强化
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'map':
        from logics.private_city import City
        process = []
        p = u.private_city
        cl = None
        for c_id in p.final_recapture:
            if cl is None:
                cl = City(u, c_id)

            map_id = game_config.cityid_cityorderid[str(c_id)]
            _main_story_cfg = game_config.map_main_story[map_id]
            name = _main_story_cfg['stage_name']
            # gift = u.gift
            d = [name, cl.recapture_rate(c_id)]
            for i in range(1, 4):
                d.append(u'无')      # 删除了 收复度奖励 这个功能
                continue
            process.append(d)

        for c_id in p.user_building.iterkeys():
            if cl is None:
                cl = City(u, c_id)

            map_id = game_config.cityid_cityorderid[str(c_id)]
            _main_story_cfg = game_config.map_main_story[map_id]
            name = _main_story_cfg['stage_name']
            # gift = u.gift
            d = [name, cl.recapture_rate(c_id)]
            for i in range(1, 4):
                d.append(u'无')  # 删除了 收复度奖励 这个功能
                continue
                # rate = _main_story_cfg['rate%s' % i]
                # if rate:
                #     _gift_id = gift._Gift__make_gift_id(int(map_id), i)
                #     d.append(u'未领取' if _gift_id in gift._gift else  u'已领取' if _gift_id in gift.old_gift else u'未达到')
                # else:
                #     d.append(u'无')

            process.append(d)
        data['process'] = process

        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'gacha':
        data['process'] = []
        data['today_process'] = []
        data['yestaday_process'] = []
        for k, v in u.gacha.gacha.iteritems():
            data['process'].append((game_config.gacha[v['c_id']]['story'], v['times']))

        for c_id, times in u.gacha.today_used.items():
            data['today_process'].append((game_config.gacha[c_id]['story'], times))

        for c_id, times in u.gacha.yestaday_used.items():
            data['yestaday_process'].append((game_config.gacha[c_id]['story'], times))
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'item':
        data['items'] = []
        for k, v in u.item.items.iteritems():
            # data['items'].append((k, game_config.item[k]['name'], sum(v)))
            data['items'].append({'id': k, 'name': game_config.item[k]['name'], 'num': sum(v)})
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'skill':
        data['used'] = []
        data['skills'] = []
        all_skill = []
        skill = u.skill
        for i in ['skill_%s' % i for i in '123']:
            _skill_id = getattr(skill, i, 0)
            if _skill_id:
                data['used'].append((game_config.leader_skill[_skill_id]['name'], skill.skill[_skill_id]))

        for _id, lv in skill.skill.iteritems():
            all_skill.append((game_config.leader_skill[_id]['name'], lv))

        row_size = 3
        div, mod = divmod(len(all_skill), row_size)
        for i in range(mod and div + 1 or div):     # 分行
            data['skills'].append(all_skill[i * row_size: (i + 1) * row_size])

        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'arena':
        al = ArenaLogic(u)
        data['top'] = al.get_top_20(num=100)
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'equip':
        data['equips'] = []
        for k, v in u.equip._equip.iteritems():
            # data['equips'].append((k, v['c_id'], game_config.equip[v['c_id']]['name'], v['lv'], v['pos']))
            data['equips'].append({
                'id': k,
                'c_id': v['c_id'],
                'name': game_config.equip[v['c_id']]['name'],
                'lv': v['lv'],
                'pos': v['pos'],
            })
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'gem':
        data['gems'] = []
        equiped_gems = {}
        for gems in u.gem.gem_pos.itervalues():
            for gem in gems:
                if gem != '0':
                    equiped_gems[gem] = equiped_gems.get(gem, 0) + 1
        for gid in game_config.gem.iterkeys():
            gem_config = game_config.gem.get(gid)
            if not gem_config: continue
            name = gem_config.get('last_name', '') + gem_config.get('first_name', '')
            num = equiped_gems.get(gid, 0) + u.gem._gem.get(gid, 0)
            if not num: continue
            data['gems'].append((gid, name, num))
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'pet':
        data['pets'] = []
        pet_pos_data = {}
        for i, pet in enumerate(u.pets.pet_pos):
            if pet not in ('0', '-1'):
                pet_pos_data[pet] = i + 1
        for pid, value in u.pets._pets.iteritems():
            pet_config = game_config.pet_detail.get(value['c_id'])
            if not pet_config: continue
            name = pet_config.get('name', '')
            data['pets'].append((pid, value['c_id'], name, pet_pos_data.get(pid, 0)))
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'medal':
        data['medals'] = []
        medal_pos_data = {}
        for medals in u.medal.medal_pos.itervalues():
            for medal in medals:
                if medal != '0':
                    medal_pos_data[medal] = medal_pos_data.get(medal, 0) + 1
        for medal_id in game_config.medal.iterkeys():
            medal_config = game_config.medal.get(medal_id)
            if not medal_config: continue
            name = medal_config.get('name', '')
            num = medal_pos_data.get(medal_id, 0) + u.medal._medal.get(medal_id, 0)
            if not num: continue
            data['medals'].append((medal_id, name, num))
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'medal_material':
        data['materials'] = []
        for material_id, num in u.medal.material.iteritems():
            material_config = game_config.material.get(material_id)
            if not material_config: continue
            name = material_config.get('name', '')
            data['materials'].append((material_id, name, num))
        return render(req, 'admin/user_attr.html', **data)
    elif attr == 'soul':
        data['souls'] = []
        for k, v in u.soul._souls.iteritems():
            # data['souls'].append((k, v['s_id'], game_config.soul_detail[v['c_id']]['name'], v['lv'], v['pos']))
            data['souls'].append({
                'id': k,
                's_id': v['s_id'],
                'name': game_config.soul_detail[v['s_id']]['name'],
                'lv': v['lv'],
                'pos': v['pos'],
            })
        return render(req, 'admin/user_attr.html', **data)

    return req.finish(u'"%s" 页面还未做 ' % name)


@require_permission
def change_arena_rank(req):
    '''
    修改竞技场排名
    :param req:
    :return:
    '''
    button = u"""<input type="button" onclick="javascript:history.go(-1)" value="返回"/><br/><br/>"""
    uid = req.get_argument('uid')
    u = User.get(uid)
    rank = int(req.get_argument('rank'))

    if not u.arena.exists_uid(u.uid):
        return req.finish('%s%s' % (button, u' 你还未加入竞技场好么, 先去把功夫练好了再来'))
    elif rank < 0:
        return req.finish('%s%s' % (button, u' 填个正数'))

    cur_rank = u.arena.get_rank()
    if rank != cur_rank:
        count = u.arena.get_arena_count()
        rank = count if rank > count else rank
        self_score = u.arena.get_multi_score([u.uid])[0]
        [[(target_uid, target_score)]] = u.arena.get_uids_by_rank([rank], withscores=True)

        u.arena.set_multi_score([(u.uid, target_score), (target_uid, self_score)])
        u.arena.refresh_opponent(force=True)
        u.arena.get(target_uid).refresh_opponent(force=True)

    return req.finish('%s%s' % (button, u'success'))


@require_permission
def set_user_value(req):
    """# set_user_value: 修改用户属性
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    uid = req.get_argument('uid')

    u = User.get(uid)
    for k in u.user_m._building_ability.iterkeys():     # 建筑物的等级
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    for k in u.user_m._base_attrs.iterkeys():
        if not settings.DEBUG:
            ignore = ['name', 'account', 'coin']
        else:
            ignore = ['name', 'account']
        if k in ignore:
            continue
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        if k == 'vip':
            max_vip = max(game_config.vip)
            if v > max_vip:
                v = max_vip
        setattr(u, k, v)
    for k in u.user_m._resources.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 洗炼石
    for k in u.user_m._equip_refine.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 锻造石
    for k in u.user_m._equip_forge.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 宠物的宠物技能石、经验球
    for k in u.user_m._pet_resources.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 行动力
    for k in u.user_m._action_point.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 木材
    for k in u.user_m._wood.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)
    # 魂石
    for k in u.user_m._soul_stone.iterkeys():
        v = req.get_argument(k, None)
        if not v: continue
        try:
            v = int(v)
        except:
            v = float(v)
        setattr(u, k, v)

    # 竞技场点数
    arena_point = req.get_argument('arena_point', 0)
    u.arena.point = int(arena_point)
    u.arena.save()
    integration = req.get_argument('integration', 0)
    u.god_field.integration = int(integration)
    god_integration = req.get_argument('god_integration', 0)
    u.god_field.god_integration = int(god_integration)
    u.god_field.save()
    exp_ball = req.get_argument('exp_ball', 0)  # 经验球
    u.cards.exp_ball = int(exp_ball)
    u.cards.save()
    u.save()
    return user(req)


@require_permission
def give_item(req, msg=None):
    """# give_item: 道具展示
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    r = []
    for k, v in game_config.item.iteritems():
        r.append({
            'c_id': k,
            'name': v['name'],
        })
    r.sort(key=lambda x: x['c_id'])
    return render(req, 'admin/item.html', **{
        'r': r,
        'msg': msg if msg else {},
    })


@require_permission
def give_item_commit(req):
    """# give_item_commit: 送道具
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    params = req.summary_params()
    uid = params.get('user_id')[0]
    u = User.get(uid)
    r = []
    flag = False
    for k, v in game_config.item.iteritems():
        num = int(params.get('item_num_%s' % k)[0])
        if num:
            u.item.add_item(k, num, immediate=True)
            flag = True
            r.append({'name': v['name'], 'c_id': k, 'num': num})
    if flag:
        u.item.save()
    return give_item(req, {
        'msg': r
    })


@require_permission
def XXXserver_overview(req):
    '''
    XXX服务器概况
    :param req:
    :return:
    '''
    r = {}
    uid = 'test'
    server_list = [x for x in settings.SERVERS if x != 'master']
    server_list.sort(key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
    cur_uid_list = []
    cur_online_uids = []
    for i in server_list:
        um = User_m.get(uid, i)
        online_uids = um.get_online_uids()
        cur_uid_list.append((i, online_uids))
        for _ in online_uids:
            if _[0] not in cur_online_uids:
                cur_online_uids.append(_[0])

    um = User_m.get(uid)
    today_online_uids = um.get_uids_by_active_days(active_days=-1)
    today = datetime.datetime.now().date()
    t_ts = int(time.mktime(today.timetuple()))
    # 半小时一个区间
    r['steps'] = steps = [t_ts + x * 1800 for x in range(1, 49)]
    r['newbie'] = newbie = [0] * len(steps)
    for uid, regist_time in um.get_today_new_uids(t_ts):
        newbie[bisect.bisect_left(steps, regist_time)] += 1

    for idx, ts in enumerate(steps):
        d = datetime.datetime.fromtimestamp(ts)
        steps[idx] = d.strftime('%H:%M')

    formatter = '%F %T'
    now = datetime.datetime.now()
    s_dt = now.date().strftime(formatter)
    e_dt = now.strftime(formatter)

    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    user_pay = {}
    for x in mysql_conn.find(s_dt, e_dt):
        x['pay_rmb'] = x['order_money'] * 1
        if x['user_id'] in user_pay:
            user_pay[x['user_id']] += x['pay_rmb']
        else:
            user_pay[x['user_id']] = x['pay_rmb']

    big_brother_uid, big_brother_pay = '', 0
    if user_pay:
        big_brother_uid, big_brother_pay = max(user_pay.iteritems(), key=lambda x: x[1])

    r['big_brother_uid'] = big_brother_uid
    r['big_brother_pay'] = big_brother_pay
    r['today'] = now.strftime('%F')
    r['cur_online_uids'] = cur_online_uids
    r['cur_uid_per_server'] = cur_uid_list
    r['today_online_udis'] = today_online_uids
    r['user_pay'] = user_pay
    r['pay_top_server'] = 0
    r['ONLINE_USERS_TIME_RANGE'] = User_m.ONLINE_USERS_TIME_RANGE

    return render(req, 'admin/server_overview.html', **r)


def server_online_user(req):
    '''
    服务器在线用户
    :param req:
    :return:
    '''
    uid = 'test'
    um = User_m.get(uid)
    page_size = 50
    page = abs(int(req.get_argument('page', 1))) or 1
    online_uids = um.get_online_uids()
    div, mod = divmod(len(online_uids), page_size)
    pages = div + 1 if mod else div
    if page > pages:
        page = pages
    uids = online_uids[(page - 1) * page_size: page * page_size]

    users = []
    for uid in uids:
        users.append(User(uid[0]).get_user_info())
    r = {
        'online_uids': online_uids,
        'cur_page_uids': uids,
        'cur_page': page,
        'pages': pages,
        'pre_page': max(page - 1, 0),
        'next_page': min(page + 1, pages),
        'users': users,
    }
    return render(req, 'admin/online_users.html', **r)


@require_permission
def del_item(req):
    '''
    删除道具
    :param req:
    :return:
    '''
    uid = req.get_argument('uid', 'test')
    item_id = int(req.get_argument('id'))
    item_num = int(req.get_argument('num'))

    user = User.get(uid)
    cur_num = user.item.get_item_count(item_id)
    if item_num > 0:
        user.item.del_item(item_id, cur_num)
        user.item.add_item(item_id, item_num)
    else:
        user.item.del_item(item_id, cur_num)
    user.item.save()
    req.request.arguments['item'] = 'item'
    return user_attr(req)


@require_permission
def del_equip(req):
    '''
    删除装备
    :param req:
    :return:
    '''
    uid = req.get_argument('uid', 'test')
    equip_id = int(req.get_argument('id'))
    user = User.get(uid)
    user.equip.remove(equip_id)
    user.equip.save()
    req.request.arguments['equip'] = 'equip'
    return user_attr(req)


@require_permission
def del_soul(req):
    '''
    删除英魂
    :param req:
    :return:
    '''
    uid = req.get_argument('uid', 'test')
    soul_id = req.get_argument('id')
    user = User.get(uid)
    user.soul.remove_pos(soul_id)
    user.soul.remove(soul_id)
    user.soul.save()
    req.request.arguments['soul'] = 'soul'
    return user_attr(req)


@require_permission
def user_reset(req):
    """# user_reset: docstring 重置玩家数据
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    uid = req.get_argument('uid', 'test')
    module_name = req.get_argument('reset_module', '')      # 重置模块
    reset_msg = []
    if module_name:
        u = User.get(uid)
        module = getattr(u, module_name)
        module.reset()
        reset_msg.append(module_name)
    return user(req, reset_msg)


def notice(req):
    return req.finish(u'页面还未做')