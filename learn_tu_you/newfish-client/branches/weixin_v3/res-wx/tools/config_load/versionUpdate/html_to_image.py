# -*- coding=utf-8 -*-
"""
Created by lichen on 19/6/12.
"""

import os

if __name__ == "__main__":
    currDir = os.walk(os.path.split(os.path.realpath(__file__))[0])
    for path, d, filelist in currDir:  
        for filename in filelist:  
            filePath = os.path.join(path, filename)
            if ".html" in filePath:
                os.system("wkhtmltoimage --quality 100 --width 659 %s %s" % (filePath, filePath.replace(".html", ".jpg")))
                exit()
