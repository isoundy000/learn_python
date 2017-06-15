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
import logging


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
                value = regPattern.group(2)
                self._generate_item("",key,value,"","")
                

class ReplaceMessage(object):
    encoding = 'utf-8'
    def __init__(self, file_path, data):
        self.filePath = file_path
        self.data = data
        self.i18nMessage = r'I18nUtil[\r|\n|\r\n]*\s*\.getMessage\((.*?)"(.*?)"'
        self.getMessage = r'(?<![I18nUtil|\.])getMessage\([\r|\n|\n\r]*\s*"(.*)".*\)'
        self.jspMessage = r'<fmt:message\s*key="(.*)"\s*>'
        self.jsMessage = r'Y.PI.I[\r|\n|\r\n]*\s*.getString\([\r|\n|\n\r]*\s*\'(.)\'.*\)'

    def replace_get_message(self, logger):
        fileStream = codecs.open(self.filePath, 'r', self.encoding)
        lines = fileStream.read()
        fileStream.close()
        if self.filePath.endswith('.java'):
            print self.filePath
            i18nMessage = re.findall(self.i18nMessage, lines, re.S)
            if i18nMessage:
                data_dict = self.data['messages']
                separate = '", "'
                keyList = [i[1] for i in i18nMessage]
                newList = list(set(keyList))
                lines = self.replace_lines_message(newList, lines, data_dict, separate, logger)
            getMessage = re.findall(self.getMessage, lines)
            if getMessage:
                data_dict = self.data['webui']
                separate = '", "'
                lines = self.replace_lines_message(getMessage, lines, data_dict, separate, logger)
        elif self.filePath.endswith('.jsp'):
            jspMessage = re.findall(self.jspMessage, lines)
            if jspMessage:
                data_dict = self.data['webui']
                separate = '" source="'
                lines = self.replace_lines_message(jspMessage, lines, data_dict, separate, logger)
        else:
            jsMessage = re.findall(self.jsMessage, lines)
            if jsMessage:
                data_dict = self.data['pi-i18n']
                separate = '" source="'
                lines = self.replace_lines_message(jsMessage, lines, data_dict, separate, logger)

        out = codecs.open(self.filePath, 'w', self.encoding)
        out.write(lines)
        out.close()
    
    def replace_lines_message(self, newList, lines, data_dict, separate, logger):
        replace_key = []
        for regKey in newList:
            value = data_dict.get(regKey)
            if not value:
                logger.error("key not legal, sourcePath is : {}, key is {}".format(self.filePath, regKey))
            else:
                targetValue = regKey + separate + value
                lines = lines.replace(regKey, targetValue)
                replace_key.append(regKey)
        for key in regKey:
            if key in data_dict:
                data_dict.pop(key)
        return lines


def test_get_logger():
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler("replace_messages.log")
    logger.addHandler(file1)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file1.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


if __name__ == '__main__':
    logger = test_get_logger()
    data = {"messages": {}, "webui": {}, "pi-i18n": {}}
    propreties1 = r'D:\strata\loginsight\components\commons-lib\lib\src\com\vmware\loginsight\i18n\messages.properties'
    parser1 = PropertiesParser(propreties1)
    parser1.load()
    for i in parser1._string_item_list:
        if i.key not in data["messages"]:
            data["messages"][i.key] = i.value.strip(" ").strip('"')
            
    propreties2 = r'D:\strata\loginsight\components\ui\application\src\webui.properties'
    parser2 = PropertiesParser(propreties2)
    parser2.load()
    for i in parser2._string_item_list:
        if i.key not in data["webui"]:
            data["webui"][i.key] = i.value.strip(" ").strip('"')
    
    jsPath = r'D:\strata\loginsight\components\ui\application\WebContent\js\pi-i18n\lang\pi-i18n.js'
    jsParser = JsParser(jsPath)
    jsParser.load()
    for i in jsParser._string_item_list:
        if i.key not in data["pi-i18n"]:
            data["pi-i18n"][i.key] = i.value.strip(" ").strip('"')
    
    rootdir = r"D:\strata"
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp") or filename.endswith(".js")):
                continue
            filePath = "\\".join([parent, filename])
            replace_message = ReplaceMessage(filePath, data)
            replace_message.replace_get_message(logger)