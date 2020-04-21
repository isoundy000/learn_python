#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from fabric.api import run, hide
import cStringIO


""" Usage:
         check to directory which contains this fabfile.py file
         >>>fab info -H your_name@dev.kaiqigu.net
"""

def info():
    uname = 'user'
    pswd = '123'
    cmd = "supervisorctl -u {uname} -p {pswd} status".format(uname=uname, pswd=pswd)
    with hide('output', 'running'):
        content = cStringIO.StringIO(run(cmd))
        result = []

        for i in content:
            result.append(i.split())

        for i in result:
            i[0] = i[0].split(":")
            i.insert(1, i[0][1])
            i.insert(1, i[0][0])
            del i[0]

            if i[2] == "RUNNING":
                i[3] = " ".join([i[3], i[4]])
                i[4] = " ".join(i[5:])
                if len(i) > 5:
                    del i[5:]
            elif i[2] == "FATAL" or i[2] == "STOPPED":
                i[4] = " ".join(i[3:])
                i[3] = None
                if len(i) > 5:
                    del i[5:]
        return result
    # Print out result to see if it's what we want
    # for i in result:
    #     print i