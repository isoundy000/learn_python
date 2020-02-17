#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import time
import random
import logging
import xmlrpclib
import copy
import urllib


# import ujson
import json

from lib.utils.debug import print_log
from lib.utils.debug import error_mail

from lib.statistics import stat

import handler_tools
from handler_tools import to_json
import game_config
import settings
from logics.share import cal_new_coin

import gevent

import tornado.web
import tornado.websocket

from lib.core.handlers.htornado import BaseRequestHandler
from lib.core.environ import Environ
from lib.core.environ import APIEnviron
from lib.db import ModelTools

import admin

PWD = os.path.abspath(os.path.dirname(__file__))


def lock(func):
    '''
    func == api
    :param func:
    :return:
    '''

    ignore_api_module = ['super_active', 'server_super_active', 'normal_exchange', 'soul', 'magic_school',
                         'server_magic_school']
    ignore_api_method = ['notify.read', 'active.active_recharge_receive', 'active.server_active_recharge_receive',
                         'active.active_consume_receive', 'active.grow_gift_receive', 'server_foundation.withdraw',
                         'arena.playerboss_award', 'item.use', 'wanted.wanted_award', 'bandit.get_reward',
                         'server_bandit.get_reward', 'server_diamond_wheel.open_diamond_wheel',
                         'bounty_order.get_reward_child_task', 'bounty_order.get_big_reward',
                         'server_bounty_order.get_reward_child_task', 'server_bounty_order.get_big_reward',
                         'code.use_code', 'daily_award.get_reward', 'daily_award.coin_award',
                         'diamond_wheel.open_diamond_wheel', 'escort.buy_goods', 'foundation.withdraw',
                         'gift.receiving_gift', 'guild_gvg.attack', 'item.exchange', 'magic_school.point_reward',
                         'mine.mining', 'one_piece.exchange', 'one_piece.step_reward', 'pay_award.get_award',
                         'private_city.get_world_reward', 'pyramid.get_wanted_reward', 'reward.daily_score_award',
                         'reward.activate_daily_task', 'reward.daily_award', 'reward.fast_finish_daily_award',
                         'reward.once_award', 'reward.wanted_award', 'reward.get_score_reward',
                         'reward.get_daily_reward', 'reward.opening_award', 'sacrifice.grace_exchange',
                         'server_magic_school.point_reward', 'server_one_piece.exchange',
                         'server_one_piece.step_reward', 'arena_new.exchange', 'arena_new.special_reward',
                         'clone_lane.draw', 'clone_lane.pack', 'clone_lane.refresh_team', 'vip_reward.vip_sign',
                         'vip_reward.every_day', 'red_bag.open_red_bag', 'gringotts.quickly_reward',
                         'gringotts.get_reward', 'gringotts.get_big_reward', 'new_rocker.open_new_rocker',
                         'team_pk_new.exchange', 'active.recall_active_recharge_receive', ]

    d = {
        'status': 9998,
        'data': {},
        'msg': game_config.return_msg_config.get(9998, 9998),
        'user_status': {},
    }

    def error(api_request_handler):
        api_request_handler.set_header('content_type', 'application/json; charset=UTF-8')
        api_request_handler.set_header('Content-Type', 'application/json; charset=UTF-8')
        r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
        api_request_handler.write(r)
        api_request_handler.finish()

    def wrapper(api_request_handler, *args, **kwargs):
        if api_request_handler.env is None:
            error(api_request_handler)
            return
        method_param = api_request_handler.env.req.get_argument('method')
        module_name, method_name = method_param.split('.')

        if method_name in ignore_api_module or method_param in ignore_api_method:
            user_m = api_request_handler.env.user.user_m
            _client = user_m.redis
            lock_key = user_m.make_key_cls('lock.%s.%s' % (user_m.uid, method_param), user_m._server_name)
            now = time.time()
            ts = now + 1
            flag = _client.setnx(lock_key, ts)
            try:
                if not (flag or (now > float(_client.get(lock_key)) and now > float(_client.getset(lock_key, ts)))):
                    error(api_request_handler)
                    return
            except:
                import traceback
                print_log(traceback.print_exc())
                error(api_request_handler)
                return

            result = func(api_request_handler, *args, **kwargs)

            if time.time() < float(_client.get(lock_key)):
                _client.delete(lock_key)
        else:
            result = func(api_request_handler, *args, **kwargs)

        return result

    return wrapper



