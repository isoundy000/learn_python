#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gevent.monkey
gevent.monkey.patch_all()

import sys
import time
import datetime
import copy

import gevent

from gevent.event import Event
from gevent.lock import RLock

import settings
env = sys.argv[1]
server_name = sys.argv[2]
CONFIG_TYPE = 1 if server_name == 'master' else int(server_name)
settings.set_evn(env, server_name)
settings.ENVPROCS = 'escort'

from lib.utils.debug import print_log, trackback

import game_config
from models.timer import Timer
from run_timer_script.timer_task import TimerTask

from run_timer_script.timer_task_escort_arrive import TimerTaskEscortArrive
from run_timer_script.timer_task_escort_npc import TimerTaskEscortNpc


# 默认所有服不分区脚本在那个区执行
DEFAULT_GLOBAL_SERVER = 1

TIMER_CONFIG = {
    # 差距多少月, 差距多少天, 当天的几点，几分，几秒, func, is_repeat, global所有服不分区(0分服,1全服,2大区(new_world))

}

# game_config定时
TIMER_GAME_CONFIG = (
    # (game_config配置名, 处理类)
    ('escort_opentime', TimerTaskEscortArrive),
    # ('escort_opentime', TimerTaskEscortNpc),
)


def reload_all_config(timer_pool, force_reload=False):
    """ 更新所有配置相关的定时脚本

    :param timer_pool:
    :param force_reload: 是否强行加载
    :return:
    """
    for config in TIMER_GAME_CONFIG:
        try:
            if len(config) == 2:
                reload_config(timer_pool, config[0], config[1], force_reload=force_reload)
            elif len(config) == 3:
                reload_mul_config(timer_pool, config[0], config[1], config[2], force_reload=force_reload)
        except:
            trackback(msg='timer, add %s ERROR: ' % str(config[0]))


def reload_all_timers(timer_pool):
    """ 更新所有的固定定时脚本

    :param timer_pool:
    :return:
    """
    for k, v in TIMER_CONFIG.iteritems():
        try:
            timer_task = TimerTask(k, v)
            if timer_task.can_add(CONFIG_TYPE, DEFAULT_GLOBAL_SERVER):
                timer_pool.add(timer_task)
                print_log(k, datetime.datetime.fromtimestamp(timer_task.next_time))
        except:
            trackback(msg='timer, add %s ERROR: ' % str(k))


def reload_config(timer_pool, config_name, class_name, force_reload=False):
    """ reload一个配置

    :param timer_pool: TimerPool实例
    :param config_name:  配置名
    :param class_name: TimerTaskBase子类
    :param force_reload: 是否强行加载
    :return:
    """
    timer_pool.lock.acquire()

    version = game_config.config_version.get(config_name, 0)
    doing = []
    del_list = []
    print_log('reload_config start: ', config_name, version)
    for pool_key, timer_task in timer_pool.pool.iteritems():
        if isinstance(timer_task, class_name):
            if timer_task.get_version() == version and not force_reload:
                print_log('reload_config return: ', config_name, timer_task.get_version())
                timer_pool.lock.release()
                return
            # 更新定时脚本
            doing.append(timer_task.get_config_id())
            if timer_task.can_add(CONFIG_TYPE, DEFAULT_GLOBAL_SERVER):
                timer_task.set_version(version)
                timer_task.parser()
                print_log('reload_config update: ', config_name, datetime.datetime.fromtimestamp(timer_task.get_next_time()))
            else:
                del_list.append(pool_key)
    # 删除无用定时脚本
    for del_key in del_list:
        print_log('reload_config delete: ', del_key)
        del timer_pool.pool[del_key]
    # 添加新的定时脚本
    config = getattr(game_config, config_name, {})
    for config_id in config.iterkeys():
        if config_id not in doing:
            timer_task = class_name(config_id, version)
            if timer_task.can_add(CONFIG_TYPE, DEFAULT_GLOBAL_SERVER):
                timer_task.parser()
                timer_pool.add(timer_task)
                print_log('reload_config add: ', config_name, config_id, datetime.datetime.fromtimestamp(timer_task.get_next_time()))

    timer_pool.lock.release()


def reload_mul_config(timer_pool, config_name, class_name, fields, force_reload=False):
    """ reload一个配置, 没有测试过

    :param timer_pool: TimerPool实例
    :param config_name:  配置名
    :param class_name: TimerTaskBase子类
    :param fields: 域, 类型为list
    :param force_reload: 是否强行加载
    :return:
    """
    timer_pool.lock.acquire()

    version = game_config.config_version.get(config_name, 0)
    doing = []
    del_list = []
    print_log('reload_mul_config start: ', config_name, version)
    for pool_key, timer_task in timer_pool.pool.iteritems():
        if isinstance(timer_task, class_name):
            if timer_task.get_version() == version and not force_reload:
                print_log('reload_mul_config return: ', config_name, timer_task.get_version())
                timer_pool.lock.release()
                return
            # 更新定时脚本
            # doing.append(timer_task.get_config_id())
            # if timer_task.can_add(CONFIG_TYPE, DEFAULT_GLOBAL_SERVER):
            #     timer_task.set_version(version)
            #     timer_task.parser()
            #     print_log('reload_config update: ', config_name, datetime.datetime.fromtimestamp(timer_task.get_next_time()))
            # else:
            del_list.append(pool_key)
    # 删除无用定时脚本
    for del_key in del_list:
        print_log('reload_config delete: ', del_key)
        del timer_pool.pool[del_key]
    # 添加新的定时脚本
    config = getattr(game_config, config_name, {})
    for config_id in config.iterkeys():
        if config_id not in doing:
            for field in fields:
                timer_task = class_name(config_id, version, field)
                if timer_task.can_add(CONFIG_TYPE, DEFAULT_GLOBAL_SERVER):
                    timer_task.parser()
                    timer_pool.add(timer_task)
                    print_log('reload_mul_config add: ', config_name, config_id,
                              datetime.datetime.fromtimestamp(timer_task.get_next_time()))

    timer_pool.lock.release()



# 注意, 正式环境禁止启动此函数
def debug_sync_change_time(timer_pool):
    """

    :param timer_pool:
    :return:
    """
    from lib.utils import change_time
    from models.config import ChangeTime

    delta_seconds = ChangeTime.get()
    delta_seconds = int(float(delta_seconds)) if delta_seconds else 0
    real_time = int(change_time.REAL_TIME_FUNC())
    sys_time = real_time + delta_seconds
    if sys_time != int(time.time()):
        change_time.change_time(sys_time)
        reload_all_config(timer_pool, force_reload=True)
        reload_all_timers(timer_pool)
        print 'debug_change_time: %s -- %s -- %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(real_time)),
                                                     time.strftime('%Y-%m-%d %H:%M:%S'),
                                                     delta_seconds)
        return True
    else:
        return False

# 每个服务器集群分别记录Timer
timer_model = Timer.get(uid='escort_timer_%s' % CONFIG_TYPE, server_name='master')


class TimerPool(object):
    def __init__(self):
        self.pool = {}
        self.lock = RLock()
        self.config_time = 0
        super(TimerPool, self).__init__()

    def add(self, task_obj):
        self.lock.acquire()

        old_t = timer_model.next_update_timestamp.get(task_obj.get_key())
        old_last_t = timer_model.last_update_timestamp.get(task_obj.get_key())

        if old_t and old_last_t and 0 < old_t <= time.time() and old_t > old_last_t:
            self.pool[str(task_obj.get_key())] = task_obj
            task_obj.next_time = old_t
            task_obj.set_next_time(old_t)
            timer_model.next_update_timestamp[task_obj.get_key()] = int(old_t)
        else:
            self.pool[str(task_obj.get_key())] = task_obj
            timer_model.next_update_timestamp[task_obj.get_key()] = int(task_obj.get_next_time())

        timer_model.save()

        self.lock.release()

    def start(self):
        """# start: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        gevent.joinall([gevent.Greenlet.spawn(self.loop)])

    def loop(self):
        """# start: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        while 1:
            gevent.sleep(1)
            now = time.time()
            self.lock.acquire()

            if self.config_time % 60 == 0:
                # from logics.share import debug_sync_change_time
                # 注意, 正式环境禁止启动此函数
                if settings.DEBUG:
                    debug_sync_change_time(self)

                if not game_config.is_config_out():
                    game_config.load_all()
                    reload_all_config(self)

            pool_copy = copy.copy(self.pool)
            del_list = []
            for k, task_obj in pool_copy.iteritems():
                if now >= int(task_obj.get_next_time()):
                    try:
                        if task_obj.is_global() == 1:
                            # gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func())], raise_error=True)
                            gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func())])
                        elif task_obj.is_global() == 2:
                            world_ids = list(set([value['world_id'] for value in game_config.new_world.itervalues()]))
                            for world_id in world_ids:
                                print_log('world func: ', task_obj.get_func(),
                                          datetime.datetime.fromtimestamp(task_obj.next_time))
                                # gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func(), world_id)], raise_error=True)
                                gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func(), world_id)])
                        else:
                            for server_name, server_cfg in settings.SERVERS.iteritems():
                                if server_name == 'master': continue
                                # if server_cfg['config_type'] != CONFIG_TYPE: continue
                                if settings.get_config_type(server_name) != CONFIG_TYPE: continue
                                print_log('func: ', task_obj.get_func(),
                                          datetime.datetime.fromtimestamp(task_obj.next_time))
                                # gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func(), server_name)], raise_error=True)
                                gevent.joinall([gevent.Greenlet.spawn(task_obj.get_func(), server_name)])
                        timer_model.last_update_timestamp[task_obj.get_key()] = now
                        if task_obj.is_repeat():
                            task_obj.parser()
                            timer_model.next_update_timestamp[task_obj.get_key()] = int(task_obj.get_next_time())
                        else:
                            del_list.append(k)
                        timer_model.save()
                        print_log('timer, run %s, is_repeat: %s' % (k, str(task_obj.is_repeat())))
                    except:
                        trackback(msg='timer, timeer %s ERROR: ' % str(k))

            for k in del_list:
                del self.pool[k]
            self.config_time += 1
            self.lock.release()


TIMER_POOL = TimerPool()

# 注意, 正式环境禁止启动此函数, 重启后加载时间
is_reload = False
if settings.DEBUG:
    is_reload = debug_sync_change_time(TIMER_POOL)


if not is_reload:
    # 加载配置中的执行时间
    reload_all_config(TIMER_POOL)

    # 固定间隔时间
    reload_all_timers(TIMER_POOL)


TIMER_POOL.start()