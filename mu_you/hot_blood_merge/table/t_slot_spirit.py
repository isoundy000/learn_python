# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_slot_spirit(Base):
    __tablename__ = 't_slot_spirit'

    rid = Column(Integer, primary_key=True)

    use_id = Column(Integer, nullable=False, default=0)

    addition = Column(Integer, nullable=False, default=0)

    l1 = Column(Integer, nullable=False, default=1)
    l2 = Column(Integer, nullable=False, default=1)
    l3 = Column(Integer, nullable=False, default=1)
    l4 = Column(Integer, nullable=False, default=1)
    l5 = Column(Integer, nullable=False, default=1)
    l6 = Column(Integer, nullable=False, default=1)
    l7 = Column(Integer, nullable=False, default=1)
    l8 = Column(Integer, nullable=False, default=1)
    l9 = Column(Integer, nullable=False, default=1)
    l10 = Column(Integer, nullable=False, default=1)
    l11 = Column(Integer, nullable=False, default=1)
    l12 = Column(Integer, nullable=False, default=1)
    l13 = Column(Integer, nullable=False, default=1)
    l14 = Column(Integer, nullable=False, default=1)
    l15 = Column(Integer, nullable=False, default=1)
    l16 = Column(Integer, nullable=False, default=1)
    l17 = Column(Integer, nullable=False, default=1)
    l18 = Column(Integer, nullable=False, default=1)
    l19 = Column(Integer, nullable=False, default=1)
    l20 = Column(Integer, nullable=False, default=1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj