#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
import json
import redis
import settings
import cPickle as pickle

from lib.db import make_redis_client

from lib.utils.debug import print_log


class ModelPayment(object):
    """支付数据, 与用户数据分离
    """
    redis = make_redis_client(settings.PAYMENT_CACHE)
    all_order_ids_key = 'payment_order_ids'             # 所有支付订单的order_id
    per_user_orders_key_prefix = 'user_order_'          # 单个用户的所有充值订单 存储key
    pay_award_key_prefix = 'pay_award'                  # 获取支付金额的奖励
    backup_pay_award_key_prefix = 'pay_award_backup'    # 备份支付奖励数据 {'uid': uid, 'pay': d, 'ts': int(time.time())}
    mobile_pay_award_prefix = 'mobile_pay'              # list 手机支付
    mobile_pay_award_backup_prefix = 'mobile_pay_backup' # SortedSet

    @classmethod
    def get(cls, uid=None):
        return cls()

    @classmethod
    def make_redis_key(cls, obj):
        """生成redis储存key, 格式为
           用户uid_充值日期_充值coin数_定单id
        """
        return '%s||%s||%s||%s' % (obj['user_id'], obj['order_time'][:10],
                                   obj['order_coin'], obj['order_id'])

    @classmethod
    def find_keys(cls, uid='*', date='*', coin='*', order_id='*'):
        """按照条件查询key
        """
        redis_key = '%s||%s||%s||%s' % (uid, date, coin, order_id)

        return cls.redis.keys(redis_key)

    @classmethod
    def exists_id(cls, redis_key):
        return cls.redis.exists(redis_key)

    @classmethod
    def exists_order_id(cls, order_id):
        '''
        是否存在此订单
        :param order_id: order_id订单id
        :return:
        '''
        rs = cls.redis.zscore(cls.all_order_ids_key, order_id)
        return False if rs is None else True

    @classmethod
    def get_record(cls, key):
        '''
        获取充值记录
        :param key: 充值的key order_id订单id
        :return:
        '''
        data = cls.redis.get(key)
        return pickle.loads(data) if data else data

    @classmethod
    def del_record(cls, key):
        '''
        删除订单数据
        :param key: order_id订单id
        :return:
        '''
        cls.redis.delete(key)

    @classmethod
    def make_user_order_index(cls, user_id):
        """单个用户的所有充值订单 存储key
        """
        return '%s_%s' % (cls.per_user_orders_key_prefix, user_id)

    @classmethod
    def set_record(cls, key, obj):
        '''
        存储订单
        :param key: order_id订单id
        :param obj: 订单数据
        :return:
        '''
        data = pickle.dumps(obj)
        cls.redis.set(key, data)
        # order_id 单独存一份索引，便于检查是否 exists 以及按时间条件查询
        cls.redis.zadd(cls.all_order_ids_key, **{obj['order_id']: int(time.time())})
        cls.redis.lpush(cls.make_user_order_index(obj['user_id']), obj['order_id'])

    @classmethod
    def find(cls, start_ts, end_ts):
        '''
        获取一段时间充值数据
        :param start_ts: 开始时间错
        :param end_ts: 结束时间错
        :return:
        '''
        keys = cls.redis.zrangebyscore(cls.all_order_ids_key, start_ts, end_ts)
        for key in keys:
            yield cls.get_record(key)

    @classmethod
    def find_by_uid(cls, uid, num=0):
        '''
        获取玩家的充值记录
        :param uid: 玩家uid
        :param num: 获取数量
        :return:
        '''
        keys = cls.redis.lrange(cls.make_user_order_index(uid), 0, num - 1)
        for key in keys:
            yield cls.get_record(key)

    @classmethod
    def get_pay_award(cls, account):
        '''
        获取支付奖励
        :param account: 支付金额
        :return:
        '''
        d = cls.redis.hget(cls.pay_award_key_prefix, account)
        return json.loads(d) if d else []

    @classmethod
    def backup_pay_award(cls, account, uid):
        '''
        备份支付奖励
        :param account: 支付金额
        :param uid: 支付uid
        :return:
        '''
        d = cls.redis.hget(cls.pay_award_key_prefix, account)
        if d:
            pipe = cls.redis.pipeline()
            pipe.hset(cls.backup_pay_award_key_prefix, account, {'uid': uid, 'pay': d, 'ts': int(time.time())})
            pipe.hdel(cls.pay_award_key_prefix, account)
            pipe.execute()


class Payment(ModelPayment):
    """支付数据, 与用户数据分离
    """
    def __init__(self, uid='payment'):
        pass

    @classmethod
    def pay(cls, obj, user):
        """记录接口
        args:
            obj: 充值数据字典对象
            user: 用户对象
        returns:
            记录成功返回true, 否则false
        """
        # redis_key = cls.make_redis_key(obj)
        if cls.exists_order_id(obj['order_id']):
            return False

        cls.set_record(obj['order_id'], obj)
        return True


import MySQLdb
escape_string = MySQLdb._mysql.escape_string
from lib.utils import md5


