# -*- encoding: utf-8 -*-
'''
Created on 2018年12月11日

@author: houguangdong
'''

# from celery import Celery
# from celery.bin import worker as celery_worker
# import celeryconfig
#
# broker = 'amqp://'
# backend = 'amqp'
# app = Celery('celery_test', backend=backend, broker=broker)
# app.config_from_object(celeryconfig)
#
# @app.task
# def mytask0(task_name):
#     print "task0: %s" % task_name
#     return task_name
#
# @app.task


class Account(list):

    ll = []

    def __init__(self, account):
        list.__init__([])
        self.append(account)

    def getlen1(self):
        print(len(self))
        print self

    @classmethod
    def getlen2(cls, self):
        cls.ll = self
        print cls.ll
        print(len(cls.ll))

if __name__ == '__main__':
    a = Account(['jone', 27, '36'])
    a.getlen1()
    a.getlen2(a)