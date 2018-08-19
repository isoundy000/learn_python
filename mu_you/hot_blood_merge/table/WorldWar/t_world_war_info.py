# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_world_war_weed_info(Base):
    __tablename__ = "t_world_war_weed_info"
    id = Column(Integer, primary_key=True)
    a = Column(Integer, nullable=False)
    b = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False, default=1)
    battle_id_1 = Column(Integer, nullable=False)
    battle_id_2 = Column(Integer, nullable=False)
    battle_id_3 = Column(Integer, nullable=False)
    a_win_count = Column(Integer, nullable=False, default=0)
    b_win_count = Column(Integer, nullable=False, default=0)
    bet_a_count = Column(Integer, nullable=False, default=0)
    bet_b_count = Column(Integer, nullable=False, default=0)
    result = Column(Integer, nullable=False)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in []:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
