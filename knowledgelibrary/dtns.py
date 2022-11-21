""" ESnet production DTN topology

"""

import json
import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from indira.knowledgelibrary.globus import Globus, Endpoint


class DTNConnector(object):
    """A DTNConnector is responsible for pairing Globus endpoints and 
    layer 2 network topology that can be provisionned either by NSI
    or OSCARS services.s 
    """
    def __init__(self, dtn, globus_endpoint, nsi_endpoint, oscars_endpoint):
        self.globus_endpoint = globus_endpoint
        self.nsi_endpoint = nsi_endpoint
        self.oscars_endpoint = oscars_endpoint
        self.dtn = dtn
        self.vlan = self.globus_endpoint.name.split('VLAN')[-1].strip().split(' ')[0].strip()
        self.name = dtn.name + '-' + self.vlan
        self.connected_to = None

    def is_connected(self):
        """Checks if the DTNConnector is connected to a remote site
        
        Returns:
            boolean: Returns True if the DTNConnector is connected, False otherwise
        """
        return self.connected_to != None


    def get_remote_connector(self, dtn):
        """Connects to another 
        
        Args:
            dtn (globus.Globus): globus
        
        Returns:
            DTNConnector: remote DTN Connector or None if connect failed.
        """
        for connector in dtn.connectors:
            if connector.vlan == self.vlan:
                return connector
        return None

    def transfer(self, src_file, dest_dtn, dest_file):
        """Summary
        
        Args:
            src_file (TYPE): Description
            dest_dtn (TYPE): Description
            dest_file (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        dest_connector = self.get_remote_connector(dtn=dest_dtn)
        res = self.dtn.globus.transfer(src_endpoint=self.globus_endpoint,
                                       dest_endpoint=dest_connector.globus_endpoint,
                                       src_file=src_file,
                                       dest_file=dest_file)
        return res


    def disconnect(self):
        """Disconnects the current connection
        Returns: True if successful, False otherwise.
        
        """
        if not self.connected_to:
            return False
        self.connected_to = None

    def __str__(self):
        res = "Share name: " + str(self.name) + "\n"
        res += "Globus share:\n\t" + self.globus_endpoint.name +"\n\t"
        res += self.globus_endpoint.legacy_name + "\n"
        res += "NSI: " + self.nsi_endpoint + "\n"
        res += "OSCARS: " + self.oscars_endpoint + "\n"
        res += "\n"
        return res

    def __repr__(self):
        return self.__str__()


class Site(object):
    """Defines a simulated site
    """
    def __init__(self, name, globus=None, domain='es.net'):
        """initializes
        
        Args:
            name (str): site name ('lbl','bnl','anl','cern')
            globus (globus.Globus, optional): globus
            domain (str, optional): default is 'es.net'
        """
        self.name = name
        self.domain = domain
        self.globus = globus

    def get_dtns(self):
        """Returns the DTN's of this site
        
        Returns:
            TYPE: Description
        """
        sites = load_sites()
        dtns = []
        if self.name in sites:
            for dtn in sites[self.name]:
                dtn = DTN(name=dtn['name'], site_name=self.name, globus=self.globus)
                dtns.append(dtn)
            return dtns
        else:
            return None

    def __str__(self):
        res = "Site: " + self.name + "\n"
        dtns = self.get_dtns()
        if dtns is None or len(dtns) == 0:
            res += "No Data Transfer Nodes at that site "
        else:
            for dtn in dtns:
                res += str(dtn)
            res += "\n"
        return res

    def __repr__(self):
        return self.__str__()   

class DTN(object):
    """Class defining an ESnet Data Transfer Node
    """
    def __init__(self, name, site_name, domain='es.net', globus=None):
        """
        Args:
            name (str): DTN name (i.e lbl-diskpt1)
            site_name (TYPE): Description
            domain (str), optional): domain name (default 'es.net').
            globus (globus.Globus), optional): Globus
        """
        self.name = name.split('.' + domain)[0]
        self.site_name = site_name
        self.domain = domain
        self.connectors = []
        self.default_endpoint = None
        if globus is None:
            self.globus = Globus()
        else:
            self.globus = globus
        json_sites = load_sites()
        json_dtn = None
        full_dtn_name = self.name + '.' + self.domain
        for (json_site_name, json_site) in json_sites.items(): 
            if json_site_name != site_name:
                continue
            for tmp_json_dtn in json_site:
                if tmp_json_dtn['name'] == full_dtn_name:
                    json_dtn = tmp_json_dtn
                    break
        if json_dtn != None:
            self.default_endpoint = Endpoint(name="Default Endpoint", globus=globus)
            self.default_endpoint.legacy_name = json_dtn['default-endpoint']
            self.default_read_endpoint = Endpoint(name="Default Read Endpoint", globus=globus)
            self.default_read_endpoint.legacy_name = json_dtn['default-read-endpoint']
            endpoints = json_dtn['endpoints']
            for endpoint in endpoints:
                router_port = get_router_port(endpoint=endpoint)
                nsi_endpoint = to_nsi(router_port)
                oscars_endpoint = to_oscars(router_port)
                globus_endpoints = self.get_globus_endpoints(vlan=router_port['vlan'])
                if len(globus_endpoints) > 0:
                    connector = DTNConnector(dtn=self,
                                             nsi_endpoint=nsi_endpoint,
                                             oscars_endpoint=oscars_endpoint,
                                             globus_endpoint=globus_endpoints[0])
                    connector.connected_to = endpoint['connected_to']
                    self.connectors.append(connector)

    def get_globus_endpoints(self, vlan=None):
        """Returns a list of globus endpoints that can be used for
        this DTN
        
        Args:
            vlan (str, optional): VLAN
        
        Returns:
            list: list of globus endpoints.
        
        Deleted Parameters:
            dtn_name (str): DTN name
        """
        res = self.globus.endpoints_search('iNDIRA-SHARE')
        endpoints = []
        site_name = self.site_name.upper()
        for endpoint in res:
            if site_name in endpoint.name:
                if vlan != None:
                    if vlan != endpoint.name.split('VLAN')[-1].strip().split(' ')[0]:
                        continue
                endpoints.append(endpoint)
        return endpoints

    def transfer(self, src_file, dest_dtn, dest_file, nsi=False):
        """Summary
        
        Args:
            src_file (TYPE): Description
            dest_dtn (TYPE): Description
            dest_file (TYPE): Description
            nsi (bool, optional): Description
        
        Returns:
            TYPE: Description
        """
        res = None
        if nsi:
            for connector in self.connectors:
                if connector.connected_to == dest_dtn.site_name:
                    res = connector.transfer(src_file=src_file,
                                             dest_dtn=dest_dtn,
                                             dest_file=dest_file)
                    return res
            return False, "No NSI connection."
        else:    
            if src_file[0] == '/':
                src_file = 'data1' + src_file
            else:
                src_file = 'data1/' + src_file        
            res = self.globus.transfer(src_endpoint=self.default_read_endpoint,
                                       dest_endpoint=dest_dtn.default_endpoint,
                                       src_file=src_file,
                                       dest_file=dest_file)

        return res

    def __str__(self):
        res = "DTN: " + self.name + "\n"
        if len(self.connectors) == 0:
            res += "No Globus enpoints"
        else:
            res += "Globus share endpoints\n"
            for connector in self.connectors:
                res += str(connector)
            res += "\n"
        return res

    def __repr__(self):
        return self.__str__() 

def load_sites():
    """Get all sites.
        A site is a list of DTN's.
    
    Returns:
        dict: sites, indexed by site's name
    """
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    file_name = "../../indi/knowledgelibrary/dtns.json"
    with (open(file_name)) as sites_file:
        return json.load(sites_file)['sites']
    return None

def get_sites(globus=None):
    """Get all sites
    
    Returns:
        list: all sites
    
    Args:
        globus (globus.Globus, optional): globus
    """
    sites = []
    json_sites = load_sites()
    for site_name in json_sites:
        sites.append(Site(name=site_name, globus=globus))
    return sites


def get_dtn(dtn_name):
    """ Get a DTN object given its name

    Args:
        dtn_name (string): name of the DTN without domain name.

    Returns:
        dict: DTN object
    """
    sites = get_sites()
    for site in sites:
        dtns = site.get_dtns()
        for dtn in dtns:
            if dtn['name'] == dtn_name:
                return dtn


def get_interface(endpoint):
    """ Get the DTN interface, vlan and IPv4 address of a
        given endpoint. 
        An interface is a dict with the following keys:
            (string) interface: name of the DTN interface (i.e. 'eth10')
            (string) vlan: configured VLAN on this interface
            (string) ipv4: configure IPv4 address 

    Args:
        endpoint (dict): endpoint object

    Returns:
        dict: interface with keys 'interface', 'vlan', and 'ipv4'
    """
    intf = endpoint['interface']
    vlan = endpoint['vlan']
    ipv4 = endpoint['ipv4']
    return {'interface': intf, 'vlan': vlan, 'ipv4': ipv4}


def get_router_port(endpoint):
    """ get the network device and port of where the endpoint is connected to.
    
    Args:
        endpoint (endpoint): endpoint
        A routerport is a dict with the following keys:
            router (string): name of the netork device
            port (string): port on the router.
            vlan (string): VLAN
    Returns:
        dict: router, port and vlan
    """
    router = endpoint['router']
    port = endpoint['port']
    vlan = endpoint['vlan']
    return {'router':router, 'port':port, 'vlan':vlan}

def to_nsi(router_port):
    """ Translates a router/port into an Open NSA address
        es.net:2013::<node>:<port>#<VLAN>
    Args:
        router_port (routerport): router and port
    
    Returns:
        string: NML
    """
    address = "es.net:2013::" + router_port['router'] + ":"
    port = router_port['port'].replace('/', '_')
    address += port + "#" + router_port['vlan']
    return address

def to_oscars(router_port):
    """ Translates a router/port into an OSCARS address
        es.net:2013::<node>:<port>#<VLAN>
    Args:
        router_port (routerport): router and port
    urn:ogf:network:domain=es.net:node=bois-cr1:port=xe-1/2/0:link=*
    Returns
        string: NML
    """
    address = "urn:ogf:network:domain=es.net:node=" + router_port['router'] + ":"
    address += router_port['port'] + ":link=*"
    return address

def do_cli():
    """ Executes the CLI
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--show-site", nargs=1, help="Display a site.")
    parser.add_argument("--list-sites", action='store_true', help="List sites.")
    parser.add_argument("--globus-user", nargs=1, help="Globus user name")
    parser.add_argument("--globus-key", nargs=1, help="Globus user key")
    parser.add_argument("--globus-dtn-ls", nargs=3,
                        help="<site> <dtn> <dir> list Globus files on a DTN")
    parser.add_argument("--globus-transfer", nargs=6,
                        help="<srcsite> <srcdtn>  <srcfile> <dstsite> <dstdtn> <dstfile>")
    parser.add_argument("--globus-transfer-nsi", nargs=6,
                        help="<srcsite> <srcdtn>  <srcfile> <dstsite> <dstdtn> <dstfile>")

    args = parser.parse_args()
    globus = None
    if args.globus_user != None and args.globus_key != None:
        globus = Globus(user=args.globus_user[0], key=args.globus_key[0])
    else:
        globus = Globus()

    if args.show_site != None:
        site = Site(name=args.show_site[0], globus=globus)
        print (site)
    elif args.list_sites:
        sites = get_sites(globus=globus)
        for site in sites:
            print (site)
    elif args.globus_dtn_ls != None:
        site = args.globus_dtn_ls[0]
        dtn = DTN(name=args.globus_dtn_ls[1], site_name=site, globus=globus)
        directory = args.globus_dtn_ls[2]
        connectors = dtn.connectors
        if len(connectors) > 0:      
            connector = connectors[0]
            files = connector.globus_endpoint.list_files(directory)
            directories = connector.globus_endpoint.list_dirs(directory)
            print ("Files:")
            for file_name in files:
                print ('\t', file_name)
            print ("Directories:")
            for dir_name in directories:
                print ('\t', dir_name)
    elif args.globus_transfer != None or args.globus_transfer_nsi != None:
        the_args = None
        nsi = False
        if args.globus_transfer != None:
            the_args = args.globus_transfer
        else:
            nsi = True
            the_args = args.globus_transfer_nsi
        site1 = the_args[0]
        dtn1 = DTN(name=the_args[1], site_name=site1, globus=globus)
        site2 = the_args[3]
        dtn2 = DTN(name=the_args[4], site_name=site2, globus=globus)
        file1 = the_args[2]
        file2 = the_args[5]
        res = dtn1.transfer(dest_dtn=dtn2, src_file=file1, dest_file=file2, nsi=nsi)
        print (res)

if __name__ == "__main__":
    do_cli()
