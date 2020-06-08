#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.Log.Write import Log
import struct


class TaskData:

    def __init__(self, sock=None):
        self._from = "user"
        self._magiccode = None
        self._length = 0
        self._type = 0
        self._seq = 0
        self._data = None
        self._sock = sock
        self._result = True
        self._event = None
        self._rid = None
        self._abnormal = None
        self._fileno = None

    def Clone(self):
        newTask = TaskData(self._sock)
        newTask._magiccode = self._magiccode
        newTask._length = self._length
        newTask._type = self._type
        newTask._seq = self._seq
        newTask._data = self._data
        newTask._result = self._result
        newTask._rid = self._rid
        newTask._abnormal = self._abnormal
        newTask._fileno = self._fileno
        return newTask

    def Copy(self, task):
        self._magiccode = task._magiccode
        self._length = task._length
        self._type = task._type
        self._seq = task._seq
        self._data = task._data
        self._result = task._result
        self._rid = task._rid
        self._abnormal = task._abnormal
        self._fileno = task._fileno

    def setRid(self, rid):
        self._rid = rid

    def Rid(self):
        return self._rid

    def From(self):
        return self._from

    def setFrom(self, connectfrom):
        self._from = connectfrom

    def Socket(self):
        return self._sock

    def Type(self):
        return self._type

    def setType(self, tasktype):
        '''
        设置类型
        :param tasktype: 0表示
        :return:
        '''
        self._type = tasktype

    def Seq(self):
        return self._seq

    def setSeq(self, seq):
        self._seq = seq

    def MagicCode(self):
        return self._magiccode

    def setMagicCode(self, magiccode):
        self._magiccode = magiccode

    def Result(self):
        return self._result

    def setResult(self, result):
        self._result = result

    def ParseHead(self, headdata):
        # Log.Write("TaskData ParseHead", len(headdata), headdata)
        # 解包
        self._magiccode, self._length, self._type, self._seq = struct.unpack("!4I", headdata)
        # Log.Write("[HEAD-RECV]%d %d %d %d"%(self._type, self._seq, self._length, self._magiccode))

    def DataLen(self):
        return self._length

    def Data(self):
        return self._data

    def setData(self, data):
        self._data = data

    def setAbnormal(self, code):
        self._abnormal = code

    def Abnormal(self):
        return self._abnormal

    def MakeData(self):
        """
        加密数据
        :return:
        """
        if self.data is None:
            self._length = 0
        else:
            self._length = len(self._data)
        data = ""
        # print self._magiccode, self._length, self._type, self._seq
        # Log.Write("[HEAD-SEND]",self._type, self._seq, self._length, self._magiccode)
        data += struct.pack("!4I", self._magiccode, self._length, self._type, self._seq)
        if self._data is not None:
            data += self._data
        return data

    def fileno(self):
        if self._sock:
            return self._sock.fileno()
        else:
            return self._fileno

    def setFileno(self, fileno):
        self._fileno = fileno