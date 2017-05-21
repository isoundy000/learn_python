# -*- coding: utf-8 -*-
'''
Created on 2017年5月18日

@author: ghou
'''

import os
import subprocess
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


remote_server = ['10.117.168.77', 'root', '!QAZ2wsx', '/usr/l10n']
remote_or_local_copy = 0
sender = 'ghou@vmware.com'
receivers = ['ghou@vmware.com']


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


def auto_push_vip_source(logger):
    # this is copy local bundle
    copy_source_path = '/root/ghou/copy/'
    if not os.path.exists(copy_source_path):
        os.system('mkdir -p %s' % copy_source_path)
    if remote_or_local_copy:
        cmd = "sshpass -p '%s' scp -r %s@%s:%s %s" % (remote_server[2], remote_server[1], remote_server[0], remote_server[3], copy_source_path)
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.info("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    else:
        # this is local bundle
        source_path = '/root/ghou/local/'
        if not os.path.exists(source_path):
            os.mkdir(source_path)
        cmd = 'cp -r %s %s' % (source_path+'.', copy_source_path)
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.info("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    # this is git repository
    target_path = '/root/ghou/g11n-translations/l10n/'
    bcompare = 'bcompare @Compare.script %s %s' % (copy_source_path, target_path)
    p = subprocess.Popen(bcompare, shell=True)
    stdout0, stderr0 = p.communicate()
    if stderr0:
        logger.info("run bcompare is out %s, err %s" % (stdout0, stderr0))
        return
    else:
        logger.info("run bcompare is success")
    # 把文件同步到git库    之后提交上去
    # -I, –ignore-times 不跳过那些有同样的时间和长度的文件      -a, –archive 归档模式，表示以递归方式传输文件，并保持所有文件属性，等于-rlptgoD
    cmd1 = 'rsync -aI %s %s' % (copy_source_path, target_path[:-5])
    p1 = subprocess.Popen(cmd1, shell=True)
    stdout1, stderr1 = p1.communicate()
    if stderr1:
        logger.info("run rsync is out %s, err %s" % (stdout1, stderr1))
        return
    else:
        logger.info("run rsync is success")
    os.chdir(target_path) # os.getcwd()
    return_message = os.popen('git status')
    if 'nothing to commit' in return_message.read():
        return
#     cmd2 = "git add . && git commit -m '%s' && git push origin master" % 'auto push vip source'
#     p2 = subprocess.Popen(cmd2, shell=True)
#     stdout2, stderr2 = p2.communicate()
#     if stderr2:
#         logger.info("run git command is out %s, err %s" % (stdout2, stderr2))
#         mail_message = '''Hi all,
#     git push is fail
#  
# thanks, %s
#         ''' % sender.split('@')[0]
#         send_mail_message(logger, 0, mail_message)
#         return
#     else:
#         logger.info("run git command is success")

    mail_message = '''Hi all,
    The attachment is the result of a comparison between the code library and the collection library
 
thanks, %s
    ''' % sender.split('@')[0]
    send_mail_message(logger, 1, mail_message)
    os.system('rm -rf %s' % copy_source_path)
    

def send_mail_message(logger, is_fujian, mail_message=None):
    os.chdir('/root/ghou/')
    #创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header(sender)
    message['To'] =  Header(receivers[0])  
    subject = 'Auto push vip source'
    message['Subject'] = Header(subject, 'utf-8')
    #邮件正文内容
    message.attach(MIMEText(mail_message, 'plain', 'utf-8'))
    if is_fujian:
        size = os.path.getsize('compare_report.html')
        if size > 4000000:
            os.system('tar -zcvf compare_report.tar.gz compare_report.html')
            fo = open('compare_report.tar.gz', 'rb')
        else:
            fo = open('compare_report.html', 'rb')
        stream = fo.read()
        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(stream, 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        contenttype = 'attachment; filename="%s"' % fo.name
        att1["Content-Disposition"] = contenttype
        message.attach(att1)
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        logger.info("Successful mail delivery")
    except smtplib.SMTPException:
        logger.info("Error: Unable to send mail")
    if os.path.exists('/root/ghou/compare_report.html'):
        os.remove('/root/ghou/compare_report.html')
    if os.path.exists('/root/ghou/compare_report.tar.gz'):
        os.remove('/root/ghou/compare_report.tar.gz')


def main():
    logger = test_get_logger()
    auto_push_vip_source(logger)


if __name__ == '__main__':
    main()