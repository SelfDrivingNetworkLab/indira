#contains rule list

import json
from rdflib import ConjunctiveGraph, Namespace, exceptions

from rdflib import URIRef, RDFS, RDF, BNode
from rdflib import Graph, Literal

from rdflib.namespace import DC, FOAF
from rdflib.tools.rdf2dot import rdf2dot
from graphviz import Digraph


class ServiceRule:
	def __init__(self, slist):
		slist=slist

	def checkvalidservices(self,slist):
		#//do matching
		#parse only one service to be define

		return

class TimeRule():
	#parse for checking time values defined if schedulestart,schedulestop, 
	
	def checkvalidservices1(self,slist):
		#//do matching
		#parse only one service to be define

		return


class Keyworkcheck():
	#check for similar keywords
	
	def checkvalidservices2(self,slist):
		#//do matching
		#parse only one service to be define

		return


class OpenLoadSchema():
	print "---- Open schema -------"
	filename="intentowlschema.rdf"
	schemagraph=ConjunctiveGraph()
	sg=Graph()
	fileflag=0

	try:
		f = open(filename)
		f.close()
		fileflag=1
	except IOError as e:
		print "file not found"
 
    
	#except IOError:
	#	print ('cannot open', filename)
	#else:
	if fileflag==1:
		sg.load(filename)

		schemagraphresult=schemagraph.parse(filename)
		print "Current active intent graph length:"
		#print len(schemagraphresult)
	
		qres1 = schemagraphresult.query(
			"""SELECT DISTINCT ?aname ?bname
			WHERE {
			?aname rdf:nodeID ?bname .
			}""")
		for row in qres1:
			print("%s knows %s" % row)
	
		#for s, p, o in sg.triples((None, RDF.type, RDF.type)):
		#	print "%s is node" %s

		#for s,p,o in sg.triples( (None, RDF.type, None) ):
		#	print "%s is a %s"%(s,o)


	# fg = Graph()
	# # ... add some triples to g somehow ...
	# fg.serialize(filename)
	# qres = fg.query(
	# 	"""SELECT DISTINCT ?aname ?bname
	# 	WHERE {
	# 	?aname ns1:hasValue ?bname .
	# 		}""")
	# for row in qres:
	# 	print("%s knows %s" % row)
	

			
	
def main():
	OpenLoadSchema()

main()