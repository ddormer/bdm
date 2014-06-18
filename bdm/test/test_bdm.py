from decimal import Decimal

from twisted.trial.unittest import TestCase

from axiom.store import Store

from bdm.ibdm import IDonation
from bdm.main import Donator, Donation


class DonatorTests(TestCase):
    """
    Tests for L{bdm.main.Donator}
    """
    def setUp(self):
        self.store = Store()
        self.donator = Donator(
            store=self.store, steamID=u'testingid')


    def test_donations(self):
        """
        Property that returns a generator for the L{Donation}s
        powered up on the L{Donator}.
        """
        donation1 = Donation(store=self.store)
        donation2 = Donation(store=self.store)
        self.donator.powerUp(donation1, IDonation)
        self.donator.powerUp(donation2, IDonation)

        donations = [donation for donation in self.donator.donations]
        self.assertItemsEqual(donations, [donation1, donation2])


    def test_addDonation(self):
        """
        Powers up a new L{Donation} item on the L{Donator}.
        """
        self.donator.addDonation(Decimal('51.23'))

        for donation in self.donator.donations:
            self.assertEqual(Decimal('51.23'), donation.amount)


    def test_getDonationAmount(self):
        """
        Returns the sum of all donations.
        """
        self.donator.addDonation(Decimal('100.5'))
        self.donator.addDonation(Decimal('50'))

        self.assertEqual(
            Decimal('150.5'),
            self.donator.getDonationAmount())


    def test_addDonationUpdateTotalAdd(self):
        """
        Adding a donation will update the total.
        """
        self.donator.addDonation(Decimal('100.5'))
        self.assertEqual(self.donator.totalAmount, Decimal('100.5'))
        self.donator.addDonation(Decimal('50'))
        self.assertEqual(self.donator.totalAmount, Decimal('150.5'))


    def test_addDonationUpdateTotalDelete(self):
        """
        Deleting a donation from the store will update the total.
        """
        d = self.donator.addDonation(Decimal('100.5'))
        self.assertEqual(self.donator.totalAmount, Decimal('100.5'))
        d.deleteFromStore()
        self.assertEqual(self.donator.totalAmount, Decimal('0'))



class DonationTests(TestCase):
    def test_installOnReference(self):
        """
        Sets the C{donator} attribute to the L{Donator} that is passed
        in.
        """
        st = Store()
        d1 = Donation(store=st)
        donator = Donator(store=st, steamID=u'testingid')

        d1.installOn(donator)
        self.assertIdentical(donator, d1.donator)
