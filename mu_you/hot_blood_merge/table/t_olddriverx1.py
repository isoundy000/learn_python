# !/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_olddriverx1(Base):
    __tablename__ = 't_olddriverx1'
    rid = Column(Integer, primary_key=True)
    s0 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s1 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s2 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s3 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s4 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s5 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s6 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s7 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s8 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s9 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s10 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    c1 = Column(Integer, nullable=False, default=0)
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
