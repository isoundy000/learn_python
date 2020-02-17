#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.options import define, options

import rela_baike_server
from rela_baike_server import RelaBaikeRequest, RelaBaikeResult, RelaBaikeServer
import logging
from logging.handlers import TimedRotatingFileHandler
logging.basicConfig()

import pdb

g_log_prefix = '../log/rela_baike_tornado.'


def getLogger(strPrefixBase):
    strPrefix = "%s%d" % (strPrefixBase, os.getpid())
    logger = logging.getLogger("RELA_BAIKE")
    logger.propagate = False
    handler = TimedRotatingFileHandler(strPrefix, 'H', 1)
    handler.suffix = "%Y%m%d_%H%M%S.log"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def makeResponseBody(retCode, errReason, dicSummary):
    dicRes = {}
    dicRes['retCode'] = retCode
    if retCode != 0:
        dicRes['error'] = errReason
    else:
        dicRes['data'] = dicSummary
    return json.dumps(dicRes)


class RelaBaikeHandler(tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(50)

    def initialize(self, relaServer, logger):
        self.__serverRelaBaike = relaServer
        self.__logger = logger

    @tornado.gen.coroutine
    def get(self):
        lstSummary = []
        retCode = 0
        errReason = ""
        try:
            utfQuery = self.get_argument('query').encode('utf8').strip()
        except:
            errReason = "Query encoding not utf-8."
            strRes = makeResponseBody(-1, errReason, lstSummary)
            self.write(strRes)
            return

        if utfQuery == "":
            strRes = makeResponseBody(0, '', lstSummary)
            self.write(strRes)
            return

        error, errReason, lstSummary = yield self.getRelaBaike(utfQuery)
        strRes = makeResponseBody(error, errReason, lstSummary)
        self.write(strRes)

    def __logResponse(self, utfQuery, relaResult):
        succ = relaResult.isSuccess()
        if succ:
            self.__logger.info("%s\tSucc\t%s" % (utfQuery, "|".join([str(item[0]) for item in relaResult])))
        else:
            self.__logger.info("%s\tError:%d" % (utfQuery, relaResult.getError()))

    @run_on_executor
    def getRelaBaike(self, utfQuery):
        error = 0
        lstSummary = []
        relaBaikeRequest = RelaBaikeRequest(content=utfQuery)
        relaBaikeResult = self.__serverRelaBaike.getRelaBaike(relaBaikeRequest)
        self.__logResponse(utfQuery, relaBaikeResult)
        if relaBaikeResult.isSuccess():
            for item in relaBaikeResult:
                baikeid = item[0]
                try:
                    dicSummary = json.loads(item[1])
                except:
                    return -2, "summary format error", lstSummary
                lstSummary.append(dicSummary)
        else:
            return relaBaikeResult.getError(), rela_baike_server.g_dic_error.get(relaBaikeResult.getError(), 'other error'), lstSummary
        return 0, 'success', lstSummary


def start():
    port = int(sys.argv[1])

    serverRelaBaike = rela_baike_server.getRelaBaikeServer()
    logger = getLogger(g_log_prefix)

    app = tornado.web.Application(handlers=[(r"/rela_baike", RelaBaikeHandler, dict(relaServer=serverRelaBaike, logger=logger))])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(port)
    http_server.start(2)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start()