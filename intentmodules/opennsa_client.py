# ./onsa reserveprovision \
# -g urn:uuid:6e1f288a-5a26-4ad8-a9bc-eb91785cee15 \
# -d icair.org:2013:topology:ps#1779 \
# -s es.net:2013::sunn-cr5:10_1_6:+#1779 \
# -b 100 -a 2016-11-15T21:00:00 -e 2016-11-15T21:30:00 \
# -u https://nsi-aggr-west.es.net:443/nsi-v2/ConnectionServiceProvider \
# -p es.net:2013:nsa:nsi-aggr-west  -r canada.eh:2016:nsa:requester \
# -h your.host.com -o 8443 \
# -l etc/hostcert/client.crt -k etc/hostcert/client.key \
# -i etc/ssl/certs \
# -y -x -z -v -q


#!/usr/bin/env python

import os
import uuid
import random
import time
import datetime

from twisted.internet import reactor, defer

from opennsa import nsa, setup
import subprocess

from subprocess import *


DYNAMICKL_SERVICE   = 'http://220.69.219.228:8010/nsi/ConnectionServiceProvider'
OPENNSA_SERVICE     = 'http://orval.grid.aau.dk:9080/NSI/services/ConnectionService'
LOCALHOST_SERVICE   = 'http://localhost:9080/NSI/services/ConnectionService'

ORVAL_REQUESTER     = 'http://orval.grid.aau.dk:7080/NSI/services/ConnectionService'
LOCAL_REQUESTER     = 'http://localhost:7080/NSI/services/ConnectionService'

HOST = 'localhost'
PORT = 7080


def matchState(query_result, expected_state):
    state =  query_result.reservationSummary[0].connectionState
    if state == expected_state:
        print 'State match (%s)' % expected_state
    else:
        print "State mismatch. Was %s, should have been %s" % (state, expected_state)


@defer.inlineCallbacks
def doMain():

    print 'OpenNSA WS test client'

    wsdl_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wsdl')

    client, factory = setup.createClient(HOST, PORT, wsdl_dir)

    reactor.listenTCP(PORT, factory)

    client_nsa      = nsa.NetworkServiceAgent('OpenNSA-testclient', LOCAL_REQUESTER)

    provider_local_aruba    = nsa.Network('Aruba',   nsa.NetworkServiceAgent('Aruba-OpenNSA', LOCALHOST_SERVICE))
    provider_orval_aruba    = nsa.Network('Aruba',   nsa.NetworkServiceAgent('Aruba-OpenNSA', OPENNSA_SERVICE))
    provider_martinique     = nsa.Network('Martinique', nsa.NetworkServiceAgent('Martinique-DynamicKL', DYNAMICKL_SERVICE))

    provider = provider_local_aruba
    #provider = provider_orval_aruba
    #provider = provider_martinique

    source_stp      = nsa.STP('Aruba', 'A1' )
    #source_stp      = nsa.STP('Aruba', 'Axel' )
    #source_stp      = nsa.STP('Martinique', 'M1')

    #dest_stp        = nsa.STP('Aruba', 'A2')
    dest_stp        = nsa.STP('Bonaire', 'B3')
    #dest_stp        = nsa.STP('Curacao', 'C3')

    start_time = datetime.datetime.utcfromtimestamp(time.time() + 3 )
    end_time   = datetime.datetime.utcfromtimestamp(time.time() + 120 )
    #start_time, end_time = end_time, start_time

    bandwidth = 200
    #service_params  = nsa.ServiceParameters('2011-09-01T08:56:00Z', '2011-10-01T08:56:00Z' , source_stp, dest_stp, bwp)
    service_params  = nsa.ServiceParameters(start_time, end_time, source_stp, dest_stp, bandwidth)
    global_reservation_id = 'urn:uuid:' + str(uuid.uuid1())
    connection_id         = 'urn:uuid:' + str(uuid.uuid1())

    print "Connection id", connection_id

    r = yield client.reserve(client_nsa, provider.nsa, None, global_reservation_id, 'Test Connection', connection_id, service_params)
    print "Reservation created. Connection ID:", connection_id

    qr = yield client.query(client_nsa, provider.nsa, None, "Summary", connection_ids = [ connection_id ] )
    matchState(qr, 'Reserved')

    d = client.provision(client_nsa, provider.nsa, None, connection_id)

    qr = yield client.query(client_nsa, provider.nsa, None, "Summary", connection_ids = [ connection_id ] )
    matchState(qr, 'Auto-Provision')

    yield d
    print "Connection provisioned"

    qr = yield client.query(client_nsa, provider.nsa, None, "Summary", connection_ids = [ connection_id ] )
    matchState(qr, 'Provisioned')

    _ = yield client.release(client_nsa, provider.nsa, None, connection_id)
    print "Connection released"

    qr = yield client.query(client_nsa, provider.nsa, None, "Summary", connection_ids = [ connection_id ] )
    matchState(qr, 'Scheduled')

    _ = yield client.terminate(client_nsa, provider.nsa, None, connection_id)
    print "Reservation terminated"

    qr = yield client.query(client_nsa, provider.nsa, None, "Summary", connection_ids = [ connection_id ] )
    matchState(qr, 'Terminated')



def main():

    d = defer.maybeDeferred(doMain)

    def p(failure):
        failure.printTraceback()

    d.addErrback(p)
    d.addBoth(lambda _ : reactor.callLater(0.1, reactor.stop) )
    return d



if __name__ == '__main__':
    #reactor.callWhenRunning(main)
    #reactor.run()
    #run child script 1
    os.system('./test.sh')
