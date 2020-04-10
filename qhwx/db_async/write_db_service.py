# -*- coding: utf-8 -*-

import os
import sys

# from rklib.model import storage_context
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jpzmg.settings")
from rklib.core import app
from django.conf import settings

app.debug = settings.DEBUG
print settings.BASE_DIR
app.init(storage_cfg_file=settings.BASE_DIR + "/config/storage.json",
         logic_cfg_file=settings.BASE_DIR + "/config/logic.json",
         model_cfg_file=settings.BASE_DIR + "/config/model.json")

from Queue import Empty
from multiprocessing import Process, Queue, Value, Manager
import time
import datetime
import traceback
import cPickle as pickle

import logging

log = logging.getLogger('daemon')
hdlr = logging.FileHandler("write_db_service.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

redis_queue = app.get_engine('redis_queues').redis_queue
darwin = True if sys.platform == "darwin" else False

from rklib.client.redis_cli import redis_manager

redis_engine = app.get_engine('redis')
# -------------------------------------------------------------------------------
_class_cache_ = {}


def _getClsByCacheKey(cache_key):
    '''
    根据cache_key获取类对象
    '''
    mc_name = cache_key[cache_key.find("|") + 1:cache_key.rfind("|")]
    myclass = _class_cache_.get(mc_name)
    if myclass:
        return myclass
    else:
        pos = mc_name.rfind(".")
        module_name = mc_name[:pos]
        class_name = mc_name[pos + 1:]
        mod = __import__(module_name, globals(), locals(), [class_name], -1)
        myclass = getattr(mod, class_name)
        _class_cache_[mc_name] = myclass
    return myclass


# -------------------------------------------------------------------------------
def _writeDB(cache_key, count, wd):
    # print key, count, wd

    res = None
    for x in range(5):
        myclass = _getClsByCacheKey(cache_key)
        pkey = cache_key[cache_key.rfind("|") + 1:]
        res = redis_engine.get_data(myclass, pkey)

        print type(res), res

        if res is not None:
            break
        time.sleep(0.01)
    if res:
        #     # myclass = _getClsByCacheKey(key)
        obj = myclass.loads(res)
        obj.need_insert = False
        obj.put_only_bottom()
    #     ttclient.delete(key)
    else:
        log.error("[0] None: " + cache_key)


# -------------------------------------------------------------------------------
def writeWorker(q, count, d):
    while True:
        try:
            key = q.get(1)
            print key
            if key:
                _writeDB(key, count, d)
                count.value += 1
        except Empty:
            time.sleep(5)
        except Exception, e:
            log.error("[0] key:" + key)
            log.error(traceback.format_exc())


# -------------------------------------------------------------------------------
def showStatus(q, count, wd):
    while True:
        if not darwin:
            log.info("[0] queue_size:%d  write_to_db_count:%d" % (q.qsize(), count.value))
        else:
            log.info("[0] queue_size:#  write_to_db_count:%d" % (count.value))
        count.value = 0
        time.sleep(10)

        # -------------------------------------------------------------------------------


def writeToDB(workQueue, workDict):
    log.info("writeToDB begin at %s", datetime.datetime.now())
    total_count = 0

    while 1:
        if redis_queue.empty():
            break

        if not darwin and workQueue.qsize() > 5000000:
            log.info("queue is full! break from loop!")
            break

        cache_key = redis_queue.get(False)
        workQueue.put(cache_key)
        total_count += 1
        if (total_count % 10000) == 0:
            log.info("[0] Read %d keys from redis queue.", total_count)

    log.info("writeToDB done. read %d keys from redis queue. ", total_count)

    # for cache_key in ttclient.iterkeys(0):
    #     workQueue.put(cache_key)
    #     total_count += 1
    #     if (total_count % 10000) == 0:
    #         log.info("[0] Read %d keys from ttserver.", total_count)
    #     if not darwin and workQueue.qsize() > 5000000:
    #         log.info("queue is full! break from loop!")
    #         break
    # ttclient.close()
    # log.info("writeToDB done. read %d keys from ttserver. ", total_count)


# -------------------------------------------------------------------------------
def main():
    print "Start!"
    import daemon
    daemon.daemonize(noClose=True)
    # 初始化工作进程
    num_of_workers = 2
    workers = []
    workQueue = Queue()
    writeCount = Value("i", 0)
    manager = Manager()
    workDict = manager.dict()
    for i in range(num_of_workers):
        worker = Process(target=writeWorker, args=(workQueue, writeCount, workDict))
        workers.append(worker)
    for worker in workers:
        worker.start()

    # 定时打印进度的进程
    sp = Process(target=showStatus, args=(workQueue, writeCount, workDict))
    sp.start()

    # 定期从ttserver读取要保存的数据
    while True:
        btime = time.time()
        try:
            writeToDB(workQueue, workDict)
        except:
            log.error(traceback.format_exc())
        etime = time.time()
        log.info("Use time: %f", etime - btime)
        stime = 1800 - (etime - btime)
        if stime > 0:
            time.sleep(stime)


if __name__ == "__main__":
    main()
