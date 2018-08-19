# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_mieshendian(Base):
    __tablename__ = 't_mieshendian'
    rid = Column(Integer, primary_key=True)
    level_max = Column(Integer, nullable=False, default=0)
    level_max_today = Column(Integer, nullable=False, default=0)
    count = Column(Integer, nullable=False, default=0)
    fail = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    point = Column(Integer, nullable=False, default=0)
    modupend = Column(TIMESTAMP, nullable=True, default=None)
    point_get = Column(Integer, nullable=True, default=0)
    point_max = Column(Integer, nullable=True, default=0)
    integral = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj