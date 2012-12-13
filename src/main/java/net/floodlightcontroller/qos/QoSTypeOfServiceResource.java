package net.floodlightcontroller.qos;

import java.io.IOException;
import java.util.Iterator;
import java.util.List;

import net.floodlightcontroller.qos.IQoSService;
import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.JsonParser;
import org.codehaus.jackson.JsonToken;
import org.codehaus.jackson.map.MappingJsonFactory;
import org.restlet.resource.Delete;
import org.restlet.resource.Post;
import org.restlet.resource.Get;
import org.restlet.resource.ServerResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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
* Implementation adopted from Firewall
*/

public class QoSTypeOfServiceResource extends ServerResource {
	public static Logger logger = LoggerFactory.getLogger(QoSTypeOfServiceResource.class);
	
	/**
	 * Get list of services
	 * @return
	 */
	@Get("json")
	public Object handleRequest(){
		IQoSService qos = 
                (IQoSService)getContext().getAttributes().
                get(IQoSService.class.getCanonicalName());
		String status = null;
		if(qos.isEnabled()){
			// gets the list of policies currently being implemented
	        return qos.getServices();
		}
		else{
			status = "Please enable Quality of Service";
			return ("{\"status\" : \"" + status + "\"}");
		}
	}
	 /**
     *
     * @param tosJson The qos policy entry in JSON format.
     * @return A string status message
     */
    @Post
    public String store(String tosJson) {
    	IQoSService qos = 
    			(IQoSService)getContext().getAttributes().
    			get(IQoSService.class.getCanonicalName());
    	
    	//dummy service
    	QoSTypeOfService service;
    	try{
    		service = jsonToService(tosJson);
    	}
    	catch(IOException e){
    		logger.debug("Error Parsing QoS Service to JSON: {}, Error: {}", tosJson, e);
    		e.printStackTrace();
    		return "{\"status\" : \"Error! Could not parse Service, see log for details.\"}";
    	}
    	String status = null;
    	if(checkIfServiceExists(service,qos.getServices())){
    		status = "Error!, This service already exists!";
    		logger.error(status);
    	}
    	else{
    		//Only add if enabled ?needed?
    		if(qos.isEnabled()){
    			status = "Adding Type Of Service: " + service.name + " " + service.tos;
    			qos.addService(service);	
    		}
    		else{
    			status = "Please enable Quality of Service";
    		}
    	}
    	return ("{\"status\" : \"" + status + "\"}");
    }
    
   /**
    * 
    * @param tosJson
    * @return
    */
    @Delete
    public String delete(String tosJson) {
    	IQoSService qos = 
    			(IQoSService)getContext().getAttributes().
    			get(IQoSService.class.getCanonicalName());
    	
    	//dummy service
    	QoSTypeOfService service;
    	
    	//Accepts just "name": "<Service-Name>"
    	//or the full service object
    	try{
    		service = jsonToService(tosJson);
    	}
    	catch(IOException e){
    		logger.debug("Error Parsing QoS Service to JSON: {}, Error: {}", tosJson, e);
    		e.printStackTrace();
    		return "{\"status\" : \"Error! Could not parse Service, see log for details.\"}";
    	}
    	String status = null;
    	if(qos.isEnabled()){
    		boolean found = false;
    		Iterator<QoSTypeOfService> sIter = qos.getServices().iterator();
    		while(sIter.hasNext()){
    			QoSTypeOfService s = sIter.next();
    			if(s.sid == service.sid){
    				found = true;
    				break;
    			}
    		}
    		if(!found){
    			status = "Error! Cannot delete a rule with this ID or NAME, does not exist.";
    			logger.error(status);
    		}
    		else{
    			qos.deleteService(service.sid);
    			status = "Type Of Service Service-ID: "+service.sid+" Deleted";
    			}
    	}
    	else{
    		status = "Please enable QoS";
    	}
    	return ("{\"status\" : \"" + status + "\"}");
    }

    /**
     * Take in a json POST and turns it into a QoS Service
     * @param tosJson
     * @return
     * @throws IOException
     */
    public static QoSTypeOfService jsonToService(String tosJson) throws IOException {
    	QoSTypeOfService service = new QoSTypeOfService();
    	MappingJsonFactory jf = new MappingJsonFactory();
    	JsonParser jp;
    	
    	try{
    		jp = jf.createJsonParser(tosJson);
    	}catch(JsonParseException e){
    		throw new IOException(e);
    	}
    	
    	//debug for dev
    	logger.info("JSON Object POSTED is " +jp.toString());
    	
    	//see if the the current token is '{' to start processing json objects
    	JsonToken tkn = jp.getCurrentToken();
    	if(tkn != JsonToken.START_OBJECT){
    		jp.nextToken();
    		if(jp.getCurrentToken() != JsonToken.START_OBJECT){
    			throw new IOException("Did not recieve START_OBJECT");
    		}
    	}
    	while(jp.nextToken() != JsonToken.END_OBJECT){
    		if (jp.getCurrentToken() != JsonToken.FIELD_NAME){
    			throw new IOException("Needed a FIELD_NAME token");
    		}
    		
    		try{
    			String s = jp.getCurrentName();
    		
    			jp.nextToken();
    			//System.out.println("Current text is "+ jp.getText()); //debug for dev
    			if(jp.getText().equals("")){
    				continue;
    			}
    		
    			//user only needs to specify with remove
    			//when it becomes stored it will get a different id
    			//Reference QoS.java:381
    			if(s == "sid"){
    				service.sid = Integer.parseInt(jp.getText());
    			}
    			else if(s == "name"){
    				service.name = jp.getText();
    			
    			}
    			// do not need to check the Byte length 0-64 here, this will be caught
    			// by the addService QoS.java:371
    			else if(s == "tos"){
    				//This is so you can enter a binary number or a integer number.
    				//It will be stored as a Byte
    				try{
    					//Try to get binary number first
    					Integer tmpInt = Integer.parseInt(jp.getText(),2);
    					service.tos = tmpInt.byteValue();
    				}catch(NumberFormatException e){
    					logger.debug("Number entered was not binary, processing as int...");
    					//Must be entered as 0-64
    					Integer tmpInt = Integer.parseInt(jp.getText());
    					service.tos = tmpInt.byteValue();
    				}
    			
    			}
    		
    		}catch(JsonParseException e){
    			logger.debug("Error getting current FIELD_NAME {}", e);
    		}catch(IOException e){
    			logger.debug("Error procession Json {}", e);
    		}
    	}
    	
		return service;
    }
    
   /**
    * Check
    * @param service
    * @param services
    * @return
    */
    public static boolean checkIfServiceExists(QoSTypeOfService service, List<QoSTypeOfService> services){
    	Iterator<QoSTypeOfService> iter = services.iterator();
    	while(iter.hasNext()){
    		QoSTypeOfService s = iter.next();
    		//catch if entire service is same or name or bits
    		if(service.isSameAs(s) || service.name.equals(s.name) || service.equals(s.tos) ){
    			return true;
    		}
    	}
    	return false;
    }

}
