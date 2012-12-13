package net.floodlightcontroller.qos;

/**
* Copyright 2012 Marist College, New York
* Author Ryan Wallner (ryan.wallner1@marist.edu)
* 
*  Licensed under the Apache License, Version 2.0 (the "License"); you may
*  not use this file except in compliance with the License. You may obtain
*  a copy of the License at
*
*         http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
*  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
*  License for the specific language governing permissions and limitations
*  under the License.
*  
**/

import net.floodlightcontroller.qos.IQoSService;
import org.restlet.resource.Get;
import org.restlet.resource.ServerResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class QoSResource extends ServerResource{
	  protected static Logger log = LoggerFactory.getLogger(QoSResource.class);
	
	/**
	 * Get basic info about the tool
	 * @return
	 */
	 @Get("json")
	 public Object handleRequest() {
		 String op = (String) getRequestAttributes().get("op");
	        IQoSService qos = 
	                (IQoSService)getContext().getAttributes().
	                get(IQoSService.class.getCanonicalName());
	        
	        if (op.equalsIgnoreCase("enable")) {
	            qos.enableQoS(true);
	            return "{\"status\" : \"success\", \"details\" : \"QoS Enabled\"}";
	        }else if (op.equalsIgnoreCase("status")) {
	            return qos.isEnabled();
	        }else if (op.equalsIgnoreCase("disable")) {
	        	qos.enableQoS(false);
	         return "{\"status\" : \"success\", \"details\" : \"QoS Disabled\"}";
	        }
		 
		 return "{\"status\" : \"failure\", \"details\" : \"Invalid Operation\"}";
	 }

}
