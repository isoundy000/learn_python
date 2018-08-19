#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_dividestallcarnival(Base):
    __tablename__ = 't_dividestallcarnival'
    rid = Column(Integer, primary_key=True)
    stall = Column(Integer, nullable=False, default=1)  # 档位
    c1 = Column(Integer, nullable=True, default=0)  # 普通档抽奖次数
    c2 = Column(Integer, nullable=True, default=0)  # 精良档抽奖次数
    c3 = Column(Integer, nullable=True, default=0)  # 史诗档抽奖次数
    c4 = Column(Integer, nullable=True, default=0)
    c5 = Column(Integer, nullable=True, default=0)
    i1 = Column(Integer, nullable=True, default=0)  # 保底次数记录
    i2 = Column(Integer, nullable=True, default=0)
    i3 = Column(Integer, nullable=True, default=0)
    i4 = Column(Integer, nullable=True, default=0)
    i5 = Column(Integer, nullable=True, default=0)
    i6 = Column(Integer, nullable=True, default=0)
    i7 = Column(Integer, nullable=True, default=0)
    i8 = Column(Integer, nullable=True, default=0)
    i9 = Column(Integer, nullable=True, default=0)
    i10 = Column(Integer, nullable=True, default=0)


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj