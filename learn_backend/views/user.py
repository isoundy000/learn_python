#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import hashlib

import settings

from lib.utils import rand_string
from lib.utils.hexie import is_hexie
from logics.pay_award import auto_give_pay_award_week_and_month

from models.user import UnameUid, UidServer
from models.user import new_uid
from models.config import ServerConfig
from models.user import User as UserM
from models.payment import Payment as PaymentM
from models.config import ConfigRefresh

from logics import platform as platform_app         # 平台登录
from logics.gift import add_gift
from lib.utils.debug import print_log
from logics.user import User
from views import ad_click

import game_config


def loading(req):
    """# login: docstring
    args:
        env:    ---    arg
    returns:
        0    ---
    """
    return 0, {}


def loading_for_test(req):
    """# loading_for_test: 为了在关闭config下载的时候，让前端手动获得新配置
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    all_config_version, client_config_version_for_test = game_config.make_client_config_version_for_test()
    return 0, None, {
        'all_config_version': all_config_version,
        'game_config_version': client_config_version_for_test
    }


def register(req):
    """# register: 注册新用户，并且将当前的uid绑定到用户上
    args:
        req:    ---    arg
    returns:
        0    ---
        1: unicode('没有用户名或者密码', 'utf-8'),
        3: unicode('这个账户已经有人了', 'utf-8'),
        5: unicode('已经绑定的账户', 'utf-8'),
        6: unicode('缺少uid', 'utf-8'),
        7：unicode('账号只能为6-20位的字母数字组合', 'utf-8')
    """
    account = req.get_argument('account', '')
    if not (account.isalnum() and 6 <= len(account) <= 20):
        return 7, None, {}
    print account, 'zzzzzzzzzzzzzzz00000000000'
    password = req.get_argument('passwd', '')
    old_account = req.get_argument('old_account', '')
    uid = req.get_argument('user_token', '')
    if not account or not password:
        return 1, None, {}          # 没有用户名或者密码
    # if not old_account:
    #     return 2, None, {}        # 没有老账户
    if UnameUid.check_exist(account):
        return 3, None, {}          # 这个账户已经有人了
    if 'fake_account_' not in old_account or not UnameUid.check_exist(old_account):
        if old_account != account:
            uu = UnameUid.get(account)
            uu.passwd = hashlib.md5(password).hexdigest()
            server_list = ServerConfig.get().server_list()
            sid, expired = uu.get_or_create_session_and_expired()
            current_server = server_list[0]['server']
            uu.current_server = current_server
            uu.save()
            return 0, None, {
                'server_list': server_list,
                'current_server': uu.current_server,
                'ks': sid,          # now + uid 唯一标识
            }
        return 5, None, {}          # 已经绑定的账户
    if uid:
        user = User.get(uid)
    else:
        return 6, None, {}          # 缺少uid
    # server_key = settings.SERVICE_NAME

    uu = UnameUid.get(old_account)
    uu.change_account_name(account)
    uu.passwd = hashlib.md5(password).hexdigest()
    # uu.servers[server_key] = user.uid
    # uu.current_server = server_key
    sid, expired = uu.get_or_create_session_and_expired(force=True)
    uu.save()

    for uid in uu.servers.itervalues():
        us = UidServer.get(uid)
        us.account = account
        us.save()

    device_mark = req.get_argument('device_mark', '')
    device_mem = req.get_argument('device_mem', '')
    user.device_mark = device_mark
    user.device_mem = device_mem
    user.update_session_and_expired(sid, expired)
    user.account = account
    user.save()

    server_list = ServerConfig.get().server_list()
    for s in server_list:
        s['uid'] = user.uid

    return 0, user, {
        'server_list': server_list,
        'current_server': uu.current_server,
        'ks': sid,
    }


def login(req):
    """# login: 登录用户
    args:
        req:    ---    arg
    returns:
        0    ---
        1: unicode('查无此人', 'utf-8'),
        2: unicode('接头暗号不对', 'utf-8'),
    """
    account = req.get_argument('account', '')
    platform = req.get_argument('pt', '')
    if not UnameUid.check_exist(account):
        return 1, None, {}  # 查无此人
    device_mark = req.get_argument('device_mark', '')
    device_mem = req.get_argument('device_mem', '')
    uu = UnameUid.get(account)
    sid, expired = uu.get_or_create_session_and_expired(force=True)
    server_list = ServerConfig.get().server_list()
    for s in server_list:
        uid = s['uid'] = uu.servers.get(s['server'], '')
        if uid:
            u = User.get(uid)
            commit = False
            if not (u.device_mark and u.device_mark == device_mark):
                u.device_mark = device_mark
                commit = True
            if not (u.device_mem and u.device_mem == device_mem):
                u.device_mem = device_mem
                commit = True
            if u.update_session_and_expired(sid, expired):
                commit = True

            if commit:
                u.save()

    uu.cur_platform = platform

    uu.save()

    return 0, None, {
        'server_list': server_list,
        'current_server': uu.current_server,
        'ks': sid,
    }


def get_user_server_list(req):
    """# login: 交给前端用户的server_list（此步不需要验证）
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    account = req.get_argument('account', '')
    version = req.get_argument('version', '')
    # 给前端填坑
    account = account.replace('37wanA545_', '37wan_')  # 用37wan_去替换37wanA545_
    account = account.replace('pipa_new_', 'pipa_')
    replace_lua_url = True if settings.ENV_NAME in [settings.ENV_IOS, settings.ENV_STG_IOS, settings.ENV_TEST_IOS] \
                                and version >= '1.2.7' else False
    if not UnameUid.check_exist(account):
        return 0, None, {   # 查无此人
            'server_list': ServerConfig.get().server_list(replace_lua_url=replace_lua_url),     # lua的url不一样
            'current_server': '',
        }
    uu = UnameUid.get(account)
    sid, expired = uu.get_or_create_session_and_expired()
    server_list = ServerConfig.get().server_list(replace_lua_url=replace_lua_url)
    device_mark = req.get_argument('device_mark', '')
    device_mem = req.get_argument('device_mem', '')
    ip = req.request.headers.get('X-Real-Ip', '')
    for s in server_list:
        uid = s['uid'] = uu.servers.get(s['server'], '')
        s['level'] = 0
        if uid:
            u = User.get(uid)
            s['level'] = u.level
            if u.regist_time and u.name:
                commit = False
                if not (u.device_mark and u.device_mark == device_mark):
                    u.device_mark = device_mark
                    commit = True
                if not (u.device_mem and u.device_mem == device_mem):
                    u.device_mem = device_mem
                    commit = True
                if not (u.ip and u.ip == ip):
                    u.ip = ip
                    commit = True
                if u.update_session_and_expired(sid, expired):
                    commit = True
                if commit:
                    u.save()

    return 0, None, {
        'server_list': server_list,
        'current_server': '',
        'ks': sid,
    }


