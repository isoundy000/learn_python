# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_instrument(Base):
    __tablename__ = "t_instrument"
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True, nullable=False)
    cid = Column(Integer, primary_key=True, nullable=False)
    ahp = Column(Integer, nullable=False, default=0)
    aatk = Column(Integer, nullable=False, default=0)
    adef = Column(Integer, nullable=False, default=0)
    aspeed = Column(Integer, nullable=False, default=0)
    acritical = Column(Integer, nullable=False, default=0)
    adodge = Column(Integer, nullable=False, default=0)
    aparry = Column(Integer, nullable=False, default=0)
    aresilience = Column(Integer, nullable=False, default=0)
    ahit = Column(Integer, nullable=False, default=0)
    aarp = Column(Integer, nullable=False, default=0)
    acriticaldmg = Column(Integer, nullable=False, default=0)
    aadddmg = Column(Integer, nullable=False, default=0)
    asubdmg = Column(Integer, nullable=False, default=0)
    aap = Column(Integer, nullable=False, default=0)
    aap_atk_p = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
