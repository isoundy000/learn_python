#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_dragonwishing(Base):
    __tablename__ = 't_dragonwishing'
    rid = Column(Integer, primary_key=True)
    mapid = Column(Integer, nullable=True, default=0)  # 地图id
    ballnum = Column(Integer, nullable=True, default=0)  # 龙珠数量
    todayball = Column(Integer, nullable=True, default=0)  # 今天龙珠状态
    rewardsta = Column(Enum("yes", "no", "get"), nullable=True, default="no")  # 大奖状态
    dicenum = Column(Integer, nullable=True, default=0)  # 筛子当前筛子剩余数量
    golddice = Column(Integer, nullable=True, default=0)  # 元宝摇骰子次数
    pos = Column(Integer, nullable=True, default=1)  # 当前位置
    path = Column(Integer, nullable=True, default=1)  # 所在路径
    event = Column(Integer, nullable=True, default=0)  # 当前事件id
    eventsta = Column(Integer, nullable=True, default=0)  # 当前事件状态
    qytime = Column(TIMESTAMP, nullable=True, default=None)  # 上次查询时间
    t1 = Column(Integer, nullable=True, default=0)  # 对应位置事件
    t2 = Column(Integer, nullable=True, default=0)
    t3 = Column(Integer, nullable=True, default=0)
    t4 = Column(Integer, nullable=True, default=0)
    t5 = Column(Integer, nullable=True, default=0)
    t6 = Column(Integer, nullable=True, default=0)
    t7 = Column(Integer, nullable=True, default=0)
    t8 = Column(Integer, nullable=True, default=0)
    t9 = Column(Integer, nullable=True, default=0)
    t10 = Column(Integer, nullable=True, default=0)
    t11 = Column(Integer, nullable=True, default=0)
    t12 = Column(Integer, nullable=True, default=0)
    t13 = Column(Integer, nullable=True, default=0)
    t14 = Column(Integer, nullable=True, default=0)
    t15 = Column(Integer, nullable=True, default=0)
    t16 = Column(Integer, nullable=True, default=0)
    t17 = Column(Integer, nullable=True, default=0)
    t18 = Column(Integer, nullable=True, default=0)
    t19 = Column(Integer, nullable=True, default=0)
    t20 = Column(Integer, nullable=True, default=0)
    t21 = Column(Integer, nullable=True, default=0)
    t22 = Column(Integer, nullable=True, default=0)
    t23 = Column(Integer, nullable=True, default=0)
    t24 = Column(Integer, nullable=True, default=0)
    t25 = Column(Integer, nullable=True, default=0)
    t26 = Column(Integer, nullable=True, default=0)
    t27 = Column(Integer, nullable=True, default=0)
    t28 = Column(Integer, nullable=True, default=0)
    t29 = Column(Integer, nullable=True, default=0)
    t30 = Column(Integer, nullable=True, default=0)
    t31 = Column(Integer, nullable=True, default=0)
    t32 = Column(Integer, nullable=True, default=0)
    t33 = Column(Integer, nullable=True, default=0)
    t34 = Column(Integer, nullable=True, default=0)
    t35 = Column(Integer, nullable=True, default=0)
    t36 = Column(Integer, nullable=True, default=0)
    t37 = Column(Integer, nullable=True, default=0)
    t38 = Column(Integer, nullable=True, default=0)
    t39 = Column(Integer, nullable=True, default=0)
    t40 = Column(Integer, nullable=True, default=0)
    t41 = Column(Integer, nullable=True, default=0)
    t42 = Column(Integer, nullable=True, default=0)
    t43 = Column(Integer, nullable=True, default=0)
    t44 = Column(Integer, nullable=True, default=0)
    t45 = Column(Integer, nullable=True, default=0)
    t46 = Column(Integer, nullable=True, default=0)
    t47 = Column(Integer, nullable=True, default=0)
    t48 = Column(Integer, nullable=True, default=0)
    t49 = Column(Integer, nullable=True, default=0)
    t50 = Column(Integer, nullable=True, default=0)
    t51 = Column(Integer, nullable=True, default=0)
    t52 = Column(Integer, nullable=True, default=0)
    t53 = Column(Integer, nullable=True, default=0)
    t54 = Column(Integer, nullable=True, default=0)
    t55 = Column(Integer, nullable=True, default=0)
    t56 = Column(Integer, nullable=True, default=0)
    t57 = Column(Integer, nullable=True, default=0)
    t58 = Column(Integer, nullable=True, default=0)
    t59 = Column(Integer, nullable=True, default=0)
    t60 = Column(Integer, nullable=True, default=0)
    t61 = Column(Integer, nullable=True, default=0)
    t62 = Column(Integer, nullable=True, default=0)
    t63 = Column(Integer, nullable=True, default=0)
    t64 = Column(Integer, nullable=True, default=0)
    t65 = Column(Integer, nullable=True, default=0)
    t66 = Column(Integer, nullable=True, default=0)
    t67 = Column(Integer, nullable=True, default=0)
    t68 = Column(Integer, nullable=True, default=0)
    t69 = Column(Integer, nullable=True, default=0)
    t70 = Column(Integer, nullable=True, default=0)
    t71 = Column(Integer, nullable=True, default=0)
    t72 = Column(Integer, nullable=True, default=0)
    t73 = Column(Integer, nullable=True, default=0)
    t74 = Column(Integer, nullable=True, default=0)
    t75 = Column(Integer, nullable=True, default=0)
    t76 = Column(Integer, nullable=True, default=0)
    t77 = Column(Integer, nullable=True, default=0)
    t78 = Column(Integer, nullable=True, default=0)
    t79 = Column(Integer, nullable=True, default=0)
    t80 = Column(Integer, nullable=True, default=0)
    t81 = Column(Integer, nullable=True, default=0)
    t82 = Column(Integer, nullable=True, default=0)
    t83 = Column(Integer, nullable=True, default=0)
    t84 = Column(Integer, nullable=True, default=0)
    t85 = Column(Integer, nullable=True, default=0)
    t86 = Column(Integer, nullable=True, default=0)
    t87 = Column(Integer, nullable=True, default=0)
    t88 = Column(Integer, nullable=True, default=0)
    t89 = Column(Integer, nullable=True, default=0)
    t90 = Column(Integer, nullable=True, default=0)
    t91 = Column(Integer, nullable=True, default=0)
    t92 = Column(Integer, nullable=True, default=0)
    t93 = Column(Integer, nullable=True, default=0)
    t94 = Column(Integer, nullable=True, default=0)
    t95 = Column(Integer, nullable=True, default=0)
    t96 = Column(Integer, nullable=True, default=0)
    t97 = Column(Integer, nullable=True, default=0)
    t98 = Column(Integer, nullable=True, default=0)
    t99 = Column(Integer, nullable=True, default=0)
    t100 = Column(Integer, nullable=True, default=0)
    t101 = Column(Integer, nullable=True, default=0)
    t102 = Column(Integer, nullable=True, default=0)
    t103 = Column(Integer, nullable=True, default=0)
    t104 = Column(Integer, nullable=True, default=0)
    t105 = Column(Integer, nullable=True, default=0)
    t106 = Column(Integer, nullable=True, default=0)
    t107 = Column(Integer, nullable=True, default=0)
    t108 = Column(Integer, nullable=True, default=0)
    t109 = Column(Integer, nullable=True, default=0)
    t110 = Column(Integer, nullable=True, default=0)
    t111 = Column(Integer, nullable=True, default=0)
    t112 = Column(Integer, nullable=True, default=0)
    t113 = Column(Integer, nullable=True, default=0)
    t114 = Column(Integer, nullable=True, default=0)
    t115 = Column(Integer, nullable=True, default=0)
    t116 = Column(Integer, nullable=True, default=0)
    t117 = Column(Integer, nullable=True, default=0)
    t118 = Column(Integer, nullable=True, default=0)
    t119 = Column(Integer, nullable=True, default=0)
    t120 = Column(Integer, nullable=True, default=0)
    c1 = Column(Integer, nullable=True, default=0)  # 商店物品1购买数量
    c2 = Column(Integer, nullable=True, default=0)  # 商店物品2购买数量
    c3 = Column(Integer, nullable=True, default=0)  # 商店物品3购买数量
    c4 = Column(Integer, nullable=True, default=0)  # 商店物品4购买数量
    c5 = Column(Integer, nullable=True, default=0)  # 今天是否刷新地图

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
