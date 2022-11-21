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


 
 
def analyze(statement):
    flag_babble=0
    fullintent=''
    sites =" "

    word_pairs_found=0

    if 'help' in statement.lower():
        print("--addintent [input parameters]: to create intents")
        print("--list: to print all intents")
        return

    if 'list' in statement.lower() or 'List' in statement.lower():
        print ("INDIRA> I am checking my intent list")
        fok=0

        with open("../../indi/knowledgelibrary/currentusage.json") as json_file:
            currentlinks = json.load(json_file)
            fok=1

            if fok==1:
                if len(currentlinks)>0:
                    print("INDIRA> Listing intents:")
                    print("Endpoint1" + "\t" +"Endpoint2" + "\t" +"Start time" + "\t" +"Stop time" + "\t" +"Bandwidth" + "\t" +"(Time Zone)")
                    for row in currentlinks:
                        currentfound=1
                        nowstart=row['start']
                        nowstop = row['stop']
                        nowbw=row['bandwidth']
                        nowzn=row['timezone']
                        demosite1=row['epname1']
                        demosite2=row['epname2']
                        print(demosite1 + "\t" +demosite2+"\t"+nowstart+"\t"+nowstop+"\t"+nowbw+"\t"+nowzn)
        json_file.close()
        return 
        #"list printed"

    if 'addintent' in statement.lower():
    	print("INDIRA> State you project id: ")
    	nuser=input(">")
    	print("INDIRA> State your endpoints and direction \n(hint: \t[sitename1->sitename2 sitename2->sitename3])\n")
    	pairs=input(nuser+">")
    	print("INDIRA> State your intended action \n(hint: \t[Connect, Transfer]\n")
    	action=input(nuser+">")
    	print("INDIRA> What are the conditions \n(hint: \t[condition bwnolimit isolated unfriendly])")
    	statementcondition = input(nuser +"> ")
    	
    	print("INDIRA> Time schedule with this intent. \n (hint: \tEnter dates in the form (YYYY-MM-DD->%H.%M.%S) or say [NOW] [AFTERHOURS]. \n(hint: [start 2008-11-10->17.53.59 stop 2008-11-20->17.53.59]\n Indira automatically converts time zones...")
    	statementtime = input(nuser +"> ")

    	#add to current file
    	endpointsite1=''
    	endpointsite2=''
    	firstsite=''
    	secondsite=''

    	breakingconnection=pairs.split('->')
    	firstsite=breakingconnection[0]
    	firstsite=firstsite.replace("'","")
    	secondsite=breakingconnection[1]
    	secondsite=secondsite.replace("'","")

    	#####checking previous intents

    	print ("INDIRA> Checking previous intents.....")

    	with open("../../indi/knowledgelibrary/currentusage.json") as json_file:
    		currentlinks = json.load(json_file)
    	
    	currentfound=0

    	if len(currentlinks)>0:

    		nowstart=0
    		nowstop = 0
    		nowbw=0
    		nowzn=0

    		for row in currentlinks:
    		# print row['start']

    			if row['epname1'].lower()==firstsite.lower() and row['epname2'].lower()==secondsite.lower():
    			#  print "found"
    				currentfound=1
    				nowstart=row['start']
    				nowstop = row['stop']
    				nowbw=row['bandwidth']
    				nowzn=row['timezone']

    			elif row['epname1'].lower()==firstsite.lower() and row['epname2'].lower()==secondsite.lower():
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
    			print ("INDIRA> Found following provisions:")
    			print ("Endpoint1" + "\t" +"Endpoint2" + "\t" +"Start time" + "\t" +"Stop time" + "\t" +"Bandwidth" + "\t" +"(Time Zone)")
    			print (firstsite + "\t" +secondsite+"\t"+nowstart+"\t"+nowstop+"\t"+nowbw+"\t"+nowzn)
    			print("\n\n")

    			print("INDIRA> Tell me about source and destination file or folders. Hint: '/www.txt->/test'")
    			statementtransfer = raw_input("> ")

    			print ("Calling globus......")

    			folderconnection=statementtransfer #re.compile("'.*?'").findall(statementtransfer)#print pairs# for folderconnection in folderpoints:
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
    				if s.name == firstsite:
    					dtnslist= s.get_dtns()
    					s1_dtn=dtnslist[0]
    					#get dtn obj
    				if s.name == secondsite:
    					dtnslist= s.get_dtns()
    					s2_dtn=dtnslist[0]

    			if s1_dtn!=None and s2_dtn!=None:
    				globuscall=s1_dtn.transfer(src_file=firstlink, dest_dtn=s2_dtn, dest_file=secondlink, nsi=True)
    				print ("Successful transfer: Check Globus Task ID:")
    				print (globuscall) 
    				return "done"
    		else:
    			print("INDIRA> Setting up intent....")
    			newdata={'epname1': firstsite,'epname2': secondsite, 'bandwidth': '500', 'start': '2017-04-15->0900', 'stop': '2017-04-15->1700', 'timezone': 'GMT'}
    			newelement={}

    			with open('../../indi/knowledgelibrary/currentusage.json') as jfile:
    				newelement=json.load(jfile)
    				newelement.append(newdata)
		    	#print"four"

    			with open('../../indi/knowledgelibrary/currentusage.json', 'w') as jfile:
    				jfile.write(json.dumps(newelement))
    			#jfile.write(json.dump(newdata))
    			#json.dump(newelement, jfile)

    			#print "two"
    			fullintent= "FOR " + nuser +" connect " +firstsite + " " +secondsite+ " " +statementcondition+" " +statementtime
    			fullintent = fullintent.replace('start', 'schedulestart')
    			fullintent = fullintent.replace('stop', 'schedulestop')

    			return fullintent

    