def restart_server():

    def restart(addr):
        workers = []
        server = xmlrpclib.Server("http://%s:9001/RPC2" % addr)

        for s in server.supervisor.getAllConfigInfo():
            name = "%(group)s:%(name)s" % s
            server.supervisor.stopProcess(name)
            server.supervisor.startProcess(name)

            workers.append("%s--%s" % (addr, name))

        return workers

    jobs = []
    jobs.append(gevent.spawn(restart, 'localhost'))

    gevent.joinall(jobs, timeout=3)

    while not all([job.value for job in jobs]):
        gevent.joinall(jobs, timeout=3)

    return [job.value for job in jobs]


class UserMixIn(object):
    """ user嵌入类

    将get_current_user独立出来方便其它Handler共用
    """
    def get_current_user(self, env):
        """ 获取当前用户对象

        首先验证用户，当用户不能通过验证时，
        尝试登陆操作

        Args:
            env: 运行环境

        Returns:
            用户对象
        """
        # user_app = env.import_app('user')
        #
        # user = user_app.auth(env, self)
        #
        # if not user:
        #     user = user_app.login(env, self)
        # if not game_config.is_config_out():
        #     game_config.load_all()
        from logics.user import User
        uid = env.req.get_argument('user_token')
        method = env.req.get_argument('method', '')
        user = User(uid)

        return user


