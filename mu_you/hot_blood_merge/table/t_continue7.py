# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_continue7(Base):
    __tablename__ = 't_continue7'
    rid = Column(Integer, primary_key=True)
    days = Column(Integer, nullable=False,default=0)
    lasttime = Column(TIMESTAMP, nullable=True)
    d1 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d2 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d3 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d4 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d5 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d6 = Column(Enum('yes','no','get'), nullable=False,default='no')
    d7 = Column(Enum('yes','no','get'), nullable=False,default='no')

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

