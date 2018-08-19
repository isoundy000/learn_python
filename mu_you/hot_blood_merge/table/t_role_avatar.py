__author__ = 'liuzhaoyang'
# -*- coding: UTF-8 -*-
# !/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()



class t_role_avatar(Base):
    __tablename__ = 't_role_avatar'
    rid = Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj