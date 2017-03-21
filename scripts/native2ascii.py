# -*- coding: utf-8 -*-
'''
Created on 2/9/2017

@author: ghou
'''
import sys
import os


native2ascii_path = "C:\\Program Files\\Java\\jdk1.7.0_67\\bin\\native2ascii.exe"


argv = sys.argv
if len(argv) != 2:
    print 'argv error:', argv
    print 'run format: python native2ascii.py (True is native2asscii or False is asscii2native)'
    sys.exit()

def rename(filepath, subpath):
    print "rename {} {}".format(filepath, filepath+'.bak')
    os.system("rename {} {}".format(filepath, subpath+'.bak'))


def native2ascii(filepath, flag):
    print '"{}" -encoding UTF8 {} {} {}'.format(native2ascii_path,filepath+'.bak',filepath, flag)
    if flag:
        os.system('"{}" -encoding UTF8 {} {}'.format(native2ascii_path,filepath+'.bak',filepath))
    else:
        os.system('"{}" -reverse -encoding UTF8 {} {}'.format(native2ascii_path,filepath+'.bak',filepath))


def del_bak(filepath):
    print "del {}".format(filepath+'.bak')
    os.system("del {}".format(filepath+'.bak'))


def bfs(root_dir, flag):
    #　os.listdir get content under path
    for subpath in os.listdir(root_dir):
        path = os.path.join(root_dir, subpath)
        if os.path.isfile(path):
            if not path.endswith(".properties"):
                continue
            rename(path, subpath)
            native2ascii(path, flag)
            del_bak(path)
        elif os.path.isdir(path):
            bfs(path, flag)


if __name__ == '__main__':
    root_dir = r'D:\testdata\ui-drop3-native'
    isConver = argv[1]
    if isConver == 'True':
        flag = True
        print 'current operation is native2ascii'
    else:
        flag = False
        print 'current operation is asscii2native'
    bfs(root_dir, flag)


"""
native2ascii：
        vsphere2016:
        ciswin\\vpx\\java
        ciswin\\vpx\\services\\perfCharts
        Vimclients-platform\\applications\\license-client\\server\\license-service\\src\\main\\resources
        vum2016:
        D:\1_GRM_product\vum\HB_drop1\drop9\drop9\integrity\vpx\serenityClient\client\flex\updatemanager-ui\swf\src\main\flex\locale
        vsphere60u2-sunrise
        D:\1_GRM_product\vsphere\vsphere60u2-sunrise\drop1\drop1\ciswin\vpx\java
        D:\1_GRM_product\vsphere\vsphere60u2-sunrise\drop1\drop1\ciswin\vpx\services\perfCharts
        VRB:
        D:\1_GRM_product\vRB\handback\drop6\ascii_version\itfm\itfm-cloud
"""