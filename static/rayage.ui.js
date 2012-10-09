// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/on", "dojo/topic", "dijit/registry", "dojo/domReady!", "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/MenuItem", "dijit/DropDownMenu",
         "dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "dijit/Dialog", "dijit/form/Select", "dijit/TooltipDialog", "dijit/form/TextBox"],
function(parser, on, topic, registry){
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

    var ui_menus_edit_cut = registry.byId("ui_menus_edit_cut");
    on(ui_menus_edit_cut, "click", function(evt){
        topic.publish("ui/menus/edit/cut");
    });
    
    var ui_menus_edit_copy = registry.byId("ui_menus_edit_copy");
    on(ui_menus_edit_copy, "click", function(evt){
        topic.publish("ui/menus/edit/copy");
    });
    
    var ui_menus_edit_paste = registry.byId("ui_menus_edit_paste");
    on(ui_menus_edit_paste, "click", function(evt){
        topic.publish("ui/menus/edit/paste");
    });

    topic.subscribe("ui/menus/edit/cut", function(){
        console.log("Example of subscribing to the cut menu topic.");
    });
    
    topic.publish("ui/ready");
});
