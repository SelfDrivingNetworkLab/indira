#!/usr/bin/env python

#Indira talks to human about network needs
import re
import random
import time
#import nltk
import pydot
#nltk.download()
import curses
import os
import sys
import json
import curses.textpad

#from nltk.corpus import treebank
#import numpy
#from nltk.tree import *
#import nltk.draw.tree.TreeView

#from nltk.tree import Tree
#from nltk.draw.tree import TreeView
import glob

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indi.intentmodules.intentmanager import intentmanagermain


from indi.knowledgelibrary.dtns import DTN
from indi.knowledgelibrary.dtns import Site
from indi.knowledgelibrary.globus import Globus
from indi.knowledgelibrary.dtns import get_sites
from indi.knowledgelibrary.dtns import get_dtn
import webbrowser

global gold
global apples
apples = 0
gold = 0
#use nltk http://www.nltk.org/

global flag_babble
flag_babble=0
global whileflag
global nwusername 
nwusername = None



reflections = {
    "am": "are",
    "was": "were",
    "i": "you",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "are": "am",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you"
}
 
psychobabble = [
 
 
 
    [r'Hello(.*)',
     ["Hello... I'm glad you could drop by today.",
      "Hi there... how are you today?",
      "Hello, how are you feeling today?"]],
 
   
   # [r'(.*) friend (.*)',
    # ["Tell me more about your friends.",
     # "When you think of a friend, what comes to mind?",
    #  "Why don't you tell me about a childhood friend?"]],
 
    [r'Yes',
     ["You seem quite sure.",
      "OK, but can you elaborate a bit?"]],
 
    [r'(.*) computer(.*)',
     ["Are you really talking about me?",
      "Does it seem strange to talk to a computer?",
      "How do computers make you feel?",
      "Do you feel threatened by computers?"]],
 
   
 
 
    [r'I want to connect (.*)',
     ["INDIRA> So you want to connect, can you give me the endpoints? hint: Endpoints = 'anl' 'bnl'\n",
      "INDIRA> So you want me to set this up - connection, can you give me endpoints? hint: Endpoints = 'sitename1' 'sitename2' \n"
      #"What would you do if you got {0}?",
      #"If you got {0}, then what would you do?"
      ]],

    [r'I want to disconnect (.*)',
     ["INDIRA> So you want to disconnect, give me the endpoints? hint: Endpoints = 'sitename1' 'sitename2'\n",
      "INDIRA> So you want me to set this up - disconnection, give me the endpoints? hint: Endpoints = 'sitename1' 'sitename2' \n"
      #"What would you do if you got {0}?",
      #"If you got {0}, then what would you do?"
      ]],

    [r'I want to transfer (.*)',
     ["INDIRA> So you want to transfer files. Tell me about the endpoints and direction \n(hint: \tpairs = sitename1->sitename2 )\n",
      "INDIRA> So you want me to set this up - transfer, tell me about the endpoints and direction \n(hint: \t pairs = sitename1->sitename2 )\n"
      #"What would you do if you got {0}?",
      #"If you got {0}, then what would you do?"
      ]],



    [r'help (.*)',
     ["INDIRA> I can configure network demands based on various QoS user needs. Working with NSI and Globus\n"
      #"What would you do if you got {0}?",
      #"If you got {0}, then what would you do?"
      ]],


    [r'done',
     ["INDIRA> I am AWESOME!",
      "INDIRA> Yeah all Done, time to party!"
      #"What would you do if you got {0}?",
      #"If you got {0}, then what would you do?"
      ]],

  
 
    [r'help',
     ["you can say:\n I want to connect endpoints,\n I want to disconnect endpoints, \n I want to transfer files ",
     # "Please consider whether you can answer your own question.",
     # "Perhaps the answer lies within yourself?",
      #"Why don't you tell me?"
      ]],
 
    [r'quit',
     ["Thank you for talking with me.",
      "Good-bye.",
      "Thank you, that will be $150.  Have a good day!"]],
 
    [r'(.*)',
     ["Something has gone wrong.",
     "Im not sure of what you are asking for..."
    #  "Let's change focus a bit... ,
      #"Can you elaborate on that?",
    ]]
]
 
 
def reflect(fragment):
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in reflections:
            tokens[i] = reflections[token]
    return ' '.join(tokens)
 
 
