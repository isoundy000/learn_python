#!/bin/bash
# Created on 2016年5月1日
# @author: zqh
# game.sh pypy namespace/main.py sid mnport redis logpath binpath
# 0       1    2                 3   4      5     6       7

cd ${7}
export PYTHONPATH=${7}
nohup ${1} ${2} ${3} ${4} ${5} ${6}/${3}.log >> ${6}/${3}.log.nohup 2>&1 &
