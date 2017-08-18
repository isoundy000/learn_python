# -*- coding: utf-8 -*-
'''
Created on 8/8/2017

@author: ghou
'''
import re
import os
import codecs
from loginsight_get_message.base.parser import Parser


class JsParser(Parser):
    encoding='utf-8'
    def __init__(self, file_path):
        sepCharReg = re.compile(r'\s*(.*):\s*([\"|\'])(.*?)\2,')
        self.lastOne = re.compile(r'\s*(.*):\s*([\"|\'])(.*?)\2')
        Parser.__init__(self, file_path, sepCharReg, None, None)

    def load(self):
        stream = self._open_resource_file()
        lines = stream.read()
        stream.close()
        lines = re.sub(r'(\"\s*\+[\n|\r\n|\r]*\s*\")', '', lines)
        if os.path.exists(self._file_path):
            os.remove(self._file_path)
        out = codecs.open(self._file_path, 'w', self.encoding)
        out.write(lines)
        out.close()
        file_stream = codecs.open(self._file_path, 'r', self.encoding)
        lines1 = file_stream.readlines()
        self._parse(lines1)

    def _parse(self, lines):
        i = iter(lines)
        for line in i:
            regPattern = self._sep_char_re.search(line)
            if regPattern:
                key = regPattern.group(1)
                value = regPattern.group(3)
                self._generate_item("", key, value, "", "")
            else:
                regPattern1 = self.lastOne.search(line)
                if regPattern1:
                    key = regPattern1.group(1)
                    value = regPattern1.group(3)
                    self._generate_item("", key, value, "", "")