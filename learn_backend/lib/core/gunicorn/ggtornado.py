#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gunicorn.workers.gtornado import TornadoWorker

# 此方法真对19.3.0版本一下，以上的版本还没有出，master已经取消了timeouts判断，tag更新后不再需要次类，直接使用新出的tag即可


class GTornadoWorker(TornadoWorker):

    def stop_ioloop(self):
        if not self.ioloop._callbacks:
            self.ioloop.stop()