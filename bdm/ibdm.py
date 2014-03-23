from zope.interface import Interface, Attribute


class IDonator(Interface):
    """
    A person who donated.
    """
    steamID = Attribute("The donator's SteamID.")

    def donations():
        """
        A generator that retrieves the L{IDonation}(s) that belong to
        this donator.
        """

    def getDonationAmount():
        """
        Retrieve the total amount of money donated.
        """

    def addDonation(amount):
        """
        Powers up a new donation on the L{IDonator}.

        @type amount: L{Decimal}
        @param amount: The donation amount in USD.
        """



class IDonation(Interface):
    """
    A monetary donation.
    """
    amount = Attribute("The amount of USD donated.")
    date = Attribute("The date at which the donation was made.")
    donator = Attribute("The donator that the donation belongs to.")
