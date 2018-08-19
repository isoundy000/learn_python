# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_gang2(Base):

    __tablename__ = "t_gang2"
    __table_args__ = {'extend_existing': True}

    gid = Column(Integer, primary_key=True, nullable=False)             # 社团id
    name = Column(String, nullable=False)
    exp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)                  # 社团经验
    rid = Column(Integer, nullable=False)                               # 社长
    rid1 = Column(Integer, nullable=True, default=None)
    rid2 = Column(Integer, nullable=True, default=None)
    rid3 = Column(Integer, nullable=True, default=None)
    content1 = Column(String, nullable=True, default=None)              # 公会公告
    content2 = Column(String, nullable=True, default=None)              # 公会宣言
    power = Column(Integer, nullable=True, default=0)                   # 工会战力
    time = Column(TIMESTAMP, nullable=False, default=datetime.now)

    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)

    opt = Column(Integer, nullable=True, default=None)                  # None=0 正常 999弹劾状态
    optparam = Column(Integer, nullable=True, default=None)             # 公会特殊状态参数
    opttime = Column(TIMESTAMP, nullable=True, default=None)            # 公会特殊状态开始时间
    contribute_week = Column(Integer, nullable=False, default=0)
    contribute_week2 = Column(Integer, nullable=False, default=0)

    bossid = Column(Integer, nullable=False, default=0)     # 公会bossid
    bosslevel = Column(Integer, nullable=False, default=0)  # 公会boss等级
    bosshp = Column(Integer, nullable=False, default=0)     # 公会boss最新血量
    bosshp2 = Column(Integer, nullable=False, default=0)    # 公会boss总血量
    bossdamage = Column(String, nullable=False)             # 公会成员对boos造成总伤害(每周 一清)
    bossrelivetime = Column(TIMESTAMP, nullable=True, default=None)  # 公会boss复活时间
    bosskilltime = Column(TIMESTAMP, nullable=True, default=None)  # 公会boss击杀时间
    bossinspire = Column(Integer, nullable=False, default=0)  # 公会boss鼓舞次数（日清）

    auto_sta = Column(Integer, nullable=False, default=0)               # 自动收人开启状态（0关闭，1开启）
    auto_lv = Column(Integer, nullable=False, default=0)                # 自动收人等级限制（开启状态下 0没有限制）


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['gid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
