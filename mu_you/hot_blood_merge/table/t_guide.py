# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_guide(Base):
    __tablename__ = 't_guide'
    rid = Column(Integer, primary_key=True)
    section = Column(Integer, primary_key=True)
    step = Column(Integer,nullable=True,default=0)
    status = Column(Enum("prepare","excute","complete"), nullable=False,default="prepare")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

