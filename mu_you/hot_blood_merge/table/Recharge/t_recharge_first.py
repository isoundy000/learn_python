# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recharge_first(Base):
    __tablename__ = 't_recharge_first'
    rid = Column(Integer, primary_key=True)
    f1 = Column(Enum("yes", "no"), nullable=False, default="no")
    f2 = Column(Enum("yes", "no"), nullable=False, default="no")
    f3 = Column(Enum("yes", "no"), nullable=False, default="no")
    f4 = Column(Enum("yes", "no"), nullable=False, default="no")
    f5 = Column(Enum("yes", "no"), nullable=False, default="no")
    f6 = Column(Enum("yes", "no"), nullable=False, default="no")
    f7 = Column(Enum("yes", "no"), nullable=False, default="no")
    f8 = Column(Enum("yes", "no"), nullable=False, default="no")
    f9 = Column(Enum("yes", "no"), nullable=False, default="no")
    f10 = Column(Enum("yes", "no"), nullable=False, default="no")
    f11 = Column(Enum("yes", "no"), nullable=False, default="no")
    f12 = Column(Enum("yes", "no"), nullable=False, default="no")
    f13 = Column(Enum("yes", "no"), nullable=False, default="no")
    f14 = Column(Enum("yes", "no"), nullable=False, default="no")
    f15 = Column(Enum("yes", "no"), nullable=False, default="no")
    f16 = Column(Enum("yes", "no"), nullable=False, default="no")
    f17 = Column(Enum("yes", "no"), nullable=False, default="no")
    f18 = Column(Enum("yes", "no"), nullable=False, default="no")
    f19 = Column(Enum("yes", "no"), nullable=False, default="no")
    f20 = Column(Enum("yes", "no"), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj