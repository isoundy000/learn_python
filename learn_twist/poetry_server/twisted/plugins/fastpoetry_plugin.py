from twisted.python import usage
from zope.interface import implements
from twisted.application import service
from twisted.application import internet
from twisted.plugin import IPlugin
from learn_twist.poetry_server.poetry_server import PoetryService, PoetryFactory


class Options(usage.Options):

    optParameters = [
        ['port', 'p', 9999, 'The port number to listen on.'],
        ['poem', None, None, 'The file containing the poem.'],
        ['iface', None, 'localhost', 'The interface to listen on.'],
    ]


class PoetryServiceMaker(object):

    implements(service.IServiceMaker, IPlugin)

    tapname = "fastpoetry"
    description = "A fast poetry service"
    options = Options

    def makeService(self, options):
        top_service = service.MultiService()

        poetry_server = PoetryService(options['poem'])
        top_service.setServiceParent(poetry_server)

        factory = PoetryFactory(poetry_server)
        tcp_service = internet.TCPServer(int(options['port']), factory, interface=options['iface'])
        tcp_service.setServiceParent(top_service)

        return top_service


service_maker = PoetryServiceMaker()

# twistd fastpoetry --help
# twistd fastpoetry --port 10000 --poem poetry/ecstasy.txt
# kill `cat twisted.pid`