#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import base64

#                 正文       title  addrs
SYS_MAIL_CMD = """echo '%s' | mail -s '%s' %s"""


def send_sys_mail(addr_list, subject, body):
    """# send_sys_mail: 用系统名义给人发邮件
    args:
        addr_list: 发件人的list
        subject: 邮件标题
        body: 邮件正文
    returns:
        0    ---
    """
    # body = body.encode('utf-8')
    # subject = '=?UTF-8?%s?='%base64.encodestring(subject).strip()  # strip是因为最后有个换行符

    addrs = ','.join(addr_list)

    cmd = SYS_MAIL_CMD % (body, subject, addrs)
    rc = os.system(cmd)