#Example setting up a service between two points
#import indi.knowledgelibrary
#system.path.append("../../")

#! /usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indi.intentmodules.intentmanager import intentmanagermain



service='For project1 connect'
fromto='lbl anl'


#print("%s, %s"), service, fromto

#print service, fromto

#string query
query=service + ' ' + fromto  + ' condition bwnolimit schedulestart 2017-04-04->09.00.00 schedulestop 2017-04-04->17.00.00'
print "do this please:"
print query

#sys.path.append("../../")
#from intentmodules.intentmanager 


#replace keywords
#throw away words

#future
#ask link generation for topology
#Do u want a link between a and b - plot new graph

intentmanagermain(query)


#json query
#qdata = {}
#qdata['service'] = 'connect'
#qdata['data'] = 'serverA'
#qdata['data'] = 'serverB'

#json_qdata = json.dumps(qdata)

#print json_qdata