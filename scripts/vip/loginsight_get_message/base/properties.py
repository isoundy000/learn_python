# -*- coding: utf-8 -*-
'''
Created on 8/8/2017

@author: ghou
'''
import re
from loginsight_get_message.base.parser import Parser


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