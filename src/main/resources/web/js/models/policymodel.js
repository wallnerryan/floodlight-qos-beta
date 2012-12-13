/*
   Copyright 2012 IBM

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

window.Policy = Backbone.Model.extend({

    defaults: {
    	sid: null,
    	name: ' ',
    	ethtype: -1,
        protocol: -1,
        ingressport: -1,
		ipdst: -1,
		ipsrc: -1,
		tos:  -1,
		vlanid: -1,
		ethsrc: ' ',
		ethdst: ' ',
		tcpudpdstport: -1,
		tcpudpsrcport: -1,
		sw: 'None',
		queue: -1,
		enqueueport: -1,
		service: ' ',
		priority: 32767,
    },

   initialize:function () {}

});

window.PolicyCollection = Backbone.Collection.extend({

    model:Policy,

    initialize:function () {},
    
      fetch:function () {
        this.initialize();
    }
});