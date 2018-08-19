# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_cup2_sign_pet3(Base):
    __tablename__ = "t_cup2_sign_pet3"
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
