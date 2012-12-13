#! /usr/bin/python
# coding: utf-8
'''
QoSManager.py -----------------------------------------------------------------------------
Developed By: Ryan Wallner (ryan.wallner1@marist.edu)
Used add Types of Service i.e.(Best Effort) and Quality of Service policy’s to the network
Utilizes the QoS modules in BigSwitch Network's Floodlight Controller
 
 NOTES:
 	This script is developed as an additional program that utilizes the QoS module
 	in floodlights opensource software defined network controller.
 	
 USAGE: 
	qosmanager.py <add | delete | modify> <service | policy> <service-obj | policy-obj> <controller-ip> <port>
	qosmanager.py <enable | disable | status> <controller-ip> <port>
	qosmanager.py <list> < policies | services > <controller-ip> <port>
 	*note: if you are deleting you can just reference the name of the service/policy
 	
 	[author] - rjwallner
------------------------------------------------------------------------------------------
'''
import sys
import os
import httplib      # basic HTTP library for HTTPS connections
import urllib       # used for url-encoding during login request
import simplejson # converts between JSON and python objects
import time

def main():
	#print (str(len(sys.argv))) 
	#checks
	if (len(sys.argv) == 2):
	 if sys.argv[1] == "--help" or sys.argv[1] == "-h" or sys.argv[1] == "help":
	  usage_help()
	  exit()
	if(len(sys.argv) == 4):
	 controller = sys.argv[2]
	 port = sys.argv[3]
	 if sys.argv[1] == "enable":
	 	enable(controller,port)
	 	exit()
	 elif  sys.argv[1] == "disable":
	 	disable(controller,port)
	 	exit()
	 elif sys.argv[1] == "status":
	 	qosStatus(controller,port)
	 	exit()
	if(len(sys.argv) == 5):
		op = sys.argv[2]
		ip = sys.argv[3]
		prt = sys.argv[4]
		if op == "services":
			listServices(ip,prt)
			exit()
		if op == "policies":
			listPolicies(ip,prt)
			exit()
		else:
			usage()
			exit()
	if (len(sys.argv)) != 6:
	 usage()
	 exit()
		
	#Define the od variables for the request
	cmd = sys.argv[1]
	s_p = sys.argv[2]
	obj = sys.argv[3]
	server = sys.argv[4]
	port = sys.argv[5]
	try:
	 helper = httpHelper(__name="QoSHTTPHelper")
	 print "Trying to connect to %s..." % server
	 helper.connect(server,port)
	except httplib.HTTPException:
	 print "Error connecting to controller,\
	 	please make sure you controller is running"
	 exit(1)
	except Exception as e:
	 print e
	 print "Error connecting to controller"
	 exit(1)
	print "Connection Succesful"
	
	if cmd == "add":
	 if s_p == "service":
	  print "Trying to add service %s" % obj
	  url = "http://%s:%s/wm/qos/service/json" % (server,port)
	  #preserve immutable
	  _json = obj
	  try:
	   req = helper.request("POST",url,_json)
	   print "[CONTROLLER]: %s" % req
	   r_j = simplejson.loads(req)
	   if r_j['status'] != "Please enable Quality of Service":
	   	write_add("service",_json) 
	   else:
	   	print "[QoSPusher] please enable QoS on controller"
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()
			
	 elif s_p == "policy":
	  print "Trying to add policy %s" % obj
	  url = "http://%s:%s/wm/qos/policy/json" % (server,port)
	  #preserve immutable
	  _json = obj
	  try:
	   req = helper.request("POST",url,_json)
	   print "[CONTROLLER]: %s" % req
	   r_j = simplejson.loads(req)
	   if r_j['status'] != "Please enable Quality of Service":
	   	write_add("policy",_json)
	   else:
	   	print "[QoSPusher] please enable QoS on controller"
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()
	  
	elif cmd == "delete":
	#preserve immutable
	 uid_o = obj
	 if s_p == "service":
	  print "Trying to delete service %s" % obj
    	  url = "http://%s:%s/wm/qos/service/json" % (server,port)
    	  url_ns = "http://%s:%s/wm/qos/service/json" % (server,port)
	  try:
	  	name_req = helper.request("GET",url_ns,None)   
	  	svs = simplejson.loads(name_req)
	  	o = simplejson.loads(uid_o)
	  	u_id_n = None
	  	for sv in  svs:
	  		if int(sv['sid']) == int(o['sid']):
	  			u_id_n = sv['name']
	  			break
	  	if u_id_n != None:
	  		req = helper.request("DELETE",url,uid_o)
	   		print "[CONTROLLER]: %s" % req
	   		r_j = simplejson.loads(req)
	   		if r_j['status'] != "Please enable Quality of Service":
	   			write_remove("service", u_id_n )
	   			#print "remove service"
	   		else:
	   			print "[QoSPusher] please enable QoS on controller"
	  	else:
	   		print "Service not found"
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()
			
	 elif s_p == "policy":
	  print "Trying to delete policy %s" % obj
    	  url = "http://%s:%s/wm/qos/policy/json" % (server,port)
          url_ns = "http://%s:%s/wm/qos/policy/json" % (server,port)
	  try:
	  	name_req = helper.request("GET",url_ns,None)   
	  	pols = simplejson.loads(name_req)
	  	o = simplejson.loads(uid_o)
	  	u_id_n = None
	  	for pol in  pols:
	  		print "comparing %s : %s " % (pol['policyid'],o['policy-id'])
	  		if int(pol['policyid']) == int(o['policy-id']):
	  			u_id_n = pol['name']
	  			break
	  	if u_id_n != None:	
	  		req = helper.request("DELETE",url,uid_o)
	   		print "[CONTROLLER]: %s" % req
	   		r_j = simplejson.loads(req)
	   		if r_j['status'] != "Please enable Quality of Service":
	   			write_remove("policy", u_id_n )
	   			#print "remove policy"
	   		else:
	   			print "[QoSPusher] please enable QoS on controller"
	   	else:
	   		print "Policy not found"
	  except Exception as e:
	  	print e
	  	print "Could Not Complete Request"
	  	exit(1)
	  	helper.close_connection()
	  
	elif cmd == "modify":
	 print "Modify Policy and Service, TODO"
	 #TODO (futures)
	 
	else:
	 print "Error parsing command %s" % s_p
	 usage()
	 exit()

