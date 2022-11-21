### Does the following functions:
### 1) Converts the incoming query into list of services and their arguments 
#### 2) Checks the graph of query with schema

import random
import json
import indi.knowledgelibrary
from rdflib import ConjunctiveGraph, Namespace, exceptions

from rdflib import URIRef, RDFS, RDF, BNode
from rdflib import Graph, Literal

from rdflib.namespace import DC, FOAF
from rdflib.tools.rdf2dot import rdf2dot
from graphviz import Digraph

from pprint import pprint

schemafilelink= "../../indi/knowledgelibrary/intentowlschema.json"

# intentowldata = {
#   "profile": [
#     "args", "args2", "args3"
#   ],
#   "service": [
#     "CONNECT", "DISCONNECT","VLAN", "TAP"
#     ],
#   "condition": [
#     "bwnolimit","isolated","unfriendly","SCHEDULESTART","SCHEDULEDURATION","SCHEDULESTOP"
#     ],
#   "bwnolimit": [
#     "nobwlimit", "nolimit"
#     ],
#    "unfriendly":[
#     "notcpdata","notcppackets"
#     ],
#    "isolated":[
#     "isolation","isolate"
#     ],
#     "SCHEDULESTART":[
#     "start","starttime", "begin"
#     ],
#     "AFTERHOURS":[
#     "afterwork","afterwards", "after"
#     ],
#     "NOW":[
#     "present","presently"
#     ]
# }


  
    
class ServiceDetail:
  __slots__=["service", "args"]

  def __init__(self,service,args):
      self.service=service
      self.args=args

def parseintent(indiquery):

  print ("############## Intent Engine #########################")
  print ("\nparsing intent: " + indiquery)
  #tokenize the input string
  servicesneeded=indiquery.split(" ")
  #print "services identified: " 
  #print servicesneeded  #this is a list of strings
  construct=[] 
 
  #parse with the json file
  with open("../../indi/knowledgelibrary/schema/indiservices.json") as json_file:
      jsonpacket = json.load(json_file)
      
  tempstring=[]

  servicefound="DUMMY"

  for idx, word in enumerate(servicesneeded):
    capsword=word.upper()
    flag=1
    argsfound=tempstring
    for s in jsonpacket["service"]:      
      if capsword == s["name"]:
        savestring=tempstring
        construct.append(ServiceDetail(servicefound,argsfound))
        flag=0
        tempstring=[]
        servicefound=capsword
    if flag==1:
      tempstring.append(word)
  #add the last element
  construct.append(ServiceDetail(servicefound,argsfound))
  return(construct)

