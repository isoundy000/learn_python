# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_kingman(Base):
    __tablename__ = 't_kingman'
    __table_args__ = {'extend_existing':True}
    rid  = Column(Integer, primary_key=True)
    boss = Column(Integer, primary_key=True)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj