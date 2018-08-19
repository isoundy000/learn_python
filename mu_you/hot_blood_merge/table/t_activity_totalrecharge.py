#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_totalrecharge(Base):
    __tablename__ = 't_activity_totalrecharge'
    rid = Column(Integer, primary_key=True)
    rmb = Column(Integer, nullable=True, default=0)
    days = Column(Integer, nullable=True, default=0)
    s11 = Column(Integer, nullable=False, default=0)
    s21 = Column(Integer, nullable=False, default=0)
    s31 = Column(Integer, nullable=False, default=0)
    s32 = Column(Integer, nullable=False, default=0)
    s33 = Column(Integer, nullable=False, default=0)
    s34 = Column(Integer, nullable=False, default=0)
    s35 = Column(Integer, nullable=False, default=0)
    s36 = Column(Integer, nullable=False, default=0)
    s37 = Column(Integer, nullable=False, default=0)
    s38 = Column(Integer, nullable=False, default=0)
    s39 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

