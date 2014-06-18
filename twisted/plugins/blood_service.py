from zope.interface import implements

from twisted.python import usage
from twisted.web.server import Site
from twisted.application.service import IServiceMaker, Service, MultiService
from twisted.application import strports
from twisted.plugin import IPlugin
from twisted.python.threadpool import ThreadPool

from axiom.store import Store

from bdm.resource import RootResource


class Options(usage.Options):
    optParameters = [
        ['steamkey', 'k', None, 'Steam developer API key.'],
        ['dbdir', 'd', 'blood.axiom', 'Database directory'],
        ['port', 'p', 'tcp:8090', 'Service strport description']]



class BloodDonationMachineServiceMaker(object):
    implements(IPlugin, IServiceMaker)
    tapname = 'blood'
    description = 'More blood for the blood god!'
    options = Options

    def makeService(self, options):
        s = MultiService()
        tps = ThreadPoolService()
        tps.setServiceParent(s)
        site = Site(
            RootResource(
                store=Store(options['dbdir']),
                steamKey=options['steamkey'],
                threadPool=tps.threadpool))
        strports.service(options['port'], site).setServiceParent(s)
        return s

serviceMaker = BloodDonationMachineServiceMaker()



class ThreadPoolService(Service):
    def __init__(self):
        self.threadpool = ThreadPool()


    def startService(self):
        self.threadpool.start()


    def stopService(self):
        self.threadpool.stop()
