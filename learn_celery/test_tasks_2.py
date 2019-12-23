#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 21:54

from tasks import video_compress, image_compress

# 启动处理视频的worker     celery worker -Q videos --loglevel=info
print(video_compress.delay('video_name'), '===')
# 启动处理图片的worker     celery worker -Q images --loglevel=info
print(image_compress.delay('image_name'))
# print(image.delay('ghou'))