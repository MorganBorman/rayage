// custom.WebsocketJsonStore

/* 
 * Implements the dojo/store api by sending messages over a specified websocket and subscribing
 * to a particular topic to resolve the deferreds.
 *
 * Essentially works similarily to JsonRestStore but over websockets and using topics to interact with
 * the existing system.
 *
 * Based on the tutorial at http://dojotoolkit.org/documentation/tutorials/1.8/creating_stores/
 * And dojo/store/JsonRest.js from the dojo toolkit.
*/

var websocket_json_store_id = 0;

define(["dojo/_base/declare", "dojo/topic", "dojo/Deferred", "dojo/json", "dojo/store/util/QueryResults"],
        function(declare, topic, Deferred, JSON, QueryResults){
    
    return declare(null, {

	    constructor: function(options){
		    // summary:
		    //		This is a basic store for communication with a server through JSON
		    //		formatted data over a websocket connection.
		    // options: custom/WebsocketJsonStore
		    //		This provides any configuration information that will be mixed into the store
		    declare.safeMixin(this, options);
		    
		    // This is the application global instance id
		    // Used to construct ids which will result in globally unique deferred id values.
		    this.store_id = websocket_json_store_id++;
		    
		    // Holds the id value of the next deferred
		    this.deferred_pos = 0;
		    
		    this.pendingDeferreds = {};
		
		    this.messageType = "WebsocketJsonStore"+this.target;
		    this.topic = "ws/message/"+this.messageType;
		    
		    var self = this;
		    
		    topic.subscribe(this.topic, function(data) {
		        if (data.hasOwnProperty("deferredId") && data.hasOwnProperty("response")) {
		            if (self.pendingDeferreds.hasOwnProperty(data.deferredId)) {
		                console.log("data: ", data);
		                self.pendingDeferreds[data.deferredId].raw_data = data
		                self.pendingDeferreds[data.deferredId].resolve(data.response);
		            }
		        }
		    });
	    },
	    
	    getNextDeferredId: function() {
	        var def_id = this.deferred_pos++;
	        return ("" + this.store_id + "_" + def_id);
	    },
	
	    // Used to store the current pending deferreds.
	    pendingDeferreds: {},
	
	    // ws: Websocket
	    //      The connected websocket to communicate over.
	    ws: null,

	    // target: String
	    //      The target attribute of all request objects sent to the server over the websocket.
	    target: "",

	    // idProperty: String
	    //		Indicates the property to use as the identity property. The values of this
	    //		property should be unique.
	    idProperty: "id",

	    get: function(id, options){
		    // summary:
		    //		Retrieves an object by its identity. This will trigger a "GET" request message to the server.
		    //      The message will contain the fields {type: String, target: String, action: "GET", id: id, deferredId: "#_#"}
		    // id: Number
		    //		The identity to use to lookup the object.
		    // options: null
		    //      No supported options
		    // returns: dojo/_base/Deferred
		    
		    // Setup the options
		    options = options || {};
		    
		    // Create a new deferred and store the pending entry
		    var def = new Deferred();
		    var def_id = this.getNextDeferredId();
		    this.pendingDeferreds[def_id] = def;
		    
		    // Create and send the request
		    var obj = {type: this.messageType, deferredId: def_id, action: "GET", id: id, options: options};
		    this.ws.send(obj);
		    
		    // Return the deferred
		    return def;
	    },

	    getIdentity: function(object){
		    // summary:
		    //		Returns an object's identity
		    // object: Object
		    //		The object to get the identity from
		    // returns: Number
		    return object[this.idProperty];
	    },

	    put: function(object, options){
		    // summary:
		    //		Stores an object. This will trigger a PUT request to the server
		    //		if the object has an id, otherwise it will trigger a POST request.
		    // object: Object
		    //		The object to store.
		    // options: null
		    //      No supported options
		    // returns: dojo/_base/Deferred
		    
		    // Setup the options
		    options = options || {};
		    var id = ("id" in options) ? options.id : this.getIdentity(object);
		    var hasId = typeof id != "undefined";
		    var action = (hasId && !options.incremental) ? "PUT" : "POST";
		    var objectData = JSON.stringify(object);
		    
		    // Create a new deferred and store the pending entry
		    var def = new Deferred();
		    var def_id = this.getNextDeferredId();
		    this.pendingDeferreds[def_id] = def;
		    
		    // Create and send the request
		    var obj = {type: this.messageType, deferredId: def_id, action: action, id: hasId ? id : null, objectData: objectData, options: options};
		    this.ws.send(obj);
            
		    // Return the deferred
		    return def;
	    },

	    add: function(object, options){
		    // summary:
		    //		Adds an object. This will trigger a PUT request to the server
		    //		if the object has an id, otherwise it will trigger a POST request.
		    // object: Object
		    //		The object to store.
		    // options: null
		    //      No supported options
		    options = options || {};
		    options.overwrite = false;
		    return this.put(object, options);
	    },

	    remove: function(id, options){
		    // summary:
		    //		Deletes an object by its identity. This will trigger a DELETE request to the server.
		    // id: Number
		    //		The identity to use to delete the object
		    // options: null
		    //      No supported options
		    options = options || {};
		    
		    // Create a new deferred and store the pending entry
		    var def = new Deferred();
		    var def_id = this.getNextDeferredId();
		    this.pendingDeferreds[def_id] = def;
		    
		    // Create and send the request
		    var obj = {type: this.messageType, deferredId: def_id, action: "DELETE", id: id, options: options};
		    this.ws.send(obj);
		    
		    // Return the deferred
		    return def;
	    },

	    query: function(query, options){
		    // summary:
		    //		Queries the store for objects. This will trigger a QUERY request to the server, with the
		    //		query added as a query string.
		    // query: Object
		    //		The query to use for retrieving objects from the store.
		    // options: __QueryOptions?
		    //		The optional arguments to apply to the resultset.
		    // returns: dojo/store/api/Store.QueryResults
		    //		The results of the query, extended with iterative methods.
		    
            //console.log("WebsocketJsonStore.query(", query, options, ")");
            
            jsonable_query = (typeof options.query == "function") ? query : options.query;
		    
		    options = {count: options.count, sort: options.sort, query: jsonable_query, queryOptions: options.queryOptions, start: options.start};
		    
		    // Create a new deferred and store the pending entry
		    var def = new Deferred();
		    var def_id = this.getNextDeferredId();
		    this.pendingDeferreds[def_id] = def;
		    
		    // Create and send the request
		    var obj = {type: this.messageType, deferredId: def_id, action: "QUERY", options: options};
		    this.ws.send(obj);
		    
		    def.total = def.then(function(){
			    return def.raw_data.total;
		    });
		    
		    // Return the deferred
		    return QueryResults(def);
	    }
    });
});
