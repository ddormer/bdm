import argparse

from axiom.store import Store
from axiom.attributes import AND
from axiom.errors import ItemNotFound

from bdm.donate import Donator

if  '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--store', metavar='<dir>', type=str,
            required=True, help='An Axiom store directory')
    parser.add_argument('--steamid', metavar='steamID', type=int,
            required=True, help='64bit representation of a Steam ID.')
    parser.add_argument('--anonymous', action='store_true',
            help='Use this flag if the user should be marked as anonymous.')
    args = parser.parse_args()

    store = Store(args.store)
    try:
        donator = store.findUnique(Donator, AND(Donator.steamID==unicode(args.steamid)))
    except ItemNotFound:
        donator = Donator(store=store, steamID=unicode(args.steamid), anonymous=args.anonymous)

    print donator
