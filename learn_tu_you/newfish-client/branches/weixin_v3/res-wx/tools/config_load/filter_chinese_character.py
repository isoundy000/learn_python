# -*- coding=utf-8 -*-
"""
Created by lichen on 17/5/2.
从前后端代码、配置等文件中找到中文字符并导出到outFile
作用：用于客户端生成特殊字体库ttf文件
"""

import sys

outFile = "chinese_character"

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u"\u4e00" and uchar <= u"\u9fa5":
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u"\u0030" and uchar <= u"\u0039":
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u"\u0041" and uchar <= u"\u005a") or (uchar >= u"\u0061" and uchar <= u"\u007a"):
        return True
    else:
        return False


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


def B2Q(uchar):
    """半角转全角"""
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7e:  # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return unichr(inside_code)


def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)


def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])


def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()


def string2List(ustring):
    """将ustring按照中文分割"""
    retList = []
    for uchar in ustring:
        if is_chinese(uchar):
            if len(uchar) == 0:
                continue
            else:
                retList.append("".join(uchar))

    return retList

def __encode(ustring):
    return ustring.encode("utf-8")

def error(args):
    raise args

def isIgnorePath(path):
    ignorePaths = ["robot", "idCard", "iploc", "game/6", "game5"]
    for _p in ignorePaths:
        if _p in path:
            print path
            return True
    return False

if __name__ == "__main__":
    # ustring = u"捕获红鹦鹉鱼"
    # ret = string2List(ustring)
    # print ret
    # print map(__encode, ret)
    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        ServerPath = "/../../../../../../server"
        ConfigPath = ServerPath + "/newfish-py/wechat/xxfish_release/config37/game"
    elif len(sys.argv) > 1 and sys.argv[1] == "-t":
        ServerPath = "/../../../../../../../gameServer"
        ConfigPath = ServerPath + "/newfish-py/wechat/xxfish_release/config37/game"
    elif len(sys.argv) > 1 and sys.argv[1] == "-k":
        ServerPath = "/../../../../../../../game_server"
        ConfigPath = ServerPath + "/xxfish_release/config37/game"
    else:
        ServerPath = "/../../../../../../../gameServer/hall37"
        ConfigPath = ServerPath + "/newfish-py/wx_superboss/xxfish_dev/config37/game"

    import os  
    import sys  
    reload(sys)  
    sys.setdefaultencoding("utf8")
    csbDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + "/../../ccs/cocosstudio/games/newfish/csb", onerror=error)
    iosCsbDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + "/../../../res-ios/ccs/cocosstudio/games/newfish/csb", onerror=error)
    configSrcDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + "/../../newfish/config_src", onerror=error)
    iosConfigSrcDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + "/../../../res-ios/newfish/config_src", onerror=error)
    serverCodeDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + ServerPath + "/newfish-py/wx_superboss/trunk/hall37-newfish/src/newfish", onerror=error)
    serverConfigDir = os.walk(os.path.split(os.path.realpath(__file__))[0] + ConfigPath, onerror=error)
    outFile = os.path.split(os.path.realpath(__file__))[0] + "/" + outFile
    pointCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:\"?></.,;'][=-`0123456789～！＠＃＄％＾＆＊（）＿＋｛｝｜：＂？＞＜／．，；＇］［＝－｀￥……（）——“”：《》？/。，‘’；、】【·"
    # pointCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!！@＠#＃$＄%％^＾&＆(（)）（）_＿+＋-－*/>＞<＜=＝:;\"\",.`~～?[]{}| ……：，。“”‘’'；！!【】｛｝|、《》?？￥"
    fileList = []
    for path, d, filelist in list(csbDir) + list(iosCsbDir):  
        for filename in filelist:  
            filePath = os.path.join(path, filename)
            if ".csd" in filePath:
                fileList.append(filePath)
    for path, d, filelist in list(configSrcDir) + list(iosConfigSrcDir):  
        for filename in filelist:  
            filePath = os.path.join(path, filename)
            fileList.append(filePath)
    for path, d, filelist in serverCodeDir:  
        for filename in filelist:  
            filePath = os.path.join(path, filename)
            if ".py" in filePath:
                fileList.append(filePath)
    for path, d, filelist in serverConfigDir:
        for filename in filelist:  
            filePath = os.path.join(path, filename)
            if isIgnorePath(path):
                continue
            if ".json" in filePath:
                fileList.append(filePath)
    allChineseCharacter = []
    for file in fileList:
        print file
        if str.split(file, "/")[-1][0] == ".":
            print "!!! ignore " + file
            continue
        fHandle = open(file, "r")
        lines = fHandle.readlines()
        for line in lines:
            ret = string2List(unicode(line))
            allChineseCharacter.extend(ret)
        fHandle.close()
    allChineseCharacter = list(set(allChineseCharacter))
    fHandle = open(outFile, "w+")
    for chineseCharacter in allChineseCharacter:
        fHandle.write("%s" % chineseCharacter)
    for character in pointCharacters:
        fHandle.write("%s" % character)
    fHandle.close



