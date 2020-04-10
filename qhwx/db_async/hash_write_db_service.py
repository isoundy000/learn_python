# -*- coding:utf-8 -*-
import datetime
import logging
import time
import sys
import os

base_dir = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(base_dir, "pid_file", "%s.pid" % os.path.basename(sys.argv[0])[:-3]), "w+") as f:
    f.write(str(os.getpid()))
sys.path.append(base_dir)

print sys.path
from jpzmg_init import project_init
from rklib.model.mysql import MysqlEngine
from rklib.model.redis import RedisEngine
from rklib.model.redis_hash import RedisHashEngine

project_init()

from rklib.core import app

log_file_name = "hash_write_db_service.log"
log = logging.getLogger(log_file_name)
format_str = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# file_handler = logging.FileHandler(log_file_name)
show_handler = logging.StreamHandler()  # 往屏幕上输出
# file_handler.setFormatter(format_str)
show_handler.setFormatter(format_str)  # 设置屏幕上显示的格式
# log.addHandler(file_handler)
log.addHandler(show_handler)
log.setLevel(logging.DEBUG)

back_redis_hash = app.get_engine('back_redis_hash')  # type: RedisHashEngine
redis_engine = app.get_engine('redis')  # type: RedisEngine
mysql_engine = app.get_engine('mysql')  # type: MysqlEngine

_class_cache_ = {}


def get_cls_by_cache_key(cache_key):
    """
    根据cache_key获取类对象
    """
    mc_name = cache_key[cache_key.find("|") + 1:cache_key.rfind("|")]
    my_class = _class_cache_.get(mc_name)
    if my_class:
        return my_class
    else:
        pos = mc_name.rfind(".")
        module_name = mc_name[:pos]
        class_name = mc_name[pos + 1:]
        mod = __import__(module_name, globals(), locals(), [class_name], -1)
        my_class = getattr(mod, class_name)
        _class_cache_[mc_name] = my_class
    return my_class


def write_to_db():
    """
    写数据到数据库
    """
    log.info("write To DB begin at %s" % datetime.datetime.now())
    total_count = 0
    err_count = 0
    while 1:
        try:
            key_all_count = back_redis_hash.hlen("back_key")
            log.info("back_key key count: %s", key_all_count)
            if key_all_count < 30000:
                data = back_redis_hash.hget_all("back_key")
            else:
                data = back_redis_hash.hscan("back_key", count=30000)[1]
            for key, val in data.items():
                log.info("key: %s    val: %s", key, val)
                val = int(val)
                if val == 0:
                    continue
                write_db(key, val)
                total_count += 1
                if (total_count % 10000) == 0:
                    log.info("[0] Read %d keys from redis queue.", total_count)
            log.info("sleep 10")
            time.sleep(10)
        except Exception as e:
            err_count += 1
            log.info("code err,  err info: %s", e)
            if err_count >= 10:
                break


def del_hash_key(cache_key):
    log.info("del hash key: %s", cache_key)
    back_redis_hash.hdelete("back_key", cache_key)
    return


def write_db(cache_key, operation):
    cls_obj = get_cls_by_cache_key(cache_key)
    pkey = cache_key[cache_key.rfind("|") + 1:]
    res = redis_engine.get_data(cls_obj, pkey)
    log.info("cache_key: %s \t lost val: %s", cache_key, operation)
    operation_count = back_redis_hash.hincrby("back_key", cache_key, -operation)
    if operation_count == 0:
        del_hash_key(cache_key)
    if operation_count < 0:
        return
    log.info("update  key: %s", cache_key)
    obj = cls_obj.loads(res)
    obj.need_insert = False
    obj.put_only_bottom()
    return


if __name__ == "__main__":
    write_to_db()
