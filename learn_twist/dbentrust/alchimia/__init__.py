#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/25 11:43
# @version: 0.0.1
# @Author: houguangdong
# @File: __init__.py.py
# @Software: PyCharm

from __future__ import absolute_import, division

from learn_twist.dbentrust.alchimia.strategy import TWISTED_STRATEGY
from learn_twist.dbentrust.alchimia.engine import TwistedEngine

wrap_engine = TwistedEngine.from_sqlalchemy_engine

del TwistedEngine


__all__ = [
    "TWISTED_STRATEGY",
    "wrap_engine"
]
