# -*- encoding: utf-8 -*-
'''
Created on 2018年5月26日

@author: houguangdong
'''
import time
from socket import AF_INET, SOCK_STREAM, socket
from gevent import monkey
monkey.patch_all()
import urllib2
from gevent.pool import Pool


HOST = '127.0.0.1'
PORT = 5000
BUFSIZE = 1024
ADDR = (HOST, PORT)


def lian_xi():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)

    client.send("hello server")
    data = client.recv(BUFSIZE)
    print data
    # 简单的一个客户端。


def download(url):
    return urllib2.urlopen(url).read()


if __name__ == '__main__':
    urls = ['http://httpbin.org/get'] * 100
    pool = Pool(20)
    print pool.map(download, urls)