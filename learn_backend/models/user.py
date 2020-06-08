#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import string
import cPickle as pickle
import datetime
import random
import settings
import game_config

from lib.utils import rand_string, generate_rank_score
from lib.db import ModelBase
from lib.db import ModelTools
from models.config import ServerConfig
from lib.utils import md5

STR_SOURCE = '0123456789'       # '0123456789abcdefghijklmnopqrstuvwxyz'


def new_uid(server_name):
    """# new_uid: 生成一个新得uid
    args:
        :    ---    arg
    returns:
        0    ---
    """
    s = server_name + rand_string(7, STR_SOURCE)
    redis = User.get_redis_client('111', server_name)
    m_key = User.make_key_cls(s, server_name)

    while redis.exists(m_key):
        s = random.sample(STR_SOURCE, 7)
        s = server_name + ''.join(s)
        m_key = User.make_key_cls(s, server_name)

    return s


class UidServer(ModelTools):
    """# UidServer: 保存全服的uid和account，server对应关系
        in redis:
            {
                h1a: {
                    h1a: {
                        server: h1,
                        account: aa
                    }
                }
            }
    """
    SERVER_NAME = 'master'
    def __init__(self, uid):
        self.uid = uid
        self._attrs = {
            'server': '',
            'account': '',
        }
        super(UidServer, self).__init__()

    @classmethod
    def make_key_cls(cls, uid, server_name):
        return super(UidServer, cls).make_key_cls(uid[:3], cls.SERVER_NAME)

    def save(self):
        """# save: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        key = self.make_key(self.uid, self.SERVER_NAME)
        d = {}
        for k in self._attrs:
            d[k] = getattr(self, k)
        s = pickle.dumps(d)
        redis = self.get_redis_client(key, self.SERVER_NAME)
        redis.hset(key, self.uid, s)

    @classmethod
    def get(cls, uid):
        key = cls.make_key_cls(uid, cls.SERVER_NAME)
        redis = cls.get_redis_client(uid, cls.SERVER_NAME)
        s = redis.hget(key, uid)
        if s is not None:
            r = pickle.loads(s)
        else:
            r = {}
        o = cls(uid)
        o._server_name = cls.SERVER_NAME
        for k, v in o._attrs.iteritems():
            setattr(o, k, r.get(k, v))
        return o

    @classmethod
    def all_uid_server(cls,):
        pass


class UnameUid(ModelBase):
    """# UnameUid: account(user_name)->uid索引表"""
    SERVER_NAME = 'master'

    def __init__(self, uid=None):
        self.uid = uid              # uid表示user_name
        self._attrs = {
            'passwd': '',
            'servers': {},          # 参加的分服, server:uid
            'init_platform': '',    # 创建用户时候，使用的平台
            'cur_platform': '',     # 最近一次登录，使用的平台
            'current_server': '',   # 当前在玩儿的分服
            'sid': '',              # session_id
            'expired': '',          # session过期时间
        }
        super(UnameUid, self).__init__(self.uid)
        self._server_name = self.SERVER_NAME

    @classmethod
    def get(cls, uid):
        o = super(UnameUid, cls).get(uid, cls.SERVER_NAME)
        return o

    @classmethod
    def check_exist(cls, account):
        '''
        检查是否没有这个账户
        '''
        r = cls.get_redis_client('yyy', cls.SERVER_NAME)
        key = cls.make_key_cls(account, cls.SERVER_NAME)
        return r.exists(key)

    def change_account_name(self, new_account):
        """# change_account_name: 把用户名换掉
        args:
            new_account:    ---    arg
        returns:
            0    ---
        """
        old_key = self.make_key(self.uid, self._server_name)
        new_key = self.make_key_cls(new_account, self._server_name)
        self.redis.rename(old_key, new_key)
        self.uid = new_account

    def get_or_create_session_and_expired(self, force=False):
        """ 获取或者创建session

        :return:
        """
        now = int(time.time())
        is_save = False
        if self.sid:
            if self.expired < now:
                self.sid = md5('%s%s' % (str(now), self.uid))
                self.expired = now + settings.SESSION_EXPIRED
                is_save = True
        else:
            self.sid = md5('%s%s' % (str(now), self.uid))
            self.expired = now + settings.SESSION_EXPIRED
            is_save = True

        if is_save and not force:
            self.save()

        return self.sid, self.expired


