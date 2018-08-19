#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_may_first(Base):

    __tablename__ = 't_activity_may_first'

    rid = Column(Integer, primary_key=True)
    day1 = Column(Integer, nullable=False, default=0)           # 每日登陆
    day2 = Column(Integer, nullable=False, default=0)           # 1激活奖励 2领取奖励 3奖励已过期
    day3 = Column(Integer, nullable=False, default=0)
    day4 = Column(Integer, nullable=False, default=0)
    day5 = Column(Integer, nullable=False, default=0)
    day6 = Column(Integer, nullable=False, default=0)
    day7 = Column(Integer, nullable=False, default=0)
    day8 = Column(Integer, nullable=False, default=0)
    day9 = Column(Integer, nullable=False, default=0)

    recharge = Column(Integer, nullable=False, default=0)       # 累计充值
    r1 = Column(Integer, nullable=False, default=0)             # 1激活奖励 2领取奖励
    r2 = Column(Integer, nullable=False, default=0)
    r3 = Column(Integer, nullable=False, default=0)
    r4 = Column(Integer, nullable=False, default=0)
    r5 = Column(Integer, nullable=False, default=0)
    r6 = Column(Integer, nullable=False, default=0)
    r7 = Column(Integer, nullable=False, default=0)
    r8 = Column(Integer, nullable=False, default=0)
    r9 = Column(Integer, nullable=False, default=0)
    r10 = Column(Integer, nullable=False, default=0)
    r11 = Column(Integer, nullable=False, default=0)
    r12 = Column(Integer, nullable=False, default=0)
    r13 = Column(Integer, nullable=False, default=0)
    r14 = Column(Integer, nullable=False, default=0)
    r15 = Column(Integer, nullable=False, default=0)
    r16 = Column(Integer, nullable=False, default=0)
    r17 = Column(Integer, nullable=False, default=0)
    r18 = Column(Integer, nullable=False, default=0)
    r19 = Column(Integer, nullable=False, default=0)
    r20 = Column(Integer, nullable=False, default=0)

    challenges = Column(Integer, nullable=False, default=0)     # 挑战次数
    c1 = Column(Integer, nullable=False, default=0)             # 1激活奖励 2领取奖励 3奖励邮寄发送
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)

    s1 = Column(Integer, nullable=False, default=0)             # 7天可兑换总的次数
    s2 = Column(Integer, nullable=False, default=0)
    s3 = Column(Integer, nullable=False, default=0)
    s4 = Column(Integer, nullable=False, default=0)
    s5 = Column(Integer, nullable=False, default=0)
    s6 = Column(Integer, nullable=False, default=0)
    s7 = Column(Integer, nullable=False, default=0)
    s8 = Column(Integer, nullable=False, default=0)
    s9 = Column(Integer, nullable=False, default=0)
    s10 = Column(Integer, nullable=False, default=0)
    s11 = Column(Integer, nullable=False, default=0)
    s12 = Column(Integer, nullable=False, default=0)
    s13 = Column(Integer, nullable=False, default=0)
    s14 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj