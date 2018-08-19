# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

from datetime import datetime


class t_log_getgold(Base):
    __tablename__ = 't_log_getgold'
    id =  Column(Integer, primary_key=True, autoincrement=True)
    rid =  Column(Integer, nullable=False)
    opt = Column(String, nullable=False,default="default")
    num =  Column(Integer, nullable=False, default=0)
    time = Column(TIMESTAMP, nullable=True, default=datetime.now)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
