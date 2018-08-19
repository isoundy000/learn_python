#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_limittimeexchange(Base):
    __tablename__ = 't_limittimeexchange'
    rid = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False, default=0)  # 手动刷新次数
    i1 = Column(Integer, nullable=True, default=None)
    c1 = Column(Integer, nullable=True, default=0)
    i2 = Column(Integer, nullable=True, default=None)
    c2 = Column(Integer, nullable=True, default=0)
    i3 = Column(Integer, nullable=True, default=None)
    c3 = Column(Integer, nullable=True, default=0)
    i4 = Column(Integer, nullable=True, default=None)
    c4 = Column(Integer, nullable=True, default=0)
    i5 = Column(Integer, nullable=True, default=None)
    c5 = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