#write to json file
def write_add(op,json_o=None):
    conf = "qos-state.json"
    pwd = os.getcwd()
    try:
    	if os.path.exists("%s/%s" % (pwd,conf)):
    	 qos_data = open(conf)
    	else:
    	 print "Does not exists, creating %s in %s " % (conf,pwd)
         qos_data = open(conf, 'w+')
         qos_data.write('{"services":[],"policies":[]}');
         qos_data.close()
         qos_data = open(conf)
    except ValueError as e:
     print "Problem with qos-state file"
     print e
     exit(1)
     
    #load and encode
    data = simplejson.load(qos_data)
    sjson = simplejson.JSONEncoder(sort_keys=False,indent=3).encode(data)
    jsond = simplejson.JSONDecoder().decode(sjson)
    o_data = simplejson.loads(json_o)
    o_data["datetime"] = time.asctime()
    
    found = False
    if op == "service":
    	for service in jsond['services']:
    		if service['name'] == o_data['name']:
    			found = True
    			break
    	if found:
    		print "[QoSPusher]: Service Already Exists"
    	else:
    		print "Writing service to qos-state.json"
    		jsond['services'].append(o_data)
    elif op == "policy":
    	for policy in jsond['policies']:
    		#print "checking %s against %s" % (policy['name'] ,o_data['name'])
    		if policy['name'] == o_data['name']:
    			found = True
    			break
    	if found:
    		print "[QoSPusher]: Policy Already Exists"
    	else:
    			print "Writing policy to qos.state.json"
    			jsond['policies'].append(o_data)
    
    #deserialize and write back
    sjson =  simplejson.JSONEncoder(sort_keys=False,indent=3).encode(jsond)
    qos_data.close()
    newd = open(conf, 'w+')
    #housekeeping
    sjson = sjson.translate(None,'\\')
    sjson = sjson.replace('"{', '{')
    sjson = sjson.replace('}"', '}')
    #incase of mis rep "<space>{|}
    sjson = sjson.replace('" {', '{')
    sjson = sjson.replace('} "', '}')
    newd.write(sjson)
    state = os.popen("echo '%s' | python -mjson.tool | more" % sjson).read()
    print state
    newd.close()
        
