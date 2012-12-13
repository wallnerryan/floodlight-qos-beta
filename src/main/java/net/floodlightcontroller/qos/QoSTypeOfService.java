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
* Implementation adopted from Firewall
* Credit To:
* @author Amer Tahir
* @edited KC Wang
**/

public class QoSTypeOfService implements Comparable<QoSTypeOfService>{
	
	//TODO create params
	
	public int sid;
	public String name;
	
	//default best effort
	public byte tos = 0x00;
	
	public QoSTypeOfService(){
		//TODO create this.param = value
		this.sid = -1;
		this.name = null;
		this.tos = 0x00;
	}
	/**
     * Generates a unique ID for the instance
     * 
     * @return int representing the unique id
     */
    public int genID() {
        int uid = this.hashCode();
        if (uid < 0) {
            uid = uid * 15551;
            uid = Math.abs(uid);
        }
        return uid;
    }
	
	/**
     * Comparison method for Collections.sort method
     * @param rule the rule to compare with
     * @return number representing the result of comparison
     * 0 if equal
     * negative if less than 'rule'
     * greater than zero if greater priority rule than 'rule'
     */
	public int compareTo(QoSTypeOfService policy) {
		return this.tos - ((QoSTypeOfService)policy).tos;
    }
	
	/**
	 * Check whether a service is the same
	 * @param service
	 * @return
	 */
	public boolean isSameAs(QoSTypeOfService service){
		//check if either the object, name or service ToS bits match
		if(this.equals(service) || (this.name == service.name) || (this.tos == service.tos)){
		return true;
		}
		else{
			return false;
		}
	}

	@Override
	public int hashCode(){
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + (int) sid;
		if(name != null){result = prime * result +  name.hashCode();}
		result = prime * result + (int) tos;
		return result;
	}
}