def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)


def _smart(v):
    t = type(v)
    if t == str:
        return v
    elif t == unicode:
        return force_str(v)
    elif (t == int) or (t == long) or (t == float):
        return str(v)
    elif t == datetime.datetime:
        return v.strftime("%Y-%m-%d %H:%M:%S")
    return str(v)


# {
#     'admin': 'default',
#     'gift_coin': 6,
#     'level': 99,
#     'old_coin': 3090,
#     'order_coin': 60,
#     'order_id': '1_1397051527.07_ypj',
#     'order_money': 6,
#     'order_time': '2014-04-09 21:52:07',
#     'platform': 'admin',
#     'product_id': 1,
#     'raw_data': 'virtual_pay_by_admin',
#     'reason': u'\u4ee3\u5145',
#     'scheme_id': 'zombiecoinTier1',
#     'user_id': u'test'
# }


def sql_value(dict_data):
    return ','.join(map(
        lambda x: """%s='%s'""" % (
            x[0], escape_string(_smart(x[1])) if x[1] is not None else 'null'
        ),
        dict_data.iteritems()
    ))


class MySQLConnect(object):
    """# ModelPayment: 支付记录，mysql"""
    def __init__(self, mysql_host):
        self.mysql_host = mysql_host
        host_config = self.mysql_host
        self.table_prefix = host_config['table_prefix']
        self.conn = MySQLdb.connect(
            host=host_config['host'],
            user=host_config['user'],
            passwd=host_config['passwd'],
            db=host_config['db'],
            charset="utf8",
        )
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        pass
        # self.cursor.close()
        # self.conn.close()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, key):
        '''
        执行sql语句
        :param sql: sql语句
        :param key: 表的标识
        :return:
        '''
        sid = int(md5(str(key)), 16)
        table = self.table_prefix + '_' + str(sid % 16)
        sql = sql % table + ';'
        self.cursor.execute(sql)
        self.conn.commit()

    def exists_order_id(self, key):
        '''
        检查是否存在此订单
        :param key:
        :return:
        '''
        sid = int(md5(str(key)), 16)
        table = self.table_prefix + '_' + str(sid % 16)
        return self.cursor.execute('select order_id from %s where order_id="%s";' % (table, key))

    def pay(self, data, user):
        """# insert: docstring
        args:
            arg:    ---    arg
            data: 支付数据
        returns:
            0    ---
        """
        key = data['order_id']
        if self.exists_order_id(key):
            return False
        sql = """insert into %s set """ + sql_value(data)
        self.execute(sql, key)
        return True

    def find(self, start_dt, end_dt):
        '''
        查找数据库的数据
        :param start_dt: 开始时间
        :param end_dt: 结束时间
        :return:
        '''
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        for table in ['%s_%s' % (self.table_prefix, x) for x in range(16)]:
            sql = 'select * from %(table)s where order_time >= "%(start_dt)s" and order_time <= "%(end_dt)s";' % \
                            {'table': table, 'start_dt': start_dt, 'end_dt': end_dt}
            count = cursor.execute(sql)
            while count > 0:
                count -= 1
                yield cursor.fetchone()

    def find_by_uid(self, user_id):
        '''
        根据用户uid查询充值记录
        :param user_id:
        :return:
        '''
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        for table in ['%s_%s' % (self.table_prefix, x) for x in range(16)]:
            sql = 'select * from %(table)s where user_id="%(user_id)s";' % {'table': table, 'user_id': user_id}
            count = cursor.execute(sql)
            while count > 0:
                count -= 1
                yield cursor.fetchone()

    def find_by_uid_spend(self, user_id):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        from datetime import datetime, timedelta
        target_time = str(datetime.today() - timedelta(days=10))[:-7]

        for table in ['%s_%s' % (self.table_prefix, x) for x in range(16)]:
            sql = 'select * from %(table)s where uid="%(user_id)s" and subtime >= "%(target_time)s";' % \
                  {'table': table, 'user_id': user_id, 'target_time': target_time}

            count = cursor.execute(sql)
            while count > 0:
                count -= 1
                yield cursor.fetchone()


def payment_insert(key, data):
    """# insert: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    with MySQLConnect(settings.PAYLOG_HOST) as c:
        if c.exists_order_id(key):
            return False
        sql = """insert into %s set """ + sql_value(data)
        c.execute(sql, key)
        return True


def spend_data(key, data):
    """# insert: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    with MySQLConnect(settings.SPENDLOG_HOST) as c:
        sql = """insert into %s set """ + sql_value(data)
        c.execute(sql, key)


def _copy_payinfo_from_redis_to_mysql():
    '''
    把redis数据插入到mysql数据库中
    :return:
    '''
    success, fail = [], []
    p = Payment()
    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    keys = p.redis.zrangebyscore(p.all_order_ids_key, 0, time.time())
    for key in keys:
        data = p.get_record(key)
        if mysql_conn.pay(data, None):      # user=None
            success.append(key)
        else:
            fail.append(key)
    return success, fail