def start():

    

  #   screen.clear()
  # #  screen.border(0)
    
    
  #   screen.addstr("************************************************************\n");
  #   screen.addstr("*************************************************************\n");
  #   screen.addstr("  ##      ####   ##    ########    ###  ######        #####  \n")
  #   screen.addstr("  ##     ##  ##  ##   ##     ###   ##  ###  ###      ##  ##\n")
  #   screen.addstr("  ##    ##   ##  ##   ##     ####  ##  ###   ##     ###  ###\n")
  #   screen.addstr("  ##   ###   ##  ##  ##      ###   ##  #######     ######## \n")
  #   screen.addstr(" ###   ##    ## ##  ##      ###   ##  ##    ##    ###   ###\n" )
  #   screen.addstr(" ##   ##     ####  ###     ###   ##  ###    ###  ###    ###\n")
  #   screen.addstr("###   ##     ###   #########    ##   ##     ###  ##      ###\n")
  #   screen.addstr("###  ###     ###   #######     ###   ##     ### ###      ###\n")

  #   screen.addstr("Intent-based Network Deployment Renderer\n")
  #   screen.addstr("************************************************************\n");
  #   screen.addstr("Starting INDIRA to talk to the Network!\n")
   
  #   screen.addstr("***********************************\n");
    
  #   screen.addstr("Hello and welcome! My name is INDIRA\n")
  #   screen.addstr("If you want to quit, just say 'quit'\n")
    
   
  #   #screen.addstr("What is you project name:")
    
  #   screen.refresh()
  #   #name  = screen.getstr()
  #   #screen.addstr(1, 0, "[" + namesq + "]")
  #  # screen.addstr("INDIRA> Welcome, "+ name +"!\n")
  #  # screen.addstr("INDIRA> Is "+ name + " your network project name? (say Y/N)\n")
  #  # newname = screen.getstr() 
  #   #raw_input("INDIRA> Is "+ name + " your network username? (say Y/N)\n")
  #  # if newname =="Y" or newname == "y":
  #  #   nwusername=name
  #  # elif newname =="N" or newname == "n":
  #  #   screen.addstr("Enter your network project name:\n")
  #  #   nwusername=  screen.getstr()       
  #  #   screen.addstr("INDIRA> Welcome, "+ nwusername +"!\n")
  #  # else:
  #  #   screen.addstr("start again\n")

  #   #print "here"
  #   screen.clear()
   # screen.addstr("INDIRA> OK lets begin. Say 'help' or 'start again' if stuck\n")
   # curses.endwin    print ("\n\n\n\n\n\n")
    print ("******************************************************************")
   # print "********************* INDIRA CHAT WINDOW ************************"

    print ("************************************************************")
    print ("  ##      ####   ##    ########    ###  ######        #####  ")
    print ("  ##     ##  ##  ##   ##     ###   ##  ###  ###      ##  ##")
    print ("  ##    ##   ##  ##   ##     ####  ##  ###   ##     ###  ###")
    print ("  ##   ###   ##  ##  ##      ###   ##  #######     ######## ")
    print (" ###   ##    ## ##  ##      ###   ##  ##    ##    ###   ###")
    print (" ##   ##     ####  ###     ###   ##  ###    ###  ###    ###")
    print ("###   ##     ###   #########    ##   ##     ###  ##      ###")
    print ("###  ###     ###   #######     ###   ##     ### ###      ###")

    print ("Intent-based Network Deployment Renderer")
    print ("************************************************************")
    print ("Starting INDIRA to talk to the Network!")
   
    print ("***********************************")
    print ("\n")
    conversation()
    try:
      conversation()
    except:
      print ("Shutting down!")

 

def conversation():
    #choice = raw_input("Do you want to begin Y/N?")
    #print "INDIRA> I can do network reservation (N) or file transfer using globus (G)."
    #print "INDIRA> What do you want to do 'N' or 'G'?"
    #nsiorglobus=raw_input(nwusernameg +"> ")
    #if nsiorglobus=='N' or nsiorglobus=='n':

    print("INDIRA> Type help if required...")
    record = " "

    while True:
    	statement = input("> ")
    	try:
    		record=analyze(statement.lower())
    		#print record

    		if 'FOR' in record:
    			print ("INDIRA> Calling the intent engine now!")
    			intentmanagermain(record)
    			break

    		if statement == "quit":
    			break
    	except:
    		print ("..") 
            #Unexpected Error in Indira:", sys.exc_info()[0]
    		#print "Try Again!"

    print ("INDIRA> you can view the details of intent rendered here: ")
    filename = '../templates/' + 'indira-gui-outputs.html'
    print (filename)
    #webbrowser.open_new_tab(filename)
    print ("\nINDIRA> Do you have any more provisions needed? (Y/N)")
    yok=raw_input("> ")

    if yok=='Y' or yok=='y':
    	conversation(nwusernameg)
    else:
    	print ("INDIRA> OK.. im exiting ")
    	choice ='n'
    	if choice == "N" or choice =="n":
    		print ("INDIRA> Okay, bye bye...")


def globusconversation(nwusername):
  flag_babble=0
  fullintent=''
  print ("printing all active endpints to choose from ANL#ep1 BNL#ep2")
  statement=raw_input(nwusername +">")

  if 'endpoint=' in statement.lower() or 'endpoints=' in statement.lower() or 'endpoints =' in statement.lower() or 'endpoint =' in statement.lower():
        #endpointsstring= nltk.word_tokenize(statement)

        #print endpointsstring
        endpointsstring1=re.compile("'.*?'").findall(statement)
        print (endpointsstring1)

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
        
        print (statementtime)
        fullintent=fullintent+ " " + statementtime

        print("INDIRA> I will provision you links, using 'NSI', now!")
        #statementgn = raw_input(nwuser +"> ") 
        print ("Intent is collected!")
        sites= " ".join(endpointsstring1)
        sites=sites.replace("'","")
        print ("INDIRA> Ive recorded your intent!")
        return "FOR " + nwusername + " connect " + sites + " " + fullintent

        whileflag=False





sys.stdout.flush()
start()
#myscreen = curses.initscr()

#myscreen.border(0)
#myscreen.addstr(12, 25, "INDIRA in action!")
#myscreen.refresh()
#myscreen.getch()

#curses.endwin
#screen = curses.initscr()

#print "curses"
#print curses
#print curses.wrapper
#curses.wrapper(start())

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