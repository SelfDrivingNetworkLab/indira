# Does following functions:
# 1) Reads the incoming query and calls engine to understand it as services and arguments
# 1b) identifies who the user is
# 2) builds an rdf graph of the incoming query
# 3) main function - calls above fn, calls intent engine to check schema and correct terms used
# 3b) once verified will call the intent renderer
# 4) takes the output of renderer and calls oscars/nsi client
#!/usr/bin/env python


import re
import os
import sys
import time
from rdflib import ConjunctiveGraph, Namespace, exceptions

from rdflib import URIRef, RDFS, RDF, BNode
from rdflib import Graph, Literal

from rdflib.namespace import DC, FOAF
from rdflib.tools.rdf2dot import rdf2dot
from graphviz import Digraph

#sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from indira.knowledgelibrary.intentengine import parseintent
from indira.knowledgelibrary.intentengine import checkwithschema
from indira.intentmodules.intentrenderer import renderermain

from indira.knowledgelibrary.dtns import DTN
from indira.knowledgelibrary.dtns import Site
from indira.knowledgelibrary.globus import Globus
from indira.knowledgelibrary.dtns import get_sites
from indira.knowledgelibrary.dtns import get_dtn

filerenderpath = "../static/"


class ServiceDetail:
    __slots__ = ["service", "args"]

    def __init__(self, service, args):
        self.service = service
        self.args = args


def intentmanagermain(indi_ip):
    systimeBefore = time.clock()
    print ("\n############## Intent Manager ########################")
    rout = 0

    understand_sites=[]
    print ("\nReceived Intent:" + indi_ip)

    understand_sites=re.compile("connect.*?condition").findall(indi_ip)

    for a in understand_sites:
        newunderstand_sites="".join(a)

    newunderstand_sites=newunderstand_sites.replace("connect ", "")
    newunderstand_sites=newunderstand_sites.replace(" condition", "")

    #print newunderstand_sites

    sitenames=newunderstand_sites.split()
    #print len(sitenames)
    demosite1 = sitenames[0]
    demosite2 = sitenames[1]


    constructlist = []
    checkedinputgraph = ConjunctiveGraph()
    constructlist = parseintent(indi_ip)

    # delete the dummy element
    for q in constructlist:
        if q.service == "DUMMY":
            constructlist.remove(q)
    # print len(constructlist)

    # check which user is involved
    # returns a list of users in the intent
    userfound = checkuser(constructlist)

    if userfound != "NOTFOUND":
        print ("User found: ")
        print (userfound)
    else:
        print ("Please state your identity as user for the intent!")
        print ("discontinue program")

    if userfound != "NOTFOUND":
        print ("Constructing RDF graph from input...")
        inputintentgraph = ConjunctiveGraph()
        inputintentgraph = constructnewgraph(constructlist, userfound)
        inputintentgraph.serialize("new.rdf")

        print ("Checking validity of input intent....")
        checkedinputgraph = checkwithschema(inputintentgraph, userfound)

        if len(checkedinputgraph) > 0:
            print ("all ok so far.....")

            # print "####################################"
            print ("Calling intent renderer....")

            rout = renderermain(checkedinputgraph, userfound)

            queryservices = inputintentgraph.query(
                    """SELECT DISTINCT ?a ?b
				WHERE {
				?a ns1:hasService ?b .
				}""")
            # for row in queryservices:
            #print ("%s hasservices %s " % row)
            sitesextracted=[]

            if rout == 1:
                print ("INDIRA> NSI has returned a connectivity error...")
                res = input(
                    "INDIRA> Do you want to transfer files with a lower QoS requirements? (Y/N)")

       #         demosite1=''
        #        demosite2=''

                if res == 'Y' or res == 'y':
                    for subj, pred, obj in checkedinputgraph:
                        #print subj, pred, obj
                        if Literal(subj).lower() == 'connect':
                            sitesextracted.append(Literal(obj))
                            #print "found"
                            #print obj

                    #print "calling globus...."#" have to code out some values here MARIAM!"

                    #print len(sitesextracted)

         #           if len(sitesextracted)>0:
          #              demosite1 = sitesextracted[0]
           #             demosite2 = sitesextracted[1]

                    print("INDIRA> State the source and destination files. Hint: '/www.txt->/test'")
                    statementtransfer_manager = input("> ") 

                    folderconnection=statementtransfer_manager #re.compile("'.*?'").findall(statementtransfer)
                    #print pairs
                    #  for folderconnection in folderpoints:
                    breakingfolderconnection=folderconnection.split('->')
                    firstlink=breakingfolderconnection[0]
                    firstlink=firstlink.replace("'","")
                    secondlink=breakingfolderconnection[1]
                    secondlink=secondlink.replace("'","")
  

                      
                    #firstlink = "/1M.dat"
                    #secondlink = "/test1"

                    s1_dtn = None
                    s2_dtn = None

                    gallsites = get_sites()
                    #print gallsites
                    #print "122"
                    #print demosite1
                    #print demosite2

                    for s in gallsites:
                        #print "here " + s.name
                        if s.name == demosite1:
                            dtnslist = s.get_dtns()
                            s1_dtn = dtnslist[0]
                         #   print "s1"
                            #print s1_dtn
                            # get dtn obj
                          #  print 444,len(demosite2),len(s.name),demosite2==s.name,demosite2,s.name
                        if s.name == demosite2:
                            dtnslist = s.get_dtns()
                            s2_dtn = dtnslist[0]
                           # print "s2"
                            #print s2_dtn

                    if s1_dtn != None and s2_dtn != None:
                        #print "in if"
                        globuscall = s1_dtn.transfer(
                            src_file=firstlink, dest_dtn=s2_dtn, dest_file=secondlink)
                        result = globuscall[0]
                        reason = globuscall[1]
                        if result == True:
                        	print ("Transfer request has been approved. Globus task identifier is: " + reason)
                        else:
                        	print ("Transfer request has been rejected because: Globus Task id = " + reason)
                    print ("done")
                    return "done"
                    # print "MARIAM CALL GLOBUS"
                    # rc=call("./nsibash.sh",shell=True)#python dtns.py --globus-transfer-nsi lbl lbl-diskpt1 /1M.dat bnl bnl-diskpt1 /test1
                    #(False, 'No NSI connection.')

                    # python dtns.py --globus-transfer lbl lbl-diskpt1 /1M.dat bnl bnl-diskpt1 /test1
                    #(True, ' bc723598-a6cb-11e6-9ad2-22000a1e3b52')

                else:
                    print (" Ok no problem.. call again")

        else:
            print ("discontinue program")
    print ("Shutting down.....")

    systimeEnd = time.clock()
    sysdiff = systimeEnd - systimeBefore
    print ("Total Indira Processing Time:")
    print (sysdiff)


