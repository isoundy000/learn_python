#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_brave_copy(Base):
    __tablename__ = "t_brave_copy"
    rid = Column(Integer, primary_key=True, nullable=False)
    map = Column(Integer, primary_key=True, nullable=False)
    point = Column(Integer, primary_key=True, nullable=False)
    kill = Column(Integer, nullable=False, default= -1)
    star = Column(Integer, nullable=False, default= 0)
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
