# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/8/15.

    一个计划任务必须配置两个参数:
        times_in_day表示一天之内的触发时间点,
        days表示计划任务在哪一天触发；

    times_in_day有两种配置方式：
        一种是硬配list，把所有时间点列出:
        "times_in_day":
        {
            "list":["10:00", "11:20", "11:30", "22:30"]
        }
        还有一种按周期配置：
        "times_in_day":
        {
            "first":"10:00",      #开始时间点
            "interval":5,         #按分钟的周期
            "count":200           #重复次数
        }


    days也有类似的两种配置方式:
        硬配list:
        "days":
        {
            "list":["20130101", "20130201", "20130301"]
        }
        还有一种按周期配置，周期支持d（天）w（周）m（月）y（年）
        "days":
        {
            "first":"20130107",
            "interval":"1d",
            "count":2000         #重复次数最多配置MAX_DAY_COUNT
        }

    按照上述配置初始化后，将会得到时间和日期两个列表

    注意：需要安装第三方模块dateutil.relativedelta:
          http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
"""

import datetime
import json

from dateutil.relativedelta import relativedelta

import freetime.util.log as ftlog


class FTCron():
    MAX_DAY_COUNT = 1000

    def __init__(self, config_json):
        self._timelist = []
        self._dayslist = []
        try:
            if isinstance(config_json, basestring):
                self._config = json.loads(config_json)
            else:
                self._config = config_json

            # 整理一天内的时间点列表
            if "list" in self._config["times_in_day"]:
                lt = self._config["times_in_day"]["list"]
                for l in lt:
                    lg = l.split(":")
                    hour = int(lg[0])
                    minu = int(lg[1])
                    sec = int(lg[2]) if len(lg) > 2 else 0
                    self._timelist.append(datetime.time(hour, minu, sec))
            else:
                first = self._config["times_in_day"]["first"]
                inter = int(self._config["times_in_day"]["interval"])
                count = self._config["times_in_day"]["count"]

                firsts = []
                if not first:
                    firsts.append(first)
                elif isinstance(first, (unicode, str)):
                    firsts.append(first)
                elif isinstance(first, list):
                    firsts = first

                for first in firsts:
                    lg = first.split(":")
                    hour = int(lg[0])
                    minu = int(lg[1])
                    sec = int(lg[2]) if len(lg) > 2 else 0
                    ftime = datetime.time(hour, minu, sec)
                    self._timelist.append(ftime)
                    dtime = datetime.timedelta(minutes=inter)
                    for x in xrange(count):
                        ftime = (datetime.datetime.combine(datetime.date(1, 1, 1), ftime) + dtime).time()
                        if ftime > self._timelist[0]:
                            self._timelist.append(ftime)
                        else:
                            ftlog.debug("warning!!! times_in_day count too large!!!", x)
                            break

            # 整理天列表
            if "list" in self._config["days"]:
                ld = self._config["days"]["list"]
                for d in ld:
                    self._dayslist.append(datetime.datetime.strptime(d, "%Y%m%d"))
            else:
                first = self._config["days"]["first"]
                inter = self._config["days"]["interval"]
                ninter = int(inter[0])
                iinter = inter[1]
                if iinter == 'd':
                    intdelta = relativedelta(days=ninter)
                if iinter == 'w':
                    intdelta = relativedelta(weeks=ninter)
                if iinter == 'm':
                    intdelta = relativedelta(months=ninter)
                if iinter == 'y':
                    intdelta = relativedelta(years=ninter)
                count = self._config["days"]["count"]
                if count > self.MAX_DAY_COUNT:
                    count = self.MAX_DAY_COUNT
                    ftlog.debug("warning!!! days count too large!!!", count)

                firsts = []
                if not first:
                    firsts.append(first)
                elif isinstance(first, (unicode, str)):
                    firsts.append(first)
                elif isinstance(first, list):
                    firsts = first

                for first in firsts:
                    if first:
                        fday = datetime.datetime.strptime(first, "%Y%m%d")
                    else:
                        fday = datetime.datetime.now()
                    self._dayslist.append(fday)
                    for x in xrange(count):
                        fday = fday + intdelta
                        self._dayslist.append(fday)

            self._dayslist.sort()
            self._timelist.sort()
        except:
            ftlog.error("parse config json error:", config_json)
            self._config = None

    def getTimeList(self):
        return self._timelist

    def getDaysList(self):
        return self._dayslist

    def getTodayNextLater(self):
        """
        如果今天有match的时间点，返回最近一个点还要等多少秒
        """
        ntime = datetime.datetime.now()
        nd = ntime.date()
        nt = ntime.time()
        # 检查日期
        for d in self._dayslist:
            if d.date() == nd:
                # 检查时间
                for t in self._timelist:
                    if t >= nt:
                        nexttime = datetime.datetime.combine(nd, t)
                        timed = nexttime - ntime
                        return timed.total_seconds()
        return -1

    def getNextTime(self, ntime=None):
        ntime = ntime or datetime.datetime.now()
        nd = ntime.date()
        for d in self._dayslist:
            if d.date() >= nd:
                for t in self._timelist:
                    nexttime = datetime.datetime.combine(d, t)
                    if nexttime >= ntime:
                        return nexttime
        return None

    def getNextLater(self, ntime=None):
        """
        返回最近一个点还要等多少秒
        """
        ntime = ntime or datetime.datetime.now()
        nexttime = self.getNextTime(ntime)
        if nexttime:
            timed = nexttime - ntime
            return timed.total_seconds()
        return -1


if __name__ == '__main__':
    conf = {
        "days": {
            "count": 365,
            "first": "",
            "interval": "1d"
        },
        "times_in_day": {
            "list": [
                "20:00",
                "00:00",
                "22:00"
            ]
        }
    }
    cron = FTCron(conf)
    print cron.getDaysList()
    print cron.getTimeList()
    nt = datetime.datetime.strptime('2017-03-17 23:00:00', '%Y-%m-%d %H:%M:%S')
    print cron.getNextTime(nt)