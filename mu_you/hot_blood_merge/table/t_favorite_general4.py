#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_favorite_general4(Base):
    __tablename__ = 't_favorite_general4'
    rid = Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)
    exp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj