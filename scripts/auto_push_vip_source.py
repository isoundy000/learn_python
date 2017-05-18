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


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file = logging.FileHandler("auto_push_vip_source.log")
    logger.addHandler(file)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def auto_push_vip_source(logger):
    # this is local bundle
    source_path = '/local/source'
    # this is copy local bundle
    copy_source_path = '/hou/copy/g11n-translations/l10n/'
    # this is origin git Repository
    target_path = '/hou/origin/g11n-translations/l10n/'
    cmd = 'cp -r % %' % source_path, copy_source_path
    p = subprocess.Popen(cmd, shell=True)
    stdout, stderr = p.communicate()
    if stderr:
        logger.info("copy local source is err %s", stderr)
    else:
        logger.info("copy local source is success")
    
    bcompare = 'bcompare @Compare.script %s %s' % copy_source_path, target_path
    p = subprocess.Popen(bcompare, shell=True)
    stdout, stderr = p.communicate()
    if stderr:
        logger.info("run l10n_parser testcase is out %s, err %s" % (stdout, stderr))
    else:
        logger.info("run l10n_parser testcase is success")
    send_mail_message(logger)


def send_mail_message(logger):
    #创建一个带附件的实例
    message = MIMEMultipart()
    subject = 'Auto push vip source'
    message['Subject'] = Header(subject, 'utf-8')
    #邮件正文内容
    message.attach(MIMEText('The attachment is the result of a comparison between the code library and the collection library', 'plain', 'utf-8'))
    fo = open('compare_report.html', 'rb')
    stteam = fo.read()
    # 构造附件1，传送当前目录下的 test.txt 文件
    att1 = MIMEText(stteam, 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    contenttype = 'attachment; filename="%s"' % fo.name
    att1["Content-Disposition"] = contenttype
    message.attach(att1)
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail('ghou@vmware.com', ['ghou@vmware.com'], message.as_string())
        logger.info("Successful mail delivery")
    except smtplib.SMTPException:
        logger.info("Error: Unable to send mail")


def main():
    logger = test_get_logger()
    auto_push_vip_source(logger)


if __name__ == '__main__':
    main()