#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_expedition2(Base):
    __tablename__ = 't_expedition2'
    rid = Column(Integer, primary_key=True)
    map = Column(Integer, primary_key=True)
    kill = Column(Integer, nullable=False, default=-1)
    point = Column(Integer, nullable=False, default=1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