class User(ModelBase):
    """# User: docstring"""
    HAS_LEADER = True                               # 表示这哥们儿有英雄称号
    ONLINE_USERS_PREFIX = 'online_users'            # redis 中 存放在线用户的key
    USERS_REGIST_PREFIX = 'regist_users'            # redis 中 存放用户注册时间的key
    USERS_CHECKIN_PREFIX = 'checkin_users'          # redis 中 存放用戶當天最後登陸時間的key

    COMBAT_RANK_KEY_PREFIX = 'combat_rank'          # 战力排行榜
    LEVEL_RANK_KEY_PREFIX = 'level_rank'            # 等级排行榜
    EQUIPMENT_RANK_KEY_PREFIX = 'equipment_rank'    # 装备排行榜
    WORLD_REGAIN_RANK_KEY_PREFIX = 'world_regain_rank'  # 世界收复度排行榜
    COMMANDER_RANK_KEY_PREFIX = 'commander_rank'    # 统帅排行榜
    LIKE_RANK_KEY_PREFIX = 'like_rank'              # 点赞排行榜

    ONLINE_USERS_TIME_RANGE = 5 * 60                # 判断用户在线的时间参考
    FREE_TRAIN_TIMES = 1                            # 学校免费训练次数
    FREE_DAILY_REWARD_TIMES = 1                     # 每日任务免费刷新次数
    PAYMENT_RATE = 10                               # 充值 vip 经验 与人民币的比例
    LEVEL_GIFT_EXPIRE = 3600                        # 等级奖励有效期


    _attrs = {}
    _base_attrs = {
        'name': '',                     # 显示的名字
        'account': '',                  # 用户的账户(UnameUid 的 key）
        'cur_platform': '',             # 最新请求，使用的平台
        'role': 1,
        'is_new': 1,
        'level': 1,
        'exp': 0,
        'coin': 0,                      # 金币
        'silver': 0,                    # 银币
        'crystal': 0,                   # 能晶
        'adv_crystal': 0,               # 高级能晶
        'pet_crystal': 0,               # 宠物能晶
        'regist_time': 0,               # 注册时间戳
        'active_time': 0,               # 最后活跃时间戳
        'online_time': 0,               # 在线时长
        'login_days': 0,                # 登录天数
        'continue_login_days': 0,       # 连续登录天数
        'dirt_silver': 0,               # 能力之尘 数量
        'dirt_gold': 0,                 # 超能之尘
        'vip': 0,                       # vip等级
        'vip_exp': 0,                   # vip经验
        'star': 0,                      # star 是个什么东西
        'dailyscore': 0,                # daily reward score
        'dailyscore_done': [],          # daily score 兑换记录
        'free_train_times': 0,          # 学校免费训练次数
        'vip_train_times': 0,           # vip 训练次数
        'free_daily_refresh': 0,        # 每日任务刷新次数
        'daily_refresh_times': 0,       # 花钱刷新每日任务次数
        'level_gift': {},               # 等级奖励
        'got_pay_award': False,         # 是否领取了内测充值奖励
        'server_open_time': 0,          # 开服时间
        'mid_qiku': '',                 # 七酷平台mid
        'platform_channel': '',         # 平台渠道标识
        'enchant': 0,                   # 魔光碎片
        'equip_smelting': 0,            # 装备熔炼值
        'coin_logs': [],                # 钻石日志最新的500条
    }
    _attrs.update(_base_attrs)

    _frozen_attrs = {                   # 存放不能随便修改的，不是整形的一些属性
        'guide': {1: 0},                # 新手引导状态
    }
    _attrs.update(_frozen_attrs)

    _countdown = {                      # 每个元素: (end_time, class_instance), 用add_countdown添加
        'countdown_func_list': [],      # 有些逻辑是倒计时的，
    }                                   # 当到达end_time时，运行class_instance.run(logics_user)
    _attrs.update(_countdown)

    WORLD_BOSS_CD_EXPIRE = 60 * 1       # 世界boss 失败 cd周期
    WORLD_BOSS_REVIVE_EXPIRE = 30 * 1   # 世界boss 购买复活次数 cd周期
    PUBLIC_CITY_UPDATE_RATE = 60 * 60   # 公共地图 点数 更新周期

    _world_boss = {
        'worldboss_cd_ts': 0,           # 世界boss 上次cd时间
        'worldboss_revive_ts': 0,       # 复活时间
        'public_city_point': 10,
        'public_city_point_max': 10,
        'public_city_point_updatetime': 0,  # 上一次行动点数更新时间
    }
    _attrs.update(_world_boss)

    ACTION_POINT_UPDATE_RATE = 60 * 3   # 行动力恢复的cd

    _action_point = {
        'action_point': 100,            # 行动点数
        'action_point_max': 100,        # 行动点数最大值
        'action_point_updatetime': 0.1, # 上一次行动点数更新时间
        'buy_ap_times': 0,              # vip 购买体力次数
    }

    _action_point.update({
        'cmdr_energy': 30,              # 统帅精力
        'cmdr_energy_max': 30,          # 统帅精力最大值
        'cmdr_energy_updatetime': 0.1,  # 上一次统帅精力更新时间
        'used_cmdr_energy': 0,
        'buy_cmdr_times': 0,            # 购买精力次数
    })
    _attrs.update(_action_point)

    CMDR_ENERGY_UPDATE_RATE = 60 * 6    # 统帅经历恢复的cd

    _building_ability = {
        'harbor_ability': 0,            # 避难所等级
        'school_ability': 0,
        'factory_ability': 0,
        'hospital_ability': 0,
        'laboratory_ability': 0,
    }
    _attrs.update(_building_ability)

    _resources = {                      # 用户的资源方面的数据
        'food': 100,                    # 现在拥有的食物
        'food_ability': 10,             # 生食物能力
        'food_pool': 0,                 # 食物池中有多少食物待取
        'food_update_time': 0.1,        # 上次食物池数值改变的时刻

        'metal': 100,                   # 材料
        'metal_ability': 10,
        'metal_pool': 0,
        'metal_update_time': 0.1,
        'metalcore': 0,                 # 精炼石不足

        'energy': 100,                  # 精力
        'energy_ability': 10,
        'energy_pool': 0,
        'energy_update_time': 0.1,
    }
    _attrs.update(_resources)

    _equip_refine = {                   # 装备洗炼的洗炼石
        'refine_stone': 0,
    }
    _attrs.update(_equip_refine)

    _equip_forge = {                    # 装备锻造
        'small_forge_stone': 0,         # 初级锻造石
        'middle_forge_stone': 0,        # 中级锻造石
        'high_forge_stone': 0,          # 高级锻造石
    }
    _attrs.update(_equip_forge)

    _wood = {                           # 主角任务的奖励
        'wood': 0,                      # 木材
    }
    _attrs.update(_wood)

    _soul_stone = {                     # 主角任务的奖励
        'soul_stone': 0,                # 魂石
    }
    _attrs.update(_soul_stone)

    MAX_WAR_FLAG_DEDICATION = 10        # 捐献的最大战旗数

    _association = {
        'association_id': 0,            # 工会id, 0为没有工会
        'association_name': '',         # 工会名字
        'association_dedication_today': {  # 今天向工会捐献的数量
            'goods': 0,
            'war_flag': 0,              # 战旗
            'today': '',                # 今天，用于刷新每天贡献上限
        },
        'join_association_date': 0,     # 加入公会的时间
        'association_dedication': 0,    # 对工会的贡献度
        'guildboss_cd_ts': 0,           # 公会boss 上次cd时间
        'guildboss_revive_ts': 0,       # 复活时间
        'rescue_date': '',              # 救援时间用于重置次数
        'rescue_cd': 0,                 # 救援cd
        'rescue_times': 0,              # 救援使用次数
        'rescue_click_times': 0,        # 救援点击次数, 用于cd期内不让发送多余信息
        'quit_ass_time': '',            # 最新的退出工会的时间
        'guild_fight_reward': 0,        # 自己参加公会战消耗砖石的奖励
        'guild_reward_log': [],         # 记录奖励领取的记录
        'guild_limit_times': 0,         # 每个用户领取工会升级奖励的次数，限制最大40次
        'guild_level_step': 0,          # 每个用户所在工会的升级级数
    }
    _attrs.update(_association)

    _attrs['online_award'] = []         # 激活的在线时长奖励
    _attrs['online_award_done'] = []    # 已经领取的在线时长奖励
    _attrs['_mark'] = 0                 # 设备登录标记，防多设备登录，递增数

    _attrs['double_pay'] = []           # 记录首充双倍的充值项
    _attrs['double_pay_refresh'] = ''   # 首充双倍刷新时间
    
    _attrs['active_double_pay'] = []            # 记录首充双倍的充值项
    _attrs['active_double_pay_refresh'] = ''    # 首充双倍刷新时间

    # 邀请码奖励  {uid: {'gift': [1, 2], 'done': [1, 2]}     用户uid： 邀请码等级奖励配置id
    _attrs['_request_code'] = {
        'master': {},
        'slave': {}
    }

    _attrs['_request_slave_gift'] = {}  # 收徒弟的 奖励记录 {'level': count}
    _attrs['mobile_award'] = {}         # 手机话费奖励 记录
    _attrs['mobile'] = ''               # 手机号

    _attrs['is_ban'] = 0                # 封号
    _attrs['ip'] = ''                   # 用户ip
    _attrs['device_mem'] = ''           # 用户内存
    _attrs['device_mark'] = ''          # mac 地址
    _attrs['like_times'] = 0            # 点赞次数
    _attrs['like_date'] = ''            # 点赞时间
    _attrs['like_log'] = {}             # 点赞记录, {'tp': ['uid', 'uid']}

    _attrs['open_door'] = False         # 是否打开过开门
    _attrs['pre_battle'] = 0            # 是否演示战前技能0:演示;1:不演示
    _pet_resources = {
        'pet_exp_ball': 0,              # 宠物经验球
        'pet_skill_stone': 0,           # 宠物技能石
    }
    _attrs.update(_pet_resources)
    _session = {
        'sid': '',                      # session_id
        'expired': 0,                   # 过期时间
    }
    _attrs.update(_session)
    _attrs['vip_week'] = 0              # 记录vip领取奖励的时间 时间为一年中第几周
    MAX_REQUEST_CODE_SLAVE_NUM = 4      # 邀请码 徒弟数

    # @classmethod
    # def __new__(cls, *args, **kwargs):
    #    return object.__new__(cls)

    def __init__(self, uid=None):
        self.uid = uid
        super(User, self).__init__(uid)

        now = time.time()

        self.food_update_time = now
        self.metal_update_time = now
        self.energy_update_time = now
        self._model_save_func_list = {} # 需要跟user.save一起运行的model.save
        self.combat_rank_key = None     # 战力排行榜的key
        self.level_rank_key = None      # 等级排行榜的key
        self.equipment_rank_key = None  # 装备排行榜的key
        self.world_regain_rank_key = None   # 世界收复度排行的key
        self.commander_rank_key = None  # 统帅能力的排行key
        self.like_rank_key = None       # 点赞排行榜的key

    def _add_model_save(self, model):
        """# add_model_save: 向_model_save_func_list中加入一个model_save_func
        args:
            save_func:    ---    arg
        returns:
            0    ---
        """
        if isinstance(model, User):
            return

        if id(model) in self._model_save_func_list:
            return

        self._model_save_func_list[id(model)] = model.save

    def update_login_stats(self, ts):
        """更新登录状态
        args:
            ts: 更新时间戳
        """
        flag = False
        today = datetime.datetime.today()
        last = datetime.datetime.fromtimestamp(self.active_time)
        delta = (today.date() - last.date()).days
        if delta > 0:
            if delta == 1:
                self.continue_login_days += 1       # 持续登录天数
            else:
                self.continue_login_days = 1

            self.login_days += 1                    # 登录天数
            self.vip_train_times = 0                # vip训练次数
            self.free_train_times = self.FREE_TRAIN_TIMES
            self.free_daily_refresh = self.FREE_DAILY_REWARD_TIMES  # 每日任务刷新次数
            self.daily_refresh_times = 0            # 花钱刷新每日任务次数
            self.dailyscore_done = []               # daily score 兑换记录
            self.dailyscore = 0                     # daily reward score
            self.buy_ap_times = 0                   # vip 购买体力次数
            self.buy_cmdr_times = 0                 # 购买统帅精力次数
            flag = True

        if not self.active_time:
            self.active_time = ts

        if not self.online_time:
            self.online_time = ts

        # 在线时长奖励 离线时间 也计算在内 2014.04.25 songming
        # if ts - self.active_time > self.ONLINE_USERS_TIME_RANGE:
        #     self.online_time = ts - (self.active_time - self.online_time)

        self.active_time = ts
        if flag:
            self.save()
        return delta

    def get_online_time(self, ts=None):
        '''
        获取在线时间
        :param ts:
        :return:
        '''
        ts = ts or int(time.time())
        return ts - self.online_time if self.online_time else 0

    def get_level_rank_key(self):
        '''
        获取等级排行的key
        :return:
        '''
        if self.level_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.level_rank_key = self.make_key_cls(self.LEVEL_RANK_KEY_PREFIX, server_name)
        return self.level_rank_key

    def get_combat_rank_key(self):
        """
        获取战力排行榜的key
        :return:
        """
        if self.combat_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.combat_rank_key = self.make_key_cls(self.COMBAT_RANK_KEY_PREFIX, server_name)
        return self.combat_rank_key
    
    def regist_user_key(self):
        """ 获取注册用户的key
        :return:
        """
        return '%s_%s' % (self.USERS_REGIST_PREFIX, self._server_name)
    
    def online_user_key(self):
        """ 获取在线用户的key
        :return:
        """
        return '%s_%s' % (self.ONLINE_USERS_PREFIX, self._server_name)

    def get_online_uids(self):
        """# 获取在线用户
        """
        r = self.redis
        ts = int(time.time())
        return r.zrevrangebyscore(self.online_user_key(), ts, ts - self.ONLINE_USERS_TIME_RANGE, withscores=1)

    def get_online_user_count(self):
        """
        获得在线用户总数
        """
        r = self.redis
        ts = int(time.time())
        return r.zcount(self.online_user_key(), ts - self.ONLINE_USERS_TIME_RANGE, ts)

    def get_today_new_uids(self, t_ts=None, only_count=False):
        """获取当天新增用户
        args:
            t_ts: 起始时间戳
            only_count: 只返回总数
        """
        r = self.redis

        if t_ts is None:
            today = datetime.datetime.now().date()
            t_ts = int(time.mktime(today.timetuple()))

        if only_count:
            return r.zcount(self.regist_user_key(), t_ts, time.time())
        else:
            return r.zrevrangebyscore(self.regist_user_key(), t_ts, time.time(), withscores=1)

    def get_register_count(self, start_ts=None, end_ts=None):
        """
        获取某天的注册用户数 - 和 get_today_new_uids 相同
        :param t_ts:
        :param only_count:
        :return:
        """
        if end_ts is None:
            today = datetime.datetime.now().date()
            end_ts = int(time.mktime(today.timetuple()))

        return self.redis.zcount(self.regist_user_key(), start_ts, end_ts)
        # return self.get_today_new_uids(t_ts, only_count=True)

    def get_checkin_user_count(self, ts=None):
        """
        按每日登錄記錄，統計當日的登錄用戶數
        :param ts: 時間戳
        :return:
        """
        str_date = time.strftime('%Y%m%d', time.localtime(ts))
        rkey = '%s_%s' % (self.USERS_CHECKIN_PREFIX, str_date)

        return self.redis.hlen(rkey)

    def get_uids_by_active_days(self, active_days=0):
        """# 按登录时间 获取所有用户
            active_days: 活跃时间    -1： 当天登录过，0: 不限制;  正整数: 最近多少天登录过
        """
        r = self.redis
        end_ts = int(time.time())
        today = datetime.datetime.now().date()
        start_ts = int(time.mktime(today.timetuple()))

        if active_days == 0:            # 不限制
            start_ts = 0
        elif active_days > 0:           # n天之前
            start_ts = start_ts - 3600 * 24 * active_days

        return r.zrevrangebyscore(self.online_user_key(), start_ts, end_ts)

    def get_user_count_by_active_days(self, active_days=0):
        """# 按登录时间 获取所有用户
            active_days: 活跃时间    -1： 当天登录过，0 :不限制;  正整数: 最近多少天登录过
        """
        r = self.redis

        end_ts = int(time.time())
        today = datetime.datetime.now().date()
        start_ts = int(time.mktime(today.timetuple()))

        if active_days == 0:
            start_ts = 0
        elif active_days > 0:
            start_ts = start_ts - 3600 * 24 * active_days

        return r.zcount(self.online_user_key(), start_ts, end_ts)

    def get_redis_userd_memory(self):
        '''
        获取redis使用的内存
        used_memory_human: Redis分配器分配的内存总量，指Redis存储的所有数据所占的内存
        used_memory_peak_human: 以更直观的格式返回redis的内存消耗峰值
        used_memory_rss: 向操作系统申请的内存大小。与 top 、 ps等命令的输出一致。
        :return:
        '''
        redis = self.redis
        info = redis.info()
        return '%s/%s/%sG' % (info.get('used_memory_human'), info.get('used_memory_peak_human'), '%0.2f' % (info.get('used_memory_rss', 0) / 1024.0 ** 3))

    def fetch_server_open_time(self):
        '''
        获取开服的时间
        :return:
        '''
        if not self.server_open_time:
            server_list = ServerConfig.get().server_list()
            server_name = self.uid[:-7]
            for i in server_list:
                if i['server'] == server_name:
                    self.server_open_time = i['open_time']
        return self.server_open_time

    def get_double_pay(self):
        """ 获取首冲双倍数据

        :return:
        """
        # 首充双倍活动时间段
        time_config = game_config.inreview.get(144, {})             # 获取活动是否开启
        time_config_name = time_config.get('name', '')
        time_config_servers = time_config.get('story', '')
        if time_config_name:
            start_time, end_time = time_config_name.split(',')
            servers = time_config_servers.split(',') if time_config_servers else []
        else:
            start_time, end_time = '', ''
            servers = []

        tody = time.strftime('%F')
        if start_time <= tody <= end_time and (not servers or (servers and self._server_name in servers)):
            pay_list = self.active_double_pay
        else:
            pay_list = self.double_pay

        return pay_list


    def update_action_point(self):
        """update_action_point: 行动点数的计时更新
                1, 只有在当前行动点数低于最大值的时候才“计时更新”
                2, 当前时刻－最后更新时刻 >= 更新周期 则行动点数做加法
        returns:
            True    ---   # 如果action_point更新了，返回True
        """
        now = time.time()
        last_update_time = self.action_point_updatetime
        if self.action_point < self.action_point_max:
            multiple, left_time = divmod(int(now - last_update_time), self.ACTION_POINT_UPDATE_RATE)  # 需要加上的总点数
            if multiple:
                self.action_point += multiple
                if self.action_point > self.action_point_max:
                    self.action_point = self.action_point_max
                self.action_point_updatetime = now - left_time  # 没有达到周期的那些时间，应该计算入下一个周期中

        last_update_time = self.public_city_point_updatetime
        if self.public_city_point < self.public_city_point_max:
            multi, left_time = divmod(int(now - last_update_time), self.PUBLIC_CITY_UPDATE_RATE)
            if multi:
                self.public_city_point += multi
                if self.public_city_point > self.public_city_point_max:
                    self.public_city_point = self.public_city_point_max
                self.public_city_point_updatetime = now - left_time

        last_update_time = self.cmdr_energy_updatetime
        if self.cmdr_energy < self.cmdr_energy_max:
            multi, left_time = divmod(int(now - last_update_time), self.CMDR_ENERGY_UPDATE_RATE)
            if multi:
                self.cmdr_energy += multi
                if self.cmdr_energy > self.cmdr_energy_max:
                    self.cmdr_energy = self.cmdr_energy_max
                self.cmdr_energy_updatetime = now - left_time

        if self.worldboss_cd_ts and now - self.worldboss_cd_ts > self.WORLD_BOSS_CD_EXPIRE:         # 世界boss攻击时间cd
            self.worldboss_cd_ts = 0

        if self.worldboss_revive_ts and now - self.worldboss_revive_ts > self.WORLD_BOSS_REVIVE_EXPIRE:     # 世界boss复活世界cd
            self.worldboss_revive_ts = 0

        if self.guildboss_cd_ts and now - self.guildboss_cd_ts > self.WORLD_BOSS_CD_EXPIRE:
            self.guildboss_cd_ts = 0
        
        if self.guildboss_revive_ts and now - self.guildboss_revive_ts > self.WORLD_BOSS_REVIVE_EXPIRE:
            self.guildboss_revive_ts = 0

        # 等级奖励
        for lv, expire in self.level_gift.items():
            if now > expire:
                self.level_gift.pop(lv)

        # 清空首充双倍记录
        time_config = game_config.inreview.get(144, {})
        time_config_name = time_config.get('name', '')
        if time_config_name:
            start_time, end_time = time_config_name.split(',')
        else:
            start_time, end_time = '', ''
        today = time.strftime('%F')
        if start_time <= today <= end_time and not (start_time <= self.active_double_pay_refresh <= end_time):
            self.active_double_pay_refresh = today      # '2020-03-10'
            self.active_double_pay = []

    def add_countdown(self, func, end_time):
        """# add_countdown: docstring
        args:
            func, end_time:    ---    arg
        returns:
            0    ---
        """
        temp_flag = time.time()
        self.countdown_func_list.append((end_time, func, temp_flag))
        return temp_flag

    @property
    def online(self):
        # 最后活跃时间在两个小时内算在线
        active = time.time() - 2 * 3600
        return self.active_time > active

    def filter_guide(self, goto=False):
        """
        过滤要进行的新手引导步骤
        args:
            goto: 若是登录操作，需要重置引导状态
        returns:
            {}: 所有需要进行引导的状态
        :param goto:
        :return:
        """
        guide = {}
        for sort, step in self.guide.iteritems():
            config = game_config.guide.get(sort)
            # 配置容错
            if not config:
                continue
            # 跳过gacha的引导
            if sort == 1 and self.level >= 3 and step < 19:
                step = 19
            # 级别大于5级就跳过sort=2(装备强化)的引导
            elif sort == 2 and self.level >= 5:
                step = max(config)
            # if step < max(config):
            # guide[sort] = config[step]['goto'] if goto and step else step
            # 不再回跳步骤
            guide[sort] = step

        return guide

    def do_guide(self, sort, step=0, save=True):
        """记录新手引导步骤
        args:
            sort: 模块分类
            step: 步骤，0表示需要开始，其它是已完成的步骤
            save: 是否保存
        """
        if sort not in self.guide or step:
            if len(game_config.guide[sort]) > 2:
                if step + 1 == max(game_config.guide[sort]):
                    step += 1
            if step >= self.guide.get(sort, 0):
                self.guide[sort] = step
                if save:
                    self.save()


    #####################################排行榜#####################################
    def get_equipment_rank_key(self):
        """ 装备强度排行

        :return:
        """
        if self.equipment_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.equipment_rank_key = self.make_key_cls(self.EQUIPMENT_RANK_KEY_PREFIX, server_name)
        return self.equipment_rank_key

    def get_world_regain_rank_key(self):
        """  世界收复排行

        :return:
        """
        if self.world_regain_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.world_regain_rank_key = self.make_key_cls(self.WORLD_REGAIN_RANK_KEY_PREFIX, server_name)
        return self.world_regain_rank_key

    def get_commander_rank_key(self):
        """ 统帅能力排行

        :return:
        """
        if self.commander_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.commander_rank_key = self.make_key_cls(self.COMMANDER_RANK_KEY_PREFIX, server_name)
        return self.commander_rank_key

    def get_like_rank_key(self):
        """ 点赞排行

        :return:
        """
        if self.like_rank_key is None:
            server_name = settings.get_father_server(self._server_name)
            self.like_rank_key = self.make_key_cls(self.LIKE_RANK_KEY_PREFIX, server_name)
        return self.like_rank_key

    def update_like_rank(self, targat_uid, num=1):
        """ 更新点赞排行

        :return:
        """
        rank_key = self.get_like_rank_key()
        fredis = self.get_father_redis()
        fredis.zincrby(rank_key, targat_uid, generate_rank_score(num))

    def day_refresh_like_times(self):
        """ 每天刷新点赞次数

        _attrs['like_times'] = 0      # 点赞次数
        _attrs['like_date'] = ''      # 点赞时间
        _attrs['like_log'] = {}      # 点赞记录,    {'tp': ['uid', 'uid']}

        :return:
        """
        str_date = time.strftime('%Y-%m-%d')
        if self.like_date != str_date:
            self.like_date = str_date
            self.like_times = 0
            self.like_log = {}
            self.save()

    #####################################排行榜#####################################

    def set_pre_battle(self, toggle):
        """
        设置是否演示战前动画
        :param toggle:
        :return:
        """
        self.pre_battle = toggle

    def get_pre_battle(self):
        """
        设置是否演示战前动画
        :return:
        """
        return self.pre_battle