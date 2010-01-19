#!/bin/sh
HOSTNAME=`hostname`
NUMBER=4
for i in `cat /usr/csl/etc/hostlist|grep -v $HOSTNAME|head -n $NUMBER`;do ssh $i killall python2.6; done
