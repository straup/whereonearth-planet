#!/usr/bin/env python

import sys
import os
import os.path
import json
import csv
import types

import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    whoami = os.path.abspath(sys.argv[0])
    bindir = os.path.dirname(whoami)
    rootdir = os.path.dirname(bindir)

    datadir = os.path.join(rootdir, 'data')
    metadir = os.path.join(rootdir, 'meta')

    lookup_path = os.path.join(metadir, "planets.csv")
    lookup_fh = open(lookup_path, 'w')

    writer = csv.writer(lookup_fh)
    writer.writerow(('exoplanet_id', 'name', 'woeid', 'foundry'))

    for root, dirs, files in os.walk(datadir):

        for f in files:

            path = os.path.join(root, f)
            logging.info("processing %s" % path)

            fh = open(path)
            data = json.load(fh)

            feature = data['features'][0]
            props = feature['properties']

            oepid = props.get('oep:id', 0)
            woeid = props.get('woe:id', 0)

            name = props.get('oep:name', '')

            if woeid == 1:
                name = 'Earth'
            elif type(name) == types.ListType:
                name = name[0]
            else:
                pass

            foundry = props.get('artisanal:foundry', 'http://developer.yahoo.com/geo/geoplanet/')

            writer.writerow((oepid, name, woeid, foundry))
