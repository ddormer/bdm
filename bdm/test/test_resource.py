from twisted.trial.unittest import TestCase
from twisted.python.threadpool import ThreadPool

from axiom.store import Store

from valve.source.a2s import NoResponseError

from bdm.resource import DonationAPI


class TestDonationAPI(TestCase):
    """
    Tests for L{bdm.resource.DonationAPI}.
    """
    def setUp(self):
        self.store = Store()
        self.threadPool = ThreadPool()
        self.threadPool.start()
        self.api = DonationAPI(self.store, 'nothing', self.threadPool)


    def tearDown(self):
        self.threadPool.stop()


    def test_serverStatsSuccess(self):
        """
        L{serverStats} returns the expected dictionary results when passed a
        valid [IP, PORT].
        """
        def _cb(result):
            expected = [{'server_name': 'Test Server',
                         'map': 'testmap',
                         'player_count': 8,
                         'max_players': 16,
                         'online': True,
                         'location': 'ZA'}]
            self.assertEqual(expected, result)

        servers = [['1.1.1.1', 27015, "ZA"]]
        return self.api.serverStats(servers, querier=MockServerQuerier).addCallback(_cb)


    def test_serverStatsOffline(self):
        """
        No exception is raised if the server is inaccesable, and the online
        status is set to C{False}
        """
        def _cb(result):
            expected = [{'server_name': '1.1.1.2', 'online': False, 'location':'ZA'}]
            self.assertEqual(expected, result)

        servers = [['1.1.1.2', 27015, "ZA"]]
        return self.api.serverStats(servers, querier=MockServerQuerier).addCallback(_cb)



class MockServerQuerier(object):
    onlineServers = ['1.1.1.1']

    def __init__(self, address, timeout=5.0):
        self.address = address[0]


    def get_info(self):
        if self.address in self.onlineServers:
            return {
                'server_name': 'Test Server',
                'map': 'testmap',
                'player_count': 8,
                'max_players': 16}
        raise NoResponseError("Server not found")