def analyze(nwuser, statement,n_or_g):
    #print "statement " + statement
    flag_babble=0
    fullintent=''
    # print "analyse"
    sites =" "

    word_pairs_found=0

    #if n_or_g=='n' or n_or_g=='N':
    if 'pairs' in statement.lower() or 'Pairs' in statement.lower() or 'pair' in statement.lower() or 'Pair' in statement.lower():
      word_pairs_found =1
        #endpointsstring= nltk.word_tokenize(statement)

        #print endpointsstring
      #  endpointsstring1=re.compile("'.*?'").findall(statement)
       
       # print endpointsstring1
    if word_pairs_found==1:
      #print statement
      statement=statement.replace("pairs", "")
      statement=statement.replace("Pairs", "")
      statement=statement.replace("pair", "")
      statement=statement.replace("pairs", "")
      statement=statement.replace("=", "")
      #print statement
      statement=statement.replace(" ", "")

      #print("INDIRA> Tell me about the endpoints and direction \n(hint: \t[sitename1->sitename2 sitename2->sitename3])\n")
      statementpairs = statement
      #print statementpairs
      #raw_input(nwuser +"> ") 
      #pairs=re.compile(" ").findall(statementpairs)
      endpointsite1=''
      endpointsite2=''
      firstsite=''
      secondsite=''
      #print "pairs"
      #print pairs 
      topograph = pydot.Dot(graph_type='digraph')
       
      #for connection in pairs:
      breakingconnection=statementpairs.split('->')
      firstsite=breakingconnection[0]
      firstsite=firstsite.replace("'","")
      secondsite=breakingconnection[1]
      secondsite=secondsite.replace("'","")
        #for site in endpointsstring1:
         #   site=site.replace("'","")
          #nodename='node'+firstsite
      nodename1=pydot.Node(firstsite, style="filled", fillcolor="green")
      topograph.add_node(nodename1)
      
          #nodename='node'+secondsite
      nodename2=pydot.Node(secondsite, style="filled", fillcolor="green")
      topograph.add_node(nodename2)
      topograph.add_edge(pydot.Edge(nodename1,nodename2))
          
      topograph.write_png('../templates/topology_graph.png')

      endpointsite1=firstsite
      endpointsite2=secondsite
      firstsite= " ".join(secondsite)
      #print "sites:"
      #print endpointsite1
      #print endpointsite2
      sites=endpointsite1+ " " + endpointsite2
      #print sites
        
        #print("INDIRA> Checking if you have any conditions associated with this intent")
        #print("INDIRA> Is there a bandwidth restriction (in bits/sec)? (hint: \t BW = 1000 , BW = unlimited")
        #bwcondition = raw_input(nwuser +"> ") 
      
      print ("INDIRA> OK cheers.......I am checking if I already have these links setup.....")

      fok=0
      with open("../../indi/knowledgelibrary/currentusage.json") as json_file:
        currentlinks = json.load(json_file)
        fok=1
      #check current ture or flase
      if fok==1:
        demosite1= endpointsite1
        demosite1=demosite1.replace("'","")
        demosite2= endpointsite2
        demosite2=demosite2.replace("'","")

        nowstart=0
        nowstop=0
        nowbw=0

        currentfound=0

        if len(currentlinks)>0:
          for row in currentlinks:
           # print row['start']
            if row['epname1'].lower()==demosite1.lower() and row['epname2'].lower()==demosite2.lower():
            #  print "found"
              currentfound=1
              nowstart=row['start']
              nowstop = row['stop']
              nowbw=row['bandwidth']
              nowzn=row['timezone']
            elif row['epname1'].lower()==demosite2.lower() and row['epname2'].lower()==demosite1.lower():
             # print "found"
              currentfound=1
              nowstart=row['start']
              nowstop = row['stop']
              nowbw=row['bandwidth']
              nowzn=row['timezone']
            else:
              s=1
              #print "notfound in local dictionary"
          if currentfound==1:
            print "INDIRA> I have found these provisions setup with following details:"
            print "Endpoint1    Endpoint2    Start time    Stop time     Bandwidth     (Time Zone)"
            print demosite1 + "\t" +demosite2+"\t"+nowstart+"\t"+nowstop+"\t"+nowbw+"\t"+nowzn
         
            print("\n\n")
            print "Do you want to use this provision? (Y/N)"
            g=raw_input(nwuser +"> ")
            if g=='Y' or g=='y':
              print "\nINDIRA> Great! Ill setup the file transfer with this provision...."

              print("INDIRA> Tell me about source and destination file or folders. Hint: '/www.txt->/test'")
              statementtransfer = raw_input(nwuser +"> ")

              print "Calling globus......"

              folderconnection=statementtransfer #re.compile("'.*?'").findall(statementtransfer)
                #print pairs
              # for folderconnection in folderpoints:
              breakingfolderconnection=folderconnection.split('->')
              firstlink=breakingfolderconnection[0]
              firstlink=firstlink.replace("'","")
              secondlink=breakingfolderconnection[1]
              secondlink=secondlink.replace("'","")
              s1_dtn=None
              s2_dtn=None

              gallsites = get_sites()
              #print sites
              for s in gallsites:
                if s.name == demosite1:
                  dtnslist= s.get_dtns()
                  s1_dtn=dtnslist[0]
                  #get dtn obj
                if s.name == demosite2:
                  dtnslist= s.get_dtns()
                  s2_dtn=dtnslist[0]

              if s1_dtn!=None and s2_dtn!=None:
                globuscall=s1_dtn.transfer(src_file=firstlink, dest_dtn=s2_dtn, dest_file=secondlink, nsi=True)
                #drawGlobusGraph(nwuser, s1_dtn.name, s2_dtn.name,firstpart, secondlink)
                #print globuscall
                #if 'True' in globuscall:
                print "Successful transfer: Check Globus Task ID:"
                print globuscall 
                return "done"
                #python dtns.py --globus-transfer-nsi lbl lbl-diskpt1 /1M.dat cern cern-diskpt1 /test1
                #(True, ' 9fa5f9f4-a6cb-11e6-9ad2-22000a1e3b52')
            else:
              print ("INDIRA> Alright, I shall set up a new link for you....")
              print("INDIRA> What conditions do you intent \n(hint: \t[condition bwnolimit isolated unfriendly])")
              statementcondition = raw_input(nwuser +"> ") 
              #print statementcondition
              if statementcondition =='start again':
                conversation()
              
              fullintent=fullintent+statementcondition

              print("INDIRA> Is there a time schedule with this intent. \n (hint: \tEnter dates in the form (YYYY-MM-DD->%H.%M.%S) or say [NOW] [AFTERHOURS]. \n(hint: [start 2008-11-10->17.53.59 stop 2008-11-20->17.53.59]\n Indira automatically converts time zones...")
              statementtime = raw_input(nwuser +"> ") 
              statementtime =statementtime.replace('start', 'schedulestart')

              statementtime =statementtime.replace('stop', 'schedulestop')
        
              #print statementtime
              fullintent=fullintent+ " " + statementtime

              print("INDIRA> OK... I am provisioning these intents, calling 'NSI', now!")
              #statementgn = raw_input(nwuser +"> ") 
              #print statementgn
              #fullintent=fullintent+' using '+ statementgn
          else: # if current is false
            time.sleep(2)
            print "\n\n\nINDIRA> OK.. I couldnt find any provisions for these endpoints. Let me set these up for you!"
            print("INDIRA> What conditions do you associate with this intent \n(hint: \t[condition bwnolimit isolated unfriendly])")
            statementcondition = raw_input(nwuser +"> ") 
            #print statementcondition
            if statementcondition =='start again':
              conversation()
            fullintent=fullintent+statementcondition

            print("INDIRA> Do you have a time schedule with this intent. Enter dates in the form (YYYY-MM-DD->%H.%M.%S) or say [NOW] [AFTERHOURS]. \n(hint: [start 2008-11-10->17.53.59 stop 2008-11-20->17.53.59]\n Indira will automatically figure out your time zones...")
            statementtime = raw_input(nwuser +"> ") 
            statementtime =statementtime.replace('start', 'schedulestart')
            statementtime =statementtime.replace('stop', 'schedulestop')
        
            fullintent=fullintent+ " " + statementtime
            print("INDIRA> I will provision you the links, using 'NSI', now!")

      flag_babble=1      


    if flag_babble==0:
      # print "calling babble"
      for pattern, responses in psychobabble:
        pattern=pattern.lower()
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
          response = random.choice(responses)
          return response.format(*[reflect(g) for g in match.groups()])
    
    if flag_babble==1:
      #print "Intent is collected!"
      #sites= " ".join(endpointsstring1)
      #sites=sites.replace("'","")
      #screen.addstr("INDIRA> Ive recorded your intent!\n")
      flag_babble=0
      return "FOR " + nwuser + " connect " + sites + " " + fullintent
      whileflag=False

    


