# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_magicstone(Base):
    __tablename__ = 't_magicstone'
    rid = Column(Integer, primary_key=True)
    slot = Column(Integer, primary_key=True)
    g1 = Column(Integer, nullable=False, default=0)
    g2 = Column(Integer, nullable=False, default=0)
    g3 = Column(Integer, nullable=False, default=0)
    g4 = Column(Integer, nullable=False, default=0)
    g5 = Column(Integer, nullable=False, default=0)
    g6 = Column(Integer, nullable=False, default=0)
    g7 = Column(Integer, nullable=False, default=0)
    g8 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj