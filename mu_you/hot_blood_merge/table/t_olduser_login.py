# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_olduser_login(Base):
    __tablename__ = 't_olduser_login'
    rid = Column(Integer, primary_key=True)
    days =  Column(Integer, nullable=False, default=None)
    lastlogin =  Column(TIMESTAMP, nullable=False, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
