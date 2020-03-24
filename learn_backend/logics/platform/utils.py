#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import base64
import hashlib
import xml.sax.handler






def xml2dict(xml_data):
    """解析支付定单数据xml到字典格式
    Args:
        xml_data: xml数据
    Returns:
        字典格式数据
    """
    if isinstance(xml_data, unicode):
        xml_data = xml_data.encode('utf-8')

    xh = XMLHandler()
    xml.sax.parseString(xml_data, xh)

    return xh.getDict()


class XMLHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        self.mapping[name] = self.buffer

    def getDict(self):
        return self.mapping