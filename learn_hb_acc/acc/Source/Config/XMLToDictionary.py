#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'ghou'

# 引入XML解析器，将尝试是否有c实现方式
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def ConvertXMLElementToDictionaryValue(elemroot):
    temp_node_dict = dict()
    for elem in elemroot:
        if elem.getchildren() != []:
            temp_node_dict[elem.tag] = ConvertXMLElementToDictionaryValue(elem)
        else:
            temp_node_dict[elem.tag] = elem.text or ""
    return temp_node_dict


def CovertXMLFileToDictionary(xml_file_path):
    """解析xml文件将所有的数据拼装成全局字典
    Args:
        xml_file_path:xml文件路径
    Returns:
         字典,例如:
         {'server':{'listenip':'0.0.0.0', 'listenport':'6000'}}
    """
    tree = ET.ElementTree(file=xml_file_path)
    treeroot = tree.getroot()
    return {treeroot.tag: ConvertXMLElementToDictionaryValue(treeroot)}