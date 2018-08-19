# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_protagonist(Base):
    __tablename__ = "t_protagonist"
    id = Column(Integer, primary_key=True)
    iid = Column(Integer, nullable=True, default=None)
    type = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    atk_a = Column(Integer, nullable=False, default=0)
    def_a = Column(Integer, nullable=False, default=0)
    hp_a = Column(Integer, nullable=False, default=0)
    train = Column(Integer, nullable=False, default=0)
    train_max = Column(Integer, nullable=False, default=0)
    train_next = Column(TIMESTAMP, nullable=True, default=None)
    fashion_cid = Column(Integer, nullable=True, default=None)  # 套装id
    fashion_status = Column(Enum("yes", "no"), nullable=True, default=None)  # 套装显示隐藏状态
    wing_level1 = Column(Integer, nullable=False, default=0)  # 翅膀品阶
    wing_level2 = Column(Integer, nullable=False, default=0)  # 翅膀星数
    wing_exp = Column(Integer, nullable=False, default=0)     # 翅膀经验
    wing_color = Column(Integer, nullable=False, default=0)   # 翅膀颜色
    wing_pro = Column(Integer, nullable=False, default=0)   # 翅膀进阶成功率

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
