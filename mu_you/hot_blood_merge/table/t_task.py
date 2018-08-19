# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_task(Base):
    __tablename__ = 't_task'
    rid = Column(Integer, primary_key=True)
    tid = Column(Integer, primary_key=True)
    status = Column(Enum('excute','complete','over'), nullable=False, default="excute")
    share = Column(Enum('no','yes','get'), nullable=False, default="no")
    tasktype = Column(Integer, nullable=False, default=0)       # {1成长2战斗3收集4其他}

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

