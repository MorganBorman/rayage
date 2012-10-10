// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/on", "dojo/topic", "dijit/registry", "dojo/data/ObjectStore", "dojo/store/Memory", "dojo/domReady!", "dijit/MenuBar", 
         "dijit/PopupMenuBarItem", "dijit/MenuItem", "dijit/DropDownMenu", "dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/layout/ContentPane", 
         "dijit/Dialog", "dijit/form/Select", "dijit/TooltipDialog", "dijit/form/TextBox"],
function(parser, on, topic, registry, ObjectStore, Memory){
    parser.parse();
    
    // Hook up all the subscribers which provide ways to manipulate the UI here
    
    // Hook up all the publishers which convey information from the UI to the rest of the application here
    
    // Create an object to hold references to all the relevant UI components
    rayage_ui = new Object();

    ///////////////////////////////////////////////////////////////////////////
    // Setup our menus
    ///////////////////////////////////////////////////////////////////////////

    rayage_ui.menus = {
        project: {
            menu: registry.byId("ui_menus_project"),
            new_project: registry.byId("ui_menus_project_new_project"),
            open_project: registry.byId("ui_menus_project_open_project"),
            new_file: registry.byId("ui_menus_project_new_file"),
        },
        edit: {
            menu: registry.byId("ui_menus_edit"),
            cut: registry.byId("ui_menus_edit_cut"),
            copy: registry.byId("ui_menus_edit_copy"),
            paste: registry.byId("ui_menus_edit_paste"),
        },
        login: {
            menu: registry.byId("ui_menus_login"),
            username: registry.byId("ui_menus_login_username"),
            password: registry.byId("ui_menus_login_password"),
            button: registry.byId("ui_menus_login_button"),
        },
        logout:  registry.byId("ui_menus_logout"),
    };
                      
    // Add some convenience methods to the login/logout items to show/hide them
    
    rayage_ui.menus.login.menu.setVisible = function(value) {
        rayage_ui.menus.login.menu.domNode.style.display = (value ? "inline" : "none");
    }
    
    rayage_ui.menus.logout.setVisible = function(value) {
        rayage_ui.menus.logout.domNode.style.display = (value ? "inline" : "none");
    }

    // Hook up the topic publishers

    // Project menu
    on(rayage_ui.menus.project.new_project, "click", function(evt){
        topic.publish("ui/menus/project/new_project");
    });

    on(rayage_ui.menus.project.open_project, "click", function(evt){
        topic.publish("ui/menus/project/open_project");
    });

    on(rayage_ui.menus.project.new_file, "click", function(evt){
        topic.publish("ui/menus/project/new_file");
    });

    // Edit menu
    on(rayage_ui.menus.edit.cut, "click", function(evt){
        topic.publish("ui/menus/edit/cut");
    });
    
    on(rayage_ui.menus.edit.copy, "click", function(evt){
        topic.publish("ui/menus/edit/copy");
    });
    
    on(rayage_ui.menus.edit.paste, "click", function(evt){
        topic.publish("ui/menus/edit/paste");
    });
    
    // Login/Logout
    
    on(rayage_ui.menus.login.button, "click", function(evt){
        var username = rayage_ui.menus.login.username.value;
        var password = rayage_ui.menus.login.password.value;
        
        topic.publish("ui/menus/login", username, password);
    });
    
    on(rayage_ui.menus.logout, "click", function(evt){
        topic.publish("ui/menus/logout");
    });
    
    ///////////////////////////////////////////////////////////////////////////
    // Setup our dialogs
    ///////////////////////////////////////////////////////////////////////////
    
    var project_selection_store = new Memory({data: []});
    var project_selection_object_store = new ObjectStore({ objectStore: project_selection_store });
    
    rayage_ui.dialogs = {
        open_project: {
            dialog: registry.byId("ui_dialogs_open_project"),
            selection: registry.byId("ui_dialogs_open_project_selection"),
            selection_store: project_selection_store,
            selection_object_store: project_selection_object_store,
            open: registry.byId("ui_dialogs_open_project_open"),
            cancel: registry.byId("ui_dialogs_open_project_cancel"),
            setSelections: function(selections) {
                rayage_ui.dialogs.open_project.selection_store.setData(selections);
                rayage_ui.dialogs.open_project.selection.setStore(rayage_ui.dialogs.open_project.selection_object_store);
            },
        }
    };
    
    on(rayage_ui.dialogs.open_project.open, "click", function(evt){
        var value = rayage_ui.dialogs.open_project.selection.get("value");
        
        topic.publish("ui/dialogs/open_project/open", value);
    });
    
    // Let the rest of the application know our UI is set up
    topic.publish("ui/ready", rayage_ui);
});