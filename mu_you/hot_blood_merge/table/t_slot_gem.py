# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_slot_gem(Base):
    __tablename__ = "t_slot_gem"
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True)
    s11 = Column(Integer, nullable=True, default=None)
    s12 = Column(Integer, nullable=True, default=None)
    s13 = Column(Integer, nullable=True, default=None)
    s14 = Column(Integer, nullable=True, default=-1)
    s21 = Column(Integer, nullable=True, default=None)
    s22 = Column(Integer, nullable=True, default=None)
    s23 = Column(Integer, nullable=True, default=None)
    s24 = Column(Integer, nullable=True, default=-1)
    s31 = Column(Integer, nullable=True, default=None)
    s32 = Column(Integer, nullable=True, default=None)
    s33 = Column(Integer, nullable=True, default=None)
    s34 = Column(Integer, nullable=True, default=-1)
    s41 = Column(Integer, nullable=True, default=None)
    s42 = Column(Integer, nullable=True, default=None)
    s43 = Column(Integer, nullable=True, default=None)
    s44 = Column(Integer, nullable=True, default=-1)
    s51 = Column(Integer, nullable=True, default=None)
    s52 = Column(Integer, nullable=True, default=None)
    s53 = Column(Integer, nullable=True, default=None)
    s54 = Column(Integer, nullable=True, default=-1)
    s61 = Column(Integer, nullable=True, default=None)
    s62 = Column(Integer, nullable=True, default=None)
    s63 = Column(Integer, nullable=True, default=None)
    s64 = Column(Integer, nullable=True, default=-1)
    s71 = Column(Integer, nullable=True, default=None)
    s72 = Column(Integer, nullable=True, default=None)
    s73 = Column(Integer, nullable=True, default=None)
    s74 = Column(Integer, nullable=True, default=-1)
    s81 = Column(Integer, nullable=True, default=None)
    s82 = Column(Integer, nullable=True, default=None)
    s83 = Column(Integer, nullable=True, default=None)
    s84 = Column(Integer, nullable=True, default=-1)
    s91 = Column(Integer, nullable=True, default=None)
    s92 = Column(Integer, nullable=True, default=None)
    s93 = Column(Integer, nullable=True, default=None)
    s94 = Column(Integer, nullable=True, default=-1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
