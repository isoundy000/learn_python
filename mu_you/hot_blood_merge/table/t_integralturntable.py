#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_integralturntable(Base):
    __tablename__ = 't_integralturntable'
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=False, default=0)  # 积分
    c2 = Column(Integer, nullable=False, default=0)  # 抽奖次数
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    i1 = Column(Integer, nullable=False, default=0)  # 每档连续未被抽中次数
    i2 = Column(Integer, nullable=False, default=0)
    i3 = Column(Integer, nullable=False, default=0)
    i4 = Column(Integer, nullable=False, default=0)
    i5 = Column(Integer, nullable=False, default=0)
    i6 = Column(Integer, nullable=False, default=0)
    i7 = Column(Integer, nullable=False, default=0)
    i8 = Column(Integer, nullable=False, default=0)
    i9 = Column(Integer, nullable=False, default=0)
    i10 = Column(Integer, nullable=False, default=0)


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj