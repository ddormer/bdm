import argparse
import sys
from decimal import Decimal

from axiom.store import Store
from axiom.attributes import AND
from axiom.errors import ItemNotFound

from bdm.donate import Donator

if  '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--store', metavar='<dir>', type=str,
            required=True, help='An Axiom store directory')
    parser.add_argument('--steamid', metavar='<int>', type=int,
            required=True, help='64bit representation of a Steam ID to donate with.')
    parser.add_argument('--amount', metavar='<float>', type=float,
            required=True, help='Amount to donate')
    args = parser.parse_args()

    store = Store(args.store)
    try:
        donator = store.findUnique(Donator,
            AND(Donator.steamID==unicode(args.steamid)))
    except ItemNotFound:
        print 'ERROR: Donator %s not found in the database.' % (args.steamid,)
        sys.exit()

    donator.addDonation(Decimal(args.amount), u'cli')
    print donator
