# -*- coding: utf-8 -*-
'''
Created on 6/21/2017

@author: ghou
'''

import os
import sys
import time
import subprocess
import logging


remote_server = ['10.117.168.77', 'root', '!QAZ2wsx', '/usr/l10n']
remote_or_local_copy = 0


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler("auto_push_vip_translate.log")
    logger.addHandler(file1)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file1.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def auto_push_vip_translate(logger):
    if os.path.exists("/root/ghou/g11n-translations"):
        os.system('rm -rf %s' % "/root/ghou/g11n-translations")
    os.chdir("/root/ghou/")
    os.system("git clone ssh://git@git.eng.vmware.com/g11n-translations.git")
    # this is copy local bundle
    copy_source_path = '/root/ghou/translate_copy/'
    if not os.path.exists(copy_source_path):
        os.system('mkdir -p %s' % copy_source_path)
    if remote_or_local_copy:
        cmd = "sshpass -p '%s' scp -r %s@%s:%s %s" % (remote_server[2], remote_server[1], remote_server[0], remote_server[3], copy_source_path)
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    else:
        # this is local bundle
        source_path = '/root/ghou/translate_local/'
        if not os.path.exists(source_path):
            os.mkdir(source_path)
        cmd = 'cp -r %s %s' % (source_path+'.', copy_source_path)
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    # this is git repository
    target_path = '/root/ghou/g11n-translations/l10n/'
    # 把文件同步到git库    之后提交上去
    # -I, –ignore-times 不跳过那些有同样的时间和长度的文件      -a, –archive 归档模式，表示以递归方式传输文件，并保持所有文件属性，等于-rlptgoD
    # -r表示recursive递归  --exclude不包含/ins目录    --recursive
    cmd1 = 'rsync -aI --recursive --include="*/" --exclude="*_en_US.json" %s %s' % (copy_source_path, target_path[:-5])
    p1 = subprocess.Popen(cmd1, shell=True)
    stdout1, stderr1 = p1.communicate()
    if stderr1:
        logger.error("run rsync is out %s, err %s" % (stdout1, stderr1))
        return
    else:
        logger.info("run rsync is success")
    os.chdir(target_path) # os.getcwd()
    return_message = os.popen('git status')
    if 'nothing to commit' in return_message.read():
        return
    cmd2 = "git add -A && git commit -m '%s' && git push origin master" % 'auto push vip translate'
    p2 = subprocess.Popen(cmd2, shell=True)
    stdout2, stderr2 = p2.communicate()
    if stderr2:
        logger.error("run git command is out %s, err %s" % (stdout2, stderr2))
    else:
        logger.info("run git command is success")
    os.system('rm -rf %s' % copy_source_path)


def main():
    argv = sys.argv
    logger = test_get_logger()
    if len(argv) == 1:
        auto_push_vip_translate(logger)
    else:
        time_number = int(sys.argv[1])
        while True:
            auto_push_vip_translate(logger)
            time.sleep(time_number)


if __name__ == '__main__':
    main()