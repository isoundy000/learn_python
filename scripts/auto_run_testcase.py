# -*-coding:utf-8-*-
'''
Created on 4/26/2017

@author: ghou
'''

import logging
import subprocess
import os
import sys
# down pytest-3.0.7.tar.gz  install
# import py.test
import django
sys.path.append('/var/lib/jenkins/workspace/grm/g11nRepository')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "g11nRepository.settings_test")


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file = logging.FileHandler("restart.log")
    logger.addHandler(file)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def auto_run_testcase(logger):
    # python -m unittest discover
    cmd = "cd /var/lib/jenkins/workspace/grm/l10n_parser && echo qwe123 | sudo -S python -m unittest discover"
    p = subprocess.Popen(cmd, shell=True)
    stdout, stderr = p.communicate()
    if stderr:
        logger.info("run l10n_parser testcase is out %s, err %s" % (stdout, stderr))
    else:
        logger.info("run l10n_parser testcase is success")

    if not os.path.exists('/var/www/g11nRepository/log'):
        cmd1 = "echo qwe123 | sudo -S mkdir -p /var/www/g11nRepository/log"
        p1 = subprocess.Popen(cmd1, shell=True)
        stdout1, stderr1 = p1.communicate()
        if stderr1:
            logger.info("mkdir log path is out %s, err %s" % (stdout1, stderr1))
        else:
            logger.info("mkdir log path  is success")


    cmd2 = "cd /var/lib/jenkins/workspace/grm/g11nRepository && echo qwe123 | sudo -S python -m unittest discover"
    p2 = subprocess.Popen(cmd2, shell=True)
    stdout, stderr = p2.communicate()
    if stderr:
        logger.info("run g11nRepository testcase is out %s, err %s" % (stdout, stderr))
    else:
        logger.info("run g11nRepository testcase is success")

#     cmd3 = "echo qwe123 | sudo -S rm -rf /var/www/g11nRepository/"
#     p3 = subprocess.Popen(cmd3, shell=True)
#     stdout3, stderr3 = p3.communicate()
#     if stderr3:
#         logger.info("delete log path is out %s, err %s" % (stdout3, stderr3))
#     else:
#         logger.info("delete log path  is success")


def main():
    logger = test_get_logger()
    auto_run_testcase(logger)


if __name__ == '__main__':
    main()
