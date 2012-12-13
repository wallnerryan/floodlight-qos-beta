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

import org.openflow.util.HexString;

import net.floodlightcontroller.qos.QoSPolicy;

public class QoSPolicy implements Comparable<QoSPolicy>{
	
	//create params
	public long policyid;
	public String name;
	public short ethtype;
	public byte protocol;
	public short ingressport;
	public int ipdst;
	public int ipsrc;
	public byte tos;
	public short vlanid;
	public String ethsrc;
	public String ethdst;
	public short tcpudpsrcport;
	public short tcpudpdstport;
	
	//Can be "all", "dpid" or [TODO: list of "dpid,dpid"]
	//TODO Morph to use a String[] of Switches
	public String sw;
	
	//If it is queuing, must ignore ToS bits. and set "enqueue".
	//port for enqueue
	public short queue;
	public short enqueueport;
	
	//default type of service to best effort
	public String service;
	
	//Defaulted Priority
	public short priority = 0;
	
	/** -1's are check in QoS.java: policyToFlowMod() **/
	public QoSPolicy(){
		this.policyid = 0;
		this.name = null;
		this.ethtype = -1;
		this.protocol = -1;
		this.ingressport = -1;
		this.ipdst = -1;
		this.ipsrc = -1;
		this.tos = -1;
		this.vlanid = -1;
		this.ethsrc = null;
		this.ethdst = null;
		this.tcpudpdstport = -1;
		this.tcpudpsrcport = -1;
		this.sw = "all";
		this.queue = -1;
		this.enqueueport = -1;
		this.service = null;
		this.priority = 32767;
		
	}
	
	/**
     * Generates a unique ID for the instance
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
     * @param rule the policy to compare with
     * @return number representing the result of comparison
     * 0 if equal
     * negative if less than 'policy'
     * greater than zero if greater priority policy than 'policy'
     */
	public int compareTo(QoSPolicy policy) {
		return this.priority - ((QoSPolicy)policy).priority;
    }
	
	/**
	 * @param policy
	 * @return
	 */
	public boolean isSameAs(QoSPolicy policy){
		//check object and unique name of policy
		if (this.equals(policy) || this.name.equals(policy.name)){
			return true;
		}
		else{
			return false;
		}
	}
	
	/**
	 * Override hashcode
	 */
	@Override
	public int hashCode(){
	final int prime = 2521;
    int result = super.hashCode();
    result = prime * result + (int) policyid;
    if(name != null){result = prime * result + name.hashCode();}
    result = prime * result + (int) ethtype;
    result = prime * result + (int) protocol;
    result = prime * result + (int) ingressport;
    result = prime * result + ipdst;
    result = prime * result + ipsrc;
    result = prime * result + (int) tos;
    result = prime * result + (int) vlanid;
    if(ethsrc != null){result = prime * result + (int) HexString.toLong(ethsrc);}
    if(ethdst != null){result = prime * result + (int) HexString.toLong(ethdst);}
    result = prime * result + (int) tcpudpsrcport;
    result = prime * result + (int) tcpudpdstport;
    if(sw != null){result = prime * result + sw.hashCode();}
    result = prime * result + (int) queue;
    result = prime * result + (int) enqueueport;
    if(service != null){result = prime * result + service.hashCode();}
    result = prime * result + (int) priority;
	
    return result;
	}
}
