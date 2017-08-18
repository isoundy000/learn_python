# -*- coding: utf-8 -*-
'''
Created on 6/9/2017

@author: ghou
'''
import re
import copy
import codecs
import os
import time
import shutil
import logging
from base.properties import PropertiesParser
from base.js import JsParser


class ReplaceMessage(object):
    encoding = 'utf-8'
    def __init__(self, file_path):
        self.filePath = file_path
        self.i18nMessage = r'I18nUtil[\r|\n|\r\n]*\s*\.(getMessage|encodeKey)\((.*?)[\r|\n|\r\n]*\s*[\r|\n|\n\r]*(\".*?\")'
        self.getMessage = r'(?<![I18nUtil|\.])getMessage\((.*?)[\r|\n|\r\n]*\s*(\".*?\")'
        self.rbacGroupDao = r'rbacGroupDAO[\r|\n|\r\n]*\s*\.createGroup\((\".*?\"),\s*(\".*?\")'
        self.jspMessage = r'(\<fmt:message\s*key\s*=\s*([\'\"])(.*?)\2)'
        self.jsMessage = r'Y\.PI\.I[\r|\n|\r\n]*\s*\.getString\([\r|\n|\r\n]*\s*([\'\"])(.*?)\1'
        self.jsCmon = r'Cmon\.resID\(([\'\"])(.*?)\1'

    def replace_get_message(self, logger, data, remove_dict):
        try:
            fileStream = codecs.open(self.filePath, 'r', self.encoding)
            lines = fileStream.read()
            fileStream.close()
        except:
            return

        if self.filePath.endswith('.java'):
            i18nMessage = re.findall(self.i18nMessage, lines)
            if i18nMessage:
                data_dict = data['messages']
                if "messages" not in remove_dict:
                    remove_dict["messages"] = []
                regPos = 2
                lines = self.replace_lines_message(i18nMessage, regPos, lines, data_dict, logger, remove_dict["messages"])
            rbacGroupDao = re.findall(self.rbacGroupDao, lines)
            rbacGroupDao = None
            if rbacGroupDao:
                data_dict = data['messages']
                if "messages" not in remove_dict:
                    remove_dict["messages"] = []
                lines = self.replace_lines_many_message(rbacGroupDao, lines, data_dict, logger, remove_dict["messages"])
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
            jsCmon = re.findall(self.jsCmon, lines)
            if jsCmon:
                data_dict = data['pi-i18n']
                if "pi-i18n" not in remove_dict:
                    remove_dict["pi-i18n"] = []
                regPos = 1
                lines = self.replace_lines_message(jsCmon, regPos, lines, data_dict, logger, remove_dict["pi-i18n"])
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
                if "'" == i[1]:
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

    def replace_lines_many_message(self, rbacGroupDao, lines, data_dict, logger, remove_list):
        replace_key = []
        for i in rbacGroupDao:
            for regKey in i:
                tmp = regKey.strip('"')
                value = data_dict.get(tmp)
                if not value:
                    logger.error("key not legal, sourcePath is : {}, key is {}".format(self.filePath, tmp))
                    continue
                if tmp in replace_key:
                    continue
                separate = ', "'
                value = value.replace('"', '\\"').replace("\\\\", "\\")
                anchor = separate[-1]
                targetValue = "".join([regKey, separate, value, anchor])
                lines = lines.replace(regKey, targetValue)
                replace_key.append(tmp)
                remove_list.append(tmp)
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
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp") or filename.endswith(".js")):
                continue
            file_path=parent  + "\\" + filename
            new_path = target_path + "\\" + file_path[3:]
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.copyfile(file_path, new_path)


if __name__ == '__main__':
    start_time = int(time.time())
    logPath = r'./log/replace_messages.log'
    if os.path.exists(logPath):
        os.remove(logPath)
    logPath1 = r'./log/not_replace_record.log'
    if os.path.exists(logPath1):
        os.remove(logPath1)
    logger = test_get_logger(logPath)
    data = {"messages": {}, "webui": {}, "pi-i18n": {}}
    parser_path = "".join([os.path.abspath('.'), os.path.sep, 'parser_file', os.path.sep])
    for fileName in os.listdir(parser_path):
        abspath =  parser_path + fileName
        fileName1 = fileName.split('.')[0]
        extension = fileName.split('.')[1]
        if fileName1 not in data.keys():
            continue
        if extension.endswith('properties'):
            parser = PropertiesParser(abspath)
            parser.load()
            for i in parser._string_item_list:
                if i.key and i.key not in data[fileName1]:
                    data[fileName1][i.key] = i.value.strip(" ")
        elif extension.endswith('js'):
            parser = JsParser(abspath)
            parser.load()
            for i in parser._string_item_list:
                if i.key and i.key not in data[fileName1]:
                    data[fileName1][i.key.strip('"')] = i.value.strip(" ")

    rootdir = r"D:\strata"
    remove_dict = {}
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not (filename.endswith(".java") or filename.endswith(".jsp") or filename.endswith(".js")):
                continue
            filePath = "\\".join([parent, filename])
            # especial method name eg: πø$7ß.java
            if parent.endswith(os.path.sep.join(['strata', 'loginsight', 'lib3rd', 'play-2.2.4', 'framework', 'test', 'integrationtest', 'app', 'controllers'])):
                continue
            replace_message = ReplaceMessage(filePath)
            replace_message.replace_get_message(logger, data, remove_dict)

    dup_key = [
        'com.vmware.loginsight.web.actions.settings.HealthActionBean.supportBundleNotFound',
        'com.vmware.loginsight.web.actions.settings.HealthActionBean.queued',
        'com.vmware.loginsight.web.actions.settings.HealthActionBean.failedLoadQueries',
        'com.vmware.loginsight.web.actions.settings.HealthActionBean.completed'
    ]
    if 'messages' in remove_dict:
        remove_dict['messages'].extend(dup_key)

    copyData = copy.deepcopy(data)
    for i, v in remove_dict.iteritems():
        dupList = list(set(v))
        for key in dupList:
            if key in copyData[i]:
                copyData[i].pop(key)

    not_replace_record = open(r'./log/not_replace_record.log', 'w')
    for key, value in copyData.iteritems():
        not_replace_record.write('{}============================================\n'.format(key))
        for k, v in value.iteritems():
            try:
                not_replace_record.write('{}, \t\t\t {}\n'.format(k, v))
            except:
                pass

    not_replace_record.close()
    end_time = int(time.time())
    total = len(data['messages']) + len(data['webui']) + len(data['pi-i18n'])
    mod = len(copyData['messages']) + len(copyData['webui']) + len(copyData['pi-i18n'])
    print 'total string is %s, replace string is %s, mod is %s,  replace string cost time is %ss' % (total, (total - mod), mod, (end_time - start_time))