def start():

    

    screen.clear()
  #  screen.border(0)
    
    
    screen.addstr("************************************************************\n");
    screen.addstr("*************************************************************\n");
    screen.addstr("  ##      ####   ##    ########    ###  ######        #####  \n")
    screen.addstr("  ##     ##  ##  ##   ##     ###   ##  ###  ###      ##  ##\n")
    screen.addstr("  ##    ##   ##  ##   ##     ####  ##  ###   ##     ###  ###\n")
    screen.addstr("  ##   ###   ##  ##  ##      ###   ##  #######     ######## \n")
    screen.addstr(" ###   ##    ## ##  ##      ###   ##  ##    ##    ###   ###\n" )
    screen.addstr(" ##   ##     ####  ###     ###   ##  ###    ###  ###    ###\n")
    screen.addstr("###   ##     ###   #########    ##   ##     ###  ##      ###\n")
    screen.addstr("###  ###     ###   #######     ###   ##     ### ###      ###\n")

    screen.addstr("Intent-based Network Deployment Renderer\n")
    screen.addstr("************************************************************\n");
    screen.addstr("Starting INDIRA to talk to the Network!\n")
   
    screen.addstr("***********************************\n");
    
    screen.addstr("Hello and welcome! My name is INDIRA\n")
    screen.addstr("If you want to quit, just say 'quit'\n")
    
   
    screen.addstr("What is you project name:")
    
    screen.refresh()
    name  = screen.getstr()
    #screen.addstr(1, 0, "[" + namesq + "]")
    screen.addstr("INDIRA> Welcome, "+ name +"!\n")
    screen.addstr("INDIRA> Is "+ name + " your network project name? (say Y/N)\n")
    newname = screen.getstr() 
    #raw_input("INDIRA> Is "+ name + " your network username? (say Y/N)\n")
    if newname =="Y" or newname == "y":
      nwusername=name
    elif newname =="N" or newname == "n":
      screen.addstr("Enter your network project name:\n")
      nwusername=  screen.getstr()       
      screen.addstr("INDIRA> Welcome, "+ nwusername +"!\n")
    else:
      screen.addstr("start again\n")

    #print "here"
    screen.clear()
    screen.addstr("INDIRA> OK lets begin. Say 'help' or 'start again' if stuck\n")
    curses.endwin()
    print "\n\n\n\n\n\n"
    print "******************************************************************"
    print "********************* INDIRA CHAT WINDOW ************************"

    try:
      conversation(nwusername)
    except:
      print "Shutting down!"

 

