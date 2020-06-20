#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/17

import json, os, fcntl
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from poker.util import timestamp


def updateStatus(status):
    stfile = None
    try:
        sid = ftcon.global_config["server_id"]
        log_path = ftcon.global_config["log_path"]
        stpath = log_path + '/status.' + sid
        if os.path.isfile(stpath):
            stfile = open(stpath, 'r')
            data = json.loads(stfile)
            stfile.close()
            stfile = None
        else:
            datas = {'creatTime': timestamp.formatTimeMs()}

        _updateProcessStatus(datas)

        datas['status'] = status
        datas['updateTime'] = timestamp.formatTimeMs()

        stfile = open(stfile, 'w')
        fcntl.flock(stfile, fcntl.LOCK_EX)
        stfile.write(json.dumps(datas, sort_keys=True, indent=4, separators=(', ', ' : ')))
        fcntl.flock(stfile, fcntl.LOCK_UN)
        stfile.close()
        stfile = None
    except:
        ftlog.error()
    finally:
        try:
            if stfile:
                fcntl.flock(stfile, fcntl.LOCK_UN)
        except:
            pass
        try:
            if stfile:
                stfile.close()
        except:
            pass


def _updateProcessStatus(datas):
    """更新进程状态"""
    if 'pid' not in datas:
        datas['pid'] = os.getpid()
        datas['ppid'] = os.getppid()