define(["dojo/_base/kernel", "dojo/_base/lang", "dojo/_base/Deferred", "dojo/_base/array", "dojo/store/Observable", "dojo/topic", "dojo/json"
], function(kernel, lang, Deferred, array, Observable, topic, JSON){

// module:
//		custom/ObservableRayageJsonStore

var ObservableRayageJsonStore = function(store, ws) {
    var observableStore = Observable(store);
    
    ws.send({'type': 'subscribe_request', 'stream': store.messageType});
    
    topic.subscribe(store.topic, function(data) {
        if (!data.hasOwnProperty("deferredId") && data.hasOwnProperty("action")) {
            console.log("action:", data.action, 'data:', data)
            switch(data.action){
                case "create": observableStore.notify(data.object); console.log("create fired."); break;
                case "update": observableStore.notify(data.object, data.object.id); console.log("update fired."); break;
                case "delete": observableStore.notify(undefined, data.object.id); console.log("delete fired."); break;
                default: break;
            }
        }
    });
    
    return observableStore;
};

lang.setObject("custom.ObservableRayageJsonStore", ObservableRayageJsonStore);

return ObservableRayageJsonStore;

});
