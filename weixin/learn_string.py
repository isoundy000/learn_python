# -*- encoding: utf-8 -*-
'''
Created on 2017年9月3日

@author: houguangdong
'''
import string
print string.capitalize('abcd')
print string.center('abcd', 8)
print string.count('aaaabb', 'b')
# 解码字符串
print 'abcd'.decode(encoding='UTF-8', errors='strict')
# 编码字符串
print 'abcd'.encode(encoding='UTF-8', errors='strict')
print 'abcd'.find('f')
print 'abcd'.rfind('b')
print 'abcd'.index('a')    # 'abcd'.index('f')
print 'abcd'.rindex('d')
# 至少有一个字符并且都是字母或者数字则返回True
print 'abcd22'.isalnum()
# 至少有一个字符并且都是字母则返回True
print 'abcd'.isalpha()
print '1234'.isdigit()
print 'ABCD'.islower()
print 'abcd'.isupper()
print '   '.isspace()
# 标题化的(单词首字母大写)则返回True
print 'Abcd'.istitle()
print 'ABCD'.title()
# 左对齐 用空格填充
print 'abcd'.ljust(8)
print 'abcd'.rjust(8)
# 用fff切分成三个值
print 'abcd'.partition('fff')
print 'abcd'.rpartition('fff')
print 'abcd'.replace('a', 'e')
print 'abcd'.split('b')
# 按照行分割 返回一个包含各行作为元素的列表
print 'abcd\nefg'.splitlines()
print 'abcd'.zfill(8)

# 字符串变量
# 'a-z'
print string.ascii_lowercase
# 'A-Z'
print string.ascii_uppercase
print string.ascii_letters
print string.digits
print string.hexdigits
print string.letters
print string.lowercase
print string.octdigits
print string.punctuation
print '111111'
print string.printable
print string.uppercase
print '222222', string.whitespace, '333333'

# 字符串模板
from string import Template
s = Template('$who like $what')
print s.substitute(who='i', what='python')
print s.safe_substitute(who='i')
print Template('${who}LikePython').substitute(who='i')

template_text = ''' Delimiter : $de Replaced:
%with_underscore Ingored: %notunderscored'''

d = {
    'de': 'not replaced',
    'with_underscore': 'replaced',
    'notunderscored': 'not replaced'
}


class MyTemplate(string.Template):
    # 重写模板 定界符(delimiter)为"%", 替换模式(idpattern)必须包含下划线(_)
    delimiter = '%'
    idpattern = '[a-z]+_[a-z]+'

print string.Template(template_text).safe_substitute(d) # 采用原来的Template渲染
print MyTemplate(template_text).safe_substitute(d) # 使用重写后的MyTemplate渲染

# 字符串技巧
a = '12345'
print a[::-1]
# join 比 + 更快
# 字符串分割
import re
s = '1234567890'
print re.findall(r'.{1,3}', s)
# 使用()括号生成字符串
sql = ('SELECT count() FROM table'
       'WHERE id = "10"'
       'GROUP BY sex'
)
print sql
# 5 将print的字符串写到文件
# 将hello world写入文件somefile.txt
print >> open('somefile.txt', "w+"), 'Hello world'
