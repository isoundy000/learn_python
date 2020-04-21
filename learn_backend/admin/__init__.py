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

from decorators import ApprovalPayment
from admin_models import Admin
from logics.gacha import Gacha
from logics.payment import virtual_pay_by_admin
from models.payment import ModelPayment, MySQLConnect
from models.notify import Notify
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
    from logics.battle import Battle as BattleLogic
    from parse_battle import parse_battle_result

    team_pos = [1, 2, 3, 4, 5, 11, 12, 13]
    attacker = User('test')
    defender = User('test1')

    for p, user in (('a', attacker), ('d', defender)):
        user.cards.reset()
        formation = int(req.get_argument('%-f_id' % p, 1))
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
    for production_id, scheme in game_config.charge_scheme.iteritems():
        buy_coin_values.append((production_id, game_config.charge[scheme]))
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

    result = [['1', 2, 4, 5, 6], [7, '2'], '3', '4', '5']
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