def get_user_server_list_huawei(req):
    """# login: 交给前端用户的server_list（此步不需要验证）
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    account = req.get_argument('account')
    old_account = req.get_argument('old_account')
    if not UnameUid.check_exist(account) and not UnameUid.check_exist(old_account):
        return 0, None, {       # 查无此人
            'server_list': ServerConfig.get().server_list(),
            'current_server': '',
        }
    if UnameUid.check_exist(account):
        uu = UnameUid.get(account)
    else:
        if UnameUid.check_exist(old_account):
            uu = UnameUid.get(account)
            old_uu = UnameUid.get(old_account)
            for k in uu._attrs.iterkeys():
                setattr(uu, k, getattr(old_uu, k))
                uu.save()
            old_uu_copy_key = old_account + '____copy'
            uu_copy = UnameUid.get(old_uu_copy_key)
            for k in uu_copy._attrs.iterkeys():
                setattr(uu_copy, k, getattr(old_uu, k))
                uu_copy.save()
            old_uu.redis.delete(old_uu._model_key)
            del old_uu
        else:
            return 0, None, {   # 查无此人
                'server_list': ServerConfig.get().server_list(),
                'current_server': '',
            }
    sid, expired = uu.get_or_create_session_and_expired()
    device_mark = req.get_argument('device_mark', '')
    device_mem = req.get_argument('device_mem', '')
    ip = req.request.headers.get('X-Real-Ip', '')
    server_list = ServerConfig.get().server_list()
    for s in server_list:
        uid = s['uid'] = uu.servers.get(s['server'], '')
        s['level'] = 0
        if uid:
            u = User.get(uid)
            s['level'] = u.level
            if u.regist_time and u.name:
                commit = False
                if not (u.device_mark and u.device_mark == device_mark):
                    u.device_mark = device_mark
                    commit = True
                if not (u.device_mem and u.device_mem == device_mem):
                    u.device_mem = device_mem
                    commit = True
                if not (u.ip and u.ip == ip):
                    u.ip = ip
                    commit = True
                if u.update_session_and_expired(sid, expired):
                    commit = True
                if commit:
                    u.save()

    return 0, None, {
        'server_list': server_list,
        'current_server': '',
        'ks': sid,
    }


def mark_user_login(req):
    """# mark_user_login: 标记用户最近登录，防多设备登录
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    user_token = req.get_argument('user_token', '')
    device_mem = req.get_argument('device_mem', '')
    frontwindow = settings.DEBUG or req.get_argument('frontwindow', '') == '5e3b4530b293b5c1f4eeca4638ab4dc1'
    u = User.get(user_token)

    if not frontwindow and (u.device_mem and u.device_mem != device_mem):
        return 9999, None, {}

    u._mark += 1
    if settings.DEBUG:
        u.device_mark = req.get_argument('device_mark', '')
    u.save()
    return 0, None, {
        'mk': u._mark,
    }


