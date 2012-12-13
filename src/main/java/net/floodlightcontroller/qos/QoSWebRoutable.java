package net.floodlightcontroller.qos;

import org.restlet.Context;
import org.restlet.routing.Router;

import net.floodlightcontroller.qos.QoSResource;
import net.floodlightcontroller.qos.QoSPoliciesResource;
import net.floodlightcontroller.restserver.RestletRoutable;

public class QoSWebRoutable implements RestletRoutable{
	
	/**
     * Create the Restlet router and bind to the proper resources.
     */
    @Override
    public Router getRestlet(Context context) {
        Router router = new Router(context);
        router.attach("/tool/{op}/json", QoSResource.class);
        router.attach("/service/json", QoSTypeOfServiceResource.class);
        router.attach("/policy/json", QoSPoliciesResource.class);
        return router;
    }

    /**
     * Set the base path for the Quality of Service
     */
    @Override
    public String basePath() {
        return "/wm/qos";
    }

}
