#!/bin/bash

#set -x
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MIDORI_HOME=$( dirname $DIR )

#
# onos-mininet:  https://ernie55ernie.github.io/sdn/2020/07/21/setting-up-onos-controller-with-mininet.html
# containernet: https://github.com/containernet/containernet
#
#
#
# onos cli in the container:
#   https://wiki.onosproject.org/display/ONOS/Single+Instance+Docker+deployment
#   ssh -p 8101 -o StrictHostKeyChecking=no karaf@localhost
#   run onos> app activate org.onosproject.fwd
#   run onos> app activate org.onosproject.openflow
#
# p4 onos mininet: https://wiki.onosproject.org/display/ONOS/Try+fabric.p4+with+ONOS+and+bmv2
#
# SDNLab: https://github.com/jorgelopezcoronado/SDNLab
# SDNLab PDF: http://ce.sc.edu/cyberinfra/workshops/Material/SDN/Lab%204%20-%20Introduction%20to%20SDN.pdf
#
# docker build -t mywordpress ./mywordpress
# docker build -t mymysql ./mymysql
# docker build -t lab-api ./backend
# docker build -t lab-web ./frontend
#
configure_midori() {
    #git clone https://github.com/stevencox/midori.git
    cd /midori
    $MIDORI_HOME/bin/configure start_node
}

wait_for_onos() {
    cd /containernet
    until $(wget --quiet http://onos:8181/onos/ui); do
	sleep 10
	echo waiting for onos...
    done
}

run_sdn_lab() {
    mn -c;
    # curl https://raw.githubusercontent.com/jorgelopezcoronado/SDNLab/master/custom_ctnnet_topology.py > cmnt.py;
    python3 /midori/cmnt.py
}

supervise() {
    # Non ideal surrogate for systemd.
    while true; do
	if [ -z $( pgrep -f "python.*main.py.*" ) ]; then
	    echo Starting Midori API...
	    $MIDORI_HOME/bin/configure start_api &
	fi
	if [ -z $( pgrep -f "rq.*worker.*" ) ]; then
	    echo Starting Midori RQ worker...
	    $MIDORI_HOME/bin/configure start_worker &
	fi
	sleep 10;
    done;
}

start() {
    configure_midori
    wait_for_onos
    supervise
}

$*