def conversation(nwusernameg):
    #choice = raw_input("Do you want to begin Y/N?")
    #print "INDIRA> I can do network reservation (N) or file transfer using globus (G)."
    #print "INDIRA> What do you want to do 'N' or 'G'?"
    #nsiorglobus=raw_input(nwusernameg +"> ")
    #if nsiorglobus=='N' or nsiorglobus=='n':

    print("INDIRA> OK. Tell me how you want as network intent. Hint say: 'I want to [connect] [disconnect] [transfer] files between sites '\n")    
    record =" "

    while True:
      statement = raw_input(nwusernameg +"> ")

      statementwords=statement.split()
      # for term in statementwords:
      #   if term.lower() == "connect":
      #     servasked="connect"
      #   if term.lower() == "disconnect":
      #     servasked="disconnect"
      #   if term.lower() == "transfer":
      #     servasked = "transfer"

      nsiorglobus ="n"
      try:
        record=analyze(nwusernameg, statement.lower(), nsiorglobus)
        print record

        if 'FOR' in record:
          print "INDIRA> Calling the intent engine now!"
          intentmanagermain(record)
          break

        if statement == "quit":
          break


      except: 
        print "Unexpected Error in Indira:", sys.exc_info()[0]
        print "Try Again!"

      
      #if 'done' in record:
        #print "done:)"

      # if nsiorglobus =='G' or nsiorglobus=='g':
      #   newname = raw_input("INDIRA> Is "+ nwusernameg + " your globus id user name? (Hint: gid@cli.globusonline.org)? (say Y/N)")
      # if newname =="Y" or newname == "y":
      #   nwusernameg=newname
      # elif newname =="N" or newname == "n":
      #   nwusernameg=  raw_input("Enter your globus id username:")      
      #   print("INDIRA> Welcome, "+ nwusernameg +"!")
      # else:
      #   print "start again"
      # print("INDIRA> OK. Tell me about your file transfers and endpoints. (hint: 'endpoints =')")
      
      # gtransfer=globusconversation(nwusernameg)
      # print gtransfer

      # if 'FOR' in gtransfer:
      #   print "INDIRA> calling intent engine"
      #   intentmanagermain(gtransfer)
      #   ### write a shell script to run at time     

    print ("INDIRA> you can view the details of intent rendered here: ")
    filename = '../templates/' + 'indira-gui-outputs.html'

    print filename
    #webbrowser.open_new_tab(filename)

   
    print "\nINDIRA> Do you have any more provisions needed? (Y/N)"
      
    yok=raw_input("> ")


    if yok=='Y' or yok=='y':
      conversation(nwusernameg)
    else:    
      print "INDIRA> OK.. im exiting "
    choice ='n'
    if choice == "N" or choice =="n":
      print ("INDIRA> Okay, bye bye...")
    


