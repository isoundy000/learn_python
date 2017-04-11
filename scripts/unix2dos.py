'''
Created on 10/25/2016
@author: ghou
'''

import sys
import os
import codecs
from subprocess import PIPE,Popen


argv = sys.argv
if len(argv) != 3:
    print 'argv error:', argv
    print 'run format python unix2dos (True or False)'
    print 'True is unix2dos, False is dos2unix'
    sys.exit()


def perform_cmd(command,std_out=PIPE, is_shell=True):
    '''perform the cmd synchronously and return the status and output of cmd'''
    process = Popen(args=command, stdout=std_out,stderr=PIPE, shell=is_shell)
    output, errorOutput = process.communicate()
    returnCode = process.returncode
    return output, errorOutput,returnCode

    
def main():
    path = argv[1]
    is_flag = argv[2]
    if is_flag == 'True':
        flag = True
    elif is_flag == 'False':
        flag = False
    else:
        return
    if not os.path.exists(path):
        return
    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    if os.path.isdir(path):
        for parent, dirNames, fileNames in os.walk(path):
            for fileName in fileNames:
                targetPath = "%stargetU2W%s" % ((CUR_PATH + os.path.sep), (os.path.sep + parent))
                if not os.path.exists(targetPath):
                    os.makedirs(targetPath)
                targetPathNew = targetPath + os.path.sep + fileName
                sourcePathNew = parent + os.path.sep + fileName
                if flag:
                    cmd = "unix2dos -k -n %s %s" % (sourcePathNew, targetPathNew)
                else:
                    cmd = "dos2unix -k -n %s %s" % (sourcePathNew, targetPathNew)
                out, outPut, returnCode = perform_cmd(cmd)
                if returnCode < 0:
                    print "Error occurred %s" % (parent + fileName)
                else:
                    print "Output for this cmd: \n%s" % outPut
    print 'target file path is %s/targetU2W' % CUR_PATH
    
   
if __name__ == "__main__":
    main()