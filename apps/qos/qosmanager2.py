#! /usr/bin/python
# coding: utf-8
'''
*******************************************************************************************
#//TODO: *add status response checking from controller. i.e 
			*add error codes... i.e 002 == policy already exists, 011== service exists etc.
			1."Service Policy or a Queuing Policy not defined. Check if Service Exists"
			2."Service Already Exists"
			3."Policy Already Exists"
			etc.
*******************************************************************************************

QoSManager.py v2---------------------------------------------------------------------------
Developed By: Ryan Wallner (ryan.wallner1@marist.edu)
Used add Types of Service i.e.(Best Effort) and Quality of Service policy’s to the network
Utilizes the QoS modules in BigSwitch Network's Floodlight Controller

 	[author] - rjwallner
------------------------------------------------------------------------------------------
'''
import sys
import os		# for file handling
import httplib		# basic HTTP library for HTTPS connections
import urllib		# used for url-encoding during login request
import simplejson	# converts between JSON and python objects
import time		# for dates in json
import argparse		# more flexible argument parser for v2

def main():
	if (len(sys.argv)) <= 1:
        	print "Type --help for help"
		exit()
	parser = argparse.ArgumentParser(description="Floodlight Quality of Service Manager")
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
	parser.add_argument('-e','--enable',
                    required=False,
		    dest="qos_op",
		    action="store_const",
		    const="enable")
	parser.add_argument('-d','--disable',
                    required=False,
		    dest="qos_op",
		    action="store_const",
                    const="disable")
	parser.add_argument('-s','--status',
                    required=False,
		    dest="qos_op",
		    action="store_const",
                    const="status")
 	parser.add_argument('-A','--add',
                    required=False,
		    dest="action_op",
		    action="store_const",
                    const="add")
   	parser.add_argument('-D','--delete',
                    required=False,
		    dest="action_op",
		    action="store_const",
                    const="delete")
   	parser.add_argument('-M','--modify',
                    required=False,
		    dest="action_op",
		    action="store_const",
                    const="modify")
   	parser.add_argument('-L','--list',
                    required=False,
		    dest="action_op",
		    action="store_const",
		    const="list")
	parser.add_argument('-t','--type',
                    required=False,
		    dest="type",
		    choices=["policy","service","policies","services"])
	parser.add_argument('-O','--json',
                    required=False,
		    dest="obj")
	args = parser.parse_args()
	
	#Init arguments
	c = args.c
	p = args.p
	obj = args.obj
	type = args.type
	qos_op = args.qos_op
	action_op = args.action_op
	

	#HTTP Helper
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(c,p)
	
	#Enable / Disable
	if qos_op == "enable":
		enable(c,p)
		exit() 
	elif qos_op == "disable":
		disable(c,p)
		exit()
	elif qos_op == "status":
		qosStatus(c,p)
		exit()
	
	#Listing
	if action_op == "list":
	 if type != None:
	  if "service" in type:
	   listServices(c,p)
	   exit()
	  elif "polic" in type:
	   listPolicies(c,p)
	   exit()
	  else:
	   print "Unknown type: %s to list" % type
	   exit()
	 else:
	  print "Must include type of to list"
	  exit()
		 	
	#Start Add / Modify / Delete
	if action_op ==  "add":	 
	 if obj == None:
	  print "Must include json object"
	  exit(1)
	 else:
	  add(type, obj, c, p, helper)
	  exit()
	if action_op ==  "delete":	 
	 if obj == None:
	  print "Error, Must include json"
	  exit(1)
	 else:
	  delete(type, obj, c, p, helper)
	  exit()
	if action_op ==  "modify":	 
	 if obj == None:
	  print "Error, Must include json"
	  exit(1)
	 else:
	  modify(type, obj, c, p, helper)
	  exit()
	else:
	 er = "Unrecognized commands"
	 print er
	 exit(1)

########
#TODO
########
def add(obj_type, json, controller, port, conn):
	 helper = conn
	 if obj_type == "service":
	  print "Trying to add service %s" % json
	  url = "http://%s:%s/wm/qos/service/json" % (controller,port)
	  #preserve immutable
	  _json = json
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
			
	 elif obj_type == "policy":
	  print "Trying to add policy %s" % json
	  url = "http://%s:%s/wm/qos/policy/json" % (controller,port)
	  #preserve immutable
	  _json = json
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
	 else:
	  print "Error parsing command %s" % type
	  exit(1)
	  
######
#TODO
######
def delete(obj_type, json, controller, port, conn):
	 helper = conn
	 if json == None:
	  print "Must include json object"
	  exit(1)
	  #preserve immutable
	 uid_o = json
	 if obj_type == "service":
	  print "Trying to delete service %s" % json
    	  url = "http://%s:%s/wm/qos/service/json" % (controller,port)
	  try:
		#Get all services on controller
	  	name_req = helper.request("GET",url,None)   
	  	svs = simplejson.loads(name_req)
	  	o = simplejson.loads(uid_o)
	  	u_id_n = None
		#Compare
	  	for sv in  svs:
	  		if int(sv['sid']) == int(o['sid']):
	  			u_id_n = sv['name']
	  			break
	  	if u_id_n != None:
	  		req = helper.request("DELETE",url,uid_o)
	   		print "[CONTROLLER]: %s" % req
	   		r_j = simplejson.loads(req)
	   		if r_j['status'] != "Please enable Quality of Service":
				#remove service
	   			write_remove("service", u_id_n )
	   		else:
	   			print "[QoSManager] please enable QoS on controller"
	  	else:
	   		print "Service not found"
	  except Exception as e:
	   print e
	   print "Could Not Complete Request"
	   exit(1)
	  helper.close_connection()

	 elif obj_type == "policy":
	  if json == None:
	   print "Must include json object"
	   exit(1)
	  print "Trying to delete policy %s" % json
    	  url = "http://%s:%s/wm/qos/policy/json" % (controller,port)
	  try:
		#Get all policies from controller
	  	name_req = helper.request("GET",url,None)   
	  	pols = simplejson.loads(name_req)
	  	o = simplejson.loads(uid_o)
	  	u_id_n = None
		#Compare
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
				#remove policy on match
	   			write_remove("policy", u_id_n )
	   		else:
	   			print "[QoSPusher] please enable QoS on controller"
	   	else:
	   		print "Policy not found"
	  except Exception as e:
	  	print e
	  	print "Could Not Complete Request"
	  	exit(1)
	  	helper.close_connection()
	
  
def modify(obj_type, json, controller, port, conn):
	 helper == conn			
	 print "Modify Policy and Service, TODO"
	 #TODO (futures)

#WRITE JSON TO QOS_STATE JSON 
# @OP = service / policy
# @JSON_O = json object to be added
#
# @author = Ryan Wallner
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
    #print state #debug
    newd.close()
        
#DELETE JSON FILE FROM STATE JSON
# @OP = sevice / policy 
# @U_ID = unique id of service of policy
#
# @author Ryan Wallner
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
    #print state #debug
    newd.close()
    
#ENABLE QoS ON CONTROLLER
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

#DISABLE QoS ON CONTROLLER
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

#LIST SERVICE FROM CONTROLLER
def listServices(ip,port):
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(ip,port)
	print "QoS at %s:%s" % (ip,port)
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

#LIST POLICIES FROM CONTROLLER
def listPolicies(ip,port):
	helper = httpHelper(__name="QoSHTTPHelper")
	helper.connect(ip,port)
	print "QoS at %s:%s" % (ip,port)
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

#GET STATUS OF QoS ON CONTROLLER
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

#HTTP HELPER CLASS
#
# Contains connection paramters and 
# a REQUEST helper for sending and
# recieving JSON
#
# @author Ryan Wallner
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
	   self.httpcon.connect()
	 except httplib.HTTPException as e:
	   print "Could not connect to server: %s:%s" % (ip, port)
	   print e
	   exit(1)
	 except Exception as e:
	 	print "Could not connect to server: %s:%s" % (ip, port)
	 	print e
		exit(1)
	 print "Connection Successful"
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
	
#Call main :)
if  __name__ == "__main__" :
	main()
