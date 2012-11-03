// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/on", "dojo/topic", "dijit/registry", "dojo/data/ObjectStore", "dojo/store/Memory", "dijit/layout/ContentPane", "dijit/TooltipDialog", "custom/BasicTerminal",
         "dojo/domReady!", "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/MenuItem", "dijit/DropDownMenu", "dijit/layout/BorderContainer", 
         "dijit/layout/TabContainer", "dijit/Dialog", "dijit/form/Select", "dijit/form/TextBox"],
function(parser, on, topic, registry, ObjectStore, Memory, ContentPane, Tooltip, BasicTerminal){
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
        tab_container: registry.byId("ui_editor_tab_container"),
        editor_instances: {},
        error_widget_instances: {},
        dirty_document_widget_instances: {}
    };
    
    on(rayage_ui.editor.tab_container, "selectChild", function() {
        var nval = rayage_ui.editor.tab_container.selectedChildWidget;
        topic.publish("ui/editor/tab_change", nval);
    });
    
    rayage_ui.editor.tab_container.watch("selectedChildWidget", function(name, oval, nval){
        if (rayage_ui.editor.editor_instances.hasOwnProperty(nval.title)) {
            var editor = rayage_ui.editor.editor_instances[nval.title];
            editor.refresh();
        }
        topic.publish("ui/editor/tab_change", nval);
    });
    
    rayage_ui.editor.addEditorTab = function(title, code, undo, iconClass, selected) {
        var pane = new ContentPane({ title: title, content: "", iconClass: iconClass });
        
        rayage_ui.editor.tab_container.addChild(pane);
        
        var editor = CodeMirror(pane.domNode, {
            value: code,
            lineNumbers: true,
            matchBrackets: true,
            mode: "clike",
            theme: "neat"
        });
        
        pane.editor = editor;
        if (selected)
            rayage_ui.editor.tab_container.selectChild(pane);
        if (undo !== null)
            editor.setHistory(undo);
        editor.refresh();

        editor.on("change", function() {
            topic.publish("ui/editor/state_change");
        });

        rayage_ui.editor.editor_instances[title] = editor;
    };

    rayage_ui.editor.addEditorErrorWidget = function(editor, id, line, errMsg) {
        if (rayage_ui.editor.error_widget_instances[id] !== undefined) {
            editor.removeLineWidget(rayage_ui.editor.error_widget_instances[id]);
            delete rayage_ui.editor.error_widget_instances[id];
        }
        var node = dojo.create("div", { innerHTML: errMsg });
        rayage_ui.editor.error_widget_instances[id] = editor.addLineWidget(line, node, {coverGutter: false, noHScroll: true});
    };
    
    rayage_ui.output = {
        tab_container: registry.byId("ui_output_tab_container"),
        terminal: registry.byId("ui_output_terminal")
        
    };
    
    on(rayage_ui.output.terminal, "inputLine", function(evt){
        topic.publish("ui/output/terminal/input_line", evt.data);
    });

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
            save_file: registry.byId("ui_menus_project_save_file"),
            delete_file: registry.byId("ui_menus_project_delete_file"),
            close_project: registry.byId("ui_menus_project_close_project")
        },
        edit: {
            menu: registry.byId("ui_menus_edit"),
            undo: registry.byId("ui_menus_edit_undo"),
            redo: registry.byId("ui_menus_edit_redo"),
            cut: registry.byId("ui_menus_edit_cut"),
            copy: registry.byId("ui_menus_edit_copy"),
            paste: registry.byId("ui_menus_edit_paste"),
            select_all: registry.byId("ui_menus_edit_select_all")
        },
        build:   registry.byId("ui_menus_build"),
        run:   registry.byId("ui_menus_run"),
        logout:  registry.byId("ui_menus_logout")
    };

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

    on(rayage_ui.menus.project.save_file, "click", function(evt) {
        var filename = rayage_ui.editor.tab_container.selectedChildWidget.title;
        topic.publish("ui/menus/project/save_file", filename);
    });

    on(rayage_ui.menus.project.delete_file, "click", function(evt){
        var filename = rayage_ui.editor.tab_container.selectedChildWidget.title;
        topic.publish("ui/menus/project/delete_file", filename);
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

    // Build project
    on(rayage_ui.menus.build, "click", function(evt){
        topic.publish("ui/menus/build");
    });

    // Run project
    on(rayage_ui.menus.run, "click", function(evt){
        topic.publish("ui/menus/run");
    });
    
    // Login/Logout
    
    on(rayage_ui.menus.logout, "click", function(evt){
        topic.publish("ui/menus/logout");
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
            }
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
            }
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
            }
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
            
    // Let the rest of the application know our UI is set up
    topic.publish("ui/ready", rayage_ui);
});
