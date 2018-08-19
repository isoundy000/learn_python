# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_signin2(Base):
    __tablename__ = 't_signin2'
    rid = Column(Integer, primary_key=True)
    days = Column(Integer, nullable=False, default=0)
    status = Column(Enum('yes','no'), nullable=False, default='no')
    time = Column(TIMESTAMP, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj