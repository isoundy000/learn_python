# -*- encoding: utf-8 -*-
'''
Created on 2019年11月12日

@author: houguangdong
'''

from twisted.application import internet
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.python import usage
from zope.interface import implements

from learn_twist.poetry_server.twisted.echo import EchoFactory

import sys
sys.path.append('/Users/houguangdong/Workspace/learn_python/learn_twist/')


class Options(usage.Options):

    optParameters = [["port", "p", 8000, "The port number to listen on."]]


class EchoServiceMaker(object):

    implements(IServiceMaker, IPlugin)
    tapname = "echo"
    description = "A TCP-based echo server."
    options = Options


    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        return internet.TCPServer(int(options["port"]), EchoFactory())


serviceMaker = EchoServiceMaker()