class APIRequestHandler(UserMixIn, BaseRequestHandler):
    """ 统一的API Handler

    全部API处理公共接口
    """
    def initialize(self):
        """ 初始化操作

        创建全局环境和运行环境
        """
        try:
            self.env = APIEnviron.build_env(self)
        except:
            import traceback
            print_log(traceback.print_exc())
            self.env = None

    determine_card_package = { # 以下这些接口判断卡包是否已满
        'private_city.recapture': {'step_n': ('0', )},
        'private_city.auto_recapture': {},
        'arena.battle': {},
        'active.fight': {'step_n': ('0',)},
    }
    # 判断单点登录 可忽略的接口、模块
    single_login_ignore_api_module = ['config']
    single_login_ignore_api_method = ['test.test', 'payment.pay']

    # 忽略消费活动的接口
    single_payment_active_api_module = ['mine']
    single_payment_active_api_method = ['gringotts.investing', 'gringotts.quickly_reward']

    def api(self):
        """ API统一调用方法
        """
        method_param = self.env.req.get_argument('method')
        module_name, method_name = method_param.split('.')
        ########################################
        # 客户端版本判断
        # game_config.version eg:{'h1': {'msg': u'当前测试已经结束啦。感谢您对《禁区》的支持，我们将于2月中旬进行第二轮测试，敬请期待。',
        #                                 'url': 'http://www.baidu.com',
        #                                 'version': '1.0.1'}
        #                         }
        uid = self.env.req.get_argument('user_token')
        all_server_flag = 'all'
        if uid and (uid[:-7] in game_config.version or all_server_flag in game_config.version):
            data = {
                'url': 'http://www.baidu.com',  # 前端需要跳转到的新包下载地址，一般是官网什么的
                'msg': u'当前测试已经结束啦。感谢您对《禁区》的支持，我们将于2月中旬进行第二轮测试，敬请期待。',
                'version': '',
                'need_upgrade': False
            }

            if settings.ENV_NAME in [settings.ENV_IOS, settings.ENV_STG_IOS, settings.ENV_TEST_IOS]:
                data.update(game_config.version.get(uid[:-7], game_config.version.get(all_server_flag, {})))
            else:
                user = self.env.user
                _platform = user.account.split('_')[0].lower()
                _version_config = game_config.version.get(uid[:-7], game_config.version.get(all_server_flag, {}))
                _platform_config = _version_config.get(_platform, [])
                if _platform_config and len(_platform_config) == 3:
                    # [[version], [url], [msg]]
                    data['version'] = _platform_config[0][0]
                    data['url'] = _platform_config[1][0]
                    data['msg'] = _platform_config[2][0]

            version = self.env.get_argument('version', '1.0.2')
            new_version = data.get('version', '')
            if new_version and version < new_version:
                data['need_upgrade'] = True

                d = {
                    'status': 0,
                    'data': {},
                    'msg': '',
                    'user_status': {},
                    'client_upgrade': data
                }
                self.set_header('content_type', 'application/json; charset=UTF-8')
                self.set_header('Content-Type', 'application/json; charset=UTF-8')
                r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
                self.write(r)
                self.finish()
                return -99009, {}, '', None

        ########################################
        # # 清档测试    2014-05-19 17:00:00 之后注册的用户不让进 测试服
        # if 'g1' in self.env.user.uid:
        #     pts = ['downjoy', 'uc', 'pp', 'kuaiyong', 'itools', 'tongbu']
        #     pt = self.env.user.account.split('_')[0]
        #     if self.env.user.regist_time > 1400490000 or pt.lower() in pts:
        #         rc = 'fuck'
        #         d = {
        #             'status': rc,
        #             'data': {},
        #             'msg': game_config.return_msg_config.get(rc, rc),
        #             'user_status': {},
        #         }
        #         self.set_header('content_type', 'application/json; charset=UTF-8')
        #         self.set_header('Content-Type', 'application/json; charset=UTF-8')
        #         r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
        #         self.write(r)
        #         self.finish()
        #         return rc, {}, d['msg'], self.env.user

        ########### 封号 start #################
        if self.env.user.is_ban:
            rc = 'error_17173'
            d = {
                'status': rc,
                'data': {},
                'msg': game_config.return_msg_config.get(rc, rc),
                'user_status': {},
            }
            self.set_header('content_type', 'application/json; charset=UTF-8')
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
            self.write(r)
            self.finish()
            return rc, {}, d['msg'], self.env.user
        ########### 封号 end #################

        ########### 多点登录判断 start #################
        device_mark = self.env.get_argument('device_mark', '')
        device_mem = self.env.get_argument('device_mem', '')
        frontwindow = settings.DEBUG or self.env.get_argument('frontwindow', '') == '5e3b4530b293b5c1f4eeca4638ab4dc1'
        mem_unavaible_api = self.env.user.device_mem and self.env.user.device_mem != device_mem
        unavaible_api = self.env.user.device_mark and self.env.user.device_mark != device_mark
        mk = self.env.req.get_argument('mk', 0)
        _mk = int(mk) if mk else 0
        if not frontwindow and (mem_unavaible_api or unavaible_api or not _mk or _mk != self.env.user._mark):
            if module_name not in self.single_login_ignore_api_module and method_param not in self.single_login_ignore_api_method:
                rc = 9527
                d = {
                    'status': rc,
                    'data': {},
                    'msg': game_config.return_msg_config.get(rc, rc),
                    'user_status': {},
                }
                self.set_header('content_type', 'application/json; charset=UTF-8')
                self.set_header('Content-Type', 'application/json; charset=UTF-8')
                r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
                self.write(r)
                self.finish()
                return rc, {}, d['msg'], self.env.user
        ########### 多点登录判断 end #################

        ########### session验证判断 start #################
        ks = self.env.get_argument('ks', '')
        if not frontwindow and settings.SESSION_SWITCH and self.env.user.session_expired(ks):
            rc = 9527
            d = {
                'status': rc,
                'data': {},
                'msg': game_config.return_msg_config.get(rc, rc),
                'user_status': {},
            }
            self.set_header('content_type', 'application/json; charset=UTF-8')
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
            self.write(r)
            self.finish()
            return rc, {}, d['msg'], self.env.user
        ########### session验证判断 end #################

        ############## 如果卡包已满，则部分接口直接跳出 #########
        if method_param in self.determine_card_package:
            need_check = True
            param_dict = self.determine_card_package[method_param]
            if param_dict:
                for k, v in param_dict.iteritems():
                    param_value = self.env.req.get_argument(k)
                    if not v or param_value in v:
                        need_check = True
                        break
                else:
                    need_check = False

            if need_check:
                if self.env.user.is_cards_full():
                    from logics import guide

                    rc = 'error_1'
                    guide.mark_guide_4_error(self.env.user, 1)
                    msg = game_config.return_msg_config[rc]
                    data = {
                        '_client_cache_update': {},
                    }
                    self.write(handler_tools.result_generator(rc, data, msg, self.env.user))
                    self.finish()
                    return rc, data, msg, self.env.user
                if self.env.user.is_equip_full():
                    rc = 'error_2'
                    msg = game_config.return_msg_config[rc]
                    data = {
                        '_client_cache_update': {},
                    }
                    self.write(handler_tools.result_generator(rc, data, msg, self.env.user))
                    self.finish()
                    return rc, data, msg, self.env.user

        ########################################
        user = self.env.user
        old_coin = user.coin
        old_level = user.level

        module = __import__('views.%s' % module_name, globals(), locals(), [method_name])
        method = getattr(module, method_name)

        if callable(method):
            msg = ''
            rc, data = method(self.env)
            if rc != 0:
                msg = data.get('custom_msg', '') or game_config.return_msg_config.get(rc) or \
                    game_config.return_msg_config.get(method_param, {}).get(rc, method_param + '_error_%s' % rc)
                if rc == 'error_14':    # 级别不足 的提示 用后端给的msg
                    rc = 'xx'
            else:
                new_coin = user.con
                # 简单粗暴的记录消费记录
                if new_coin < old_coin:
                    from models.payment import spend_insert
                    arguments = copy.deepcopy(self.env.req.summary_params())
                    for _ in ['method', 'user_token', 'mk']:
                        arguments.pop(_, None)

                    spend_data = {
                        'coin_1st': old_coin,
                        'coin_2nd': new_coin,
                        'coin_num': old_coin - new_coin,
                        'goods_cnname': '',
                        'goods_name': '',
                        'goods_num': 1,
                        'goods_subtype': '',
                        'goods_type': method_param,
                        'level': user.level,
                        'subtime': time.strftime('%F %T'),
                        'uid': user.uid,
                        'args': json.dumps(arguments, separators=(',', ':')),
                    }
                    spend_insert('%s_%s' % (user.uid, time.time()), spend_data)
                    if module_name not in self.single_payment_active_api_module and method_param not in self.single_payment_active_api_method:
                        coin = cal_new_coin(old_coin, new_coin, method_param)
                        # 钻石摩天轮的消耗钻石开启摩天轮的活动
                        try:
                            user.diamond_wheel.pay_coin(coin)
                        except:
                             pass
                        # 开服的钻石摩天轮的消耗钻石开启摩天轮的活动
                        try:
                            user.server_diamond_wheel.pay_coin(coin)
                        except:
                             pass
                        # 赛亚人归来活动
                        user.super_active.add_score(old_coin - new_coin, save=True)
                        try:
                            # 新服人归来活动
                            user.server_super_active.add_score(old_coin - new_coin, save=True)
                        except:
                            pass
                        # 悬赏令消耗的钻石
                        try:
                            user.bounty_order.use_coin(coin)
                        except:
                            import traceback
                            print_log(traceback.print_exc())

                        try:
                            user.server_bounty_order.use_coin(coin)
                        except:
                            import traceback
                            print_log(traceback.print_exc())

                        # 全服神龙消耗的钻石数量
                        try:
                            user.large_super_all.use_coin_or_action_point(coin=coin)
                        except:
                            import traceback
                            print_log(traceback.print_exc())

                        # 全服宇宙最强消耗的钻石数量
                        try:
                            user.large_super_rich.use_coin_or_action_point(coin=coin)
                        except:
                            import traceback
                            print_log(traceback.print_exc())

                        # 开服充值活动
                        user.server_active_recharge.reward_coin(old_coin - new_coin)
                        user.consume_reward.add_score(old_coin - new_coin, method_param)

                        if 'foundation.activate' not in method_param:
                            #消费钻石，领取奖励活动
                            user.active_consume.add_consume_coin(coin)

                # 用户到2级才回调积分墙接口
                if old_level < user.level and user.level in [2, 3, 4, 5]:
                    from views import ad_click
                    ad_click.ad_callback(self, user.level)

            self.set_header('content_type', 'application/javascript; charset=UTF-8')
            self.set_header('Content-Type', 'application/javascript; charset=UTF-8')

            # 关于客户端数据缓存的更新
            client_cache_update = {}
            for k, v in self.env.user.__class__.__dict__.iteritems():
                if 'fget' in dir(v) and k not in self.env.user.user_m._attrs:
                    obj = getattr(self.env.user, '_' + k, None)
                    if obj and getattr(obj, '_diff', None):
                        client_cache_update[k] = obj._client_cache_update()

            data['_client_cache_update'] = client_cache_update
            # self.env.user.reward.do_task_api(method_param, self.env, rc, data)
            # self.env.user.daily_score.do_daily_score_api(method_param, self.env, rc, data)
            # try:
            #     self.env.user.recall_daily_score.do_daily_score_api(method_param, self.env, rc, data)
            # except:
            #     import traceback
            #     print_log(traceback.print_exc())
            # self.env.user.bounty_order.do_task_api(method_param, self.env, rc, data)
            # self.env.user.server_bounty_order.do_task_api(method_param, self.env, rc, data)
            # self.env.user.role_reward.do_role_reward_api(method_param, self.env, rc, data)
            self.write(handler_tools.result_generator(rc, data, msg, self.env.user))
            self.finish()
            return rc, data, msg, self.env.user

    # if not settings.DEBUG:
    api = stat(api)
    if not settings.DEBUG:
        api = error_mail(api, settings.ADMIN_LIST)
    api = lock(api)

    def on_finish(self):
        """ 处理异步方法
        """
        if self.env is not None:
            for callback in self.env.callbacks:
                callback(self.env)

            self.env.finish()

    @tornado.web.asynchronous
    def get(self):
        """ 处理GET请求
        """
        user_agent = self.request.headers.get('User-Agent')
        skip = settings.DEBUG or (self.env is not None and self.env.get_argument('browser', '') == 'a7b87e9d6faae5e7c4962d001bbd62b1')

        if not skip and (user_agent is not None or self.env is None or not self.env.req.get_argument('method')):
            d = {
                'status': 9999,
                'data': {},
                'msg': game_config.return_msg_config.get(9999, 9999),
                'user_status': {},
            }
            self.set_header('content_type', 'application/json; charset=UTF-8')
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
            self.write(r)
            self.finish()
            return
        self.api()


    @tornado.web.asynchronous
    def post(self):
        """ 处理POST请求
        """
        self.get()


