import json

from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred
from twisted.web.client import getPage
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET

from axiom.errors import ItemNotFound

from bdm.main import Donation, Donator
from bdm.error import BloodyError, PaypalError


class RootResource(Resource):
    def __init__(self, store):
        Resource.__init__(self)
        self.putChild("api", DonationAPI(store))
        self.putChild("paypal", PayPal(store))



class PayPal(Resource):
    isLeaf = True

    def __init__(self, store):
        self.store = store
        Resource.__init__(self)


    def verify(self, request):
        """
        Verify PayPal IPN data.
        """
        paypalURL = 'https://www.paypal.com/cgi-bin/webscr'

        def _cb(response):
            if response == 'INVALID':
                raise PaypalError(
                    'IPN data invalid. txn_id: %s', (data['txn_id']))

            elif response == 'VERIFIED':
                return None

            else:
                raise PaypalError('Unrecognized verification response: %s', (response,))

        data = request.content.read()
        params = '?cmd=_notify-validate&' + data

        d = getPage(paypalURL+params, method='POST')
        d.addCallback(_cb)
        return d


    def process(self, data):
        paymentStatus = data['payment_status'].lower()
        steamID = data.get('custom', ['Anonymous'])[0]
        txn_id = data['txn_id'][0]
        ipn_id = data['ipn_track_id'][0]
        amount = data.get('settle_amount', [data['mc_gross']])[0]

        if paymentStatus == 'completed':
            donator = self.store.findOrCreate(Donator, steamID=steamID)
            donator.addDonation(amount, txn_id=txn_id, ipn_id=ipn_id)

        if paymentStatus == 'refunded':
            donation = self.store.findUnique(
                Donation, txn_id=data['parent_txn_id'][0])
            donation.deleteFromStore()

        if paymentStatus == 'canceled_reversal':
            pass

        if paymentStatus == 'reversed':
            pass



    def render_POST(self, request):
        """
        Recieve PayPal callback.
        """
        print request.args

        d = self.verify(request)
        d.addCallback(self.process, request.args)
        return ''



class DonationAPI(Resource):
    isLeaf = True

    def __init__(self, store):
        self.store = store
        Resource.__init__(self)


    def render(self, request):
        d = maybeDeferred(Resource.render, self, request)
        d.addBoth(writeJSON, request)
        return NOT_DONE_YET


    def recent(self, limit):
        """
        Retrieve a list of recent donations.
        """
        donations = []
        for donation in self.store.query(
            Donation, limit=limit, sort=Donation.date.descending):
            donations.append(donation.toDict())
        return donations


    def steamID(self, steamid):
        try:
            donator = self.store.findUnique(
                Donator, Donator.steamID == unicode(steamid))
        except ItemNotFound:
            raise BloodyError("SteamID '%s' not found." % (steamid,))

        donations = []
        for donation in donator.donations:
            donations.append(donation.toDict())
        return donations


    def render_GET(self, request):
        if not request.postpath:
            return "maybe sam dox"

        name = request.postpath[0]
        if name == u'steamid':
            if len(request.postpath[1]) <= 1 or request.postpath[1] is None:
                raise Exception("No SteamID provided.")
            return self.steamID(request.postpath[1])

        if name == u'recent':
            try:
                limit = request.postpath[1]
            except IndexError:
                limit = 10
            return self.recent(limit)

        return NoResource('')



def writeJSON(d, request):
    """
    Uses json.dumps on the result and writes it to the request, with
    support for Failures.
    """
    request.setHeader('content-type', 'application/json')

    if isinstance(d, Failure):
        if d.check(BloodyError):
            request.setResponseCode(500)
            if hasattr(d.value, 'errorCode'):
                if d.value.errorCode:
                    request.setResponseCode(d.value.errorCode)
            request.write(json.dumps({'error': d.value.message}))
        else:
            d.raiseException()
    else:
        request.write(json.dumps(d))
    request.finish()
