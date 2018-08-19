#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_manor_shop(Base):
    __tablename__ = 't_manor_shop'
    rid = Column(Integer, primary_key=True)
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
    c11 = Column(Integer, nullable=False, default=0)
    c12 = Column(Integer, nullable=False, default=0)
    c13 = Column(Integer, nullable=False, default=0)
    c14 = Column(Integer, nullable=False, default=0)
    c15 = Column(Integer, nullable=False, default=0)
    c16 = Column(Integer, nullable=False, default=0)
    c17 = Column(Integer, nullable=False, default=0)
    c18 = Column(Integer, nullable=False, default=0)
    c19 = Column(Integer, nullable=False, default=0)
    c20 = Column(Integer, nullable=False, default=0)
    c21 = Column(Integer, nullable=False, default=0)
    c22 = Column(Integer, nullable=False, default=0)
    c23 = Column(Integer, nullable=False, default=0)
    c24 = Column(Integer, nullable=False, default=0)
    c25 = Column(Integer, nullable=False, default=0)
    c26 = Column(Integer, nullable=False, default=0)
    c27 = Column(Integer, nullable=False, default=0)
    c28 = Column(Integer, nullable=False, default=0)
    c29 = Column(Integer, nullable=False, default=0)
    c30 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj