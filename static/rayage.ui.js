// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/on", "dojo/topic", "dijit/registry", "dojo/data/ObjectStore", "dojo/store/Memory", "dijit/layout/ContentPane", "dojo/domReady!", "dijit/MenuBar", 
         "dijit/PopupMenuBarItem", "dijit/MenuItem", "dijit/DropDownMenu", "dijit/layout/BorderContainer", "dijit/layout/TabContainer", 
         "dijit/Dialog", "dijit/form/Select", "dijit/TooltipDialog", "dijit/form/TextBox"],
function(parser, on, topic, registry, ObjectStore, Memory, ContentPane){
    parser.parse();
    
    // Hook up all the subscribers which provide ways to manipulate the UI here
    
    // Hook up all the publishers which convey information from the UI to the rest of the application here
    
    // Create an object to hold references to all the relevant UI components
    rayage_ui = new Object();

    ///////////////////////////////////////////////////////////////////////////
    // Setup our panes
    ///////////////////////////////////////////////////////////////////////////
    
    rayage_ui.editor = {
        welcome_tab: registry.byId("ui_editor_welcome_tab"),
        tab_container: registry.byId("ui_editor_tab_container")
    };
    
    on(rayage_ui.editor.tab_container, "selectChild", function() {
        var nval = rayage_ui.editor.tab_container.selectedChildWidget;
        topic.publish("ui/editor/tab_change", nval);
    });
    
    rayage_ui.editor.tab_container.watch("selectedChildWidget", function(name, oval, nval){
        topic.publish("ui/editor/tab_change", nval);
    });
    
    rayage_ui.editor.addEditorTab = function(title, code, iconClass) {
        var pane = new ContentPane({ title: title, content: "", iconClass: iconClass });
        
        rayage_ui.editor.tab_container.addChild(pane);
        
        var editor = CodeMirror(pane.domNode, {
            value: code,
            lineNumbers: true,
            matchBrackets: true,
            mode: "clike",
            theme: "neat",
        });
        
        pane.editor = editor;
        rayage_ui.editor.tab_container.selectChild(pane);
    };
    
    rayage_ui.output = {
        tab_container: registry.byId("ui_output_tab_container"),
    };

    ///////////////////////////////////////////////////////////////////////////
    // Setup our menus
    ///////////////////////////////////////////////////////////////////////////

    rayage_ui.menus = {
        project: {
            menu: registry.byId("ui_menus_project"),
            new_project: registry.byId("ui_menus_project_new_project"),
            open_project: registry.byId("ui_menus_project_open_project"),
            delete_project: registry.byId("ui_menus_project_delete_project"),
            new_file: registry.byId("ui_menus_project_new_file"),
            delete_file: registry.byId("ui_menus_project_delete_file"),
            close_project: registry.byId("ui_menus_project_close_project"),
        },
        edit: {
            menu: registry.byId("ui_menus_edit"),
            undo: registry.byId("ui_menus_edit_undo"),
            redo: registry.byId("ui_menus_edit_redo"),
            cut: registry.byId("ui_menus_edit_cut"),
            copy: registry.byId("ui_menus_edit_copy"),
            paste: registry.byId("ui_menus_edit_paste"),
            select_all: registry.byId("ui_menus_edit_select_all"),
        },
        login: {
            menu: registry.byId("ui_menus_login"),
            dialog: registry.byId("ui_menus_login_dialog"),
            username: registry.byId("ui_menus_login_username"),
            password: registry.byId("ui_menus_login_password"),
            button: registry.byId("ui_menus_login_button"),
        },
        logout:  registry.byId("ui_menus_logout"),
    };
                      
    // Add some convenience methods to the login/logout items to show/hide them
    
    rayage_ui.menus.login.menu.setVisible = function(value) {
        rayage_ui.menus.login.menu.domNode.style.display = (value ? "inline" : "none");
        rayage_ui.menus.login.dialog.domNode.style.display = (value ? "inline" : "none");;
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

    on(rayage_ui.menus.project.delete_project, "click", function(evt){
        topic.publish("ui/menus/project/delete_project");
    });

    on(rayage_ui.menus.project.new_file, "click", function(evt){
        topic.publish("ui/menus/project/new_file");
    });

    on(rayage_ui.menus.project.delete_file, "click", function(evt){
        topic.publish("ui/menus/project/delete_file");
    });

    on(rayage_ui.menus.project.close_project, "click", function(evt){
        topic.publish("ui/menus/project/close_project");
    });

    // Edit menu
    on(rayage_ui.menus.edit.undo, "click", function(evt){
        topic.publish("ui/menus/edit/undo");
    });
    
    on(rayage_ui.menus.edit.redo, "click", function(evt){
        topic.publish("ui/menus/edit/redo");
    });
    
    on(rayage_ui.menus.edit.cut, "click", function(evt){
        topic.publish("ui/menus/edit/cut");
    });
    
    on(rayage_ui.menus.edit.copy, "click", function(evt){
        topic.publish("ui/menus/edit/copy");
    });
    
    on(rayage_ui.menus.edit.paste, "click", function(evt){
        topic.publish("ui/menus/edit/paste");
    });
    
    on(rayage_ui.menus.edit.select_all, "click", function(evt){
        topic.publish("ui/menus/edit/select_all");
    });
    
    // Login/Logout
    
    var login_method = function(evt){
        var username = rayage_ui.menus.login.username.value;
        var password = rayage_ui.menus.login.password.value;
        
        topic.publish("ui/menus/login", username, password);
    }
    on(rayage_ui.menus.login.button, "click", login_method);
    
    on(rayage_ui.menus.logout, "click", function(evt){
        topic.publish("ui/menus/logout");
    });
    
    // some handlers to make the login tooltipdialog respond to pressing the enter key correctly
    on(rayage_ui.menus.login.username, "keyup", function(evt){
        if (evt.keyCode == dojo.keys.ENTER) {
            rayage_ui.menus.login.password.focus();
        }
    });
    
    on(rayage_ui.menus.login.password, "keyup", function(evt){
        if (evt.keyCode == dojo.keys.ENTER) {
            rayage_ui.menus.login.button.focus();
            login_method();
        }
    });
    
    ///////////////////////////////////////////////////////////////////////////
    // Setup our dialogs
    ///////////////////////////////////////////////////////////////////////////

    var template_selection_store = new Memory({data: []});
    var template_selection_object_store = new ObjectStore({ objectStore: template_selection_store });
        
    var project_selection_store = new Memory({data: []});
    var project_selection_object_store = new ObjectStore({ objectStore: project_selection_store });
    
    rayage_ui.dialogs = {
        new_project: {
            dialog: registry.byId("ui_dialogs_new_project"),
            selection: registry.byId("ui_dialogs_new_project_selection"),
            name: registry.byId("ui_dialogs_new_project_name"),
            selection_store: template_selection_store,
            selection_object_store: template_selection_object_store,
            new_project: registry.byId("ui_dialogs_new_project_open"),
            cancel: registry.byId("ui_dialogs_new_project_cancel"),
            setSelections: function(selections) {
                rayage_ui.dialogs.new_project.selection_store.setData(selections);
                rayage_ui.dialogs.new_project.selection.setStore(rayage_ui.dialogs.new_project.selection_object_store);
            },
        },
        new_file: {
            dialog: registry.byId("ui_dialogs_new_file"),
            selection: registry.byId("ui_dialogs_new_file_selection"),
            name: registry.byId("ui_dialogs_new_file_name"),
            selection_store: template_selection_store,
            selection_object_store: template_selection_object_store,
            new_file: registry.byId("ui_dialogs_new_file_new"),
            cancel: registry.byId("ui_dialogs_new_file_cancel"),
            setSelections: function(selections) {
                rayage_ui.dialogs.new_file.selection_store.setData(selections);
                rayage_ui.dialogs.new_file.selection.setStore(rayage_ui.dialogs.new_file.selection_object_store);
            },
        },
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
    
    // Open project dialog
    on(rayage_ui.dialogs.open_project.open, "click", function(evt){
        var value = rayage_ui.dialogs.open_project.selection.get("value");
        topic.publish("ui/dialogs/open_project/open", value);
    });
    
    on(rayage_ui.dialogs.open_project.cancel, "click", function(evt){
        var value = rayage_ui.dialogs.open_project.dialog.hide();
    });

    // New project dialog
    on(rayage_ui.dialogs.new_project.new_project, "click", function(evt){
        var name = rayage_ui.dialogs.new_project.name.get("value")
        var template = rayage_ui.dialogs.new_project.selection.get("value");
        topic.publish("ui/dialogs/new_project/new", name, template);
    });
    
    on(rayage_ui.dialogs.new_project.cancel, "click", function(evt){
        var value = rayage_ui.dialogs.new_project.dialog.hide();
    });
    
    // New file dialog
    on(rayage_ui.dialogs.new_file.new_file, "click", function(evt){
        var name = rayage_ui.dialogs.new_file.name.get("value")
        var type = rayage_ui.dialogs.new_file.selection.get("value");
        topic.publish("ui/dialogs/new_file/new", name, type);
    });
    
    on(rayage_ui.dialogs.new_file.cancel, "click", function(evt){
        var value = rayage_ui.dialogs.new_file.dialog.hide();
    });
    
    jQuery(function($, undefined) {
        $('#term_demo').terminal(function(command, term) {
            if (command !== '') {
                var result = window.eval(command);
                if (result != undefined) {
                    term.echo(String(result));
                }
            }
        }, {
            greetings: 'Javascript Interpreter',
            name: 'js_demo',
            height: 200,
            width: 450,
            prompt: 'js> ',
            enabled: false,
            onBlur: function(term) {
                    console.log("onBlur");
                },
            onFocus: function(term) {
                    console.log("onFocus");
                },
            });
            
        // Let the rest of the application know our UI is set up
        topic.publish("ui/ready", rayage_ui);
    });
});
