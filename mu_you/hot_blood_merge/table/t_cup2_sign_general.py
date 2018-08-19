# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_cup2_sign_general(Base):
    __tablename__ = "t_cup2_sign_general"
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)
    level1 = Column(Integer, nullable=False)
    level2 = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    atk = Column(Integer, nullable=False)
    def_ = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    critical = Column(Integer, nullable=False)
    dodge = Column(Integer, nullable=False)
    parry = Column(Integer, nullable=False)
    resilience = Column(Integer, nullable=False)
    hit = Column(Integer, nullable=False)
    arp = Column(Integer, nullable=False)
    criticaldmg = Column(Integer, nullable=False)
    aadddmg = Column(Integer, nullable=False)
    asubdmg = Column(Integer, nullable=False)
    radddmg = Column(Integer, nullable=False)
    rsubdmg = Column(Integer, nullable=False)
    ap = Column(Integer, nullable=False)
    ap_atk_p = Column(Integer, nullable=False)
    skilllevel = Column(Integer, nullable=False)
    power = Column(Integer, nullable=False)
    level3 = Column(Integer, nullable=False)
    cover_d = Column(Integer, nullable=True, default=0)
    cover_l = Column(Integer, nullable=True, default=0)
    cover_p = Column(Integer, nullable=True, default=0)
    skill_adddamage = Column(Integer, nullable=False, default=0)

    protagonist_wing_level1 = Column(Integer, nullable=False, default=0)  # 翅膀品阶
    protagonist_wing_color = Column(Integer, nullable=False, default=0)   # 翅膀颜色

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
