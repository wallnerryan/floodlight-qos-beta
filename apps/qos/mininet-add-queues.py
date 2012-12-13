#! /usr/bin/python
#  coding: utf-8

'''
Add queues to Mininet using ovs-vsctl and ovs-ofctl
@Author Ryan Wallner
'''

import os
import sys
import time
import subprocess

def find_all(a_str, sub_str):
    start = 0
    b_starts = []
    while True:
        start = a_str.find(sub_str, start)
        if start == -1: return b_starts
        #print start
        b_starts.append(start)
        start += 1


if os.getuid() != 0:
        print "Root permissions required"
        exit()


cmd = "ovs-vsctl show"
p = os.popen(cmd).read()
#print p

brdgs = find_all(p, "Bridge")
print brdgs

switches = []
for bn in brdgs:
        sw =  p[(bn+8):(bn+10)]
        switches.append(sw)

ports = find_all(p,"Port")
print ports

prts = []
for prt in ports:
        prt = p[(prt+6):(prt+13)]
        if '"' not in prt:
                print prt
                prts.append(prt)
config_strings = {}
for i in range(len(switches)):
        str = ""
        sw = switches[i]
        for n in range(len(prts)):
                #verify correct order
                if switches[i] in prts[n]:
                        #print switches[i]
                        #print prts[n]
                        port_name = prts[n]
                        str = str+" -- set port %s qos=@defaultqos" % port_name
        config_strings[sw] = str

#build queues per sw
print config_strings
for sw in switches:
        queuecmd = "sudo ovs-vsctl %s -- --id=@defaultqos create qos type=linux-htb other-config:max-rate=1000000000 queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate=1000000000 other-config:max-rate=1000000000 -- --id=@q1 create queue other-config:max-rate=20000000 -- --id=@q2 create queue other-config:max-rate=2000000 other-config:min-rate=2000000" % config_strings[sw]
        q_res = os.popen(queuecmd).read()
        print q_res




