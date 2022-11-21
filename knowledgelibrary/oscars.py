""" This modules parses the JSON topology describing the links between ESnet and its sites.
"""

import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

#import urllib2
import argparse
import os
import ssl

import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from indira.profile.profile import get_profile
oscartopofile="../../indira/knowledgelibrary/sitetopo.json"


def get_sites(file):
    with (open(file)) as topo_file:
        topo = json.load(topo_file)
        nes = topo['data']['networkEntities']
        sites = {}
        for ne in nes:
            sites[ne['shortName']] = ne
        return sites


def get_endpoints(site):
    """
    Returns a list of endpoints that can be used in conjunction of NSI/OSCARS to
    provision a layer 2 circuit. There is not at the moment a source of truth for this
    information and this function is making some assumptions that are likely to be not
    be fully accurate. Do not rely on this code to perform operational functions.
    :param site: a network entity object representing the site.
    :return: list of interfaces.
    """

    global sites
    global oscars_topo
    
    sites = get_sites(oscartopofile)
    #print site
    
    oscars_topo = get_oscars_topo()
   # print oscars_topp
    #check of site exists
    sitename=site.lower()
    if not sitename in sites:
        print (sitename,"does not have known OSCARS endpoints.")
        return
    
    #print sitename
    interfaces = sites[sitename]['interfaces']
    #print interfaces

    ifs = {}
    for iface in interfaces:
        port = parse_interface(iface['interface'])
        if port == None:
            continue
        oscars_port = get_oscars_port(iface['device'],port)
        if oscars_port == None:
            continue
        urn = make_urn(iface['device'], port)
        if not urn in ifs:
            ifs[urn] = oscars_port
        continue
    return ifs

def make_urn(node, port):
    return "urn:ogf:network:domain=es.net:node=" + node + ":port=" + port + ":link=*"


def resolve(site,profile=None):
    '''
    Returns the OSCARS URN of the port connected to the site that has the largest capacity.
    :param site:
    :return:
    '''
    endpoints = get_endpoints(site)
    if len(endpoints) == 0:
        return None
    max_capacity = 0
    endpoint = None
    for (urn, oscars_port) in endpoints.items():
        capacity = int(oscars_port['capacity'])
        if capacity > max_capacity:
            max_capacity = capacity
            endpoint = urn
    return urn

def print_site_endpoints(site):
    print (site['fullName'], "(", site['shortName'], ")")
    endpoints = get_endpoints(site)
    seen = []
    if len(endpoints) == 0:
        print ("\t No OSCARS endpoints")
    else:
        for (urn, oscars_port) in endpoints.items():
            if urn in seen:
                continue
            capacity = oscars_port['capacity']
            print ("\t", urn, '(' + str(int(capacity) / 1000000000) + 'G)')
            seen.append(urn)

def list():
    sorted = sites.keys()
    sorted.sort()
    for (site_name) in sorted:
        site = sites[site_name]
        print_site_endpoints(site)
        print

def parse_interface(interface):
    dot = interface.split('.')
    under = interface.split('_')
    hyphen = interface.split('-')
    slash = interface.split('/')

    parsed = None
    if  len(slash) == 3:
        # Juniper port signature. Strip trailing vlan.
        parsed = dot[0]
    elif len(under) == 3:
        # ALU port signature
        parsed = hyphen[1]
        parsed = parsed.replace("_", "/")
        # Verifies that it seems valid
        try:
            int(parsed[0])
        except ValueError:
            parsed = None
    return parsed

def get_oscars_port(router,router_port) :
    nodes = oscars_topo['domains'][0] ['nodes']
    for node in nodes:
        node_id = node['id'].split(':')[4].split('=')[-1]
        if node_id != router:
            continue
        ports = node['ports']
        for port in ports:
            port_id = port['id'].split(':')[5].split('=')[-1]
            if port_id != router_port:
                continue
            links = port['links']
            for link in links:
                if 'vlanRangeAvailability' in link:
                    return port
    return None

def get_oscars_topo():

    #new ssl command
    context=ssl._create_unverified_context()

    req = urllib2.Request('http://oscars.es.net/topology-publisher')
        
    try:
        retfile=urllib2.urlopen(req, context=context)
    except urllib2.HTTPError as e:
        print (e.code)
        print (e.read()) 
    
    return json.load(retfile)

def do_cli():

    global sites

    parser = argparse.ArgumentParser()

    parser.add_argument("--endpoints", nargs=1,help="Prints all ESnet's endpoint to a given site.")
    parser.add_argument("--resolve", nargs=1, help="Prints ESnet's endpoint to a given site.")
    parser.add_argument("--show", nargs=1, help="Print all links to a given site.")
    parser.add_argument("--list", nargs='*', help="Displays all sites links.")

    args = parser.parse_args()

    if args.endpoints != None:
        site_name = args.endpoints[0]
        if not site_name in sites:
            print (site_name,"does not have known OSCARS endpoints.")
            return
        print_site_endpoints(sites[site_name])
    elif args.resolve != None:
        site_name = args.resolve[0]
        if not site_name in sites:
            print ("unknown site",site_name)
        else:
            endpoint = resolve(sites[site_name])
            if endpoint == None:
                print ("No link to ",site_name)
            else:
                print (endpoint)
    elif args.show != None:
        site_name = args.show[0]
        if not site_name in sites:
            print (site_name,"unknown site",site_name)
            return
        print_site_endpoints(sites[site_name])
    elif args.list != None:
        list()

if __name__ == "__main__":
  
    

    this_dir = os.path.split(__file__)[0]
    site_topo_file_path = os.path.join(this_dir, "sitetopo.json")
    sites = get_sites(site_topo_file_path)
    oscars_topo = get_oscars_topo()

do_cli()
#get_endpoints('ANL')