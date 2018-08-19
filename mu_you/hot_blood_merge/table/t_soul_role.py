# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_soul_role(Base):
    __tablename__ = "t_soul_role"
    rid = Column(Integer, primary_key=True)
    soul  = Column(Integer, nullable=False, default=0)
    hunt  = Column(Integer, nullable=False, default=1)
    last  = Column(Integer, nullable=True, default=None)
    t1 = Column(TIMESTAMP, nullable=True, default=None)
    t2 = Column(TIMESTAMP, nullable=True, default=None)
    t3 = Column(TIMESTAMP, nullable=True, default=None)
    t4 = Column(TIMESTAMP, nullable=True, default=None)
    t5 = Column(TIMESTAMP, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
