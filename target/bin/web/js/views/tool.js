/*
   Copyright 2012 IBM & Marist College 2012

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

window.ToolListView = Backbone.View.extend({

	initialize:function () {
			console.log('...Initializing Tools Page');
        	this.template = _.template(tpl.get('tools-list'));
        	this.model.bind("change", this.render, this);
        	this.model.bind("add", this.render, this);
        	
    	},

	render:function (eventName) {
       		$(this.el).html(this.template({ntools:tl.length}));
			_.each(this.model.models, function (t) {
				$(this.el).find('#tools > tbody:first-child').append(new ToolsListItemView({model:t}).render().el);
			}, this);
			return this;
	},
});

window.ToolsListItemView = Backbone.View.extend({

	tagName:"tr",

	initialize:function () {
        this.template = _.template(tpl.get('tools-list-item'));
        this.model.bind("change", this.render, this);
        this.model.bind("destroy", this.render, this);
      },
      
    render:function () {
    	$(this.el).html(this.template(this.model.toJSON()));
        return this;
    },
    
});


window.ToolDetailsView = Backbone.View.extend({

	initialize:function () {
        this.template = _.template(tpl.get('tool'));
        this.model.bind("change", this.render, this);
        this.model.bind("add", this.render, this);
    },
    
    events:{
        "click #enable-button":"enableToolFunction",
        "click #disable-button":"disableToolFunction"
		//TODO add / remove qos policies
    },

    render:function (event) {
        $(this.el).html(this.template(this.model.toJSON()));
        if (!event) var event = window.event;
    	if (event.target) targ = event.target;
    	if(targ.name != null){
        	//console.log(targ.name);
        	if(targ.name == "Quality" || targ.name == 'quality of service'){
        		$(this.el).find('#qos').show();
         		//Services & Policies
       	 		$(this.el).find('#services').html(new ServiceListView({model:this.model.services}).render().el);
				$(this.el).find('#policies').html(new PolicyListView({model:this.model.policies}).render().el);
			}
			if(targ.name == "Firewall"){
			console.log("Firewall specific load");
			}
		}
		return this;
    },
    
    enableToolFunction:function (event){
    	model = this.model;
    	if (!event) var event = window.event;
    	if (event.target) targ = event.target;
    	if(targ.name != null){
    		switch (targ.name.toLowerCase()){
    			case 'firewall':
    				//TODO send a post to enable
    				alert('Enabling: '+targ.name);
    				$.ajax({
  						type: 'GET',
 						url:hackBase + "/wm/firewall/module/enable/json",
  						async: false,
  						success:function (data){
  							console.log(data);
  							model.set({enabled: "true"});
  							},
  						error:function(data){
  							console.log(data);
  							},
						});
    				break;
    			case 'quality of service':
    				//TODO send a post to enable
    				alert('Enabling: '+targ.name);
    				$.ajax({
  						type: 'GET',
 						url:hackBase + "/wm/qos/tool/enable/json",
  						async: false,
  						success:function (data){
  							console.log(data);
  							model.set({enabled: "true"});
  							},
  						error:function(data){
  							console.log(data);
  							},
  						});
    				break;
    			default:
    				console.log("Cannot enable this tool");
    		}
    	}
    },
    disableToolFunction:function (event){
    	model = this.model;
    	if (!event) var event = window.event;
    	if (event.target) targ = event.target;
    	if(targ.name != null){
    		switch (targ.name.toLowerCase()){
    			case 'firewall':
    				//TODO send a post to disable
    				alert('Disabling: '+targ.name);
    				$.ajax({
  						type: 'GET',
 						url:hackBase + "/wm/firewall/module/disable/json",
  						async: false,
  						success:function (data){
  							console.log(data);
  							model.set({enabled: "false"});
  							},
  						error:function(data){
  							console.log(data);
  							},
						});
    				break;
    			case 'quality of service':
    				//TODO send a post to disable
    				alert('Disabling: '+targ.name);
    				$.ajax({
  						type: 'GET',
 						url:hackBase + "/wm/qos/tool/disable/json",
  						async: false,
  						success:function (data){
  							console.log(data);
  							model.set({enabled: "false"});
  							},
  						error:function(data){
  							console.log(data);
  							},
  						});
    				break;
    			default:
    				console.log("Cannot disable this tool");
    		}
    	}
    },

});