def pay_lock(tp, payment, func, args):
    api_tp = ['androidky']

    if tp in api_tp:
        locked = False

        redis = ModelTools.get_redis_client('pay_lock', 'master')

        lock_key = ModelTools.make_key_cls('pay_lock.%s' % tp, 'master')
        now = time.time()
        ts = now + 1
        flag = redis.setnx(lock_key, ts)
        try:
            if not (flag or (now > float(redis.get(lock_key)) and now > float(redis.getset(lock_key, ts)))):
                locked = True
        except:
            import traceback
            print_log(traceback.print_exc())

        if locked:
            d = payment.ERROR_RETURN.get(tp)
        else:
            d = func(*args)

        if time.time() < float(redis.get(lock_key)):
            redis.delete(lock_key)
    else:
        d = func(*args)

    return d


class Pay(BaseRequestHandler):

    def get(self):
        from views import payment
        method = self.get_argument('method', 'callback')
        tp = self.get_argument('tp', 'apple')

        func = getattr(payment, method)

        d = pay_lock(tp, payment, func, [self])

        self.write(d)
        self.finish()

    if not settings.DEBUG:
        get = error_mail(get, settings.ADMIN_LIST)

    def post(self):
        return self.get()


class PayCallBack(BaseRequestHandler):

    def get(self, tp):
        from views import payment

        func = payment.callback

        d = pay_lock(tp, payment, func, [self, tp])

        self.write(d)
        self.finish()

    if not settings.DEBUG:
        get = error_mail(get, settings.ADMIN_LIST)

    def post(self, tp):
        return self.get(tp)


