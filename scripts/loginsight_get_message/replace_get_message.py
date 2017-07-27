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
import shutil
import copy
from time import sleep


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
                

class ReplaceMessage(object):
    encoding = 'utf-8'
    def __init__(self, file_path):
        self.filePath = file_path
        self.i18nMessage = r'I18nUtil[\r|\n|\r\n]*\s*\.(getMessage|encodeKey)\((.*?)[\r|\n|\r\n]*\s*[\r|\n|\n\r]*(\".*?\")'
        self.getMessage = r'(?<![I18nUtil|\.])getMessage\((.*?)[\r|\n|\r\n]*\s*(\".*?\")'
        self.jspMessage = r'(\<fmt:message\s*key\s*=\s*([\'\"])(.*?)\2)'
        self.jsMessage = r'Y\.PI\.I[\r|\n|\r\n]*\s*\.getString\([\r|\n|\r\n]*\s*([\'\"])(.*?)\1'

    def replace_get_message(self, logger, data, remove_dict):
        try:
            fileStream = codecs.open(self.filePath, 'r', self.encoding)
            lines = fileStream.read()
            fileStream.close()
        except:
            filename = os.path.basename(self.filePath)
            newFile = r'D:\vip_testdata\except\\' + filename
            shutil.copyfile(self.filePath, newFile)
            return

        if self.filePath.endswith('.java'):
            i18nMessage = re.findall(self.i18nMessage, lines)
            if i18nMessage:
                data_dict = data['messages']
                if "messages" not in remove_dict:
                    remove_dict["messages"] = []
                regPos = 2
                lines = self.replace_lines_message(i18nMessage, regPos, lines, data_dict, logger, remove_dict["messages"])
            getMessage = re.findall(self.getMessage, lines)
            if getMessage:
                data_dict = data['webui']
                if "webui" not in remove_dict:
                    remove_dict["webui"] = []
                regPos = 1
                lines = self.replace_lines_message(getMessage, regPos, lines, data_dict, logger, remove_dict["webui"])
        elif self.filePath.endswith('.jsp'):
            jspMessage = re.findall(self.jspMessage, lines)
            if jspMessage:
                data_dict = data['webui']
                if "webui" not in remove_dict:
                    remove_dict["webui"] = []
                regPos = 2
                lines = self.replace_lines_message(jspMessage, regPos, lines, data_dict, logger, remove_dict["webui"])
        else:
            jsMessage = re.findall(self.jsMessage, lines)
            if jsMessage:
                data_dict = data['pi-i18n']
                if "pi-i18n" not in remove_dict:
                    remove_dict["pi-i18n"] = []
                regPos = 1
                lines = self.replace_lines_message(jsMessage, regPos, lines, data_dict, logger, remove_dict["pi-i18n"])

        out = codecs.open(self.filePath, 'w', self.encoding)
        out.write(lines)
        out.close()

    def replace_lines_message(self, regularRule, regPos, lines, data_dict, logger, remove_list):
        replace_key = []
        for i in regularRule:
            regKey = i[regPos]
            tmpValue = None
            tmpKey = None
            if self.filePath.endswith('.jsp') and "${beanClass}" in regKey:
                endString = regKey.split("}")[-1]
                num = 0
                for key, value in data_dict.iteritems():
                    if endString and key.endswith(endString):
                        tmpKey = key
                        num += 1
                if num == 1:
                    tmpValue = data_dict.get(tmpKey)
            if self.filePath.endswith('java'):
                tmp = regKey.strip('"')
                value = data_dict.get(tmp)
            else:
                value = data_dict.get(regKey)
            if not value:
                value = tmpValue
            if not value:
                logger.error("key not legal, sourcePath is : {}, key is {}".format(self.filePath, regKey.strip('"')))
                continue
            if regKey.strip('"') in replace_key:
                continue
            if self.filePath.endswith('.java'):
                separate = ', "'
                value = value.replace('"', '\\"').replace("\\\\", "\\")
                anchor = separate[-1]
                targetValue = "".join([regKey, separate, value, anchor])
                lines = lines.replace(regKey, targetValue)
            elif self.filePath.endswith('.jsp'):
                separate = ' source="'
                if "'" == i[0]:
                    separate = " source='"
                    value = value.replace("'", "\\'").replace("\\\\", "\\")
                else:
                    value = value.replace('"', '\\"').replace("\\\\", "\\")
                targetValue = "".join([i[0], separate, value, separate[-1]])
                lines = lines.replace(i[0], targetValue)
            elif self.filePath.endswith('js'):
                separate = '", "'
                if "'" == i[0]:
                    separate = "', '"
                    value = value.replace("'", "\\'").replace("\\\\", "\\")
                else:
                    value = value.replace('"', '\\"').replace("\\\\", "\\")
                anchor = separate[0]
                targetValue = "".join([regKey, separate, value, anchor])
                lines = lines.replace(regKey + anchor, targetValue)
            replace_key.append(regKey.strip('"'))
            if "${beanClass}" in regKey:
                remove_list.append(tmpKey)
            else:
                remove_list.append(regKey.strip('"'))
        return lines


def test_get_logger(logPath):
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler(logPath)
    logger.addHandler(file1)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file1.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def copy_file(rootdir, target_path):
    for parent,dirnames,filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp") or filename.endswith(".js")):
                continue
            file_path=parent  + "\\" + filename
            new_path = target_path + "\\" + file_path[3:]
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.copyfile(file_path, new_path)


if __name__ == '__main__':
    import time
    start_time = int(time.time())
    logPath = r'./replace_messages.log'
    if os.path.exists(logPath):
        try:
            os.remove(logPath)
        except:
            pass
    logger = test_get_logger(logPath)

    data = {"messages": {}, "webui": {}, "pi-i18n": {}}
    propreties1 = r'D:\strata\loginsight\components\commons-lib\lib\src\com\vmware\loginsight\i18n\messages.properties'
    parser1 = PropertiesParser(propreties1)
    parser1.load()
    for i in parser1._string_item_list:
        if i.key and i.key not in data["messages"]:
            data["messages"][i.key] = i.value.strip(" ")

    propreties2 = r'D:\strata\loginsight\components\ui\application\src\webui.properties'
    parser2 = PropertiesParser(propreties2)
    parser2.load()
    for i in parser2._string_item_list:
        if i.key and i.key not in data["webui"]:
            data["webui"][i.key] = i.value.strip(" ")

    jsPath = r'D:\strata\loginsight\components\ui\application\WebContent\js\pi-i18n\lang\pi-i18n.js'
    jsParser = JsParser(jsPath)
    jsParser.load()
    for i in jsParser._string_item_list:
        if i.key and i.key not in data["pi-i18n"]:
            data["pi-i18n"][i.key.strip('"')] = i.value.strip(" ")

    skip_path_list = [
        'D:\strata\loginsight\lib3rd\play-2.2.4\framework\test\integrationtest\app\controllers\πø$7ß.java',
    ]

    print 'messages', len(data['messages'])
    print 'webui', len(data['webui'])
    print 'pi-i18n', len(data['pi-i18n'])

    rootdir = r"D:\vip_testdata\test_source_file"
    remove_dict = {}
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp") or filename.endswith(".js")):
                continue
            filePath = "\\".join([parent, filename])
            if filePath in skip_path_list:
                continue
            replace_message = ReplaceMessage(filePath)
            replace_message.replace_get_message(logger, data, remove_dict)

    copyData = copy.deepcopy(data)
    for i, v in remove_dict.iteritems():
        dupList = list(set(v))
        for key in dupList:
            if key in copyData[i]:
                copyData[i].pop(key)

    print 'messages_mod', len(copyData['messages'])
    print 'webui_mod', len(copyData['webui'])
    print 'pi-i18n_mod', len(copyData['pi-i18n'])
    print len(data['messages']) + len(data['webui']) + len(data['pi-i18n']) - len(copyData['messages']) - len(copyData['webui']) - len(copyData['pi-i18n'])
    not_replace_record = open(r'./not_replace_record.log', 'w')
    for key, value in copyData.iteritems():
        not_replace_record.write('{}============================================\n'.format(key))
        for k, v in value.iteritems():
            try:
                not_replace_record.write('{}, \t\t\t {}\n'.format(k, v))
            except:
                pass
    not_replace_record.close()
    end_time = int(time.time())
    print end_time - start_time