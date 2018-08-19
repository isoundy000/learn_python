# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_trial_role(Base):
    __tablename__ = 't_trial_role'
    __table_args__ = {'extend_existing':True}

    rid = Column(Integer, primary_key=True)

    init = Column(Boolean, nullable=False, default=False)

    i11 = Column(Integer, nullable=True, default=None)
    i12 = Column(Integer, nullable=True, default=None)
    i13 = Column(Integer, nullable=True, default=None)
    i14 = Column(Integer, nullable=True, default=None)
    i15 = Column(Integer, nullable=True, default=None)
    i16 = Column(Integer, nullable=True, default=None)
    i17 = Column(Integer, nullable=True, default=None)
    i18 = Column(Integer, nullable=True, default=None)
    i19 = Column(Integer, nullable=True, default=None)

    i21 = Column(Integer, nullable=True, default=None)
    i22 = Column(Integer, nullable=True, default=None)
    i23 = Column(Integer, nullable=True, default=None)
    i24 = Column(Integer, nullable=True, default=None)
    i25 = Column(Integer, nullable=True, default=None)
    i26 = Column(Integer, nullable=True, default=None)
    i27 = Column(Integer, nullable=True, default=None)
    i28 = Column(Integer, nullable=True, default=None)
    i29 = Column(Integer, nullable=True, default=None)

    i31 = Column(Integer, nullable=True, default=None)
    i32 = Column(Integer, nullable=True, default=None)
    i33 = Column(Integer, nullable=True, default=None)
    i34 = Column(Integer, nullable=True, default=None)
    i35 = Column(Integer, nullable=True, default=None)
    i36 = Column(Integer, nullable=True, default=None)
    i37 = Column(Integer, nullable=True, default=None)
    i38 = Column(Integer, nullable=True, default=None)
    i39 = Column(Integer, nullable=True, default=None)

    i41 = Column(Integer, nullable=True, default=None)
    i42 = Column(Integer, nullable=True, default=None)
    i43 = Column(Integer, nullable=True, default=None)
    i44 = Column(Integer, nullable=True, default=None)
    i45 = Column(Integer, nullable=True, default=None)
    i46 = Column(Integer, nullable=True, default=None)
    i47 = Column(Integer, nullable=True, default=None)
    i48 = Column(Integer, nullable=True, default=None)
    i49 = Column(Integer, nullable=True, default=None)

    s11 = Column(Integer, nullable=False, default=0)  # 0: 可战斗 1: 不可战斗 2: 战斗胜利,不可再次战斗
    s12 = Column(Integer, nullable=False, default=0)
    s13 = Column(Integer, nullable=False, default=0)
    s14 = Column(Integer, nullable=False, default=0)
    s15 = Column(Integer, nullable=False, default=0)
    s16 = Column(Integer, nullable=False, default=0)
    s17 = Column(Integer, nullable=False, default=0)
    s18 = Column(Integer, nullable=False, default=0)
    s19 = Column(Integer, nullable=False, default=0)

    s21 = Column(Integer, nullable=False, default=0)
    s22 = Column(Integer, nullable=False, default=0)
    s23 = Column(Integer, nullable=False, default=0)
    s24 = Column(Integer, nullable=False, default=0)
    s25 = Column(Integer, nullable=False, default=0)
    s26 = Column(Integer, nullable=False, default=0)
    s27 = Column(Integer, nullable=False, default=0)
    s28 = Column(Integer, nullable=False, default=0)
    s29 = Column(Integer, nullable=False, default=0)

    s31 = Column(Integer, nullable=False, default=0)
    s32 = Column(Integer, nullable=False, default=0)
    s33 = Column(Integer, nullable=False, default=0)
    s34 = Column(Integer, nullable=False, default=0)
    s35 = Column(Integer, nullable=False, default=0)
    s36 = Column(Integer, nullable=False, default=0)
    s37 = Column(Integer, nullable=False, default=0)
    s38 = Column(Integer, nullable=False, default=0)
    s39 = Column(Integer, nullable=False, default=0)

    s41 = Column(Integer, nullable=False, default=0)
    s42 = Column(Integer, nullable=False, default=0)
    s43 = Column(Integer, nullable=False, default=0)
    s44 = Column(Integer, nullable=False, default=0)
    s45 = Column(Integer, nullable=False, default=0)
    s46 = Column(Integer, nullable=False, default=0)
    s47 = Column(Integer, nullable=False, default=0)
    s48 = Column(Integer, nullable=False, default=0)
    s49 = Column(Integer, nullable=False, default=0)

    stage = Column(Integer, nullable=False, default=1)                  # 第几关卡
    box_open_count = Column(Integer, nullable=False, default=0)         # 宝箱开启次数
    reset_count = Column(Integer, nullable=False, default=0)            # 重置次数
    challenge_count = Column(Integer, nullable=False, default=0)        # 挑战次数
    point = Column(Integer, nullable=False, default=0)                  # 试炼点
    current_position = Column(Integer, nullable=True, default=None)     # 当前怪物位置

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name in ['point']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
