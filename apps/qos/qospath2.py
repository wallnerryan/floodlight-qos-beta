#! /usr/bin/python
"""
QoSPath.py v2---------------------------------------------------------------------------------------------------
Developed By: Ryan Wallner (ryan.wallner1@marist.edu)
Add QoS to a specific path in the network. Utilized circuit pusher developed by KC Wang
[Note]
	*the circuitpusher.py is needed in the same directory for this application to run
	 succesfully! This circuitpusher instance is used WITHOUT pushing statis flows. 
	 the static flows are commented out, circuitpusher is only used to get route.

	[author] - rjwallner
-----------------------------------------------------------------------------------------------------------------------
"""
import sys
import os
import re
import time
import simplejson #used to process policies and encode/decode requests
import subprocess #spawning subprocesses
import argparse

def main():
	
	parser = argparse.ArgumentParser(description="QoS Path Pusher")
	parser.add_argument('-p','--port',
                    required=False,
                    default="8080",
                    type=str,
                    dest='p',
                    metavar="P")
        parser.add_argument('-c','--controller',
                    required=False,
                    default="127.0.0.1",
                    dest="c",
                    type=str,
                    metavar="C")
	parser.add_argument("-a","--add",
		    required=False,
		    dest="action_op",
		    action="store_const",
		    const="add",
		    metavar="add")
	parser.add_argument("-d","--delete",
                    required=False,
		    dest="action_op",
                    action="store_const",
                    const="delete",
                    metavar="delete")
	parser.add_argument("-N","--name",
                    required=True,
                    dest="name")
	parser.add_argument("-J","--json",
		    required=False,
		    dest="obj")
	parser.add_argument("-S","--src-ip",
		    required=False,
		    dest="src_ip")
	parser.add_argument("-D","--dest-ip",
		    required=False,
		    dest="dest_ip")
	args = parser.parse_args()

	#initialize arguments
	c = args.c
	p = args.p
	name = args.name
	action = args.action_op
	src = args.src_ip
	dest = args.dest_ip
	json = args.obj

	# Add/ Delete
	if action == "add":
		print "add"
		if src != None and dest != None and json != None:
			#syntax check ip addresses
        		#required fields
        		#Credit: Sriram Santosh
        		ipPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        		if len(re.findall(ipPattern,src)) > 0:
                		print "src good"
        		else:
                		print "bad src"
                		exit(1)
        		if len(re.findall(ipPattern,dest)) > 0:
                		print "dest good"
        		else:
                		print "bad dest"
                		exit(1)
			#all goes well, add
			add(name,src,dest,json,c,p)
			exit()
		else:
			print "Missing arguments, check src, dest, and json"
			exit(1)
	elif action == "delete":
		print "delete"
		delete(name,c,p)
		exit()
	else:
		print "action not unrecognized"
		exit(1)

