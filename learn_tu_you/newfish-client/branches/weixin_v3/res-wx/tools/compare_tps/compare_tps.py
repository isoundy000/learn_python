#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/9/6
import os, sys


def _tps_intact_dir(dir, tps_list, pre_str):
    data = os.walk(dir)
    for root, dirs, files in data:
        for name in files:
            if name.find('.tps') != -1:
                tps_list.append(pre_str + u'.tps')
        for name in dirs:
            if name == u"tps":
                continue
            _tps_intact_dir(dir + '/' + name, tps_list, pre_str + '/' + name)
        return
    pass


def _tps_app_dir(dir, tps_list, pre_str):
    data = os.walk(dir)
    for root, dirs, files in data:
        for name in files:
            if name.find('.tps') != -1:
                tps_list.append(pre_str+'/'+name)
        for name in dirs:
            _tps_app_dir(dir+'/'+name, tps_list, pre_str+'/'+name)
        return
    pass


# /Users/szj/Documents/wxproj/client-2019-2-18/res-wx/art/atlas
def gen_tps_intact_dir(dir):
    if not os.path.exists(dir) or not os.path.isdir(dir):
        print("Error:"+dir)
        print('error dir: not exists or not file')
        return set()
    tps_list = []
    _tps_intact_dir(dir, tps_list, u'')
    return set(tps_list)


def gen_tps_app_dir(dir):
    if not os.path.exists(dir) or not os.path.isdir(dir):
        print("Error:"+dir)
        print('error dir: not exists or not file')
        return set()
    tps_list = []
    _tps_app_dir(dir, tps_list, u'')
    return set(tps_list)


def compare_a_b_dir(a, b):
    intact_set=gen_tps_intact_dir(a)
    app_set=gen_tps_app_dir(b)
    only_intact=intact_set-app_set
    print(u'-------------------only in intact----------')
    for one in only_intact:
        print(one)
    print(u'-------------------only in app----------')
    only_app=app_set-intact_set
    for one in only_app:
        print(one)
    pass


def work(argv):
    print(argv)
    print(len(argv))
    print(__file__)
    print(os.path.realpath(__file__))
    print(os.path.split(os.path.realpath(__file__)))
    parent_folder = os.path.split(os.path.realpath(__file__))[0]
    work_folder = os.path.realpath(os.path.join(parent_folder, u'../../art/atlas'))
    print(work_folder)
    # work_folder = u"/Users/szj/Documents/wxproj/client-2019-2-18/res-wx/art/atlas"
    compare_a_b_dir(work_folder, work_folder+"/tps")


# python compare_tps.py
# 比较res-wx/art/atlas和res-wx/art/atlas/tps是否一一对应
if __name__ == "__main__":
    work(sys.argv)