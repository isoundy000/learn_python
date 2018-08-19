# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_world_war_battle(Base):
    __tablename__ = "t_world_war_battle"
    id = Column(Integer, primary_key=True, autoincrement=True)
    a = Column(Integer, nullable=False)
    a_server_id = Column(Integer, nullable=True)
    b = Column(Integer, nullable=False)
    b_server_id = Column(Integer, nullable=True)
    phase = Column(Integer, nullable=False, default=1)
    round = Column(Integer, nullable=False, default=1)
    result = Column(Enum('success','fail'), nullable=True)
    a_star = Column(Integer, nullable=False, default=0)
    b_star = Column(Integer, nullable=False, default=0)
    report = Column(Text, nullable=True)
    reward = Column(Enum('yes','no'), nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in []:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