#Add a Quality of Service Path
# @NAME  -Name of the Path
# @SRC   -Source IP
# @DEST  -Destination IP
# @JSON  -Json object of the policy
# @C, @P -Controller / Port
# 
# Author- Ryan Wallner	
def add(name,src,dest,json,c,cprt):
   print "Trying to create a circuit from host %s to host %s..." % (src,dest)
   c_pusher = "circuitpusher.py"
   qos_pusher = "qosmanager2.py"
   pwd = os.getcwd()
   print pwd
   try:
     if (os.path.exists("%s/%s" % (pwd,c_pusher))) and (os.path.exists("%s/%s" % (pwd,qos_pusher))):
      print "Necessary tools confirmed.. %s , %s" % (c_pusher,qos_pusher)
     else:
       print "%s/%s does not exist" %(pwd,c_pusher)
       print "%s/%s does not exist" %(pwd,qos_pusher)
   except ValueError as e:
     print "Problem finding tools...%s , %s" % (c_pusher,qos_pusher)
     print e
     exit(1)
    
   #first create the circuit and wait to json to pupulate  
   print "create circuit!!!"
   try:
   	cmd = "--controller=%s:%s --type ip --src %s --dst %s --add --name %s" % (c,cprt,src,dest,name)
   	print './circuitpusher.py %s' % cmd
   	c_proc = subprocess.Popen('./circuitpusher.py %s' % cmd, shell=True)
   	print "Process %s started to create circuit" % c_proc.pid
   	#wait for the circuit to be created
   	c_proc.wait()
   except Exception as e:
   	print "could not create circuit, Error: %s" % str(e)
   
   try:
   	subprocess.Popen("cat circuits.json",shell=True).wait()
   except Exception as e:
   	print "Error opening file, Error: %s" % str(e)
   	#cannot continue without file
   	exit()
   
   print "Opening circuits.json in %s" % pwd
   try:
   	circs = "circuits.json"
   	c_data = open(circs)
   except Exception as e:
   	print "Error opening file: %s" % str(e)
   
   print "Creating a QoSPath from host %s to host %s..." % (src,dest)
   #Sleep purely for end user
   time.sleep(3)
   for line in c_data:
        data = simplejson.loads(line)
        if data['name'] != name:
        	continue
        else:
        	sw_id = data['Dpid']
        	in_prt = data['inPort']
        	out_prt = data['outPort']
        	print"QoS applied to switch %s for circuit %s" % (sw_id,data['name'])
        	print "%s: in:%s out:%s" % (sw_id,in_prt,out_prt)
        	p = simplejson.loads(json)
        	#add necessary match values to policy for path
        	p['sw'] = sw_id
        	p['name'] = name+"."+sw_id
        	#screwed up connectivity on this match, remove
        	#p['ingress-port'] = str(in_prt)
        	p['ip-src'] = src
        	p['ip-dst'] = dest
        	keys = p.keys()
        	l = len(keys)
        	queue = False
        	service = False
        	for i in range(l):
        		if keys[i] == 'queue':
        			queue = True
        		elif keys[i] == 'service':
        			service = True
        	
        	if queue and service:
        		polErr()
        	elif queue and not service:
        		p['enqueue-port'] = str(out_prt)
        		pol = str(p)
        		print "Adding Queueing Rule"
        		sjson =  simplejson.JSONEncoder(sort_keys=False,indent=3).encode(p)
			print sjson
        		cmd = "./qosmanager2.py --add --type policy --json '%s' -c %s -p %s" % (sjson,c,cprt)
        		p = subprocess.Popen(cmd, shell=True).wait()
        	elif service and not queue:
        		print "Adding Type of Service"
        		sjson =  simplejson.JSONEncoder(sort_keys=False,indent=3).encode(p)
        		print sjson
        		cmd = "./qosmanager2.py --add --type policy --json '%s' -c %s -p %s" % (sjson,c,cprt)
        		p = subprocess.Popen(cmd, shell=True).wait()
        	else:
        		polErr()
        		
def polErr():
	print """Your policy is not defined right, check to 
make sure you have a service OR a queue defined"""
	
#Delete a Quality of Service Path
# @NAME  -Name of the Path
# @C, @P -Controller / Port
# 
# Author- Ryan Wallner  
def delete(name,c,p):
	print "Trying to delete QoSPath %s" % name
	# circuitpusher --controller {IP:REST_PORT} --delete --name {CIRCUIT_NAME}
	try:
		print "Deleting circuit"
		cmd = "./circuitpusher.py --controller %s:%s --delete --name %s" % (c,p,name)
		subprocess.Popen(cmd,shell=True).wait()
	except Exception as e:
		print "Error deleting circuit, Error: %s" % str(e)
		exit()
	
	qos_s = os.popen("./qosmanager2.py --list --type policies --controller %s --port %s" %(c,p)).read()
	#pull only the right info from response
	qos_s = qos_s[qos_s.find("[",qos_s.find("[")+1):qos_s.rfind("]")+1]
	data = simplejson.loads(qos_s)
	sjson = simplejson.JSONEncoder(sort_keys=False,indent=3).encode(data)
	jsond = simplejson.JSONDecoder().decode(sjson)
	#find policies that start with "<pathname>."
	l = len(jsond)
	for i in range(l):
		n = jsond[i]['name']
		if name in n:
			pol_id =  jsond[i]['policyid']
			try:
				cmd = "./qosmanager2.py --delete --type policy --json '{\"policy-id\":\"%s\"}' -c %s -p %s " % (pol_id,c,p)
				print cmd
				subprocess.Popen(cmd,shell=True).wait() 
			except Exception as e:
				print "Could not delete policy in path: %s" % str(e)

#Call main :)
if  __name__ == "__main__" :
	main()
