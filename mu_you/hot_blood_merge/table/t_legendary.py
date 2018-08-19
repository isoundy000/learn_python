#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'ghou'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_legendary(Base):
    __tablename__ = 't_legendary'
    rid = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=True, default=0)  # 购买挑战次数
    k1 = Column(Integer, nullable=True, default=0)  # 坑1 1表示打过了
    i1 = Column(String, nullable=True, default=0)  # 奖励的索引值 从1开始
    k2 = Column(Integer, nullable=True, default=0)  # 坑2 1表示打过了
    i2 = Column(String, nullable=True, default=0)
    k3 = Column(Integer, nullable=True, default=0)
    i3 = Column(String, nullable=True, default=0)
    k4 = Column(Integer, nullable=True, default=0)
    i4 = Column(String, nullable=True, default=0)
    k5 = Column(Integer, nullable=True, default=0)
    i5 = Column(String, nullable=True, default=0)
    k6 = Column(Integer, nullable=True, default=0)
    i6 = Column(String, nullable=True, default=0)
    k7 = Column(Integer, nullable=True, default=0)
    i7 = Column(String, nullable=True, default=0)
    k8 = Column(Integer, nullable=True, default=0)
    i8 = Column(String, nullable=True, default=0)
    k9 = Column(Integer, nullable=True, default=0)
    i9 = Column(String, nullable=True, default=0)
    k10 = Column(Integer, nullable=True, default=0)
    i10 = Column(String, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
