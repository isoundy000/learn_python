#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings
import cPickle as pickle
import time

import auth
import os, datetime, logging
from lib.db import ModelTools
import game_config


def require_permission(view_func):
    """
    装饰器，用于判断管理后台的帐号是否有权限访问
    """
    def wrapped_view_func(request, *args, **kwargs):

        path = request.request.path
        admin = auth.get_admin_by_request(request)
        request.uname = admin.username if admin else 'default'
        # 所有不进行登录直接访问后续页面的请求都踢回登录页面
        if not settings.DEBUG:
            if admin is None:
                return request.redirect("/%s/admin/login/" % settings.URL_PARTITION)
            # 视图权限
            # 请求的路径需要在用户自己的视图列表里查找
            if not auth.has_left_view(path, admin.left_href_list, admin.right_links):
                # print path, admin.left_href_list, admin.right_links
                writeLog(request, path, 3)
                Logging(admin).add_admin_logging(request, path, 3)
                # return request.redirect("/%s/admin/login/" % settings.URL_PARTITION)
                return request.finish(u'没权限')

        result = view_func(request, *args, **kwargs)
        writeLog(request, path, 1)
        # if not settings.DEBUG and view_func.func_name == path.split('/')[-2]:
        #     Logging(admin).add_admin_logging(request, path, 1)
        if view_func.func_name == path.split('/')[-2]:
            Logging(admin).add_admin_logging(request, path, 1)
        return result

    return wrapped_view_func


def writeLog(request, path, flag=0):
    action = log_contrast(request, path)
    uname = request.uname
    if action and uname:
        strLog = u'<' + uname + u'>' + action
        if flag == 1:
            strLog = u'success__' + strLog
        elif flag == 2:
            strLog = u'faile__' + strLog
        elif flag == 3:
            strLog = u'Permission denied__' + strLog
        else:
            strLog = u'<flag=' + str(flag) + u'>' + strLog
        writeFile(strLog)
    else:
        pass


def log_contrast(request, path):
    try:
        if '/admin/index/' in path:
            return 'login<' + u'>'
        elif '/admin/config/upload/' in path:
            config_name = request.request.arguments.get('config_name')
            return u'修改游戏配置<' + config_name + u'>'
        elif '/admin/virtual_pay/' in path:
            params = dict(request.request.arguments.iteritems())
            return u'后台虚拟充值<' + params.__str__() + u'>'
        else:
            params = dict(request.request.arguments.iteritems())
            return path + '<' + params.__str__() + '>'
    except:
        params = dict(request.request.arguments.iteritems())
        return path + '<' + params.__str__() + '>'


def writeFile(log):
    now = datetime.datetime.now()
    fdir = settings.BASE_ROOT + '/logs/config_logs'
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    fname = datetime.datetime.strftime(now, '%Y%m%d') + '.log'
    fd = fdir + '/' + fname

    # 删掉30天前的记录
    if not os.path.exists(fd):
        dir_list = os.listdir(fdir)
        for fname_t in dir_list:
            try:
                fname_t_list = fname_t.split('.')
                if len(fname_t_list) != 2 or fname_t_list[1] != 'log':
                    continue
                fname_date = datetime.datetime.strftime(fname_t_list[0], '%Y%m%d')
            except:
                continue
            if (now - datetime.timedelta(days=30)).date() > fname_date.date():
                os.remove(fdir + '/' + fname_t)

    logger = logging.getLogger()
    hdlr = logging.FileHandler(fd)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info(log)
    logger.removeHandler(hdlr)


class Logging(ModelTools):

    SERVER_NAME = 'master'

    EXPIRE_DAY = 30

    IGNORE = ['adminlog', '/admin/left/', '/admin/sets/']

    def __init__(self, admin):
        self.admin = admin
        self._key = self.make_key_cls(time.strftime('%Y-%m-%d'), self.SERVER_NAME)
        self.redis = self.get_redis_client(self._key, self.SERVER_NAME)

    def log_contrast(self, request, path):
        try:
            if '/admin/index/' in path:
                return u'登录', ''
            elif '/admin/config/upload/' in path:
                config_name = request.request.arguments.get('config_name')
                return u'修改游戏配置', config_name
            elif '/admin/virtual_pay/' in path:
                params = dict(request.request.arguments.iteritems())
                return u'后台虚拟充值', params.__str__()
            elif '/admin/give_item_commit/' in path:
                keys = [(item.rsplit('_', 1)[-1], num[0]) for item, num in request.request.arguments.iteritems()
                        if 'item_num' in item and int(num[0])]
                return u'赠送道具', str(keys)
            elif '/admin/give_card_commint/' in path:
                arguments = request.request.arguments
                cards = [(k, int(arguments.get('card_lv_%s' % k, ['0'])[0]),
                          int(arguments.get('card_evolv_%s' % k, ['0'])[0]),
                          int(arguments.get('card_num_%s' % k, ['0'])[0])
                          ) for k in game_config.character_detail if int(arguments.get('card_num_%s' % k, ['0'])[0])]
                return u'赠送卡牌', str(cards)
            elif '/admin/give_equip_commit/' in path:
                arguments = request.request.arguments
                equips = [(k, int(arguments.get('equip_lv_%s' % k, ['0'])[0]),
                           int(arguments.get('equip_num_%s' % k, ['0'])[0]))
                          for k in game_config.equip if int(arguments.get('equip_lv_%s' % k, ['0'])[0])
                          and int(arguments.get('equip_num_%s' % k, ['0'])[0])]
                return u'赠送装备', equips
            elif '/admin/give_gem_commit/' in path:
                arguments = request.request.path
                gems = [(k, int(arguments.get('gem_num_%s' % k, ['0'])[0])) for k in game_config.gem if int(arguments.get('gem_num_%s' % k, ['0'])[0])]
                return u'赠送宝石', gems
            elif '/admin/give_seed_commit/' in path:
                arguments = request.request.path
                seeds = [(k, int(arguments.get('seed_num_%s' % k, ['0'])[0]))for k in game_config.seed if int(arguments.get('seed_num_%' % k, ['0'])[0])]
                return u'赠送种子', seeds
            else:
                params = dict(request.request.arguments.iteritems())
                return '%s' % path, params.__str__()
        except:
            params = dict(request.request.arguments.iteritems())
            return '%s' % path, params.__str__()

    def add_admin_logging(self, request, path, status):
        """添加后台记录
        args:
            method:
            args: 请求参数
            data: 结果
        """
        for ignore in self.IGNORE:
            if ignore in path:
                return

        action, args = self.log_contrast(request, path)         # 动作
        result = {
            'admin': self.admin.username if self.admin else '', # 后台账号
            'action': action,
            'dt': time.strftime('%Y-%m-%d %H:%M:%S'),           # 操作时间
            'args': args,   # 参数
            'status': status,  # 状态 1.成功 2.失败 3.权限问题
            'ip': request.request.headers.get('X-Real-Ip', '')
        }
        self.redis.lpush(self._key, pickle.dumps(result))

    def get_all_logging(self, day=EXPIRE_DAY):
        data = []
        now = datetime.datetime.now()
        for i in [(now - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in xrange(0, day)]:
            data.extend(self.get_logging(i))
        return data

    def get_logging(self, time_str):
        """ 获取指定时间的日志

        :param time_str: "%Y-%m-%d"
        :return:
        """
        data = []
        key = self.make_key_cls(time_str, self.SERVER_NAME)
        for k in self.redis.lrange(key, 0, -1):
            data.append(pickle.loads(k))
        return data