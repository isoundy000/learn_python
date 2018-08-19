#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'yanglei'

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_role_groundhog(Base):
    __tablename__ = 't_role_groundhog'
    rid = Column(Integer, primary_key=True)
    maxintegal = Column(Integer, nullable=False, default=0)
    todayintegal = Column(Integer, nullable=False, default=0)
    times = Column(Integer, nullable=False, default=0)
    box1 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    box2 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    box3 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    box4 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    box5 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj