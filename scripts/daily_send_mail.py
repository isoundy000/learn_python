# -*- coding: utf-8 -*-
'''
Created on 8/25/2016

@author: ghou
'''

import os
import subprocess
import logging
import datetime
import traceback
import jenkins
from django.core.mail import send_mail
os.environ['DJANGO_SETTINGS_MODULE']='g11nRepository.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "g11nRepository.settings")


user_info = {
    'username': 'ghou',
    'password': 'Donga@1234'
}


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file = logging.FileHandler("daily_send_mail.log")
    logger.addHandler(file)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def daily_send_mail(logger):
    supervisor_status = "sudo supervisorctl status"
    p = subprocess.Popen(supervisor_status, shell=True)
    stdout, stderr = p.communicate()
    content = 'Hi All, \n'
    content += 'This is %s report' % (datetime.date.today()+datetime.timedelta(days=1)) +'\n\n'
    content += 'GRM(gabi.eng.vmware.com):\n'
    if stderr:
        supervisor_message = '1 Supervisor process is down'
        logger.warning("supervisor process is down, err %s" % stderr)
    else:
        supervisor_message = '1 Supervisor process is running successfully.'
    content += supervisor_message + '\n'
    rabbitmq_status = "sudo rabbitmqctl status"
    p1 = subprocess.Popen(rabbitmq_status, shell=True)
    stdout, stderr = p1.communicate()
    if stderr:
        rabbitmq_message = '2 Rabbitmq process is down'
        logger.warning("rabbitmq process is down, err %s" % stderr)
    else:
        rabbitmq_message = '2 Rabbitmq process is running successfully.'
    content += rabbitmq_message + '\n'
    cpu_status = "/usr/bin/top -bcn 1 |grep Cpu | awk -F 'us,' '{print $1}' | awk -F ':' '{print $2}'"
    p2 = subprocess.Popen(cpu_status, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p2.communicate()
    if stderr:
        cpu_use_rate = '3 cpu command is err'
        logger.info("cpu command err message %s" % stderr)
    else:
        try:
            cpu_rate = stdout.split(' ')[1]
        except:
            print(traceback.format_exc())
        cpu_use_rate = '3 CPU used rate %s%%.' % cpu_rate
    content += cpu_use_rate + '\n'
    memory_status = "free -m | grep 'cache' | awk '{print $4}'"
    p3 = subprocess.Popen(memory_status, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p3.communicate()
    if stderr:
        memory_free = '4 Memory command is err'
        logger.info("memory command err message is %s" % stderr)
    else:
        number = stdout.split('\n')[1]
        memory_free = '4 Memory free %sM.' % number.strip('\n')
    content += memory_free + '\n'
    var_disk_residue = "df -h | awk '{print $4}' | sed -n '12p'"
    p4 = subprocess.Popen(var_disk_residue, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p4.communicate()
    if stderr:
        disk_residue = '5 var disk residue command is err'
        logger.info("var disk residue command message is %s" % stderr)
    else:
        disk_residue = '5 /var/ disk free %s.' % stdout.strip('\n')
    content += disk_residue
    content += '\n\nGRM_DB(gabi-db.eng.vmware.com):\n'
    cat_gabi_db = "cat /var/www/g11nRepository/ghou.txt | sed -n '2p'" # sshpass -p Dong!123 ssh ghou@gabi-db.eng.vmware.com free -m | grep 'cache' | awk '{print $4}'
    p5 = subprocess.Popen(cat_gabi_db, shell=True, stdout=subprocess.PIPE)
    stdout1, stderr1 = p5.communicate()
    if stderr1:
        memory_free1 = '1 server memory command is err'
        logger.info("memory command err message is %s" % stderr1)
    else:
        memory_free1 = '1 Server memory free %sM.' % stdout1.strip('\n')
    content += memory_free1 + '\n'
    cat_mnt_data = "cat /var/www/g11nRepository/ghou.txt | sed -n '3p'" # sshpass -p Dong!123 ssh ghou@gabi-db.eng.vmware.com df -h | awk '{print $4}' | sed -n '13p'
    p6 = subprocess.Popen(cat_mnt_data, shell=True, stdout=subprocess.PIPE)
    stdout2, stderr2 = p6.communicate()
    if stderr2:
        mnt_disk = '2 df -h command is err'
        logger.info("df -h command err message is %s" % stderr2)
    else:
        mnt_disk = '2 /mnt/data disk free %s.' % stdout2.strip('\n')
    content += mnt_disk
    content += '\n\nGRM(jenkins build):\n'
    #　sudo pip install python-jenkins (need setup jenkins package)
    server=jenkins.Jenkins("http://gabi.eng.vmware.com:8080", username=user_info['username'], password=user_info['password'])
    jobs_list = server.get_all_jobs('/api/python')
    i = 1
    flag = False
    for item in jobs_list:
        if item['color'] == 'red':
            name = item['name']
            config_xml = server.get_job_config(name).encode('utf-8')
            if '<triggers/>' in config_xml:
                continue
            list1 = name.split('-', 1)
            if len(list1) == 2:
                item_number = list1[0].strip().encode('utf-8')
                product_name = list1[1].strip()
                flag = True
                content += '%s %s product(release_%s) is build fail' % (i, product_name, item_number)
            content += '\n'
            i+=1
    if not flag:
        content += "All product's builds are successful."
        content += '\n'
    content += '\n'
    #　g11n-grm-project@vmware.com
    send_mail("GRM daily maintenance information", content, 'ghou@vmware.com', ['g11n-grm-project@vmware.com'], auth_user=user_info['username'], auth_password=user_info['password'])


def main():
    logger = test_get_logger()
    daily_send_mail(logger)


if __name__ == '__main__':
    main()