def new_account(req):
    """# new_account: 创建一个账户，作为用户绑定账户前的替代物
    args:
        env:    ---    arg
    returns:
        0    ---
    """
    version = req.get_argument('version', '')

    f_account = 'fake_account_' + rand_string(8)
    while UnameUid.check_exist(f_account):
        f_account = 'fc' + rand_string(8)
    replace_lua_url = True if settings.ENV_NAME in [settings.ENV_IOS, settings.ENV_STG_IOS, settings.ENV_TEST_IOS] and \
                              version >= '1.2.7' else False
    return 0, None, {
        'fake_account': f_account,
        'server_list': ServerConfig.get().server_list(replace_lua_url=replace_lua_url)
    }


def new_user(req):
    """# new_user: 新进入一个分服
    args:
        env:    ---    arg
    returns:
        0    ---
        return 1, None, {}      # 必须指定account
        return 2, None, {}      # 在这个服务器上已经有账户了
    """
    role = int(req.get_argument('role', '1'))
    account = req.get_argument('account', '')   # 如果不是空字符串
    # 给前端填坑
    account = account.replace('37wanA545_', '37wan_')
    account = account.replace('pipa_new_', 'pipa_')
    platform = req.get_argument('pt', '')
    server_name = req.get_argument('server_name', '')
    if not server_name:
        server_list = ServerConfig.get().server_list()
        server_name = server_list[0]['server']

    if not account:
        return 1, None, {}                      # 必须指定account

    try:
        for_ip = req.request.headers.get('X-Forwarded-For', '')
        ip = for_ip.replace('127.0.0.1', '').replace(',', '').replace(' ', '')
    except:
        ip = ''

    uid = new_uid(server_name)
    user = User.get(uid)
    user.account = account
    user.ip = ip

    us = UidServer.get(uid)
    us.server = server_name
    us.account = account

    uu = UnameUid.get(account)
    if server_name in uu.servers:
        return 2, None, {}        # 在这个服务器上已经有账户了

    uu.servers[server_name] = uid
    uu.current_server = server_name
    uu.init_platform = platform
    sid, expired = uu.get_or_create_session_and_expired(force=True)     # 服务器中各个session_sid, session_expired过期时间

    user.update_session_and_expired(sid, expired)                       # 更新本服服务器的session_sid, session_expired
    user.role = role
    role_detail_config = game_config.role_detail[role]
    role_config = game_config.role

    user.cards.position_num = role_config[1]['position_num']            # 位置数量
    user.cards.alternate_num = role_config[1]['alternate_num']          # 助威数量
    # user.cards.open_position = [int(x) for x in role_config[1]['open_position']]      # 开启的位置
    # user.cards.formation['own'] = [role_config[1]['open_formation']]                  # 阵型
    # user.cards.formation['current'] = [role_config[1]['open_formation']]              # 当前阵型

    user.food_ability = role_detail_config['food_produce']      # 生食物能力
    user.metal_ability = role_detail_config['metal_produce']    # 生铁能力
    user.energy_ability = role_detail_config['energy_produce']
    user.harbor_ability = role_config[1]['harbor']              # 避难所等级
    user.school_ability = role_config[1]['school']              # 学校等级
    user.factory_ability = role_config[1]['factory']
    user.hospital_ability = role_config[1]['hospital']
    user.laboratory_ability = role_config[1]['laboratory']

    # 初始 food、metal 都为1000
    # user.food = 99999
    # user.metal = 99999
    # user.crystal = 99999          # 能晶
    # user.energy = 99999
    # user.coin = 99999
    user.food = 3000
    user.metal = 1000
    user.energy = 1000              # 精力
    user.coin = 20
    user.silver = 300               # 银币
    user.crystal = 50

    for i in xrange(1, 11):
        card = role_detail_config['position%d' % i]
        if not card: continue
        card_id = user.cards.new(card)
        user.cards.set_alignment(card_id, i if i <= 5 else i + 5)

    for i in role_detail_config['character_bag']:
        for j in xrange(i[1]):
            card_id = user.cards.new(i[0])

    for i in role_detail_config['item']:
        user.item.add_item(i[0], i[1])

    for i in role_detail_config['equip']:
        for ii in xrange(i[1]):
            user.equip.new(i[0])

    user.is_new = 0
    user.regist_time = int(time.time())
    user.update_regist_status(user.regist_time)
    # user.exp += 20450       # 给渠道升级爽一爽
    us.save()
    uu.save()
    user.save()
    user.cards.save()
    user.item.save()
    user.equip.save()
    return 0, user, {'uid': user.uid, 'ks': sid}