class Login(BaseRequestHandler):

    def api(self):
        import game_config
        if not game_config.is_config_out():
            game_config.load_all()
        method = self.get_argument('method', 'new_user')
        print '------------', method
        from views import user
        msg = ''
        is_login = True
        if method == 'loading':
            rc, user, data = 0, None, {}
            # 通过version配置的格式 来判断是否提交了新版本的version
            # 如果提交了新版version 开始强制更新前端，则老版本前端包不再下载各个 game_config 配置，等到更新完新版客户端之后再去下载game_config 配置
            # 老版本的version配置格式 {'version': '','url': '','msg': unicode('''《超级英雄》敬请期待！''','utf-8'),}
            # 新版本的version配置格式 按平台区分更新信息 {'sogou':[],'androidcmge':[],'itools':[], ...}
            # 这代码为了解决 前端 遗留bug， 等更新完新客户端之后 可删除
            version_info = {}
            for version_info in game_config.version.itervalues():
                break
            need_upgrade = 'tongbu' in version_info or 'cmge' in version_info or 'itools' in version_info
            version = self.get_argument('version', '1.0.2')
            if version < '1.0.7' and need_upgrade:
                is_login = False
        else:
            func = getattr(user, method)
            rc, user, data = func(self)
            method_param = '%s.%s' % ('user', func.__name__)
            if rc != 0:
                msg = game_config.return_msg_config.get(method_param, {}).get(rc, method_param + '_error_%d' % rc)

        # get_user_server_list 接口判断客户端是否需要强制更新
        if method == 'new_user':
            from models.user import UnameUid

            account = self.get_argument('account', '')
            uu = UnameUid.get(account)
            cur_server = uu.current_server
            if cur_server and cur_server in game_config.version:
                client_upgrade = {
                    'url': 'http://www.baidu.com',      # 前端需要跳转到的新包下载地址，一般是官网什么的
                    'msg': u'当前测试已经结束啦。感谢您对《禁区》的支持，我们将于2月中旬进行第二轮测试，敬请期待。',
                    'version': '',
                    'need_upgrade': False
                }

                _platform = account.split('_')[0].lower()
                _version_config = game_config.version[cur_server]
                _platform_config = _version_config.get(_platform, [])
                if _platform_config and len(_platform_config) == 3:
                    # [[version], [url], [msg]]
                    client_upgrade['version'] = _platform_config[0][0]
                    client_upgrade['url'] = _platform_config[1][0]
                    client_upgrade['msg'] = _platform_config[2][0]

                version = self.get_argument('version', '1.0.2')
                new_version = client_upgrade.get('version', '')
                if new_version and version < new_version:
                    client_upgrade['need_upgrade'] = True

                    d = {
                        'status': 0,
                        'data': {},
                        'msg': '',
                        'user_status': {},
                        'client_upgrade': client_upgrade
                    }
                    self.set_header('content_type', 'application/json; charset=UTF-8')
                    self.set_header('Content-Type', 'application/json; charset=UTF-8')
                    r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
                    self.write(r)
                    self.finish()
                    return -99009, {}, '', None

        ########################################
        self.set_header('content_type', 'application/json; charset=UTF-8')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        try:
            r = handler_tools.result_generator(rc, data, msg, user, login=True, request=self)
            self.write(r)
        finally:
            self.finish()
            return rc, data, msg, user

    if not settings.DEBUG:
        api = stat(api, 'login')
        api = error_mail(api, settings.ADMIN_LIST)

    def get(self):
        """# get: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        user_agent = self.request.headers.get('User-Agent')
        skip = settings.DEBUG or self.get_argument('browser', '') == 'a7b87e9d6faae5e7c4962d001bbd62b1'
        skip = True
        if not skip and (user_agent is not None or not self.get_argument('method')):
            d = {
                'status': 9999,
                'data': {},
                'msg': '',
                'user_status': {},
            }
            self.set_header('content_type', 'application/json; charset=UTF-8')
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            r = json.dumps(d, ensure_ascii=False, encoding="utf-8", indent=2, default=to_json)
            self.write(r)
            self.finish()
            return
        # 登录接口的调用
        self.api()

    def post(self):
        """# post: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        self.get()


class AdminHandler(BaseRequestHandler):

    def get(self, tag_name):
        """# get: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        method = getattr(admin, tag_name)
        return method(self)

    def post(self, tag_name):
        """# post: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        method = getattr(admin, tag_name)
        return method(self)


class ConfigHandler(BaseRequestHandler):

    def get(self):
        import game_config
        if not game_config.is_config_out():
            game_config.load_all()

        from views import config
        method = self.get_argument('method', 'resource_version')
        func = getattr(config, method)
        d = {
            'status': 0,
            'data': func(self),
            'msg': '',
            'user_status': {},
        }

        self.set_header('content_type', 'application/json; charset=UTF-8')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        r = json.dumps(d, ensure_ascii=False, separators=(',', ':'), encoding="utf-8", default=to_json)
        self.write(r)
        self.finish()

    if not settings.DEBUG:
        get = error_mail(get, settings.ADMIN_LIST)

    def post(self):
        self.get(self)


class AdClick(BaseRequestHandler):

    def get(self, tp):
        # type: (object) -> object
        from views import ad_click

        func = getattr(ad_click, '%s_click' % tp)
        if settings.DEBUG:
            print '=== AdClick ===:', self.request.arguments
            path = os.path.join(settings.BASE_ROOT, 'logs', 'adclick_%s_%s.txt' % (tp, time.strftime('%F-%T')))
            f = open(path, 'w')
            f.write(repr(self.request))
            f.close()

        d = func(self)
        # 由tornado自动判断是否转JSON
        # d = json.dumps(d, ensure_ascii=False, encoding="utf-8", default=to_json)
        if d is not None:
            self.write(d)
            self.finish()

    if not settings.DEBUG:
        get = error_mail(get, settings.ADMIN_LIST)

    def post(self, tp):
        return self.get(tp)


class ZhiChong360Handler(BaseRequestHandler):
    ''' 360支付游戏直冲接口

    '''
    def get(self, tag_name):
        from views import zhichong360

        func = getattr(zhichong360, tag_name, None)

        result = ''
        if callable(func):
            result = func(self)
            result = json.dumps(result, ensure_ascii=False, separators=(',', ':'), encoding="utf-8", default=to_json)

        self.write(result)
        self.finish()

    def post(self, tag_name):
        return self.get(tag_name)


class CMGEHandler(BaseRequestHandler):
    """ 针对中手游需求提供接口

    """
    ENV_MAPPING = {
        'cloud_ios': 1,
        'cloud_android': 2,
        'dev': 3,
        'test': 4,
    }
    DEFAULT_ENV = 2     # 默认环境标示为Android和IOS越狱

    def initialize(self, env_name):
        self.env_name = env_name
        self.env_type = self.ENV_MAPPING.get(self.env_name, self.DEFAULT_ENV)

    def get(self, tag_name):
        """# get: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        from views import cmge

        func = getattr(cmge. tag_name, None)

        if callable(func):
            result = func(self, env_type=self.env_type)
        else:
            result = {'code': '1'}

        r = json.dumps(result, ensure_ascii=False, separators=(',', ':'), encoding="utf-8", default=to_json)
        self.write(r)
        self.finish()

    def post(self, tag_name):
        """# post: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return self.get(tag_name)


class AdvertHandler(BaseRequestHandler):
    """ 针对IOS广告需求提供接口

    """
    app_store_uri = 'https://itunes.apple.com/cn/app/chao-ji-ying-xiong-dong-zuo/id683031739?mt=8'

    def get(self):
        """# get: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        from models.code import AppStoreAdver
        ip = self.request.headers.get('X-Real-Ip', '')
        AppStoreAdver.set(ip)

        self.redirect(self.app_store_uri)

    def post(self):
        """# post: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return self.get()


if __name__ == '__main__':
    pass