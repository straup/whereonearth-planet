#!/usr/bin/env python

import sys
import os
import os.path
import json
import utils
import pprint

import xmltodict
import random

import ArtisinalInts

import logging
logging.basicConfig(level=logging.INFO)

def generate_lookup_table(options):

    lookup = {}

    for root, dirs, files in os.walk(options.woeplanets):

        for f in files:

            if not f.endswith(".json") :
                continue

            path = os.path.join(root, f)
            path = os.path.abspath(path)

            fh = open(path, 'r')
            data = json.load(fh)
            fh.close()

            f = data['features'][0]
            props = f['properties']

            try:
                lookup[ props['oep:id'] ] = props['woe:id']
            except Exception, e:
                pass

    return lookup
            
def import_planets(options):

    lookup = generate_lookup_table(options)

    for root, dirs, files in os.walk(options.exoplanets):

        for f in files:

            if not f.endswith(".xml") :
                continue

            path = os.path.join(root, f)
            path = os.path.abspath(path)

            fh = open(path, 'r')

            # this is a total hack... but it does mean you
            # can ignore all that foofy xml :D :D :D

            data = xmltodict.parse(fh)
            data = json.loads(json.dumps(data))

            props = {}

            for k, v in data['planet'].items():

                if k == 'star':
                    for _k, _v in data['planet']['star'].items():
                        props[ 'oep-star:%s' % _k ] = _v
                elif k == 'properties':
                    props['oep:mass'] = data['planet']['properties']['mass']
                    props['oep:radius'] = data['planet']['properties']['radius']

                    for _k, _v in data['planet']['properties']['orbit'].items():
                        props[ 'oep-orbit:%s' % _k ] = _v

                else:
                    k = "oep:%s" % k
                    props[k] = v

            oepid = props['oep:id']
            woeid = lookup.get(oepid, 0)

            if woeid != 0:

                woe_root = utils.woeid2path(woeid)
                woe_root = os.path.join(os.path.abspath(options.woeplanets), woe_root)

                fname = "%s.json" % woeid
                woe_path = os.path.join(woe_root, fname)

                woe_fh = open(woe_path, 'r')
                woe_data = json.load(woe_fh)

                woe_features = woe_data['features'][0]
                old_props = woe_features['properties']
                
                for k in ('woe:id', 'placetype', 'artisanal:id', 'artisanal:foundry'):
                    props[k] = old_props[k]

            else:

                woeid, foundry = get_artisanal_int()

                props['woe:id'] =  woeid
                props['placetype'] = 'planet'
                props['artisanal:id'] = woeid
                props['artisanal:foundry'] = foundry

            feature = {
                'id': woeid,
                'properties': props
                }

            woe_data = {
                'type': 'FeatureCollection',
                'features': [ feature ],
                'geometry': { 'type': 'Polygon', 'coordinates': [] }
                }

            woe_root = utils.woeid2path(woeid)
            woe_root = os.path.join(os.path.abspath(options.woeplanets), woe_root)

            if not os.path.exists(woe_root):
                os.makedirs(woe_root)
            
            fname = "%s.json" % woeid

            woe_path = os.path.join(woe_root, fname)

            woe_fh = open(woe_path, 'w')
            woe_data = json.dump(woe_data, woe_fh, indent=2)
            woe_fh.close()
            
            print woe_path

def get_artisanal_int():

    i = random.randrange(0, 3)

    while True:

        try:
            if i == 0:
                int, ignore = ArtisinalInts.get_mission_integer()
                return int, "http://www.missionintegers.com/"
            elif i == 1:
                int, ignore = ArtisinalInts.get_brooklyn_integer()        
                return int, "http://www.brooklynintegers.com/"
            else:
                int, = ArtisinalInts.get_london_integer()
                return int, "http://www.londonintegers.com/"
        except Exception, e:
            print e

    return None

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser(usage='')

    parser.add_option('--exoplanets', dest='exoplanets',
                        help='',
                        action='store')

    parser.add_option('--woeplanets', dest='woeplanets',
                        help='',
                        action='store')

    parser.add_option('--debug', dest='debug',
                        help='Enable debug logging',
                        action='store_true', default=False)

    options, args = parser.parse_args()

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


    import_planets(options)
    logging.info("done");

    sys.exit()
