#!/bin/bash
cd ../../opennsa
./onsa reserveprovision -g urn:uuid:6e1f288a-5a26-4ad8-a9bc-eb91785cee15 -d es.net:2013::bnl-mr2:xe-1_2_0:+#1000 -s es.net:2013::lbl-mr2:xe-9_3_0:+#1000 -b 5096 -a 2016-11-13T09:00:00 -e 2017-04-04T17:00:00 -u https://nsi-aggr-west.es.net:443/nsi-v2/ConnectionServiceProvider -p es.net:2013:nsa:nsi-aggr-west -r canada.eh:2016:nsa:requester -h 198.128.151.17 -o 8443 -l /etc/hostcert/muclient.crt -k /etc/hostcert/muclient.key -i /etc/ssl/certs/ -y -x -z -v -q;
exit;