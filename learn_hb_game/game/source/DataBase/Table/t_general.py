#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column
Base = declarative_base()
from Source.DataBase.Common.DBEngine import DBEngine, session_scope
from Source.GameOperation.General.CreateGeneral import CreateGeneral


class t_general(Base):
    '''
    武将信息
    '''
    __tablename__ = 't_general'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    exp = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    atk = Column(Integer, nullable=False)
    def_ = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=True, default=0)
    critical = Column(Integer, nullable=True, default=0)        # 暴击
    dodge = Column(Integer, nullable=True, default=0)           # 闪避
    parry = Column(Integer, nullable=True, default=0)           # 招架

    bhp = Column(Integer, nullable=False)
    batk = Column(Integer, nullable=False)
    bdef = Column(Integer, nullable=False)
    bspeed = Column(Integer, nullable=True, default=0)
    bcritical = Column(Integer, nullable=True, default=0)
    bdodge = Column(Integer, nullable=True, default=0)
    bparry = Column(Integer, nullable=True, default=0)

    potential = Column(Integer, nullable=False)                 # 潜力点
    skillexp = Column(Integer, nullable=False)                  # 技能经验
    skilllevel = Column(Integer, nullable=False)                # 技能等级
    combexp = Column(Integer, nullable=False)                   # 合体技经验
    comblevel = Column(Integer, nullable=False)                 # 合体技等级
    breaknum = Column(Integer, nullable=False)                  # 突破等级

    def selfCopy(self, target):
        self.id = target.id
        self.cid = target.cid
        self.level = target.level
        self.exp = target.exp
        self.atk = target.atk
        self.def_ = target.def_
        self.hp = target.hp
        self.speed = target.speed
        self.critical = target.critical
        self.dodge = target.dodge
        self.parry = target.parry
        self.batk = target.batk
        self.bdef = target.bdef
        self.bhp = target.bhp
        self.bspeed = target.bspeed
        self.bcritical = target.bcritical
        self.bdodge = target.bdodge
        self.potential = target.potential
        self.skilllevel = target.skilllevel
        self.breaknum = target.breaknum

    def OffSlot(self):
        self.atk = self.batk
        self.def_ = self.bdef
        self.hp = self.bhp
        self.speed = self.bspeed
        self.critical = self.bcritical
        self.dodge = self.bdodge
        self.parry = self.bparry
        return

    @staticmethod
    def LoadRoleData(roleid):
        with session_scope() as session:
            generallist = session.query(t_general).filter(t_general.rid == roleid).all()
            result = {}
            for general in generallist:
                result[general.id] = general
            if len(result) == 0:
                general = t_general()
                CreateGeneral(roleid, 10102, general)
                general.hp = 9999
                general.def_ = 10000
                general.atk = 9999
                DBEngine.Add(general)
                result[general.id] = general
                general = t_general()
                CreateGeneral(roleid, 10102, general)
                general.hp = 9999
                general.def_ = 10000
                general.atk = 9999
                DBEngine.Add(general)
                result[general.id] = general
                general = t_general()
                CreateGeneral(roleid, 10102, general)
                general.hp = 9999
                general.def_ = 10000
                general.atk = 9999
                DBEngine.Add(general)
                result[general.id] = general
            return result