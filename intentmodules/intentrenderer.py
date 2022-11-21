# does the following actions:
# called by intent manager, reads json files
# 1) takes rdf input and first bw is determined, time topo, provision
# pass back rdf graph to manager

# 2) Checks the graph of query with schema


import os
import sys

import random
import json
import indi.knowledgelibrary
import datetime
from pytz import timezone
from datetime import datetime
from datetime import timedelta
from dateutil import parser

from rdflib import ConjunctiveGraph, Namespace, exceptions

from rdflib import URIRef, RDFS, RDF, BNode
from rdflib import Graph, Literal

from rdflib.namespace import DC, FOAF
from rdflib.tools.rdf2dot import rdf2dot
from graphviz import Digraph

from pprint import pprint
from indi.knowledgelibrary.oscars import get_endpoints
#from indi.knowledgelibrary.dtns import get_site_onsa

import subprocess
from subprocess import call
import time


# read json files
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
profilefile = "../../indi/knowledgelibrary/profiles.json"
schemafilelink = "../../indi/knowledgelibrary/intentowlschema.json"

oscartopofile = "../../indi/knowledgelibrary/sitetopo.json"
currentusefile = "../../indi/knowledgelibrary/currentusage.json"


class ServiceDetail:
    __slots__ = ["service", "args"]

    def __init__(self, service, args):
        self.service = service
        self.args = args


class ProfileDetail:
    __slots__ = ["name", "description", "bandwidth", "topology", "timezone"]

    def __init__(self, name, description, bandwidth, topology, timezone):
        self.name = name
        self.description = description
        self.bandwidth = bandwidth
        self.topology = topology
        self.timezone = timezone


