from zope.interface import implements

from twisted.python import usage
from twisted.web.server import Site
from twisted.application.service import IServiceMaker
from twisted.application import strports
from twisted.plugin import IPlugin

from axiom.store import Store

from bdm.resource import RootResource


class Options(usage.Options):
    optParameters = [
        ['steamkey', 'k', None, 'Steam developer API key.'],
        ['dbdir', 'd', 'blood.axiom', 'Database directory'],
        ['port', 'p', 'tcp:8080', 'Service strport description']]



class BloodDonationMachineServiceMaker(object):
    implements(IPlugin, IServiceMaker)
    tapname = 'blood'
    description = 'More blood for the blood god!'
    options = Options

    def makeService(self, options):
        site = Site(
            RootResource(
                store=Store(options['dbdir']),
                steamKey=options['steamkey']))
        return strports.service(options['port'], site)

serviceMaker = BloodDonationMachineServiceMaker()
