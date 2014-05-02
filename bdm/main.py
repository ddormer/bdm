from decimal import Decimal

from zope.interface import implements

from epsilon.extime import Time

from axiom.item import Item
from axiom.attributes import text, point2decimal, timestamp, reference

from bdm.ibdm import IDonator, IDonation


class Donator(Item):
    implements(IDonator)

    steamID = text(allowNone=True, default=u'Anonymous')

    @property
    def donations(self):
        return self.powerupsFor(IDonation)


    def getDonationAmount(self):
        return sum(donation.amount for donation in self.donations)


    def addDonation(self, amount):
        Donation(store=self.store, amount=amount).installOn(self)



class Donation(Item):
    implements(IDonation)

    amount = point2decimal(allowNone=False, default=Decimal('0'))
    date = timestamp(defaultFactory=lambda: Time(), indexed=True)
    donator = reference()

    def installOn(self, donator):
        self.donator = donator
        donator.powerUp(self, IDonation)



def donationToDict(donation):
    return {
        'donator': getattr(getattr(donation, 'donator', None), 'steamID', None),
        'amount': str(donation.amount),
        'date': donation.date.asPOSIXTimestamp()}