#delete from json file
def write_remove(op,u_id):
    conf = "qos-state.json"
    pwd = os.getcwd()
    try:
      if os.path.exists("%s/%s" % (pwd,conf)):
       print "Opening qos-state.json in %s" % pwd
       qos_data = open(conf)
      else:
       print "%s/%s does not exist" %(pwd,conf)
    except ValueError as e:
     print "Problem with qos-state file"
     print e
     exit(1)

    #load and encode    
    data = simplejson.load(qos_data)
    sjson = simplejson.JSONEncoder(sort_keys=False,indent=3).encode(data)
    jsond = simplejson.JSONDecoder().decode(sjson)
        
    if op == "service":
     print "Deleting service from qos-state.json"
     try:
     	found = False
     	for srv in range(len(jsond['services'])):
     		if u_id == jsond['services'][srv]['name']:
     			found = True
     			del jsond['services'][srv]
     			break;
     	if not found:
     		print "Could not find service to delete from %s" % conf
     except ValueError as e:
      "Could not delete service, does not exist"
    elif op == "policy":
     print "Deleting policy from qos.state.json"
     try:
     	found = False
     	for pol in range(len(jsond['policies'])):
     		if u_id == jsond['policies'][pol]['name']:
     			found = True
     			del jsond['policies'][pol]
     			break;
     	if not found:
     		print "Could not find service to delete from %s" % conf
     except ValueError as e:
     	  "Could not delete policy, does not exist"
    
    #deserialize and write back
    sjson =  simplejson.JSONEncoder(sort_keys=False,indent=3).encode(jsond)
    qos_data.close()
    newd = open(conf, 'w+')
    sjson = sjson.translate(None,'\\')
    sjson = sjson.replace('"{', '{')
    sjson = sjson.replace('}"', '}')
    #incase of mis rep "<space>{|}
    sjson = sjson.replace('" {', '{')
    sjson = sjson.replace('} "', '}')
    newd.write(sjson)
    state = os.popen("echo '%s' | python -mjson.tool | more" % sjson).read()
    print state
    newd.close()
    
def enable(ip,port):
	  helper = httpHelper(__name="QoSHTTPHelper")
	  helper.connect(ip,port)
	  print "Enabling QoS at %s:%s" % (ip,port)
	  url = "http://%s:%s/wm/qos/tool/enable/json" % (ip,port)
	  try:
	   req = helper.request("GET",url,None)
	   print "[CONTROLLER]: %s" % req
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()
	  
def disable(ip,port):
	  helper = httpHelper(__name="QoSHTTPHelper")
	  helper.connect(ip,port)
	  print "Disabling QoS at %s:%s" % (ip,port)
	  url = "http://%s:%s/wm/qos/tool/disable/json" % (ip,port)
	  try:
	   req = helper.request("GET",url,None)
	   print "[CONTROLLER]: %s" % req
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()

def listServices(ip,port):
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(ip,port)
	print "Disabling QoS at %s:%s" % (ip,port)
	url = "http://%s:%s/wm/qos/service/json" % (ip,port)
	try:
	 req = helper.request("GET",url,None)
	 print "listing services..."
	 srvs = os.popen("echo '%s' | python -mjson.tool | more" % req).read()
	 print "[CONTROLLER]: %s" % srvs
	except Exception as e:
	 print e
	 print "Could Not Complete Request"
	 exit(1)
	helper.close_connection()

def listPolicies(ip,port):
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(ip,port)
	print "Disabling QoS at %s:%s" % (ip,port)
	url = "http://%s:%s/wm/qos/policy/json" % (ip,port)
	try:
	 req = helper.request("GET",url,None)
	 print "listing policies"
	 pols = os.popen("echo '%s' | python -mjson.tool | more" % req).read()
	 print "[CONTROLLER]: %s" % pols
	except Exception as e:
	 print e
	 print "Could Not Complete Request"
	 exit(1)
	helper.close_connection()