def globusconversation(nwusername):
  flag_babble=0
  fullintent=''
  print "printing all active endpints to choose from ANL#ep1 BNL#ep2"
  statement=raw_input(nwusername +">")

  if 'endpoint=' in statement.lower() or 'endpoints=' in statement.lower() or 'endpoints =' in statement.lower() or 'endpoint =' in statement.lower():
        #endpointsstring= nltk.word_tokenize(statement)

        #print endpointsstring
        endpointsstring1=re.compile("'.*?'").findall(statement)
        print endpointsstring1

        print("INDIRA> Tell me about the traffic direction \n(hint: \t[Pairs = 'All'] for bidirectional links, or \n\t[Pairs = 'sitename1->sitename2' 'sitename2->sitename3'])")
        statementpairs = raw_input(nwusername +"> ") 

        # if statementpairs =='start again':
        #   conversation()

        # pairs=re.compile("'.*?'").findall(statementpairs)
        # #print pairs
        # #fullintent=pairs
        # ###Drawing the topology graph
        # topograph = pydot.Dot(graph_type='digraph')
        # for site in endpointsstring1:
        #     site=site.replace("'","")
        #     nodename='node'+site
        #     nodename=pydot.Node(site, style="filled", fillcolor="green")
        #     topograph.add_node(nodename)
        # for connection in pairs:
        #     breakingconnection=connection.split('->')
        #     firstsite=breakingconnection[0]
        #     firstsite=firstsite.replace("'","")
        #     secondsite=breakingconnection[1]
        #     secondsite=secondsite.replace("'","")
        #     topograph.add_edge(pydot.Edge(firstsite,secondsite))
        # topograph.write_png('../templates/topology_graph.png')

        # #print("INDIRA> Checking if you have any conditions associated with this intent")
        #print("INDIRA> Is there a bandwidth restriction (in bits/sec)? (hint: \t BW = 1000 , BW = unlimited")
        #bwcondition = raw_input(nwuser +"> ") 


        print("INDIRA> Tell me about the file locations to move \t[Pairs = 'ANL#ep1/share/data.txt->BNL#ep2/~/myfile.txt'])")
        statementtransfer = raw_input(nwusername +"> ") 

        print("INDIRA> Checking if you have any conditions associated with this intent \n(hint: \t[condition bwnolimit isolated unfriendly])")
        statementcondition = raw_input(nwusername +"> ") 
        #print statementcondition
        if statementcondition =='start again':
          conversation()
        fullintent=fullintent+statementcondition

        print("INDIRA> Do you have a time schedule with this intent. Enter dates in the form (YYYY-MM-DD->%H.%M.%S) or say [NOW] [AFTERHOURS]. \n(hint: [start 2008-11-10->17.53.59 stop 2008-11-20->17.53.59]\n Indira will automatically figure out your time zones...")
        statementtime = raw_input(nwusername +"> ") 
        statementtime =statementtime.replace('start', 'schedulestart')

        statementtime =statementtime.replace('stop', 'schedulestop')
        
        print statementtime
        fullintent=fullintent+ " " + statementtime

        print("INDIRA> I will provision you links, using 'NSI', now!")
        #statementgn = raw_input(nwuser +"> ") 
        print "Intent is collected!"
        sites= " ".join(endpointsstring1)
        sites=sites.replace("'","")
        print "INDIRA> Ive recorded your intent!"
        return "FOR " + nwusername + " connect " + sites + " " + fullintent

        whileflag=False





sys.stdout.flush()
myscreen = curses.initscr()

myscreen.border(0)
myscreen.addstr(12, 25, "INDIRA in action!")
myscreen.refresh()
myscreen.getch()

#curses.endwin
screen = curses.initscr()

#print "curses"
#print curses
#print curses.wrapper
curses.wrapper(start())

#curses.endwin

#def curses_main(args):
 #   w    = curses.initscr()
  #  curses.echo()
   # while 1:
    #    w.addstr(0, 0, ">")
     
     #   w.clrtoeol()
      #  s   = w.getstr()
       # if s == "q":    break
        #w.insertln()
        #w.addstr(1, 0, "[" + s + "]")

#curses.wrapper(curses_main)