# build graph? and show services
def constructnewgraph(constructlist1, user):
    service = URIRef('ex:service')
    hasService = URIRef('ex:hasService')
    hasArguments = URIRef('ex:hasArguments')

    g = ConjunctiveGraph()
    intentnodeString = Literal(user)
    intentNode = BNode(intentnodeString)

    for q in constructlist1:
        sn = URIRef(q.service)
        if sn.upper() != "FOR":
            g.add((intentNode, hasService, Literal(sn)))
            for r in q.args:
                g.add((sn, hasArguments, Literal(r)))
    #print "Graph constructed for intent input!"

    # for subj, pred, obj in g:
    # print subj, pred, obj

    dot = Digraph(comment='Input Intent')
    for subj, pred, obj in g:
        dot.node(subj, subj)
        dot.node(obj, obj)
        dot.edge(subj, obj, pred, constraint='false')

    # print(dot.source)
    dot.format = 'png'
    # filenameput=filerenderpath+'/inputintent-dot'
    dot.render('../static/inputintent-dot', view=False)

    print ("Creating intent graph in html output....")
    try:
        fname = '../templates/userinput.html'
        file = open(fname, 'w')
        firstpart = """<!DOCTYPE html>
		<html>
		<head>
		<title>First graph</title>
		<meta name="description" content="A concept map diagram ." />
		<meta charset="UTF-8">
		<script src="go.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/gojs/1.6.7/go-debug.js"></script>

		<link href="../assets/css/goSamples.css" rel="stylesheet" type="text/css" />  
		<script src="goSamples.js"></script>  <!-- this is only for the GoJS Samples framework -->
		<script id="code">
		function init() {
		if (window.goSamples) goSamples();  // init for these samples -- you don't need to call this
		var $ = go.GraphObject.make;  // for conciseness in defining templates
		myDiagram =
		$(go.Diagram, "myDiagramDiv",  // must name or refer to the DIV HTML element
			{\n
			initialAutoScale: go.Diagram.Uniform,  // an initial automatic zoom-to-fit\n
			contentAlignment: go.Spot.Center,  // align document to the center of the viewport\n
			layout:\n
			$(go.ForceDirectedLayout,  // automatically spread nodes apart\n
				{ defaultSpringLength: 30, defaultElectricalCharge: 100 })\n
			});\n
		// define each Node's appearance\n
		myDiagram.nodeTemplate =
		$(go.Node, "Auto",  // the whole node panel
			{ locationSpot: go.Spot.Center },
			// define the node's outer shape, which will surround the TextBlock\n
			$(go.Shape, "Rectangle",
				{ fill: $(go.Brush, "Linear", { 0: "rgb(254, 201, 0)", 1: "rgb(254, 162, 0)" }), stroke: "black" }),
				$(go.TextBlock, 
				{ font: "bold 10pt helvetica, bold arial, sans-serif", margin: 4 },
				new go.Binding("text", "text"))
			);
			// replace the default Link template in the linkTemplateMap
			myDiagram.linkTemplate =
			$(go.Link,  // the whole link panel
				$(go.Shape,  // the link shape
					{ stroke: "black" }),
					$(go.Shape,  // the arrowhead
						{ toArrow: "standard", stroke: null }),
						$(go.Panel, "Auto",
							$(go.Shape,  // the label background, which becomes transparent around the edges
								{ fill: $(go.Brush, "Radial", { 0: "rgb(240, 240, 240)", 0.3: "rgb(240, 240, 240)", 1: "rgba(240, 240, 240, 0)" }),
								stroke: null }),
						$(go.TextBlock,  // the label text
							{ textAlign: "center",
							font: "10pt helvetica, arial, sans-serif",
							stroke: "#555555", margin: 4 },
							new go.Binding("text", "text"))
								));
						// create the model for the concept map\n"""
        file.write(firstpart)
        cnode = 0

        # create a list of ids for plotting the js graph
        uniqueidlist = []
        for subj, pred, obj in g:
            flagnodefound = 0
            for j in uniqueidlist:
                if Literal(subj) == j:
                    flagnodefound = 1
            if flagnodefound == 0:
                uniqueidlist.append(Literal(subj))

        for subj, pred, obj in g:
            flagnodefound = 0
            for j in uniqueidlist:
                if Literal(obj) == j:
                    flagnodefound = 1
                    # print "found name " + j
            if flagnodefound == 0:
                # print obj
                uniqueidlist.append(Literal(obj))
        # adding links

        nodeDAstring = ''
        linkDAstring = ''
        tempstr = ""
        for j in uniqueidlist:
            # print nodeDAstring
            # print uniqueidlist.index(j)
            checkcommas = j.replace("'", "")

            tempstr = "{ key:" + str(uniqueidlist.index(j)) + \
                ", text: '" + checkcommas + "' },"
            # print tempstr
            nodeDAstring += tempstr

        tempstr = ""
        for subj, pred, obj in g:
            # print uniqueidlist.index(Literal(subj)),
            # uniqueidlist.index(Literal(obj)), pred
            tempstr = "{ from:" + str(uniqueidlist.index(Literal(subj))) + ", to:" + str(
                uniqueidlist.index(Literal(obj))) + ", text: '" + Literal(pred) + "'},"
            linkDAstring += tempstr

        file.write("""   var nodeDataArray = [""")

        file.write(nodeDAstring)

        file.write("{} ];")
        file.write("    var linkDataArray = [")
        file.write(linkDAstring)
        file.write("{} ];")
        secondpart = """    
				myDiagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
				}
				</script>
				</head>
				<body onload="init()">
				<div id="sample">
				<h3>User Intent</h3>
				<div id="myDiagramDiv" style="background-color: whitesmoke; border: solid 1px black; width: 100%; height: 700px"></div>
				<p>
				The actual user intent received by INDIRA. 
				See also the <a href="interactiveForce.html">Interactive Force</a> sample that uses the exact same data
				but a different node template and a customized <a>ForceDirectedLayout</a>.
				</p>
				</div>
				</body>
				</html>"""
        file.write(secondpart)
        file.close()
    except:
        print("file writing error occured")
        sys.exit(0)

    return g


