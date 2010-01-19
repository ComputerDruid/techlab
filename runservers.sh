#!/bin/sh
HOSTNAME=`hostname`
NUMBER=4
for i in `cat /usr/csl/etc/hostlist|grep -v $HOSTNAME|head -n $NUMBER`;do konsole --new-tab -e ssh $i ~/techlab/runscript.sh; done
