import argparse
import sys

from axiom.store import Store
from axiom.attributes import AND
from axiom.errors import ItemNotFound

from bdm.donate import Donator

if  '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--store', metavar='<dir>', type=str,
            required=True, help='An Axiom store directory')
    parser.add_argument('--steamid', metavar='<int>', type=int,
            required=True, help='64bit representation of the steam donators steam ID.')
    parser.add_argument('--new-steamid', metavar='<int>', type=int,
            help='64bit representation of the new steam ID.')
    parser.add_argument('--anonymous', action='store_true',
            help='Should the user should be marked as anonymous?')
    args = parser.parse_args()

    store = Store(args.store)
    try:
        donator = store.findUnique(Donator,
            AND(Donator.steamID==unicode(args.steamid)))
    except ItemNotFound:
        print 'ERROR: Donator %s not found in the database.' % (args.steamid,)
        sys.exit()

    donator.anonymous = args.anonymous
    if args.new_steamid != None:
        #Only update steamID if it doesn't already belong to another Donator.
        try:
            other = store.findUnique(Donator, AND(Donator.SteamID==unicode(args.new_steamid)))
            print 'ERROR: Steam ID change failed. Steam ID belongs to another Donator:'
            print other
            sys.exit()
        except ItemNotFound:
            donator.steamid = unicode(args.new_steamid)

    print donator
