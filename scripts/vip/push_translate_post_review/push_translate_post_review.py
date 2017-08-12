# -*- coding: utf-8 -*-
'''
Created on 8/3/2017

@author: ghou
'''
import os
import sys
import re
import time
import subprocess
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


argv = sys.argv
if len(argv) not in [1, 2]:
    print 'argv error:', argv
    print 'run format: "python post_review_translate.py(Manual)" or "python post_review_translate.py 3600 &"'
    sys.exit()


def test_get_logger(name):
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler(name)
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
        if len(value_list) > 1:
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
    targetdirnames = []
    for product in os.listdir(data['post_target_path']):
        targetdirnames.append(product)
    copydirnames = []
    for product in os.listdir(data['post_copy']+'l10n/bundles/'):
        if product in targetdirnames:
            copydirnames.append(product)
    for product in copydirnames:
        os.chdir(data['post_target_path'])
        os.system('git branch feature/%s && git checkout feature/%s' % (product, product))
        list_new = "".join([data['post_copy'], 'l10n/bundles/'])
        cmd1 = 'rsync -aI --recursive --include="*/" --exclude="*_en_US.json" %s %s' % (list_new+product, data['post_target_path']+product)
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
        os.system('git add -A && git commit -m %s' % product)
        os.system("git rev-parse HEAD > commit.log")
        commitLog = open('commit.log')
        commit = commitLog.readline().strip('\n').strip(' ')
        commitLog.close()
        cmd3 = "/build/apps/bin/post-review -o %s > ghou.txt" % commit
        p3 = subprocess.Popen(cmd3, shell=True)
        stdout3, stderr3 = p3.communicate()
        if stderr3:
            logger.error("run git command is out %s, err %s" % (stdout3, stderr3))
        else:
            logger.info("run git command is success， time is %s" % now)
        time.sleep(30)
        ghouTxt = open('ghou.txt')
        review_url = ''
        for line in ghouTxt.readlines():
            if re.search('.*reviewboard.*', line):
                review_url = line
        ghouTxt.close()
        for pm_email, product_list in data.iteritems():
            if product in product_list:
                mail_message = '''Hi %s,
    this is the post review url %s
thanks, %s
        ''' % (pm_email.split('@')[0], review_url, data['sender'].split('@')[0])
                send_mail_message(logger, data, pm_email, mail_message)
                break
        os.system('git checkout master')
        os.system('rm -rf ghou.txt')
        os.system('rm -rf commit.log')
    os.system('rm -rf %s' % data['post_copy'])


def send_mail_message(logger, data, pm_email, mail_message=None):
    # Create an instance with an attachment
    message = MIMEMultipart()
    message['From'] = Header(data['sender'])
    message['To'] =  Header(pm_email)
    subject = 'post review of email'
    message['Subject'] = Header(subject, 'utf-8')
    # Mail text content
    message.attach(MIMEText(mail_message, 'plain', 'utf-8'))
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(data['sender'], [pm_email], message.as_string())
        logger.info("Successful mail delivery")
    except smtplib.SMTPException:
        logger.info("Error: Unable to send mail")


def main():
    argv = sys.argv
    logger = test_get_logger('post_review_translate.log')
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