require(["dojo/topic"],
function(topic){
    
    var rayage_ws = null;
    var rayage_ui = null;
    
    var on_ui_ws_ready = function(){};
    
    topic.subscribe("ws/ready", function(ws){
        rayage_ws = ws;
        if (rayage_ui != null) {
            on_ui_ws_ready();
        }
    });
    
    topic.subscribe("ui/ready", function(ui){
        rayage_ui = ui;
        if (rayage_ws != null) {
            on_ui_ws_ready();
        }
    });
    
    on_ui_ws_ready = function(){
        rayage_ws.connect();
        
        topic.subscribe("ws/connection/opened", function() {
            rayage_ws.send({type: 'admin_module_tree_request'});
        });
        
        topic.subscribe("ws/message/admin_module_tree", function(data) {
            rayage_ui.module_tree.store.setData(data.modules);
            //rayage_ui.module_tree.store.remove('EU');
        });
    };
});