def renderermain(graphinput, user):
    # Record rdf
    time.sleep(5)

    print (" ################ Intent Renderer ###################")
    print ("\n")

    rendergraph = ConjunctiveGraph()
    rendergraph = graphinput
    hasService = URIRef('ex:hasService')
    hasArguments = URIRef('ex:hasArguments')
    hasCondition = URIRef('ex:hasCondition')
    hasBandwidth = URIRef('ex:hasBandwidth')
    hasDate = URIRef('ex:hasDate')
    hasTime = URIRef('ex:hasTime')
    hasZone = URIRef('ex:hasZone')
    
    #for subj, pred, obj in rendergraph:
     #   print subj, pred, obj

    posbw = renderbw(user, rendergraph)

    print ("Rendering bandwidth permissions.... " + posbw)
    for subj, pred, obj in rendergraph:
        if str(obj) == "bwnolimit":   # MK Update this
            rendergraph.remove((subj, pred, obj))
            rendergraph.add((subj, hasBandwidth, Literal(posbw)))

    timefns = rendertime(user, rendergraph)
    for t in timefns:
        for subj, pred, obj in rendergraph:
            # print subj,pred, obj
            if t.service.upper() == str(subj).upper():
                rendergraph.remove((subj, pred, obj))
                fulltime = t.args
                # print fulltime
                tdate = fulltime.split()[0]
                ttime = fulltime.split()[1]
                ttime = ttime.replace(':', ".")
                ztime = fulltime.split()[2]
                rendergraph.add((subj, hasDate, Literal(tdate)))
                rendergraph.add((subj, hasTime, Literal(ttime)))
                rendergraph.add((subj, hasZone, Literal(ztime)))

    endpointdata = rendertopology(user, rendergraph)
    # for a in endpointdata:
    #	print a.service, a.args
    # update graph
    for subj, pred, obj in rendergraph:
        for a in endpointdata:
            if str(obj).upper() == a.service.upper():
                rendergraph.remove((subj, pred, obj))
                dotcheck = a.args
                dotcheck = a.args.replace(':', ".")
                rendergraph.add((subj, pred, Literal(dotcheck)))

    # if unfriendly asked

    # if isolated asked
    # renderprovision() call nsi
    print ("Final rendering graph created and saved....")

    rdot = Digraph(comment='Rendered Intent')
    for subj, pred, obj in rendergraph:
        #print "new"
        #print subj, pred, obj
        rdot.node(subj, subj)
        rdot.node(obj, obj)
        rdot.edge(subj, obj, pred, constraint='false')

        # print(dot.source)
    rdot.format = 'png'
    rdot.render('../static/renderintent.dot', view=False)
    # call an exe file....

    # extracting data from RDF graph constructed
    print ("Creating rendered graph in html output....")
    try:
        fname = '../templates/renderedinput.html'
        file = open(fname, 'w')
        firstpart = """<!DOCTYPE html>
		<html>
		<head>
		<title>Rendered Intent</title>
		<meta name="description" content="A concept map diagram ." />
		<meta charset="UTF-8">
		<script src="go.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/gojs/1.6.7/go-debug.js"></script>

		<link href="../assets/css/goSamples.css" rel="stylesheet" type="text/css" />  
		<script src="goSamples.js"></script>  
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
        for subj, pred, obj in rendergraph:
            flagnodefound = 0
            for j in uniqueidlist:
                if Literal(subj) == j:
                    flagnodefound = 1
            if flagnodefound == 0:
                uniqueidlist.append(Literal(subj))

        for subj, pred, obj in rendergraph:
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
        for subj, pred, obj in rendergraph:
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
				<h3>Rendered Input</h3>
				<div id="myDiagramDiv" style="background-color: whitesmoke; border: solid 1px black; width: 100%; height: 700px"></div>
				<p>
				The Rendered intent created by INDIRA to call NSI. 
				</p>
				</div>
				</body>
				</html>"""
        file.write(secondpart)
        file.close()
    except:
        print("file writing error occured")
        sys.exit(0)

    #############################
    print ("Calling NSI......")
    # check if file exists
    try:
        os.remove('./nsibash.sh')
    except OSError:
        pass

    #cmd ='./test'
    # os.system(cmd)

    #test=subprocess.Popen(["..\..\opennsa\./onsa --help"],stdout=subprocess.PIPE)
    # output=test.communicate()[0]

    # need to extract data from graph
    locallysave_eps = []
    localsrcname = ""
    localdestname = ""

    for subj, pred, obj in rendergraph:
        #print subj, pred, obj
        if Literal(subj).lower() == 'connect':
            locallysave_eps.append(Literal(obj))
            #print obj
        if Literal(subj).lower() == 'disconnect':
            locallysave_eps.append(Literal(obj))
            #print obj
        if Literal(subj).lower() == 'transfer':
            locallysave_eps.append(Literal(obj))
        
        if pred == hasBandwidth:
            if Literal(obj).lower() == 'unlimited':
                localbwvalue = 100
            else:
                numberextracted = Literal(obj)
                #print numberextracted
                localbwvalue = int(numberextracted)
            #print localbwvalue
        if Literal(subj).upper() == 'SCHEDULESTART':
            year = 2016
            month = 11
            day = 13
            hr = 12
            minu = 00
            secs = 00
            localzone = 'GMT'
            # convertime=''

            # print subj
            if pred == hasDate:
                datestring = Literal(obj)
                year, month, day = datestring.split("-")
            if pred == hasTime:
                timestring_local = Literal(obj)
                hr, minu, secs = timestring_local.split(".")
            if pred == hasZone:
                localzone = Literal(obj).split("+")[0]

            convertzone = timezone(localzone)
            converttime = convertzone.localize(
                datetime(int(year), int(month), int(day), int(hr), int(minu), int(secs)))
            # print converttime
            converttime2 = converttime.astimezone(timezone('GMT'))
            # print converttime2

            converttime2 = str(converttime2)
            newdatensi = converttime2.split(" ")[0]
            timehalf = converttime2.split(" ")[1]
            newtimensi = timehalf.split("+")[0]
            newstarttime = newdatensi + "T" + newtimensi

            # print newstarttime

        if Literal(subj).upper() == 'SCHEDULESTOP':
            #print "stop"
            year = 2016
            month = 11
            day = 13
            hr = 17
            minu = 00
            secs = 00
            localzone = 'GMT'
            # convertime=''

            #print subj
            if pred == hasDate:
                datestring = Literal(obj)
                year, month, day = datestring.split("-")
            if pred == hasTime:
                timestring_local = Literal(obj)
                hr, minu, secs = timestring_local.split(".")
            if pred == hasZone:
                localzone = Literal(obj).split("+")[0]

            convertzone = timezone(localzone)
            converttime = convertzone.localize(
                datetime(int(year), int(month), int(day), int(hr), int(minu), int(secs)))
            #print converttime
            converttime2 = converttime.astimezone(timezone('GMT'))
            #print converttime2

            converttime2 = str(converttime2)
            newdatensi = converttime2.split(" ")[0]
            timehalf = converttime2.split(" ")[1]
            newtimensi = timehalf.split("+")[0]
            newstoptime = newdatensi + "T" + newtimensi

            #print newstoptime

            # remove after testing
