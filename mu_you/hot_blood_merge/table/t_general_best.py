# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_general_best(Base):
    __tablename__ = "t_general_best"
    rid = Column(Integer, primary_key=True, nullable=False)
    cid = Column(Integer, primary_key=True, nullable=False)
    num = Column(Integer, nullable=False)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
