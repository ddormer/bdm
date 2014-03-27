import json

from twisted.internet.defer import maybeDeferred
from twisted.web import http
from twisted.web.client import getPage
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET

from axiom.errors import ItemNotFound

from bdm.main import Donation, Donator
from bdm.error import BloodyError, PaypalError
from bdm.constants import CODE


def _writeJSONResponse(result, request, code=CODE.SUCCESS, status=http.OK):
    """
    Serializes C{result} to JSON and writes it to C{request}.

    @param result: The content to be serialized and written to the request.
    @type result: An object accepted by json.dumps.

    @param request: The request object to write JSON to.
    @type request: L{twisted.web.server.Request}

    @param code: A code to include in the JSON response.
    @type code: C{int}

    @param status: The HTTP status the response will have.
    @type status: C{int}
    """
    response = {
        u'code': code.value,
        u'result': result}
    request.setHeader('content-type', 'application/json')
    request.setResponseCode(status)
    request.write(json.dumps(response))
    request.finish()



def _mapErrorCodeToStatus(code):
    """
    Maps a L{CODE} constant to a HTTP code.
    """
    if code == 103:
        return http.NOT_FOUND
    return http.INTERNAL_SERVER_ERROR



def _writeJSONErrorResponse(f, request):
    """
    Serializes a L{Failure} to JSON and writes it to the C{request}

    @param f: The L{Failure} to serialize.
    @type f: L{Failure}

    @param request: The request object to write the JSON to.
    @type request: L{twisted.web.server.Request}
    """
    code = getattr(f.value, 'code', CODE.UNKNOWN)
    return _writeJSONResponse(
        result=f.getErrorMessage().decode('ascii'),
        request=request,
        code=code,
        status=_mapErrorCodeToStatus(code))



def jsonResult(f):
    """
    Decorator for render_* methods.

    Serializes the return value or exception to JSON and then writes it to the request
    object.
    """
    def _inner(self, request):
        d = maybeDeferred(f, self, request)
        d.addCallback(_writeJSONResponse, request)
        d.addErrback(_writeJSONErrorResponse, request)
        return NOT_DONE_YET
    return _inner


from twisted.web.static import File
class RootResource(Resource):
    def __init__(self, store, steamKey):
        Resource.__init__(self)
        self.putChild("api", DonationAPI(store, steamKey))
        self.putChild("paypal", PayPal(store))
        self.putChild("static", File('bdm/static/'))
        self.putChild("", File('bdm/static/html/index.html'))



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

    def __init__(self, store, steamKey):
        self.store = store
        self.steamKey = steamKey
        Resource.__init__(self)


    def recent(self, limit):
        """
        Retrieve a list of recent donations.

        XXX: This entire method is slow and terrible.
        """
        def _cb(players):
            donators = []
            for donation in donations:
                steamid = donation.donator.steamID
                try:
                    player = players[donation.donator.steamID].copy()
                except KeyError:
                    player = {
                        'steamid': steamid,
                        'personaname': 'Anonymous'}

                player['date'] = donation.date.asPOSIXTimestamp()
                player['amount'] = str(donation.amount)
                donators.append(player)
            return donators


        donations = []
        steamids = set()
        for donation in self.store.query(
            Donation, limit=limit, sort=Donation.date.descending):
            steamids.add(donation.donator.steamID)
            donations.append(donation)

        d = self.getPlayerSummaries(steamids)
        d.addCallback(_cb)
        return d


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


    def getPlayerSummaries(self, steamids):
        def _cb(response):
            r = json.loads(response)['response']
            players = {}
            for player in r['players']:
                p = player['steamid']
                players[p] = player

            return players


        url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?'
        params = 'key=%s&steamids=%s' % (self.steamKey, ','.join(steamids))

        d = getPage(str(url+params))
        d.addCallback(_cb)
        return d


    @jsonResult
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
