# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_limittime_shop(Base):
    __tablename__ = 't_limittime_shop'
    rid = Column(Integer, primary_key=True)
    luck = Column(Integer, nullable=False, default=0)
    count = Column(Integer, nullable=False, default=0)
    time = Column(TIMESTAMP, nullable=True,default=None)
    i1 = Column(Integer, nullable=True, default=None)
    s1 = Column(Enum('yes','no','get'), nullable=True, default=None)
    i2 = Column(Integer, nullable=True, default=None)
    s2 = Column(Enum('yes','no','get'), nullable=True, default=None)
    i3 = Column(Integer, nullable=True, default=None)
    s3 = Column(Enum('yes','no','get'), nullable=True, default=None)
    i4 = Column(Integer, nullable=True, default=None)
    s4 = Column(Enum('yes','no','get'), nullable=True, default=None)
    i5 = Column(Integer, nullable=True, default=None)
    s5 = Column(Enum('yes','no','get'), nullable=True, default=None)
    i6 = Column(Integer, nullable=True, default=None)
    s6 = Column(Enum('yes','no','get'), nullable=True, default=None)


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
