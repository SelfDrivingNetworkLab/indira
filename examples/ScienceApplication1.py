#Example Science Application Demands certain services from network
#import indi.knowledgelibrary


#! /usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indi.intentmodules.intentmanager import intentmanagermain

#Parameters asked for
service='connect'
connection_points='LBL ANL BNL'
condition = 'bwnolimit isolated unfriendly notcpdata'
user='PhysicistJohn'
time='now'


#print("%s, %s"), service, fromto

#print service, fromto

#string query
query='For ' + user + ' ' + service + ' ' + connection_points  + ' condition ' + condition + ' schedulestart ' + time  + ' schedulestop ' + 'afterhours'
print query

intentmanagermain(query)

#json query
#qdata = {}
#qdata['service'] = 'connect'
#qdata['data'] = 'serverA'
#qdata['data'] = 'serverB'

#json_qdata = json.dumps(qdata)

#print json_qdata