# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_general_map(Base):
    __tablename__ = "t_general_map"
    rid = Column(Integer, primary_key=True, nullable=False)
    map = Column(Integer, primary_key=True, nullable=False)
    status = Column(Integer, nullable=False, default = 0)#0未通关 1通关
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

