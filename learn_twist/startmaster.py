#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/22 15:31
# @version: 0.0.1
# @Author: houguangdong
# @File: startmaster.py
# @Software: PyCharm

# import uvloop
# import asyncio
# from twisted.internet import asyncioreactor

# loop = uvloop.new_event_loop()
# asyncio.set_event_loop(loop)
# asyncioreactor.install(eventloop=loop)


if __name__ == "__main__":
    from learn_twist.master.master import Master
    master = Master()
    master.config('config.json', 'app_main.py')
    master.start()

