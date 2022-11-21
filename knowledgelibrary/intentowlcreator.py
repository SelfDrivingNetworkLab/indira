#creation of OWL file for intent

import json
from rdflib import ConjunctiveGraph, Namespace, exceptions

from rdflib import URIRef, RDFS, RDF, BNode
from rdflib import Graph, Literal

from rdflib.namespace import DC, FOAF
from rdflib.tools.rdf2dot import rdf2dot
from graphviz import Digraph


# ,
# 	"condition": [{
# 		"args": "bwnolimit",
# 		"value": "VALUE"
# 	}, {
# 		"args": "isolation",
# 		"value": "VALUE"
# 	}, {
# 		"args": "unfriendly",
# 		"value": "VALUE"
# 	}, {
# 		"args": "SCHEDULESTART",
# 		"value": "VALUE"
# 	}, {
# 		"args": "SCHEDULEDURATION",
# 		"value": "VALUE"
# 	}, {
# 		"args": "SCHEDULESTOP",
# 		"value": "VALUE"
# 	}]


intentowldata = {
	"profile": [
		"args", "args2", "args3"
	],
	"service": [
		"CONNECT", "DISCONNECT","VLAN", "TAP"
		],
 	"condition": [
 		"bwnolimit","isolation","unfriendly","SCHEDULESTART","SCHEDULEDURATION","SCHEDULESTOP"
 		],
 	"bwnolimit": [
 		"nobwlimit", "nolimit"
 	 	],
 	 "unfriendly":[
 	 	"notcpdata","notcppackets"
 	 	]
}


def main():
	#with open('indiservicestest.json','w') as outfile:
	parsed=json.dumps(intentowldata)
	intentjson=json.loads(parsed)
	
	
	hasClass = URIRef('ex:hasClass')
	hasValue = URIRef('ex:hasValue')

	g = ConjunctiveGraph()
	intentnodeString=Literal("IntentOWL")
	intentNode=BNode(intentnodeString)

	#add classes
	for key in intentjson:
		g.add((intentNode, hasClass, Literal(key)))

	#add values to classes
	for key in intentjson:
		for v in intentjson[key]:
			nkey=BNode(Literal(key))
			g.add((nkey,hasValue, Literal(v)))
	

	for subj, pred, obj in g:
		print subj,pred, obj

    	#print val
    	#construct.append(ServiceDetail(servicefound,argsfound))
        
	print "Graph Constructed:"

	
	dot=Digraph(comment='Intent OWL/schema graph')
	for subj, pred, obj in g:
	 	dot.node(subj, subj)
	 	dot.node(obj,obj)
	 	dot.edge(subj,obj, constraint='false')

	print(dot.source)
	dot.format='png'
	dot.render('inputowlintent.dot', view='False')


	print "---- Create a new file and save graph -------"
	filename="intentowlschema.rdf"

	g.serialize(filename, format='pretty-xml')

def add_to_schema(k, r, v):
	#open file
	#Read graph
	#add graph
	return


main()