def rename(env):
    """修改名字
    args:
        show_name: 显示的名字
    """
    user = env.user
    show_name = env.get_argument('show_name')
    if is_hexie(show_name):
        return 10240, {}

    user.name = show_name

    user.save()

    return 0, {'show_name': show_name}


def all_config(req):
    """# all_config: 获取所有配置
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    config_name = req.get_argument('config_name', '')
    result = {}
    if not config_name:
        config_name_list = game_config.config_name_list
        for i in config_name_list:
            if i[5]:
                result[i[0]] = getattr(game_config, i[0])
    else:
        result[config_name] = getattr(game_config, config_name)
    return 0, None, result


def guide(env):
    """新手引导
    args:
        guide_team: 模块分类
        guide_id: 已完成步骤
    """
    user = env.user
    guide_team = env.get_argument('guide_team', '')
    guide_id = env.get_argument('guide_id', '')
    if not guide_team.isdigit() or not guide_id.isdigit():
        return 1, {}

    sort = int(guide_team)
    step = int(guide_id)

    if sort in game_config.guide and step in game_config.guide[sort]:
        user.user_m.do_guide(sort, step)

    return 0, {}


def main_page(env):
    """# main_page: 进入游戏主场景
    args:
        env:    ---    arg
    returns:
        0    --
    """
    user = env.user
    building_ability = {}
    for k in user.user_m._building_ability.iterkeys():  # 建筑物信息
        building_ability[k] = getattr(user, k)

    m_id_7ku = env.get_argument('m_id_7ku', '')
    if not user.mid_qiku and m_id_7ku and user.mid_qiku != m_id_7ku:
        user.mid_qiku = m_id_7ku
        ad_click.update_qiku_mid_info(user, m_id_7ku)   # 更新设备激活信息

    # 平台标识
    platform_channel = env.get_argument('platform_channel', '')
    if user.platform_channel == '' and platform_channel != '':
        user.platform_channel = platform_channel        # 更新平台标识

    user.user_m.fetch_server_open_time()                # 开服时间
    # user.user_m.update_food_pool(need_save=False)
    # user.user_m.update_energy_pool(need_save=False)
    # user.user_m.update_metal_pool()
    user.reward.update_gift_task()
    user.cards.check_card_rank()
    user.user_m.day_refresh_like_times()
    if hasattr(user, 'auto_vip_reward'):
        user.auto_vip_reward()

    version_parameter = env.get_argument('version', '')
    is_new_version, has_version_reward = False, False
    if hasattr(user, 'version_reward'):
        is_new_version, has_version_reward = user.version_reward.check(version_parameter)

    # 自动发放悬赏令的奖励
    if hasattr(user, 'bounty_order'):
        user.bounty_order.login_auto_give_reward()
    if hasattr(user, 'server_bounty_order'):
        user.server_bounty_order.login_auto_give_reward()

    # 自动发放古灵阁的奖励
    if hasattr(user, 'gringotts'):
        user.gringotts.gringotts_auto_give_reward()

    # 检查回归玩家是否有未领取的返还钻石，进行自动邮件发放
    try:
        if hasattr(user, 'king'):
            user.king.auto_send_rebate_coin()
    except:
        pass

    # 自动给予月卡和周卡奖励
    # update on 2014-09-02: 只自动发周卡奖励
    auto_give_pay_award_week_and_month(user)
    resource = {}
    for k in user.user_m._resources.iterkeys():
        resource[k] = getattr(user, k)

    building = {}

    # 记录在线时间
    user.update_online_status()

    data = {

    }


    return 0, data


def havest(env):
    """# havest: docstring
    args:
        env:    ---    arg
    returns:
        0    ---
    """
    user = env.user

    r = {}
    for resource_name in ['food', 'metal', 'energy']:
        resource_value = getattr(user, resource_name)
        getattr(user.user_m, 'update_' + resource_name + '_pool')(need_save=False)
        resource_pool_value = getattr(user, resource_name + '_pool')
        r[resource_name] = resource_pool_value

        setattr(user, resource_name, resource_pool_value + resource_value)
        setattr(user, resource_name, '_pool', 0)

    rc, return_data = main_page(env)
    return_data['resource_add'] = r

    return 0, return_data


def info(env):
    '''
    获取玩家信息
    :param env:
    :return:
    '''
    uid = env.get_argument('uid')
    uid = uid.encode('utf-8')
    if ArenaM.is_robot(uid):
        user = ArenaM.robot_generate(uid, env.user.user_m._server_name)
    elif UserM.get_server_name(uid) not in settings.SERVERS:
        return 1, {}
    else:
        user = User(uid)
    if user.regist_time:
        return 0, user.get_user_info()
    else:
        return 1, {}


def online_award(env):
    '''
    在线奖励
    :param env:
    :return:
    '''
    user = env.user
    reward = user.get_online_award()
    rc, data = main_page(env)
    data['reward'] = reward
    return rc, data


def level_award(env):
    '''
    获取等级奖励
    :param env:
    :return:
    '''
    user = env.user
    lv = int(env.get_argument('lv'))
    config = game_config.level_gift.get(lv)
    if not config or lv not in user.level_gift:
        return 1, {}    # 奖励已领取或者已过期

    if config.get('buy', 0) > 0:
        return 2, {}

    if user.coin < config['coin']:
        return 'error_4', {}

    user.level_gift.pop(lv)
    user.coin -= config['coin']
    reward = add_gift(user, config['reward'])
    return 0, {'reward': reward}


def refresh(env):
    return 0, {}


def platform_access(env):
    """平台登录验证入口
    每个平台处理函数返回值默认返回平台ID,如果需要多个返回值，需包含openid字段表示平台ID,其它字段自定义
    Args:
        channel: 固定参数，平台名字， 区分处理函数
        session_id: 固定参数，默认平台sid, 具体每个平台含义与前端商定
        user_id: 固定参数，默认表示平台ID, 具体每个平台含义与前端商定
    登录接口
    """
    channel = env.get_argument('channel', 'cmge')

    access_funcname = 'login_verify_%s' % channel
    access_func = getattr(platform_app, access_funcname, None)

    openid = None
    if callable(access_func):
        openid = access_func(env)

    if isinstance(openid, dict):
        return 0, None, openid

    if openid is not None:
        return 0, None, {'openid': openid}

    return 1, None, {}


def top_combat(env):
    '''
    获取战力排行榜
    :param env:
    :return:
    '''
    page = int(env.get_argument('page', 0))
    if page < 0:
        page = 0
    return 0, env.user.get_top(page=page, tp='combat')


def top_level(env):
    '''
    获取等级排行榜
    :param env:
    :return:
    '''
    page = int(env.get_argument('page', 0))
    if page < 0:
        page = 0
    return 0, env.user.get_top(page=page, tp='level')


def top_gacha_score(env):
    '''
    获取抽卡排行积分
    :param env:
    :return:
    '''
    page = int(env.get_argument('page', 0))
    if page < 0:
        page = 0
    return 0, env.user.get_top(page=page, tp='gacha_score')


def top_world_boss_hurt(env):
    '''
    获取世界boss伤害排行榜
    :param env:
    :return:
    '''
    page = int(env.get_argument('page', 0))
    boss = WBM.get(1, env.user._server_name)
    p_key = boss.get_last_rank_key()
    return 0, env.user.get_top(page=page, tp='worldboss', p_key=p_key)


NEW_RANK_KEY = {
    'combat', 'level', 'gacha_score', 'orange_card',
    'purple_card', 'equipment', 'world_regain', 'commander', 'like'
}


def top_rank(env):
    """ 最强排行
        sort: combat: 战斗力, level: 等级, gacha_score: gacha积分,
                orange_card: 橙卡. purple_card: 紫卡, equipment: 装备强度,
                world_regain: 世界收复, commander: 统率能力, like: 点赞排行
        page: 页面默认为0, 首页

        -1: 没有该类排行榜

    :param env:
    :return:
    """
    sort = env.get_argument('sort', '')
    page = int(env.get_argument('page', 0))
    if sort not in NEW_RANK_KEY:
        return -1, {}

    if page < 0:
        page = 0

    return 0, env.user.get_top(page=page, tp=sort)


def watch_pay_award(env):
    '''
    查看支付奖励
    :param env:
    :return:
    '''
    user = env.user
    if user.got_pay_award:
        return 1, {}  # 已领取




def set_pre_battle(env):
    """设置是否演示战前动画
    """
    user = env.user
    toggle = int(env.get_argument('toggle'))
    if toggle in (0, 1):
        toggle = user.set_pre_battle(toggle)

    return 0, {'pre_battle', toggle}


def add_step(env):
    '''
    增加
    :param env:
    :return:
    '''
    step = env.get_argument('step', '')
    if step:
        env.user.step.add_step(step)
    return 0, {}


def change_name(env):
    """修改名字
    args:
        show_name: 显示的名字
    """
    user = env.user
    name = env.get_argument('name')
    if u'' == name:
        return 1, {}    # 格式不对，请重新输入名字
    if is_hexie(name):
        return 10240, {}
    num = user.item.get_item_count(208)
    if num and num >= 1:
        user.item.del_item(208, 1)
    else:
        pay_config = game_config.pay.get(34, [])
        cost = pay_config['coin'][0]
        if cost and user.coin < cost:
            return 'error_4', {}    # 钻石不足
        user.coin -= cost
    user.name = name
    user.item.save()
    user.save()
    return 0, {'name': name}