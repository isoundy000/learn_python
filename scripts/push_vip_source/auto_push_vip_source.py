# -*- coding: utf-8 -*-
'''
Created on 2017年5月18日

@author: ghou
'''

import os
import sys
import time
import subprocess
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


argv = sys.argv
if len(argv) not in [1, 2]:
    print 'argv error:', argv
    print 'run format: "python auto_push_vip_source.py(Manual)" or "python auto_push_vip_source.py 3600 &"'
    sys.exit()


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler("auto_push_vip_source.log")
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


def auto_push_vip_source(data, logger):
    now = int(time.time())
    os.chdir(data['workspace'])
    compare_report_html = data['workspace'] + '/compare_report.html'
    compare_report_zip = data['workspace'] + '/compare_report.tar.gz'
    git_rep = data['workspace'] + "/g11n-translations"
    if os.path.exists(compare_report_html):
        os.remove(compare_report_html)
    if os.path.exists(compare_report_zip):
        os.remove(compare_report_zip)
    if os.path.exists(git_rep):
        os.system('rm -rf %s' % git_rep)
    os.system(data['git_lib'])
    # this is copy local bundle
    if not os.path.exists(data['source_copy']):
        os.system('mkdir -p %s' % data['source_copy'])
    remote_or_local_copy = int(data['remote_or_local_copy'])
    if remote_or_local_copy:
        cmd = "sshpass -p '%s' scp -r %s@%s:%s %s" % (data['remote_server'][2], data['remote_server'][1], data['remote_server'][0], data['remote_server'][3], data['source_copy'])
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    else:
        # this is local bundle
        if not os.path.exists(data['source_local']):
            os.mkdir(data['source_local'])
        cmd = 'cp -r %s %s' % (data['source_local']+'.', data['source_copy'])
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    list_new = data['target_path'].split('g11n-translations/')
    bcompare1 = 'bcompare @%s/Compare.script %s %s %s' % (data['workspace'], data['target_path'], data['source_copy']+list_new[1], compare_report_html)
    p = subprocess.Popen(bcompare1, shell=True)
    stdout0, stderr0 = p.communicate()
    if stderr0:
        logger.error("run bcompare is out %s, err %s" % (stdout0, stderr0))
        return
    else:
        logger.info("run bcompare is success")
    # Synchronize files to the GIT library and submit them later
    # -I, –ignore-times don't skip files that have the same time and length  -a, –archive Archive mode, which means to transfer files in a recursive manner and keep all file attributes equal to -rlptgoD
    # -r Represents recursive recursion --exclude doesn't contain/ins Catalog --recursive
    cmd1 = 'rsync -aI --recursive --include="*/" --include="*_en_US.json" --exclude="*" %s %s' % (data['source_copy']+list_new[1], data['target_path'])
    p1 = subprocess.Popen(cmd1, shell=True)
    stdout1, stderr1 = p1.communicate()
    if stderr1:
        logger.error("run rsync is out %s, err %s" % (stdout1, stderr1))
        return
    else:
        logger.info("run rsync is success")
    os.chdir(data['target_path']) # os.getcwd()
    return_message = os.popen('git status')
    if 'nothing to commit' in return_message.read():
        return
    cmd2 = "git add -A && git commit -m '%s' && git pull && git push origin master" % 'auto push vip source'
    p2 = subprocess.Popen(cmd2, shell=True)
    stdout2, stderr2 = p2.communicate()
    if stderr2:
        logger.error("run git command is out %s, err %s" % (stdout2, stderr2))
        mail_message = '''Hi all,
    git push is fail
 
thanks, %s
        ''' % data['sender'].split('@')[0]
        send_mail_message(logger, 0, data, mail_message)
        return
    else:
        logger.log(41, ("run git command is success, time is %s" % now))
    os.system('rm -rf %s' % data['source_copy'])
    mail_message = '''Hi all,
    The attachment is the result of a comparison between the code library and the collection library

thanks, %s
    ''' % data['sender'].split('@')[0]
    send_mail_message(logger, 1, data, mail_message)


def send_mail_message(logger, is_fujian, data, mail_message=None):
    os.chdir(data['workspace'])
    # Create an instance with an attachment
    message = MIMEMultipart()
    message['From'] = Header(data['sender'])
    message['To'] =  Header(data['receivers'][0])
    subject = 'Auto push vip source'
    message['Subject'] = Header(subject, 'utf-8')
    # Mail text content
    message.attach(MIMEText(mail_message, 'plain', 'utf-8'))
    if is_fujian:
        size = os.path.getsize('compare_report.html')
        if size > 4000000:
            os.system('tar -zcvf compare_report.tar.gz compare_report.html')
            fo = open('compare_report.tar.gz', 'rb')
        else:
            fo = open('compare_report.html', 'rb')
        stream = fo.read()
        # Construct the attachment 1 to transfer the test.txt file in the current directory
        att1 = MIMEText(stream, 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # The filename here can be written arbitrarily, what name is written, what name is displayed in the mail
        contenttype = 'attachment; filename="%s"' % fo.name
        att1["Content-Disposition"] = contenttype
        message.attach(att1)
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(data['sender'], data['receivers'], message.as_string())
        logger.info("Successful mail delivery")
    except smtplib.SMTPException:
        logger.info("Error: Unable to send mail")


def main():
    argv = sys.argv
    logger = test_get_logger()
    data = read_config()
    if len(argv) == 1:
        auto_push_vip_source(data, logger)
    else:
        time_number = int(sys.argv[1])
        while True:
            auto_push_vip_source(data, logger)
            time.sleep(time_number)


if __name__ == '__main__':
    main()