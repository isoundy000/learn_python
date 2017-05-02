# -*-coding:utf-8-*-
'''
Created on 4/26/2017

@author: ghou
'''

import logging
import subprocess
# down pytest-3.0.7.tar.gz  install
import py.test


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file = logging.FileHandler("restart.log")
    logger.addHandler(file)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.NOTSET)
    return logger


def auto_run_testcase(logger):
    # run testcase
    # python -m unittest discover
    shell1 = 'cd /var/lib/jenkins/workspace/grm'
    


def main():
    logger = test_get_logger()
    auto_run_testcase(logger)


if __name__ == '__main__':
    main()
