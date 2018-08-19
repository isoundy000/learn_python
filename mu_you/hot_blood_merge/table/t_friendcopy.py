# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_friendcopy(Base):
    __tablename__ = 't_friendcopy'
    rid = Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)
    kill = Column(Integer, nullable=True, default = -1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
