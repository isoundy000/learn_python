# -*- coding: utf-8 -*-
'''
Created on 8/3/2017

@author: ghou
'''
import os
import sys
import time
import subprocess
import logging


argv = sys.argv
if len(argv) not in [1, 2]:
    print 'argv error:', argv
    print 'run format: "python post_review_translate.py(Manual)" or "python post_review_translate.py 3600 &"'
    sys.exit()


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler("post_review_translate.log")
    logger.addHandler(file1)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file1.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def read_config():
    file1 = open('./config', mode='r')
    stream_data = file1.readlines()
    lines = iter(stream_data)
    data = {}
    for line in lines:
        line = line.strip('\n').strip()
        if not line:
            continue
        if line[0] == '#':
            continue
        key, value = line.split(' ', 1)
        value_list = value.split(',')
        if len(value_list)>1:
            if len(value_list) == 2:
                data[key] = [value_list[0].strip(' ')]
            else:
                data[key] = [i and i.strip(' ') for i in value_list]
        else:
            data[key] = value.strip(' ')
    file1.close()
    return data


def post_review_translate(data, logger):
    now = int(time.time())
    os.chdir(data['post_workspace'])
    git_rep = data['post_workspace'] + "/g11n-translations"
    if not os.path.exists(git_rep):
        os.system(data['git_lib'])
    else:
        os.system('rm -rf %s' % git_rep)
        os.system(data['git_lib'])
    # this is copy local bundle
    if not os.path.exists(data['post_copy']):
        os.system('mkdir -p %s' % data['post_copy'])
    remote_or_local_copy = int(data['remote_or_local_copy'])
    if remote_or_local_copy:
        cmd = "sshpass -p '%s' scp -r %s@%s:%s %s" % (data['remote_server'][2], data['remote_server'][1], data['remote_server'][0], data['remote_server'][3], data['post_copy'])
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    else:
        # this is local bundle
        if not os.path.exists(data['post_local']):
            os.mkdir(data['post_local'])
        cmd = 'cp -r %s %s' % (data['post_local'], data['post_copy'])
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    # Synchronize files to the GIT library and submit them later
    # -I, –ignore-times don't skip files that have the same time and length  -a, –archive Archive mode, which means to transfer files in a recursive manner and keep all file attributes equal to -rlptgoD
    # -r Represents recursive recursion --exclude doesn't contain/ins Catalog --recursive
    list_new = data['translate_target_path'].split('g11n-translations/')
    productList = data['translate_target_path'] + os.path.sep + "bundles"
    for parent, dirnames, filenames in os.walk(data['translate_target_path']):
        if parent:
            pass
    cmd1 = 'rsync -aI --recursive --include="*/" --exclude="*_en_US.json" %s %s' % (data['translate_copy']+list_new[1], data['translate_target_path'])
    p1 = subprocess.Popen(cmd1, shell=True)
    stdout1, stderr1 = p1.communicate()
    if stderr1:
        logger.error("run rsync is out %s, err %s" % (stdout1, stderr1))
        return
    else:
        logger.info("run rsync is success")
    os.chdir(data['translate_target_path']) # os.getcwd()
    return_message = os.popen('git status')
    if 'nothing to commit' in return_message.read():
        return
    cmd2 = "/build/apps/bin/post-review -o %s --username=%s" % ('commit', 'username')
    p2 = subprocess.Popen(cmd2, shell=True)
    stdout2, stderr2 = p2.communicate()
    if stderr2:
        logger.error("run git command is out %s, err %s" % (stdout2, stderr2))
    else:
        logger.info("run git command is success， time is %s" % now)
    os.system('rm -rf %s' % data['translate_copy'])


def main():
    argv = sys.argv
    logger = test_get_logger()
    data = read_config()
    if len(argv) == 1:
        post_review_translate(data, logger)
    else:
        time_number = int(sys.argv[1])
        while True:
            post_review_translate(data, logger)
            time.sleep(time_number)


if __name__ == '__main__':
    main()
