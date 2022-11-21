#!/bin/bash
#this is a comment-the first line sets bash as the shell script
cd /Users/mkiran/SWProjects/opennsa/;
#print "ffff"
./onsa reserveprovision -g urn:uuid:6e1f288a-5a26-4ad8-a9bc-eb91785cee15  -d icair.org:2013:topology:ps#1779 -s es.net:2013::sunn-cr5:10_1_6:+#1779  -b 100 -a 2016-11-15T21:00:00 -e 2016-11-15T21:30:00  -u https://nsi-aggr-west.es.net:443/nsi-v2/ConnectionServiceProvider -p es.net:2013:nsa:nsi-aggr-west  -r canada.eh:2016:nsa:requester  -h your.host.com -o 8443  -l etc/hostcert/client.crt -k etc/hostcert/client.key  -i etc/ssl/certs  -y -x -z -v -q;
exit;
