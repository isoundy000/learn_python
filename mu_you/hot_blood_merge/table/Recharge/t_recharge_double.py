# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recharge_double(Base):
    __tablename__ = 't_recharge_double'
    rid = Column(Integer, primary_key=True)
    s1 = Column(Enum('yes','no'),nullable=False, default='no')
    s2 = Column(Enum('yes','no'),nullable=False, default='no')
    s3 = Column(Enum('yes','no'),nullable=False, default='no')
    s4 = Column(Enum('yes','no'),nullable=False, default='no')
    s5 = Column(Enum('yes','no'),nullable=False, default='no')
    s6 = Column(Enum('yes','no'),nullable=False, default='no')
    s7 = Column(Enum('yes','no'),nullable=False, default='no')
    s8 = Column(Enum('yes','no'),nullable=False, default='no')
    s9 = Column(Enum('yes','no'),nullable=False, default='no')
    s10 = Column(Enum('yes','no'),nullable=False, default='no')


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
