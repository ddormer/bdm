from twisted.trial.unittest import TestCase

from axiom.store import Store

from bdm.main import Donation
from bdm.resource import DonationAPI


class TestDonationAPI(TestCase):
    """
    Tests for L{bdm.resource.DonationAPI}.
    """
