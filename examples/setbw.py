#Example setting up a service between two points
#import indi.knowledgelibrary


#! /usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indi.intentmodules.intentmanager import intentmanagermain


service='connect'
fromto='LBL ANL'
condition = 'no_bw_constraints'

#print("%s, %s"), service, fromto

#print service, fromto
def test():
	#string query
	query=service + ' ' + fromto + ' ' + 'condition bwnolimit schedulestart 1000 420'
	return query

#intentmanagermain(query)

#json query
#qdata = {}
#qdata['service'] = 'connect'
#qdata['data'] = 'serverA'
#qdata['data'] = 'serverB'

#json_qdata = json.dumps(qdata)

#print json_qdata