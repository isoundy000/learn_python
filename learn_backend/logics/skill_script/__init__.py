#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import imp
from lib.utils.debug import print_log
_skill_dir = os.path.dirname(os.path.abspath(__file__))     # + os.sep + os.pardir + os.sep + 'skill_script' + os.sep
_exclude_files = ['__init__', '_utils']
all_skill = {}


def load_all():
    """# load_all: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    for _root, _dirs, _files in os.walk(_skill_dir):
        for _f in _files:
            _name, _ext = os.path.splitext(_f)
            if _ext == '.py' and _name not in _exclude_files:
                # __all__.insert(0, _name)
                s= _skill_dir
                # m = imp.load_source(_name, s)
                m = __import__(_name, globals=globals(), fromlist=['logics', 'script_skill'])
                all_skill[_name] = m


load_all()