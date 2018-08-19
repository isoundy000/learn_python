# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_ktv(Base):
    __tablename__ = 't_ktv'
    __table_args__ = {'extend_existing':True}
    key = Column(String, primary_key=True)
    type = Column(Enum('string','int','float'), nullable=False, default='string')
    value = Column(String, nullable=True, default=None)

    @classmethod
    def load_to_dict(cls, session):
        result = {}
        for ktv in session.query(cls).all():
            result[ktv.key] = ktv
        return result