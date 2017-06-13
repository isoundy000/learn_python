# -*- coding: utf-8 -*-
'''
Created on 6/9/2017

@author: ghou
'''

from abc import ABCMeta, abstractmethod
import codecs
import re
import os
import sys
from  xml.dom import  minidom
from xml.sax.saxutils import *


class Parser(object):
    '''
    super class for resx_old ,property and vmsg l10nparser
    '''
    encoding = 'utf-8'
    need_escaped = False
    STRING = 0
    LAYOUTINFO = 1
    OTHER = 2

    __metaclass__ = ABCMeta
    def __init__(self, file_path, sep_char_re, ver_char_re, value_splitor):

        self._file_path = file_path
        self._sep_char_re = sep_char_re
        self._ver_char_re = ver_char_re
        self._value_splitor = value_splitor
        self._string_item_list = []


    @classmethod
    def store(cls, targ_string_items, targ_file_path, entities = {}):
        out = codecs.open(targ_file_path, 'w', cls.encoding)
        if out.mode[0] != 'w':
            raise ValueError, 'Steam should be opened in write mode!'

        try:
            for item in targ_string_items:
                value = item.value
                if cls.need_escaped and value.strip():
                    value = escape(value, entities)
                out.write(''.join((item.block, value)))
            out.close()
        except IOError, e:
            raise

    @classmethod
    def compose(cls, targ_string_items, entities = {}):
        strList = []
        for item in targ_string_items:
            value = item.value
            if cls.need_escaped and value.strip():
                value = escape(value, entities)
            strList.append(''.join((item.block, value)))
        block = ''.join(strList)
        return block

    def load(self):
        """ Load properties_old from an open file stream """
        stream = self._open_resource_file()
        lines = stream.readlines()
        self._parse(lines)

    @abstractmethod
    def _parse(self, lines):
        return

    def _generate_item(self, comment, key, value, block, hashcode = None, type=STRING, **kwargs):
        """
        generate the object contains key, value, comment,block
        kwargs:Extended parameter for special parser type, as 'keytrunk for rc parser'
        """
        stringItemsDic = {}
        stringItemsDic.update(comment = comment,
                              key = key,
                              value = value,
                              block = block,
                              hashcode = hashcode,
                              type = type)
        stringItemsDic.update(kwargs)
        sitem = StringItems(stringItemsDic)
        self._string_item_list.append(sitem)
        return sitem

    def _open_resource_file(self):
        try:
            file_stream = codecs.open(self._file_path, 'r', self.encoding)
        except IOError:
            print "No such file or directory!"
            sys.exit(0)
        else:
            return file_stream

    def _add_prev_next_hashcode(self):
        for i in xrange(len(self._string_item_list)):
            if i > 0:
                prevhashcode = self._string_item_list[i - 1].hashcode
            else:
                prevhashcode = 0
            if i < len(self._string_item_list) - 1:
                nexthashcode = self._string_item_list[i + 1].hashcode
            else:
                nexthashcode = 0
            self._string_item_list[i].prevhashcode = prevhashcode
            self._string_item_list[i].nexthashcode = nexthashcode


def c_mul(a, b):
    return eval(hex((long(a) * b) & 0xFFFFFFFFL)[:-1])

       
def getHashCode(s):
    if not s:
        return 0 # empty
    value = ord(s[0]) << 7
    for char in s:
        value = c_mul(1000003, value) ^ ord(char)
    value = value ^ len(s)
    if value == -1:
        value = -2
    return value


class StringItems(object):
    __slots__ = ['key',
                 'keytrunk',
                 'value',
                 'comment',
                 'block',
                 'globalid',
                 'hashcode',
                 'type',
                 'prevhashcode',
                 'nexthashcode',
                 'filepath',
                 'fileid']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize attributes with parameters and set default value, if None. 
        """
        for dic in args:
            for key in dic:
                setattr(self, key, dic[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

        for s in self.__slots__:
            if getattr(self, s, None) is None:
                setattr(self, s, "")

    def __unicode__(self):
        return u'%s********%s' % (self.key, self.value)

    def to_dic(self):
        return {s: getattr(self, s, None) for s in self.__slots__}


class PropertiesParser(Parser):
    encoding='utf-8'
    def __init__(self,file_path):
        sep_char_re=re.compile(r'(?<!\\)(\s*\=)|(?<!\\)(\s*\:)')
        ver_char_re=re.compile(r'(\s*\=)|(\s*\:)')
        value_splitor = re.compile(r'\r\n|\r|\n')
        self.__whitespace_re = re.compile(r'(?<![\\\=\:])(\s)')
        self.__whitespace_re_no_sep = re.compile(r'(?<![\\])(\s)')
        Parser.__init__(self,file_path,sep_char_re,ver_char_re,value_splitor)

    def _parse(self, lines):
        line_no=0
        i = iter(lines)
        comment=""
        block=""
        for line in i:
            line_no += 1
            line_after_strip = line.strip()
            # Skip null lines
            if not line_after_strip:
                block+=line
                continue

            # Skip lines which are comments
            if line[0] == '#':
                comment+=line
                block+=line
                continue
            if line[0]=="[" and line[-1]=="]":
                comment+=line
                block+=line
                continue
            sep_id_x = -1
            m = self._sep_char_re.search(line)
            if m:
                first, last = m.span()
                start, end = 0, first
                whitespace_re = self.__whitespace_re
            else:
                if self._ver_char_re.search(line):
                    whitespace_re = self.__whitespace_re_no_sep
                else:
                    comment+=line
                    block+=line
                    continue
                start, end = 0, len(line)

            m2 = whitespace_re.search(line, start, end)
            if m2:
                first, last = m2.span()
                if first!=0:
                    sep_id_x = first
                elif m:
                    first, last = m.span()
                    sep_id_x = last - 1
            elif m:
                first, last = m.span()
                sep_id_x = last - 1

            while line.strip()[-1] == '\\':
                next_line = i.next()
                line_no += 1
                line = line+next_line
                if next_line == '\n' or next_line == '\r' or next_line == '\r\n' or next_line == '\n\r':
                    break
            if sep_id_x != -1:
                key, value = line[:sep_id_x], line[sep_id_x+1:]
                block+=line[:sep_id_x+1]
            else:
                key,value = line,''
                block+=key

            s_block=""
            v_range_list=[]
            v_range_iter=self._value_splitor.finditer(value)
            for match in v_range_iter:
                v_range_list.append(match)

            if v_range_list:
                v_range_first, v_range_last = v_range_list[-1].span()
                if v_range_last == len(value):# means newline symbol is the last char.
                    s_block=value[v_range_first:]
                    value = value[:v_range_first]

            comment=comment.strip()
            key=key.strip()
            hashcode=getHashCode(value)
            self._generate_item(comment,key,value,block,hashcode)
            comment=""
            block=s_block
        if block : self._generate_item(comment,"","",block,"")
        
        
class JsParser(Parser):
    encoding='utf-8'
    def __init__(self, file_path):
        self.multiLineReg = re.compile(r'(\"\s*\+[\n|\r\n|\r]*\s*\")')
        sepCharReg = re.compile(r'\s*(.*):\s*["|\'](.*)["|\'],')
        Parser.__init__(self, file_path, sepCharReg, None, None)

    def load(self):
        stream = self._open_resource_file()
        lines = stream.read()
        lines = re.sub(r'(\"\s*\+[\n|\r\n|\r]*\s*\")', '', lines)
        out = codecs.open(r'D:\vip_testdata\pi-i18n.js', 'w', self.encoding)
        out.write(lines)
        out.close( )
        file_stream = codecs.open(r'D:\vip_testdata\pi-i18n.js', 'r', self.encoding)
        lines1 = file_stream.readlines()
        self._parse(lines1)
        
    def _parse(self, lines):
        i = iter(lines)
        for line in i:
            regPattern = self._sep_char_re.search(line)
            if regPattern:
                key = regPattern.group(1)
                value = regPattern.group(2)
                self._generate_item("",key,value,"","")


if __name__ == '__main__':
    data = {"messages": [], "webui": [], "pi-i18n": []}
    propreties1 = r'D:\strata\loginsight\components\commons-lib\lib\src\com\vmware\loginsight\i18n\messages.properties'
    parser1 = PropertiesParser(propreties1)
    parser1.load()
    for i in parser1._string_item_list:
        data["messages"].append((i.key, i.value))

    propreties2 = r'D:\strata\loginsight\components\ui\application\src\webui.properties'
    parser2 = PropertiesParser(propreties2)
    parser2.load()
    for i in parser2._string_item_list:
        data["webui"].append((i.key, i.value))
    
    jsPath = r'D:\\strata\loginsight\components\ui\application\WebContent\js\pi-i18n\lang\pi-i18n.js'
    jsParser = JsParser(jsPath)
    jsParser.load()
    for i in jsParser._string_item_list:
        data["pi-i18n"].append((i.key, i.value))
    rootdir = r"D:\strata"
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp")):
                continue
            filePath = "\\".join([parent, filename])
            file_stream = codecs.open(filePath, 'r', 'utf-8')
            print file_stream.read()