def checkwithactive(constructlist1):
    # owllink= rdflib.URIRef('http://www.w3.org/2002/07/owl#Ontology')
    service = URIRef('ex:service')
    hasService = URIRef('ex:hasService')
    hasArguments = URIRef('ex:hasArguments')

    g = ConjunctiveGraph()
    intentnodeString = URIRef('Intent')
    intentNode = BNode(intentnodeString)

    for q in constructlist1:
        sn = URIRef(q.service)
        print (sn)
        print (q.args)
        g.add((intentNode, hasService, Literal(sn)))
        for r in q.args:
            g.add((sn, hasArguments, Literal(r)))

    #print len(g)

    # for subj, pred, obj in g:
    # print subj, pred, obj

    print ("---- Open Active Intents -------")
    filename = "../knowledgelibrary/activeintents.rdf"
    oldgraph = Graph()
    newg = g

    fileflag = 0

    try:
        f = open(filename)
        f.close()
        fileflag = 1
    except IOError as e:
        print ("file not found")

    # except IOError:
    #	print ('cannot open', filename)
    # else:
    if fileflag == 1:
        oldgraphresult = oldgraph.parse(filename, format="n3")
        # print "Current active intent graph length:"
        # print len(oldgraphresult)
        # print "---- Merge Intents -------"

        for oldsubj, oldpred, oldobj in oldgraphresult:
            for newsubj, newpred, newobj in g:
                if newsubj == oldsubj and oldobj == newobj:
                    print ("Repeated intent found: ")
                    print (newsubj, newobj)

        newg = oldgraphresult + g
        # break
    # finally:
    #	print "Done"
        #rdf2dot(oldgraphresult, "/Users/mkiran/try.dot")
        # draw graph using graphviz since rdf is not working
        dot = Digraph(comment='Intent')
        for subj, pred, obj in newg:
            dot.node(subj, subj)
            dot.node(obj, obj)
            dot.edge(subj, obj, pred, constraint='false')

        # print(dot.source)
        dot.format = 'png'
        # filenameput=filerenderpath+'/inputintent-dot'
        dot.render('../static/inputintent-dot', view='False')

        # print "---- Saving Active Intents -------"

        newg.serialize(filename, format='turtle')

        # 	print i	print "Parents, *backward* from `ex:gm1`:"
    # for i in g.transitive_subjects(parent, momOfMom):
    #	print i
#	g.close()


def checkuser(constructlist1):
    user = "NOTFOUND"
    for q in constructlist1:
        sn = URIRef(q.service)
        if sn.upper() == "FOR":
            # print q.args
            user = Literal(q.args)
    return user


def readactiveintents():
    # print "---- Open Active Intents File for checking -------"
    filenametest = "../knowledgelibrary/activeintents.rdf"
    oldgraph = Graph()

    fileflag = 0

    try:
        f = open(filenametest)
        f.close()
        fileflag = 1
    except IOError as e:
        print ("file not found")

    if fileflag == 1:
        oldgraphresult = oldgraph.parse(filenametest, format="n3")
        # print "Current active intent graph length:"
        # print len(oldgraphresult)

        # dot=Digraph(comment='Intent')
        # for subj, pred, obj in oldgraphresult:
        #	print subj,pred,obj

        print (oldgraphresult.serialize(format='turtle'))


# readactiveintents()
