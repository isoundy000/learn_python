'''
Created on 10/24/2016

@author: ghou
'''
import os
import sys
import codecs

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.join(CUR_PATH, "..")
sys.path.insert(0, ROOT_PATH)

from convert.encoding import EncodingConverter
from base import PostHandlerConstants as CON


argv = sys.argv
if len(argv) != 3:
    print 'argv error:', argv
    print 'run format: python uft_8_sig2utf_8.py encoding.lis (True or False)'
    print 'True is utf-8-sig to utf-8. False is utf-8 to utf-8-sig'
    sys.exit()


def encode_converter(filePath, fileRoot, flag, successCount):
    """
    encode converter 
    params: filePath 
    flag: flag is True, utf-8-sig to utf-8. flag is False utf-8 to utf-8-sig
    """
    if flag:
        # utf_8_sig to utf-8
        dictNew = {
            CON.ENCODING: 'utf-8-sig',     # UTF-8 with Signature
            CON.TARGET_ENCODING: 'utf-8',  # UTF-8 without Signature
        }
    else:
        # utf-8 to utf_8_sig
        dictNew = {
            CON.ENCODING: 'utf-8',
            CON.TARGET_ENCODING: 'utf-8-sig',
        }

    sourcePath = fileRoot + 'source' + os.path.sep + filePath 
    targetPath = fileRoot + 'target' + os.path.sep + filePath
    if not os.path.exists(sourcePath):
        print 'file is not exists ' + filePath
        return successCount

    converter = EncodingConverter(sourcePath, dictNew, targetPath)
    converter.run()
    successCount += 1
    print 'file is converter success ' + filePath
    return successCount
    
    
def main():
    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    fileRoot = CUR_PATH + os.path.sep
#     files = fileRoot + 'encoding.lis'
#     flag = False
    files = argv[1]
    isConver = argv[2]
    if isConver == 'True':
        flag = True
        print 'current operation is uft-8-sig to utf-8'
    else:
        flag = False
        print 'current operation is utf-8 to uft-8-sig'
        
    fileStream = codecs.open(files, 'r', 'utf-8')
    lines = fileStream.readlines()
    successCount = 0
    for line in lines:
        if " " not in line:
            continue
        encoding, filePath = line.split(" ", 1)
        filePath = filePath.strip()
        if encoding.strip() not in ['utf-8-sig', 'utf_8_sig']:
            continue
        successCount = encode_converter(filePath, fileRoot, flag, successCount)
    print 'total success count is ' + str(successCount)


if __name__ == "__main__":
    main()