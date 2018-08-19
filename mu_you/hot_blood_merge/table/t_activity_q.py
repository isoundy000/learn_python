# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_q(Base):
    __tablename__ = 't_activity_q'
    rid = Column(Integer, primary_key=True)

    i1 = Column(Integer, nullable=False, default=0)
    i2 = Column(Integer, nullable=False, default=0)
    i3 = Column(Integer, nullable=False, default=0)
    i4 = Column(Integer, nullable=False, default=0)
    i5 = Column(Integer, nullable=False, default=0)
    i6 = Column(Integer, nullable=False, default=0)
    i7 = Column(Integer, nullable=False, default=0)
    i8 = Column(Integer, nullable=False, default=0)
    i9 = Column(Integer, nullable=False, default=0)
    i10 = Column(Integer, nullable=False, default=0)
    i11 = Column(Integer, nullable=False, default=0)
    i12 = Column(Integer, nullable=False, default=0)
    i13 = Column(Integer, nullable=False, default=0)
    i14 = Column(Integer, nullable=False, default=0)
    i15 = Column(Integer, nullable=False, default=0)
    i16 = Column(Integer, nullable=False, default=0)
    i17 = Column(Integer, nullable=False, default=0)
    i18 = Column(Integer, nullable=False, default=0)
    i19 = Column(Integer, nullable=False, default=0)
    i20 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
