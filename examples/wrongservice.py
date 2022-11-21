#Example setting up a service between two points
#import indi.knowledgelibrary


#! /usr/bin/env python

import os
import sys



service='dothis'
fromto='serverA serverB'

#print("%s, %s"), service, fromto

#print service, fromto

#string query
query=service + ' ' + fromto
print query

sys.path.append("../../")
from knowledgelibrary import intentengine

intentengine.main(query)

#Connect port1@device port2@device 
#vlan

#json query
#qdata = {}
#qdata['service'] = 'connect'
#qdata['data'] = 'serverA'
#qdata['data'] = 'serverB'

#json_qdata = json.dumps(qdata)

#print json_qdata