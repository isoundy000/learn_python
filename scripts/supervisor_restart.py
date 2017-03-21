# -*- coding: utf-8 -*-
'''
Created on 1/5/2017

@author: ghou
'''

import logging
import subprocess


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


def restart_supervisor(logger):
    kill_supervisor_process = "ps -aux | grep 'supervisor' | awk '{print $2}' | sudo xargs kill -9"
    p = subprocess.Popen(kill_supervisor_process, shell=True)
    stdout, stderr = p.communicate()
    if stdout or stderr:
        logger.info("kill supervisor is out %s, err %s" % (stdout, stderr))
    else:
        print 'kill supervisor process is success'
  
    kill_celery_worker = "ps -aux | grep 'celery worker' | awk '{print $2}' | sudo xargs kill -9"
    p2 = subprocess.Popen(kill_celery_worker, shell=True)
    stdout2, stderr2 = p2.communicate()
    if stdout2 or stderr2:
        logger.info("kill celery worker process is out %s, err %s" % (stdout2, stderr2))
    else:
        print 'kill all celery worker process is success'

    kill_celery_beat = "ps -aux | grep 'celery beat' |  awk '{print $2}' | sudo xargs kill -9"
    p3 = subprocess.Popen(kill_celery_beat, shell=True)
    stdout3, stderr3 = p3.communicate()
    if stdout3 or stderr3:
        logger.info("kill celery beat process is out %s, err %s" % (stdout3, stderr3))
    else:
        print 'kill celery beat process is success'

    rm_supervisor_sock = "sudo rm /tmp/supervisor.sock"
    code4 = subprocess.call(rm_supervisor_sock, shell=True)
    if code4 != 0:
        logger.info("rm supervisor sock is err %s, may be the file does not exist" % str(code4))
    else:
        print 'rm supervisor sock is success'

    start_supervisor = "sudo supervisord -c /etc/supervisord.conf"
    code5 = subprocess.call(start_supervisor, shell=True)
    if code5 != 0:
        logger.info("start supervisor is err %s" % str(code5))
    else:
        print 'start supervisor is success'

    start_apache2 = "sudo service apache2 restart"
    code6 = subprocess.call(start_apache2, shell=True)
    if code6 != 0:
        logger.info("restart apache2 is err %s" % str(code6))
    else:
        print 'restart apache2 is success'


def main():
    logger = test_get_logger()
    restart_supervisor(logger)


if __name__ == '__main__':
    main()