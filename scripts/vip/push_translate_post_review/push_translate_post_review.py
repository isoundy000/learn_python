# -*- coding: utf-8 -*-
'''
Created on 8/3/2017

@author: ghou
'''
import os
import sys
import time
import subprocess


argv = sys.argv
if len(argv) not in [1, 2]:
    print 'argv error:', argv
    print 'run format: "python post_review_translate.py(Manual)" or "python post_review_translate.py 3600 &"'
    sys.exit()


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
    dirnames = [product for product in os.listdir(data['post_target_path']) if os.path.isdir(product)]
    for product in dirnames:
        os.chdir(data['post_target_path'])
        os.system('git branch feature/%s && git checkout feature/%s' % product)
        list_new = data['post_copy'].split(product)
        cmd1 = 'rsync -aI --recursive --include="*/" --exclude="*_en_US.json" %s %s' % (list_new[0]+product, data['post_target_path']+product)
        p1 = subprocess.Popen(cmd1, shell=True)
        stdout1, stderr1 = p1.communicate()
        if stderr1:
            logger.error("run rsync is out %s, err %s" % (stdout1, stderr1))
            continue
        else:
            logger.info("run rsync is success")
        return_message = os.popen('git status')
        if 'nothing to commit' in return_message.read():
            continue
        os.system('git add -A && git commit -m %s' % ('check %s change code' % product))
        commit = os.popen("git rev-parse HEAD")
        cmd3 = "/build/apps/bin/post-review -o %s" % commit
        p3 = subprocess.Popen(cmd3, shell=True)
        stdout3, stderr3 = p3.communicate()
        if stderr3:
            logger.error("run git command is out %s, err %s" % (stdout3, stderr3))
        else:
            logger.info("run git command is success， time is %s" % now)
        os.system('git checkout master')
    os.system('rm -rf %s' % data['post_copy'])


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
