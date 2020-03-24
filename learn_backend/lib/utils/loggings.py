#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import os
import logging

import settings


class LoggingUtil(object):
    """ 日志工具类

    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __init__(self, path, file_name):
        self.new_file_path = self.file_path(path)
        self.file_name = os.path.join(self.new_file_path, file_name)
        self.check_path()
        self.logger = logging.getLogger(os.path.join(path, file_name))
        self.fhandler = logging.FileHandler(self.file_name)
        self.fhandler.setLevel(logging.DEBUG)
        self.fhandler.setFormatter(self.formatter)
        self.logger.addHandler(self.fhandler)
        self.logger.setLevel(logging.DEBUG)

    def file_path(self, path):
        """ 文件的路径

        :return:
        """
        return os.path.join(settings.BASE_ROOT, 'logs', path)

    def check_path(self):
        """ 检查路径

        :return:
        """
        if not os.path.exists(self.new_file_path):
            os.makedirs(self.new_file_path)

    def add_msg(self, sort, msg, *args, **kwargs):
        """ 添加信息

        :param sort: 类型
        :param msg: 信息
        :return:
        """
        if isinstance(sort, int):
            name = logging._levelNames.get(sort)
        else:
            name = sort
        name = name.lower()
        if hasattr(self.logger, name):
            func = getattr(self.logger, name)
            func(msg, *args, **kwargs)
            return True
        else:
            return False

    def into(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)


class LoggingCache(object):
    """ 日志缓存类

    """
    logging_pool = {}

    @classmethod
    def get_logging_with_filename(cls, path, filename, logging_class=LoggingUtil):
        """ 通过文件名获取logging

        :param path:
        :param filename:
        :return:
        """
        f = os.path.join(path, filename)
        logging_util = cls.logging_pool.get(f)
        if logging_util:
            return logging_util

        logging_util = logging_class(path, filename)

        cls.logging_pool[f] = logging_util

        return logging_util