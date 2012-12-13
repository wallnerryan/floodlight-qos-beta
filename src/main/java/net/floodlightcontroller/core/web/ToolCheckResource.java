package net.floodlightcontroller.core.web;

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
*  Provides a way of knowing which tools are enabled/available on the controller
*  Information provided by the tools.properties file.
*    
**/

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.Properties;
import org.restlet.resource.Get;
import org.restlet.resource.ServerResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.floodlightcontroller.firewall.IFirewallService;
import net.floodlightcontroller.qos.IQoSService;

public class ToolCheckResource extends ServerResource {
	public static Logger logger = LoggerFactory.getLogger(ToolCheckInfo.class);
	
    	public class ToolCheckInfo{
    		IQoSService qos = 
                    (IQoSService)getContext().getAttributes().
                    get(IQoSService.class.getCanonicalName());
    		IFirewallService firewall = 
                    (IFirewallService)getContext().getAttributes().
                    get(IFirewallService.class.getCanonicalName());
    		
    		protected Properties prop = new Properties();
    		protected String[] tools;
    		protected String is_enabled;
    		protected String currentTool;
    		    		
    		public HashMap<String,String> getTools(){
    			HashMap<String,String> toolSet = 
    					new HashMap<String,String>();
    			try {
    				//load a properties file
    				prop.load(new FileInputStream("src/main/resources/tools.properties"));
    				tools = prop.getProperty("tools").split(",");
    				//Return tools  from props
    				for (int i=0; i<tools.length; i++){
    					//Tool information from properties file
    					currentTool = tools[i];
    					is_enabled = prop.getProperty(tools[i]);
    					toolSet.put(currentTool, is_enabled);
    				}
    			} catch (FileNotFoundException e) {
    				e.printStackTrace();
    			} catch(IOException e) {
    				e.printStackTrace();
    			}
    			logger.debug("Toolset is: {}",toolSet);
    			return toolSet;
    		}
    	
    		//Courtesy of Jacob
    		public boolean classExists(String className)
    		{
    			try {
    		Class.forName (className);
    		return true;
    			}
    			catch (ClassNotFoundException exception) {
    				return false;
    			}
    		}
    	
    		public ToolCheckInfo(){
    			this.getTools();
    		}
    	}
    	@Get("json")
        public ToolCheckInfo toolCheck() {
    		//return a simple list of tool for the webUI to get
            return new ToolCheckInfo();
        }
}