#	localsrcname=locallysave_eps[0]
    #	localdestname=locallysave_eps[1]
    #print "Connection points: " + len(locallysave_eps)
    if len(locallysave_eps) >= 2:
        localsrcname = locallysave_eps[0]
        localdestname = locallysave_eps[1]
    else:
        print ("NSI called")

        #only takes two site names as arguments. Please start again!"

    time.sleep(2)
    globalidnsi = "urn:uuid:6e1f288a-5a26-4ad8-a9bc-eb91785cee15"
    #print localsrcname
    #print localdestname

    # HARD CODED VALUES

    hardsource = "es.net:2013::lbl-mr2:xe-9_3_0:+#1000"
    harddestination = "es.net:2013::bnl-mr2:xe-1_2_0:+#1000"

    ##########################

    #print "Creating bash file...."
    try:
        fname = './nsibash.sh'
       # print "h"
        file = open(fname, 'w')
        file.write("#!/bin/bash")
        file.write("\n")

        file.write("cd ../../opennsa")
        file.write("\n")
       # print "g"
        #print "constructing nsi commands...."
        params = "./onsa reserveprovision"
       # print params
        params = params + " -g " + globalidnsi
       # print params
        params = params + " -d " + harddestination  # localdestname
       # print params
        params = params + " -s " + hardsource  # localsrcname
       # print params
        params = params + " -b " + str(localbwvalue)
       # print params
       # print newstarttime
       # print newstoptime
        params = params + " -a " + newstarttime
       # print params
        params = params + " -e " + newstoptime
       # print params
        params = params + " -u https://nsi-aggr-west.es.net:443/nsi-v2/ConnectionServiceProvider"
        params = params + " -p es.net:2013:nsa:nsi-aggr-west"
        params = params + " -r canada.eh:2016:nsa:requester"
        params = params + " -h 198.128.151.17 -o 8443"
        params = params + " -l /etc/hostcert/muclient.crt -k /etc/hostcert/muclient.key"
        params = params + " -i /etc/ssl/certs/ -y -x -z -v -q;"
       # print params

        file.write(params)
        file.write("\n")
        file.write("exit;")
        file.close()
    except:
        pass
        #####print("file writing error occured")
       ### #sys.exit(0)

    #print "Running the bash file...."

    time.sleep(2)
    print ("\n\n")
    print ("OOPS! Something has gone horribly wrong!")
    return 1
    # os.chmod('./nsibash.sh',0755)
    # rc=call("./nsibash.sh",shell=True)


def rendertopology(u, rgraph):
    hasService = URIRef('ex:hasService')
    hasArguments = URIRef('ex:hasArguments')
    hasCondition = URIRef('ex:hasCondition')

    profiles = get_profiles(profilefile)
    owlschema = get_schema(schemafilelink)

    usr = u.split("'")
    retval = 0

    # check if asked topology ok or not
    for row in profiles:
        if row['name'].upper() == usr[1].upper():
            topologies = row['topology']

    flagchktopo = 0
    print ("Checking topology permissions...")
    for topo in topologies:
        #print "Topology permissions are:"
        #print topo
        if topo == '*':
            flagchktopo = 1

    topook = 0
    topoargslist = []
    possibleserviceslist = []

    for key in owlschema:
        for val in owlschema[key]:
            if key.upper() == "SERVICE":
                possibleserviceslist.append(val)
    # search for topology arguments
    for subj, pred, obj in rgraph:
        for s in possibleserviceslist:
            if str(subj).upper() == s:
                topoargslist.append(str(obj))

    print ("Topology asked for.....")
    print (topoargslist)
    flagstop = 0

    if len(topoargslist) < 2:
        print ("Sorry you need more than one site for establishing connections!")
        flagstop = 1

    if flagstop != 1:
        notfoundtopo = []
        if flagchktopo == 0:  # if all not allowed
            for askedtopo in topoargslist:
                found = 0
                # nftopo=askedtopo
                for topo in topologies:
                    if askedtopo.upper() == topo.upper():
                        found = 1
                if found == 0:
                    notfoundtopo.append(askedtopo)
        print ("From above, not allowed site(s) :")
        print (notfoundtopo)

    if len(notfoundtopo) > 0:
        print ("Sorry you dont have access to the following sites: ")
        print (notfoundtopo)
        flagstop = 1

    # repalcing NSI DTN code here from OSCARS topology endpoints

    endpointsfortopo = []
    if flagstop != 1:
        allinterfaces = []
        for askedtopo in topoargslist:
            print ("Getting NSI endpoint details for site (topology): " + askedtopo)
            ### commenting out old code with #%#
            #%#allinterfaces=get_endpoints(askedtopo)

            # HARDCODE
            # get_site_onsa(askedtopo)
            allinterfaces.append("es.net:2013::lbl-mr2:xe-9_3_0#1000")
            allinterfaces.append("es.net:2013::bnl-mr2:xe-9_3_0#1001")
            allinterfaces.append("es.net:2013::bnl-mr2:xe-9_3_0#1000")

            if len(allinterfaces) >= 0:
                # selecting one interface on random that in available
                # read current interfaces in use
                # get user time zone
                # currentusedinterfaces=get_current_interface_used(currentusefile)
                # if len(currentusedinterfaces)<=0:
                # 	print "No current interfaces used"
                # else:
                # 	for row in currentusedinterfaces:
                # 		if row['name'].lower()==askedtopo.lower():
                # 			endpointused=row['endpoint']
                # 			for ep in allinterfaces:
                # 				if endpointused==ep:
                # 					allinterfaces.remove(ep)

                # randomly select one item from endpoints:
                endpoint = random.choice(allinterfaces)
                #endpoint=allinterfaces[0]
                print ("adding :" + endpoint)

                # print endpoint
                endpointsfortopo.append(ServiceDetail(askedtopo, endpoint))
                # print "All interface details are:"
            if len(allinterfaces) <= 0:
                print ("Error: no interfaces found!!!")

    return endpointsfortopo


