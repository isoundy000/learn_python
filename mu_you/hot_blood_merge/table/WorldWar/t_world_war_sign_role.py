# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_world_war_sign_role(Base):
    __tablename__ = 't_world_war_sign_role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, nullable=False)
    rid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    vip = Column(Integer, nullable=False)
    power = Column(Integer, nullable=False, default=0)
    cup_point = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in []:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
