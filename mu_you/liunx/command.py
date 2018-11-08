#!/usr/bin/env python
#coding: utf-8

# Linux如何查看端口
# 1、lsof -i:端口号 用于查看某一端口的占用情况，比如查看8000端口使用情况，lsof -i:8000
# 可以看到8000端口已经被轻量级文件系统转发服务lwfs占用
# 2、netstat - tunlp | grep
# 端口号，用于查看指定的端口号的进程情况，如查看8000端口的情况，netstat - tunlp | grep 8000
# 说明一下几个参数的含义：
#                                 -t (tcp) 仅显示tcp相关选项
#                                 -u (udp)仅显示udp相关选项
#                                 -n 拒绝显示别名，能显示数字的全部转化为数字
#                                 -l 仅列出在Listen(监听)的服务状态
#                                 -p 显示建立相关链接的程序名

# 附加一个python端口占用监测的程序，该程序可以监测指定IP的端口是否被占用。
# scan_port.py

import socket, time, thread
socket.setdefaulttimeout(3)         # 设置默认超时时间


def socket_port(ip, port):
    """
    输入IP和端口号，扫描判断端口是否占用
    """
    try:
        if port >= 65535:
            print u'端口扫描结束'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            lock.acquire()
            print ip, u':', port, u'端口已占用'
            lock.release()
    except:
        print u'端口扫描异常'


def ip_scan(ip):
    """
    输入IP，扫描IP的0-65534端口情况
    """
    try:
        print u'开始扫描 %s' % ip
        start_time = time.time()
        for i in range(0, 65534):
            thread.start_new_thread(socket_port, (ip, int(i)))
        print u'扫描端口完成，总共用时：%.2f' % (time.time() - start_time)
    except:
        print u'扫描ip出错'


if __name__ == '__main__':
    url = raw_input('Input the ip you want to scan: ')
    lock = thread.allocate_lock()
    ip_scan(url)