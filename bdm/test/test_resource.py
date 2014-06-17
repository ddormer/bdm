from twisted.trial.unittest import TestCase

from axiom.store import Store

from bdm.main import Donation
from bdm.resource import DonationAPI


class TestDonationAPI(TestCase):
    """
    Tests for L{bdm.resource.DonationAPI}.
    """
    def setUp(self):
        self.store = Store()
        self.api = DonationAPI(self.store, 'nothing')


    def tearDown(self):
        self.api.threadPool.stope()


    def test_serverStats(self):
        def _cb(result):
            self.assertEqual([{
                'server_name': 'Test Server',
                'map': 'testmap',
                'player_count': 8,
                'max_players': 16
            }], result)

        servers = [['1.1.1.1', 27015]]

        return self.api.serverStats(servers, querier=MockServerQuerier).addCallback(_cb)



class MockServerQuerier(object):
    def __init__(self, address, timeout=5.0):
        pass


    def get_info(self):
        return {
            'server_name': 'Test Server',
            'map': 'testmap',
            'player_count': 8,
            'max_players': 16
        }
