# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_protagonist_game(Base):
    __tablename__ = 't_protagonist_game'
    rid = Column(Integer, primary_key=True)
    mapid = Column(Integer, nullable=True, default=0)  # 关卡id
    pointid = Column(Integer, nullable=True, default=0)  # 吃豆位置

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj