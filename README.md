# INDIRA: Network Intent Automation for Wide Area Networks 

INDIRA is designed as a intent-driven networking demo to show how simple english conversation commands can be translated into network automation commands. INDIRA uses its own easy to understand OWL ontology on how network demands can made such as bandwidth, start and end time and more. These are then mapped to specific API calls such as NSI or Globus commands which are the tools that actually render the network command.


# Running INDIRA

go to intentmodules folder


	$ run indira.py

indira will call the engine which will render commands to nsi



# indi
intent-based network deployment framework



to be added later - tests

Measurement parameters
-------------------------

To test the performance of the intent framework.

Graphs to be plotted:
- intent query arrival time versus setup time -> one client?
- intent query arrival time versus setup time -> two clients?
- Throughput = total number of requests or queries versus query completion time using one client
- Throughput = total number of requests or queries versus query completion time using increasing clients (3 axes)
- query completion time = avg completion time versus number of tenants
- query loss ration = unsuccessful intents versus number of tenants
- percentages of which service requests on the network over 1 month

terms to be discussed further:
-query completion time = delay
-when is the network saturation peak reached?
-what is the overload peak?
-effect on current intents when new intents arrive? - performance evaluations
-latency?
-workload?
- survey - on how good the ontology is.. where you able to define your use cases, is there anything missing?

## NSI Commands

Here are the steps to working and installing NSI:

The link for NSI project:


The only python based NSI client that I know of is in this project: https://github.com/NORDUnet/opennsa


The onsa documentation is here: https://github.com/NORDUnet/opennsa/blob/master/docs/cli.md


Steps to install:

sudo apt-get install python-twisted

sudo apt-get install python-psycopg2

go to website for twistar, download tar file, tar -xvzf file.tar.gz

sudo apt-get install python-setuptools

python setup.py build

sudo python setup.py install

sudo apt-get update

sudo apt-get install postgresql postgresql-contrib

download pyopenssl 0.14, unzip, build and install (use page:http://stackoverflow.com/questions/22073516/failed-to-install-python-cryptography-package-with-pip-and-setup-py

go to opennsa, build and install

Keys
create crt, csr, key file using ( useful page for setting up keys: https://help.ubuntu.com/lts/serverguide/certificates-and-security.html)

send John Macauley keys to update and test nsi (Certificates are copied to etc/ssl/certs/nsi-aggr-west.es.net/)
