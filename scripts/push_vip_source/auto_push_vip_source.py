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


remote_server = ['10.117.168.77', 'root', '!QAZ2wsx', '/usr/l10n']
remote_or_local_copy = 0
sender = 'ghou@vmware.com'
receivers = ['ghou@vmware.com']
# receivers = ['ghou@vmware.com', 'nannany@vmware.com', 'huihuiw@vmware.com', 'gongy@vmware.com', 'linr@vmware.com', 'longl1@vmware.com']


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
    if os.path.exists('/root/ghou/compare_report.html'):
        os.remove('/root/ghou/compare_report.html')
    if os.path.exists('/root/ghou/compare_report.tar.gz'):
        os.remove('/root/ghou/compare_report.tar.gz')
    if os.path.exists("/root/ghou/g11n-translations"):
        os.system('rm -rf %s' % "/root/ghou/g11n-translations")
    os.chdir("/root/ghou/")
    os.system("git clone ssh://git@git.eng.vmware.com/g11n-translations.git")
    # this is copy local bundle
    copy_source_path = '/root/ghou/copy/'
    if not os.path.exists(copy_source_path):
        os.system('mkdir -p %s' % copy_source_path)
    if remote_or_local_copy:
        cmd = "sshpass -p '%s' scp -r %s@%s:%s %s" % (remote_server[2], remote_server[1], remote_server[0], remote_server[3], copy_source_path)
        p = subprocess.Popen(cmd, shell=True)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
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
            logger.error("copy local source is out %s, err %s" % (stdout, stderr))
            return
        else:
            logger.info("copy local source is success")
    # this is git repository
    target_path = '/root/ghou/g11n-translations/l10n/'
    bcompare_source = copy_source_path + 'l10n/'
    compare_report_html = '/root/ghou/compare_report.html'
    bcompare1 = 'bcompare @/root/ghou/Compare.script %s %s %s' % (target_path[:-1], bcompare_source[:-1], compare_report_html)
    p = subprocess.Popen(bcompare1, shell=True)
    stdout0, stderr0 = p.communicate()
    if stderr0:
        logger.error("run bcompare is out %s, err %s" % (stdout0, stderr0))
        return
    else:
        logger.info("run bcompare is success")
    # 把文件同步到git库    之后提交上去
    # -I, –ignore-times 不跳过那些有同样的时间和长度的文件      -a, –archive 归档模式，表示以递归方式传输文件，并保持所有文件属性，等于-rlptgoD
    # -r表示recursive递归  --exclude不包含/ins目录    --recursive
    cmd1 = 'rsync -aI --recursive --include="*/" --include="*_en_US.json" --exclude="*" %s %s' % (copy_source_path, target_path[:-5])
    p1 = subprocess.Popen(cmd1, shell=True)
    stdout1, stderr1 = p1.communicate()
    if stderr1:
        logger.error("run rsync is out %s, err %s" % (stdout1, stderr1))
        return
    else:
        logger.info("run rsync is success")
    data = []
    for parent, dirnames, filenames in os.walk(target_path):
        if 'messages_en_US.json' in filenames and parent[len(target_path):]:
            data.append(parent[len(target_path):])
    data1 = []
    for parent, dirnames, filenames in os.walk(copy_source_path):
        if 'messages_en_US.json' in filenames and parent[len(copy_source_path)+len('l10n/'):]:
            data1.append(parent[len(copy_source_path)+len('l10n/'):])
    delete_path = list(set(data).difference(set(data1)))
    for path in delete_path:
        rm_path = target_path + path
        os.system('rm -rf %s' % rm_path)
#     os.chdir(target_path) # os.getcwd()
#     return_message = os.popen('git status')
#     if 'nothing to commit' in return_message.read():
#         return
#     cmd2 = "git add -A && git commit -m '%s' && git push origin master" % 'auto push vip source'
#     p2 = subprocess.Popen(cmd2, shell=True)
#     stdout2, stderr2 = p2.communicate()
#     if stderr2:
#         logger.error("run git command is out %s, err %s" % (stdout2, stderr2))
#         mail_message = '''Hi all,
#     git push is fail
#     
# thanks, %s
#         ''' % sender.split('@')[0]
#         send_mail_message(logger, 0, mail_message)
#         return
#     else:
#         logger.info("run git command is success")
#     os.system('rm -rf %s' % copy_source_path)
#     mail_message = '''Hi all,
#     The attachment is the result of a comparison between the code library and the collection library
#  
# thanks, %s
#     ''' % sender.split('@')[0]
#     send_mail_message(logger, 1, mail_message)
    

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
    

def main():
    argv = sys.argv
    logger = test_get_logger()
    if len(argv) == 1:
        auto_push_vip_source(logger)
    else:
        time_number = int(sys.argv[1])
        while True:
            auto_push_vip_source(logger)
            time.sleep(time_number)


if __name__ == '__main__':
    main()