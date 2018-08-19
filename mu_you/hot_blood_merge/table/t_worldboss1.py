#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_worldboss1(Base):
    __tablename__ = 't_worldboss1'
    id = Column(Integer, primary_key=True, default=1)
    level = Column(Integer, nullable=False, default=1)
    hp = Column(Integer, nullable=False ,default=5000000)
    time = Column(Integer, nullable=True, default=None)
    killrid = Column(Integer, nullable=True, default=None)
    killdamage = Column(Integer, nullable=True, default=None)
    first = Column(Enum('yes','no'), nullable=False, default='yes')
    hp2 = Column(Integer, nullable=True ,default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['time', 'killrid', 'killdamage']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj