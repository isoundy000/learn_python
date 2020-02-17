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

import cPickle
import cStringIO
import re
import itertools
from lib.utils import change_time
from models.config import ChangeTime

from admin_models import Admin
from decorators import require_permission


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
def skill(req, battle_msg=''):
    """# skill: 上传skill的页面, 同时展示skill
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    script_path = settings.BASE_ROOT + '/logics/skill_script/'
    root, dir, files = list(os.walk(script_path))[0]
    fls = [i for i in files if (i.endswith('.py')) and i != '__init__.py']
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
    # from logics.battle import Battle as BattleLogic
    # from parse_battle import parse_battle_result

    team_pos = [1, 2, 3, 4, 5, 11, 12, 13]
    attacker = User('test')
    defender = User('test1')

    for p, user in (('a', attacker), ('d', defender)):
        user.cards.reset()
        formation = int(req.get_argument('%-f_id' % p, 1))


    return battle_index(req, battle_process=battle_process, battle_result=battle_result)


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

    cur_date = time.localtime(time.time())     # time.time() == u.regist_time
    cur_date = time.strftime('%Y-%m-%d %H:%M', cur_date)
    return render(req, 'admin/user.html', **{
        'user': u,
        'reset_msg': reset_msg,
        'user_attrs': user_attrs,
        'msgs': msgs,
        'settings': settings,
        'cur_date': cur_date,
    })