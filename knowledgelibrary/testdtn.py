##testing dtn names

import os
import sys

import random
import json

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indi.knowledgelibrary.dtns import DTN
from indi.knowledgelibrary.dtns import Site
from indi.knowledgelibrary.globus import Globus
from indi.knowledgelibrary.dtns import get_sites
from indi.knowledgelibrary.dtns import get_dtn

demosite1 = 'lbl'
demosite2 ='cern'
firstlink ="/1jdhkjkd.dat"
secondlink ="/test1"

s1_dtn=None
s2_dtn=None
#globj=Globus('mkiran', 'id_rsa')
#print globj
#demosite1_cons=Site(demosite1)

sites = get_sites()
#print sites
for s in sites:
	if s.name == demosite1:
		dtnslist= s.get_dtns()
 		#print dtnslist[0]
 		#if len()
 		#for ds in dtnslist:
 			
 		s1_dtn=dtnslist[0]	
 		#get dtn obj
 	if s.name == demosite2:
		dtnslist= s.get_dtns()
 		#print dtnslist[0]

 		#for ds in dtnslist:
 			#print "here"
 		#	site2_dtn= ds
		#	print site2_dtn.name
			#lbldtn=get_dtn(site2_dtn.name)
		s2_dtn=dtnslist[0]

if s1_dtn!=None and s2_dtn!=None:
	#print s1_dtn, s2_dtn
	globuscall=s1_dtn.transfer(src_file=firstlink, dest_dtn=s2_dtn, dest_file=secondlink)
	print globuscall
			#for sd in site2_dtn:
			#	anl_dtn=sd.get_dtn()


# dtn1 = DTN(name=the_args[1], site_name=site1, globus=globus)

# demosite1dtn = demosite1_cons.get_dtns()
# gdtn1 = DTN(demosite1,demosite1dtn)
# demosite2_cons=Site(demosite2)
# demosite2dtn = demosite2_cons.get_dtns()
# gdtn2 = DTN(demosite2, demosite2dtn, globj)
# print "here"
# print gdtn1
# print gdtn2