def qosStatus(ip,port):
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(ip,port)
	print "QoS at %s:%s" % (ip,port)
	url = "http://%s:%s/wm/qos/tool/status/json" % (ip,port)
	try:
	 req = helper.request("GET",url,None)
	 pols = os.popen("echo '%s' | python -mjson.tool | more" % req).read()
	 print "[CONTROLLER]: %s" % pols
	except Exception as e:
	 print e
	 print "Could Not Complete Request"
	 exit(1)
	helper.close_connection()
	
class httpHelper:
	
	__name = "None"
	httpcon = None
	
	#initialize
	def __init__(self, **kvargs):
	 self._attributes = kvargs
	def set_attributes(self, key, value):
	 self.attributes[key] = value
	 return
	def get_attributes(self, key):
	 return self._attributes.get(key,None)
		
	def connect(self,ip,port):		
	 try:
	   self.httpcon = httplib.HTTPConnection(ip,port)
	 except httplib.HTTPException:
	   print "Could not connect to server: %s:%s" % (ip, port)
	 except Exception as e:
	 	print "Could not connect to server: %s:%s" % (ip, port)
	 	print e
	 print "Connected to: %s:%s" % (ip,port)
	 return self.httpcon
	
	def close_connection(self):
	 try:
	  self.httpcon.close()
	 except httplib.HTTPException:
	  print "Could not close connection"
	 except Exception as e:
	  print "Could not close connection"
	  print e
	 print "Closed connection successfully"

		
	def request(self, method, url, body, content_type="application/json"):
	 headers = { "Content-Type" : content_type }
	 self.httpcon.request(method, url,body, headers)
	 response = self.httpcon.getresponse()
	 s = response.status
	 ok = httplib.OK
	 acc = httplib.ACCEPTED
	 crtd = httplib.CREATED
	 ncontnt = httplib.NO_CONTENT
	 if s != ok and s != acc and s != crtd and s != ncontnt:
		print "%s to %s got an unexpected response code: %d %s (content = '%s')" \
			% (method, url, response.status, response.reason, response.read())
	 return response.read()
	
def usage():
	print '''type "qos_pusher.py --help" for more details
	qosmanager.py < add | delete | modify > <service | policy> <service object | policy object > <controller-ip> <port>
	qosmanager.py < enable | disable | status > <controller-ip> <port> 
	qosmanager.py <list> < policies | services > <controller-ip> <port>'''
def usage_help():
	print '''
	        ###################################
		qosmanager.py
		Author: Ryan Wallner (Ryan.Wallner1@marist.edu)
		QoSPusher is a simple service and policy tool for 
		Floodlight's Quality of Service Module
		All additions and removals are saves to qos-state.json in 
		you current working directory.
		
		To check the status of the controller
		qospucher.py status 127.0.0.1 8080
			
		To Add a service:
		qosmanager.py add service '{"name": "Express Fowarding", "tos": "101000"}' 127.0.0.1 8080
							
		To Delete a service:
		qosmanager.py delete service '{"sid":"<#>"} localhost 8080
							
		To Add a policy:
		qosmanager.py add policy "{}" 127.0.0.1 8080
							
		To Delete a policy:
		qosmanager.py delete policy "{"policy-id":"<#>"}" localhost 8080
		
		To see a list of Policies or Services
		qosmanager.py  list services localhost 8080
		qosmanager.py  list policies localhost 8080
		
		To Modify a Service or Policy
		[NAME must be included, then include any parameters you want to modify]
		**Modify the ip-src and vlan-id **
		qosmanager.py modify policy "{'name':'<name of policy>', 'ip-src':'10.0.0.1','vlan-id':'5'}" 127.0.0.1 8080
		
		**Modify ToS bits**
		qosmanager.py modify service "{'name':'<name of service>', 'tos':'101000'}" localhost 8080
		
		###################################
		'''
#Call main
if  __name__ == "__main__" :
	main()