def rendertime(u, rgraph):

    # time values
    AFTERHOURS_val = 1700

    recordtimefns = []
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"

    for subj, pred, obj in rgraph:
        if str(subj).find("SCHEDULE") != -1:
            # can have more than one time condition
            recordtimefns.append(ServiceDetail(str(subj), str(obj)))

    # get user time zone
    profiles = get_profiles(profilefile)
    usr = u.split("'")
    tzone = ""

    for row in profiles:
        if row['name'].upper() == usr[1].upper():
            tzone = row['timezone']

    # update time values
    if len(recordtimefns) == 0:
        print ("No Time Condition found. Schedule to start asap....")
    else:
        print ("Time conditions found...")
        timestringafter = 0
        timestringnow = 0
        for a in recordtimefns:
            # print a.service
            # print a.args
            if a.args.upper() == "AFTERHOURS":
                a.args = AFTERHOURS_val
                now_time = datetime.now(timezone(tzone))
                new_time = now_time.replace(hour="17", minute="01")
                a.args = new_time.strftime(fmt)
                timestringafter = 1
            if a.args.upper() == "NOW":
                now_time = datetime.now(timezone(tzone))
                a.args = now_time.strftime(fmt)
                timestringnow = 1
                # if neither of the above
            if '->' in a.args:
                # print "found ->"
                date_str = a.args
                # print date_str
                date_str = date_str.replace("->", " ")
                # print date_str
                date_str = date_str.replace(".", ":")
                # print date_str
                time_tuple = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                datetime_obj_tz = time_tuple.replace(tzinfo=timezone(tzone))
                datetime_obj_tz = datetime_obj_tz.strftime(
                    "%Y-%m-%d %H:%M:%S %Z%z")
                # print datetime_obj_tz
                a.args = datetime_obj_tz

            print (a.args)

    print ("checking time values given are correct ....")
    start_flag = 0
    stop_flag = 0
    for a in recordtimefns:
        if a.service.upper() == "SCHEDULESTART":
            start = parser.parse(a.args)
            start_flag = 1
            #print start
        if a.service.upper() == "SCHEDULESTOP":
            stop = parser.parse(a.args)
            stop_flag = 1
            #print stop
    if start_flag == 1 and stop_flag == 1:
        diff = stop - start
        #print diff.total_seconds()
        if diff.total_seconds() > 0:
            print ("time duration is ok...")
        else:
            print ("sorry illegal times set")

    return recordtimefns


def renderbw(u, rgraph):

    profiles = get_profiles(profilefile)

    totalprofiles = len(profiles)
    # print totalprofiles

    usr = u.split("'")
    retval = 0

    for row in profiles:
        if row['name'].upper() == usr[1].upper():
            retval = row['bandwidth']
    return retval


def get_profiles(file_name):
    """ Read the profile.json file and loads profiles as objects
    Args:
        file_name (string): pathname of the profile.json file
    """
    profiledoc = json.loads(open(profilefile).read())
    # print(profiledoc)
    return profiledoc


def get_schema(sfile_name):
    schemadoc = json.loads(open(schemafilelink).read())
    # print(profiledoc)
    return schemadoc


def get_current_interface_used(current_filename):
    currentusedoc = json.loads(open(current_filename).read())
    return currentusedoc
