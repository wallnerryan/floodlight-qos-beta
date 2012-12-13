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
*
**/

import java.util.List;
import net.floodlightcontroller.qos.QoSPolicy;
import net.floodlightcontroller.core.module.IFloodlightService;


public interface IQoSService extends IFloodlightService {
	
	/**
     * Enables/disables the Quality of Service Tool.
     * @param enable Whether to enable or disable the Tool.
     */
    public void enableQoS(boolean enable);
    
    /**
     * Checked the enabledness
     * @param boolean.
     */
    public boolean isEnabled();
    
    /**
     * Adds a Type of Service
     */
    public void addService(QoSTypeOfService service);
    
    /**
     * Adds a Type of Service
     */
    public List<QoSTypeOfService> getServices();

    /**
     * Deletes a Type of Service
     */
    public void deleteService(int sid);

    /**
     * Returns all of the QoS rules
     * @return List of all rules
     */
    public List<QoSPolicy> getPolicies();
    
    /**
     * 
     * @param policy
     */
    public void addPolicyToNetwork(QoSPolicy policy);
    
    /**
     * Adds a QoS Policy
     */
    public void addPolicy(QoSPolicy policy, String swid);

    /**
     * adds policy to switch
     */
    public void addPolicy(QoSPolicy policy);
    
    /**
     * 
     * @param policy from all switches
     */
    public void deletePolicyFromNetwork(String policyName);
    
    /**
     * Deletes a QoS Policy
     */
    public void deletePolicy(QoSPolicy policy);
    
    /**
     * deletes policy from switches
     */
    public void deletePolicy(String switches, String policyName);

}