def checkwithschema(inputquerygraph,user):

  print ("Checking schema....")
  service = URIRef('ex:service')
  hasService = URIRef('ex:hasService')
  hasArguments = URIRef('ex:hasArguments')
  hasCondition = URIRef('ex:hasCondition')
  #for subj, pred, obj in inputquerygraph:
   # print subj, pred, obj

  schema=json.loads(open(schemafilelink).read())
  #schema=json.loads(jsonschemadata)

  
  #pprint(schema)  

  #start creating new graph which is checked
  newinputgraph = ConjunctiveGraph()
  newnodeString=Literal(user)
  newNode=BNode(newnodeString)
 
  servicecount=0
 
  #checking services in intent query
  servicelist=[]
  newServiceData=[]
  for subj, pred, obj in inputquerygraph:
    if pred == hasService:
      stringobj=str(obj)
      servicelist.append(stringobj)
     # print "**** " + subj + " " + obj
      #print out attributes and save them
      
  conflictservice=[]
  for key in schema:
    for v in schema[key]:
      if key.upper() == "SERVICE":
        #print key, v
        for c in servicelist:
          if str(v)==c:
            conflictservice.append(c)

  conflictflag=0

  if len(conflictservice)==0:
    print ("No services asked for! please check")
    conflictflag=1

  if len(conflictservice)>1:
    print ("You have conflicting services asked for! please check")
    print (conflictservice)
    print (servicelist)
    conflictflag=1

  if conflictflag==0:
      newinputgraph.add((newNode,hasService,Literal(conflictservice[0]))) 

      #add its elements:
      for subj, pred, obj in inputquerygraph:
        if str(subj) == conflictservice[0]:
          stringobj=str(obj)
          newinputgraph.add((subj,hasArguments,Literal(stringobj))) 




  #MK: found error here

  #first replace likable words to condition arguments

  for subj, pred, obj in inputquerygraph:
    for key in schema:
      for v in schema[key]:
        if v == str(obj):
          if key.upper()!="CONDITION" and key.upper() !="SERVICE":
            print ("found similar word")
            print (key, v)
            print (len(inputquerygraph))
            inputquerygraph.remove((subj, pred, obj))
            inputquerygraph.add((subj, pred, Literal(key)))
            print (len(inputquerygraph))
          #for c in servicelist:
           # if str(v)==c:
            #  conflictservice.append(c)

  #checking conditions dont conflict
  conflictcondition=[] #no conflicts within the 6 elements
  for subj, pred, obj in inputquerygraph:
    for key in schema:
      for v in schema[key]:
        if key.upper() == "CONDITION":
          if v==str(obj):
            conflictcondition.append(str(obj))
  
  #print "found conditions:"
  #print conflictcondition 
  if len(conflictcondition)>0:
    #add elements to new graph
    for c in conflictcondition:
      newinputgraph.add((newNode,hasCondition,Literal(c))) 
  
      #add arguments to conditions
      for subj, pred, obj in inputquerygraph:
        if str(subj) == c:
          newinputgraph.add((subj,hasArguments,Literal(str(obj))))


  print ("Graph constructed in memory ....")
  #for subj, pred, obj in inputquerygraph:
    #print subj, pred, obj      

  #printing new graph:
  dot=Digraph(comment='Parsed Intent')
  for subj, pred, obj in newinputgraph:
    dot.node(subj, subj)
    dot.node(obj,obj)
    dot.edge(subj,obj, pred, constraint='false')

  #print(dot.source)
  dot.format='png'
  dot.render('../static/parsedintent.dot', view=False)
  ##########
  print ("Creating parsed intent in html output....")
  try:
    fname='../templates/parsedintent.html'
    file=open(fname,'w')
    firstpart="""<!DOCTYPE html>
    <html>
    <head>
    <title>Parsed Intent</title>
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
    cnode=0
    

    # create a list of ids for plotting the js graph
    uniqueidlist=[]
    for subj, pred, obj in newinputgraph:
      flagnodefound=0
      for j in uniqueidlist:
        if Literal(subj)==j:
          flagnodefound=1
      if flagnodefound==0:
        uniqueidlist.append(Literal(subj))

    for subj, pred, obj in newinputgraph:
      flagnodefound=0
      for j in uniqueidlist:
        if Literal(obj)==j:
          flagnodefound=1
          #print "found name " + j
      if flagnodefound==0:
        #print obj
        uniqueidlist.append(Literal(obj))
    # adding links
    
    nodeDAstring=''
    linkDAstring=''
    tempstr=""
    for j in uniqueidlist:
      #print nodeDAstring
      #print uniqueidlist.index(j)
      checkcommas=j.replace("'", "")

      tempstr="{ key:" + str(uniqueidlist.index(j)) + ", text: '"+ checkcommas +"' },"
      #print tempstr
      nodeDAstring += tempstr
    
    tempstr=""
    for subj, pred, obj in newinputgraph:
      #print uniqueidlist.index(Literal(subj)), uniqueidlist.index(Literal(obj)), pred
      tempstr="{ from:"+ str(uniqueidlist.index(Literal(subj))) +", to:"+ str(uniqueidlist.index(Literal(obj)))  +", text: '"+ Literal(pred) +"'}," 
      linkDAstring +=tempstr

      
  
    file.write("""   var nodeDataArray = [""")
    
    file.write(nodeDAstring)
    
    
    file.write("{} ];")
    file.write("    var linkDataArray = [")
    file.write(linkDAstring)
    file.write("{} ];")
    secondpart="""    
        myDiagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
        }
        </script>
        </head>
        <body onload="init()">
        <div id="sample">
        <h3>Parsed Intent</h3>
        <div id="myDiagramDiv" style="background-color: whitesmoke; border: solid 1px black; width: 100%; height: 700px"></div>
        <p>
        The intermediate parsing of intent, removing likable conditions, conflicting services and correcting some provisions.
        </p>
        </div>
        </body>
        </html>"""
    file.write(secondpart)
    file.close()
  except:
    print("file writing error occured")
    sys.exit(0)
  ###########



  if conflictflag==1:
    emptygraph=ConjunctiveGraph()
    return emptygraph

  return newinputgraph
