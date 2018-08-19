#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_cornucopia(Base):
    __tablename__ = 't_cornucopia'
    rid = Column(Integer, primary_key=True)
    count =  Column(Integer, nullable=False, default=0)
    r1 = Column(Enum("yes","no", "get"), nullable=False, default="no")
    r2 = Column(Enum("yes","no", "get"), nullable=False, default="no")
    r3 = Column(Enum("yes","no", "get"), nullable=False, default="no")
    r4 = Column(Enum("yes","no", "get"), nullable=False, default="no")
    r5 = Column(Enum("yes","no", "get"), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

