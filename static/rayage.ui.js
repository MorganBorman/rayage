// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/ready", "dojo/on", "dojo/topic", "dijit/registry"],
function(parser, ready, on, topic, registry){
    ready(function(){
        parser.parse();
        
        // Hook up all the subscribers which provide ways to manipulate the UI here
        
        // Hook up all the publishers which convey information from the UI to the rest of the application here
        
        // Potential topic organization
        /*
        ui/menus/project/create_project
        ui/menus/project/open_project
        ui/menus/project/create_file
        
        ui/menus/edit/copy
        ui/menus/edit/cut
        ui/menus/edit/paste
        ui/menus/edit/select_all
        ui/menus/edit/find
        
        ui/menus/login
        ui/menus/logout
        
        ui/dialogs/open_project/accept
        ui/dialogs/open_project/show
        ui/dialogs/open_project/hide
        
        ui/ready
        
         data-dojo-props="disabled:true"
        
        */
        
        // This doesn't work yet
        var ui_menus_edit_cut = registry.byId("ui_menus_edit_cut");
        on(ui_menus_edit_cut, "click", function(evt){
            topic.publish("ui/menus/edit/cut");
        });
        
        topic.subscribe("ui/menus/edit/cut", function(){
            alert("cut through topics.");
        });
        
        topic.publish("ui/ready");
    });
});
