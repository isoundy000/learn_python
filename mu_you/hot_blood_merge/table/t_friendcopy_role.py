# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_friendcopy_role(Base):
    __tablename__ = 't_friendcopy_role'
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=True, default = 3)
    c2 = Column(Integer, nullable=True, default = 0)
    c3 = Column(Integer, nullable=True, default = 0)
    c4 = Column(Integer, nullable=True, default = 0)
    c5 = Column(Integer, nullable=True, default = 0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
