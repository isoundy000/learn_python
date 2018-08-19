# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_singlerechargegift_new(Base):
    __tablename__ = 't_activity_singlerechargegift_new'
    rid = Column(Integer, primary_key=True)
    r1 = Column(Integer, nullable=False, default=0) # 记录充值次数
    r2 = Column(Integer, nullable=False, default=0)
    r3 = Column(Integer, nullable=False, default=0)
    r4 = Column(Integer, nullable=False, default=0)
    r5 = Column(Integer, nullable=False, default=0)
    r6 = Column(Integer, nullable=False, default=0)
    r7 = Column(Integer, nullable=False, default=0)
    r8 = Column(Integer, nullable=False, default=0)
    r9 = Column(Integer, nullable=False, default=0)
    r10 = Column(Integer, nullable=False, default=0)
    c1 = Column(Integer, nullable=False, default=0) # 记录领奖次数
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj