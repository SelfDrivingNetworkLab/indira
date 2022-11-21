#Example setting up a service between two points
#import indi.knowledgelibrary


#! /usr/bin/env python

import os
import sys



service='connect'
fromto='h1@lbl.gov h2@anl.gov'
condition = 'no_bw_constraints'

#print("%s, %s"), service, fromto

#print service, fromto

#string query
query=service + ' ' + fromto+ ' ' + condition  
print query

sys.path.append("../../")
from knowledgelibrary import intentengine

intentengine.main(query)

#json query
#qdata = {}
#qdata['service'] = 'connect'
#qdata['data'] = 'serverA'
#qdata['data'] = 'serverB'

#json_qdata = json.dumps(qdata)

#print json_qdata