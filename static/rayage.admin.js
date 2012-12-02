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
        
        topic.subscribe("ui/nav_menu/click", function(item) {
            if (item.type == "folder") return; // Don't do anything when they click on folders
            
            var open_modules = rayage_ui.tab_container.getChildren();
            
            // if the tab for that nav item is already open, switch to it
            var module_open = false;
            dojo.forEach(open_modules, function(module) {
                if (module.id == item.id) {
                    rayage_ui.tab_container.selectChild(module);
                    module_open = true;
                    var module_open = false;
                }
            });
            
            if (module_open) return;
            
            // otherwise open it (instantiate the dojo module of that type with the parameters specified)
            require([item.type], function(module) {
                var instantiation_params = jQuery.extend(true, {}, item.params);
                instantiation_params.id = item.id;
                instantiation_params.title = item.name;
                instantiation_params.closable = true;
                instantiation_params.iconClass = "rayage_icon rayage_icon_admin_" + item.iconClass;
                instantiation_params.ws = rayage_ws;
                
                var module_instance = module(instantiation_params);
                
                rayage_ui.tab_container.addChild(module_instance);
                rayage_ui.tab_container.selectChild(module_instance);
            });
        });
        
        topic.subscribe("ui/menus/open_rayage", function() {
            window.open("/");
        });
        
        topic.subscribe("ui/menus/logout", function() {
            window.location = "/logout";
        });
        
        topic.subscribe("ws/message/admin_module_tree", function(data) {
            rayage_ui.module_tree.store.setData(data.modules);
        });
        
        topic.subscribe("ws/connection/closed", function() {
            topic.publish("notify/disconnected");
        });
    };
});
