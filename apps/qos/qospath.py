#! /usr/bin/python
"""
QoSPath.py ---------------------------------------------------------------------------------------------------
Developed By: Ryan Wallner (ryan.wallner1@marist.edu)
Add QoS to a specific path in the network. Utilized circuit pusher developed by KC Wang
[Note]
	*the circuitpusher.py is needed in the same directory for this application to run
	 succesfully! This circuitpusher instance is used WITHOUT pushing statis flows. 
	 the static flows are commented out, circuitpusher is only used to get route.

 USAGE: 
		qospath.py <add> --qos-path <name> <source-ip> <dest-ip> <policy-object> <controller-ip> <port>
		qospath.py <delete> --qos-path <name> <controller-ip> <port>
 		*note: This adds the Quality of Service to each switch along the path between hosts
 		*note Policy object can exclude the "sw" ,"enqueue-port" parameters and  
	     "ip-src", "ip-dst" and "ingress-port" match parameters. 
	     They will be modified based on the route anyway.

	[author] - rjwallner
-----------------------------------------------------------------------------------------------------------------------
"""
import sys
import os
import time
import simplejson #used to process policies and encode/decode requests
import subprocess #spawning subprocesses

def main():
	#checks
	if (len(sys.argv) == 2):
	 if sys.argv[1] == "--help" or sys.argv[1] == "help" or sys.argv[1] == "--h" :
	  usage_help()
	  exit()
	if (len(sys.argv)) == 9:
		p_name = sys.argv[3]
		src = sys.argv[4]
		dst = sys.argv[5]
		pol = sys.argv[6]
		c_ip = sys.argv[7]
		prt = sys.argv[8]
		add(p_name,src,dst,pol,c_ip,prt)
		exit()
	if (len(sys.argv)) == 6:
		p_name = sys.argv[3]
		c_ip = sys.argv[4]
		prt = sys.argv[5]
		delete(p_name,c_ip,prt)
		exit()
	else:
	 usage()
	 exit()

def add(name, ip_src, ip_dst, p_obj, c_ip, port):
   print "Trying to create a circuit from host %s to host %s..." % (ip_src, ip_dst)
   c_pusher = "circuitpusher.py"
   qos_pusher = "qosmanager.py"
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
   	cmd = "--controller=%s:%s --type ip --src %s --dst %s --add --name %s" % (c_ip,port,ip_src,ip_dst,name)
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
   
   print "Creating a QoSPath from host %s to host %s..." % (ip_src, ip_dst)
   time.sleep(5)
   for line in c_data:
        data = simplejson.loads(line)
        if data['name'] != name:
        	continue
        else:
        	sw_id = data['Dpid']
        	in_prt = data['inPort']
        	out_prt = data['outPort']
        	print"QoS applied to this switch for circuit %s" % data['name']
        	print "%s: in:%s out:%s" % (sw_id,in_prt,out_prt)
        	p = simplejson.loads(p_obj)
        	#add necessary match values to policy for path
        	p['sw'] = sw_id
        	p['name'] = name+"."+sw_id
        	#screwed up connectivity on this match, remove
        	#p['ingress-port'] = str(in_prt)
        	p['ip-src'] = ip_src
        	p['ip-dst'] = ip_dst
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
        		cmd = "./qosmanager.py add policy '%s' %s %s" % (sjson,c_ip,port)
        		p = subprocess.Popen(cmd, shell=True).wait()
        	elif service and not queue:
        		print "Adding Type of Service"
        		sjson =  simplejson.JSONEncoder(sort_keys=False,indent=3).encode(p)
        		print sjson
        		cmd = "./qosmanager.py add policy '%s' %s %s" % (sjson,c_ip,port)
        		p = subprocess.Popen(cmd, shell=True).wait()
        	else:
        		polErr()
        		
def polErr():
	print """Your policy is not defined right, check to 
make sure you have a service OR a queue defined"""
	
def delete(name,c_ip,port):
	print "Trying to delete QoSPath %s" % name
	# circuitpusher --controller {IP:REST_PORT} --delete --name {CIRCUIT_NAME}
	try:
		print "Deleting circuit"
		cmd = "./circuitpusher.py --controller %s:%s --delete --name %s" % (c_ip,port,name)
		subprocess.Popen(cmd,shell=True).wait()
	except Exception as e:
		print "Error deleting circuit, Error: %s" % str(e)
		exit()
	
	qos_s = os.popen("./qosmanager.py list policies %s %s" %(c_ip,port)).read()
	qos_s = qos_s[qos_s.find("[",qos_s.find("[")+1):qos_s.rfind("]")+1]
	#print qos_s
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
				cmd = "./qosmanager.py delete policy '{\"policy-id\":\"%s\"}' %s %s " % (pol_id,c_ip,port)
				print cmd
				subprocess.Popen(cmd,shell=True).wait() 
			except Exception as e:
				print "Could not delete policy in path: %s" % str(e)

def usage():
	print '''type "qospath.py --help" for more details
		#qospath.py <add> --qos-path <name> <source-ip> <dest-ip> <policy-object> <controller-ip> <port>
		#qospath.py <delete> --qos-path <name> <controller-ip> <port>
	        *Policy object can exclude the "sw" ,"enqueue-port" parameters and  
	        "ip-src", "ip-dst" and "ingress-port" match parameters. 
	         They will be modified based on the route anyway.'''
def usage_help():
	print '''
	        ###################################
		QoSPath.py
		Author: Ryan Wallner (Ryan.Wallner1@marist.edu)
		QoSPath is a simple service that utilizes KC Wang's 
		CircuitPusher  to push Quality of Service along a
		specific path in the network.
			
		To add a QoS Path with a Policy
		*note other match fields can be added to the policy object
		qospath.py add  --qos-path Path-Name 10.0.0.1  10.0.0.2  '{"queue":"2"}' 127.0.0.1 8080
		qospath.py add  --qos-path Path-Name 10.0.0.1  10.0.0.2  '{"service":"Best Effort"}' 127.0.0.1 8080
		
		To delete a QoS Path 
		qospath.py delete  --qos-path  "Path-Name"  127.0.0.1 8080
		
		###################################
		'''
#Call main
if  __name__ == "__main__" :
	main()
