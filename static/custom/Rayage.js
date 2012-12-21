var icon_mimes = ["text-x-csrc", "text-x-chdr", "text-x-cppsrc", "text-x-cpphdr", "text-x-generic"];

//Gets the rayage icon class based on the mimetype
var get_icon_class = function(mimetype) {
    var safemime = mimetype.replace("/", "-").replace("+", "p");
    
    if ($.inArray(safemime, icon_mimes) == -1) {
        safemime = "text-x-generic";
    }
    
    return 'rayage_icon rayage_icon_src_' + safemime;
}

// custom.Rayage
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/Rayage.html",
        "dojo/topic", "custom/RayageWebsocket", "dijit/layout/ContentPane", "custom/debounce", "dojo/on", "dojo/dom-attr", "dojo/dom-construct", 
        "dojo/_base/unload", 
        "dijit/layout/BorderContainer", "custom/RayageMenu", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "custom/BasicTerminal",
        "custom/RayageNewProjectDialog", "custom/RayageOpenProjectDialog", "custom/RayageNewFileDialog", "custom/RayageDisconnectedDialog"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             topic, RayageWebsocket, ContentPane, debounce, on, domAttr, domConstruct,
             baseUnload) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            reconnect: function(){
                RayageWebsocket.connect();
            },
            
            editor_instances: {},
            dirty_document_widget_instances: {},
            error_widget_instances: {},
            
            addEditorTab: function(title, code, undo, iconClass, selected) {
                var pane = new ContentPane({ title: title, content: "", iconClass: iconClass });
                
                this.editor_tab_container.addChild(pane);
                
                var editor = CodeMirror(pane.domNode, {
                    value: code,
                    lineNumbers: true,
                    matchBrackets: true,
                    mode: "clike",
                    theme: "neat"
                });
                
                pane.editor = editor;
                if (selected)
                    this.editor_tab_container.selectChild(pane);
                if (undo !== null)
                    editor.setHistory(undo);
                editor.refresh();

                editor.on("change", function() {
                    topic.publish("ui/editor/state_change");
                });

                this.editor_instances[title] = editor;
            },
            
            addEditorErrorWidget: function(editor, id, line, errMsg) {
                if (this.error_widget_instances[id] !== undefined) {
                    editor.removeLineWidget(this.error_widget_instances[id]);
                    delete this.error_widget_instances[id];
                }
                var node = dojo.create("div", { innerHTML: errMsg });
                this.error_widget_instances[id] = editor.addLineWidget(line, node, {coverGutter: false, noHScroll: true});
            },
            
            startup: function() {
                this.border_container.startup();
                
                var self = this;
                
                this.main_menu.setFunctionalityGroups(["user"], "disabled", true);
                
                RayageWebsocket.url = "wss://" + document.location.hostname + ":" + document.location.port + "/ws";
                
                topic.subscribe("ws/message/redirect", function(data) {
                    window.location = data.target;
                });
                
                topic.subscribe("ws/message/login_success", function() {
                    self.main_menu.setFunctionalityGroups(["user"], "disabled", false);
                    self.main_menu.setFunctionalityGroups(["project", "file"], "disabled", true);
                });
                
                topic.subscribe("ui/menus/logout", function() {
                    window.location = "/logout";
                });
                
                topic.subscribe("ui/menus/project/new", function() {
        	        RayageWebsocket.send({"type": "template_list_request"});
                });
                
                on(self.editor_tab_container, "selectChild", function() {
                    var nval = self.editor_tab_container.selectedChildWidget;
                    topic.publish("ui/editor/tab_change", nval);
                });
                
                self.editor_tab_container.watch("selectedChildWidget", function(name, oval, nval){
                    if (self.editor_instances.hasOwnProperty(nval.title)) {
                        var editor = self.editor_instances[nval.title];
                        editor.refresh();
                    }
                    topic.publish("ui/editor/tab_change", nval);
                });
        
                topic.subscribe("ui/menus/file/new", function() {
                	RayageWebsocket.send({"type": "file_type_list_request"});
                });

                topic.subscribe("ui/menus/file/save", function() {
                    // TODO: Synchronize state
                    var filename = self.editor_tab_container.selectedChildWidget.title;
                    RayageWebsocket.send({"type": "save_file_request", "filename": filename});
                });
                
                topic.subscribe("ui/menus/file/revert", function() {
                    var filename = self.editor_tab_container.selectedChildWidget.title;
                	if (confirm("Do you really want to revert back to the saved state?")) {
                    	RayageWebsocket.send({"type": "revert_file_request", "filename": filename});
                    }
                });

                topic.subscribe("ui/menus/project/delete", function() {
                    if (confirm("Do you really want to delete this project?")) {
                        // delete it!
                        RayageWebsocket.send({"type": "delete_project_request"});
                    }
                });

                topic.subscribe("ui/menus/file/delete", function() {
                    // TODO: Synchronize project state (before tabs refresh)
                    var filename = self.editor_tab_container.selectedChildWidget.title;
                    if (confirm("Do you really want to delete " + filename + "?")) {
                        // delete it!
                        RayageWebsocket.send({"type": "delete_file_request", "file": filename});
                    }
                });
                
                topic.subscribe("ws/message/file_type_list", function(data) {
                    self.new_file_dialog.setSelections(data.types);
                    self.new_file_dialog.show();
                });
                
                topic.subscribe("ui/menus/edit/undo", function() {
                	var editor = self.editor_tab_container.selectedChildWidget.editor;
                	editor.undo();
                });
                
                topic.subscribe("ui/menus/edit/redo", function() {
                	var editor = self.editor_tab_container.selectedChildWidget.editor;
                	editor.redo();
                });
                
                topic.subscribe("ui/menus/edit/select_all", function() {
                	var editor = self.editor_tab_container.selectedChildWidget.editor;
                	var lines = editor.lineCount();
                	
                	start = {line: 0, ch: 0};
                	end = {line: lines, ch: 0};
                	
                	editor.setSelection(start, end);
                });
                

                topic.subscribe("ui/dialogs/new_file/new", function(name, type) {
                    // TODO: synchronize the project state (get latest undo state)
                    RayageWebsocket.send({"type": "new_file_request", "name": name, "filetype": type});
                    self.new_file_dialog.hide();
                });
                
                topic.subscribe("ui/dialogs/new_project/new", function(name, template) {
                    RayageWebsocket.send({"type": "new_project_request", "name": name, "template": template});
                });
                
                topic.subscribe("ws/message/template_list", function(data) {
                    self.new_project_dialog.setSelections(data.templates);
                    self.new_project_dialog.show();
                });
                
                topic.subscribe("ui/menus/project/close", function() {
                    RayageWebsocket.send({"type": "close_project_request"});
                });
                
                topic.subscribe("ui/menus/project/save", function() {
                    var editor_tab_children = self.editor_tab_container.getChildren();		
                    for(var i = 0; i < editor_tab_children.length; i++) {
                            var filename = editor_tab_children[i].title;
                            RayageWebsocket.send({"type": "save_file_request", "filename": filename});
                    }
                });
                
                topic.subscribe("ui/editor/tab_change", function(current_tab) {
                    window.setTimeout(function(){
                        var disable_edit_menu = (current_tab.editor == undefined);
                        self.main_menu.setFunctionalityGroups(["file"], "disabled", disable_edit_menu);
                    }, 1);
                });
                
                topic.subscribe("ws/message/close_project_acknowledge", function() {
                    var editor_tab_children = self.editor_tab_container.getChildren();
                    for(var i = 0; i < editor_tab_children.length; i++) {
                        self.editor_tab_container.removeChild(editor_tab_children[i]);
                    }
                
                    self.editor_tab_container.addChild(self.editor_welcome_tab);
                    
                    self.main_menu.setFunctionalityGroups(["user"], "disabled", false);
                    self.main_menu.setFunctionalityGroups(["project", "file"], "disabled", true);
                });
                
                topic.subscribe("ui/menus/project/open", function() {
                    RayageWebsocket.send({"type": "project_list_request"});
                });
                
                topic.subscribe("ws/message/project_state", function(data) {
                    var editor_tab_children = self.editor_tab_container.getChildren();

                    for(var i = 0; i < editor_tab_children.length; i++) {
                        self.editor_tab_container.removeChild(editor_tab_children[i]);
                    }
                    self.editor_instances = {};
                    self.dirty_document_widget_instances = {};
                
                    var project_id = data.id;
                    var files = data.files;

                    for(var i = 0; i < files.length; i++) {
                        var iconClass = get_icon_class(files[i].mimetype);
                        
                        self.addEditorTab(files[i].filename, files[i].data, files[i].undo_data, iconClass, files[i].selected);
                        // Adding a rayageDirty property to each editor because marking a CodeMirror instance as
                        // dirty is non-trivial.
                        self.editor_instances[files[i].filename].rayageDirty = files[i].modified;
                    }

                    topic.publish("ui/editor/state_change");
                    
                    self.new_project_dialog.hide();
                    self.open_project_dialog.hide();
                    
                    self.main_menu.setFunctionalityGroups(["user"], "disabled", false);
                    self.main_menu.setFunctionalityGroups(["project"], "disabled", false);
                    if (files.length > 0) {
                        self.main_menu.setFunctionalityGroups(["file"], "disabled", false);
                    } else {
                        self.main_menu.setFunctionalityGroups(["file"], "disabled", true);
                    }
                });

                topic.subscribe("ui/dialogs/open_project/open", function(data) {
                    RayageWebsocket.send({"type": "open_project_request", 'id': data});
                });

                topic.subscribe("ui/menus/build", function() {
                    var projectDirty = false;
                    var unsavedFiles = [];

                    for (var filename in self.editor_instances) {
                        var editor = self.editor_instances[filename];

                        if (!editor.isClean() || editor.rayageDirty === true) {
                                projectDirty = true;
                                unsavedFiles.push(filename);
                        }
                    }
                    
                    if (!projectDirty || confirm("You have unsaved files. Continuing will save them before building.\nContinue?")) {
                        // This probably should be changed to a save all request of some kind
                        for (var i=0,len=unsavedFiles.length; i<len; i++) {
                            var filename = unsavedFiles[i];
                            RayageWebsocket.send({"type": "save_file_request", "filename": filename});
                        }
                        RayageWebsocket.send({"type": "build_project_request"});
                    }
                });

                topic.subscribe("ui/menus/run", function() {
                    var args = self.main_menu.run_arguments_input.value;
                    RayageWebsocket.send({"type": "run_project_request", "args": args});
                });
                
                on(self.output_terminal, "inputLine", function(evt){
                    RayageWebsocket.send({"type": "run_stdin_data", "data": evt.data});
                });
                
                topic.subscribe("ws/message/run_stdout_data", function(data) {
                    self.output_terminal.outputOutLine(data.data);
                });
                
                topic.subscribe("ws/message/run_stderr_data", function(data) {
                    self.output_terminal.outputErrLine(data.data);
                });

                topic.subscribe("ws/message/project_list", function(data) {
                    self.open_project_dialog.setSelections(data.projects);

                    // Toggle Project List form between projects and no projects state
                    var open = self.open_project_dialog.open_button;
                    var selection = self.open_project_dialog.project_select;
                    if (data.projects.length < 1) {
                        // Add a no projects option and disable open and select elements.
                        selection.addOption({ label: "No Projects", value: "" });
                        selection.set('disabled', true);
                        open.set('disabled', true);
                    } else {
                        // If there are projects then enable the open and select elements.
                        selection.set('disabled', false);
                        open.set('disabled', false);
                    }

                    self.open_project_dialog.show();
                });

                topic.subscribe("ui/editor/state_change", function(delay) {
                    // delay is by default 250 ms
                    // but it can optionally be set to 0 for things like saving.
                    delay = typeof delay !== 'undefined' ? delay : 250;
                    debounce(function() {
                        var serialized = {"files": Array(), "type": "project_state_push"};
                        for (var filename in self.editor_instances) {
                            var editor = self.editor_instances[filename];

                            if ((!editor.isClean() || editor.rayageDirty === true)
                                && self.dirty_document_widget_instances[filename] === undefined) {
                                
                                var dirty = domConstruct.create("div");
                                domAttr.set(dirty, "class", "error-bg");
                                domAttr.set(dirty, "innerHTML", "This document is unsaved.");
                                domAttr.set(dirty, "style", "text-align: center;");
                                                                 
                                var w = editor.addLineWidget(0, dirty, {coverGutter: true, noHScroll: true, above: true});
                                self.dirty_document_widget_instances[filename] = w;
                            }

                            var file = { "data": editor.getValue(),
                                         "filename": filename,
                                         "modified": !editor.isClean(),
                                         "undo_data": editor.getHistory()};
                            serialized.files.push(file);
                        }
                        RayageWebsocket.send(serialized);
                    }, delay)();
                });

                topic.subscribe("ws/message/build_error_list", function(data) {
                    for(var i=0, len=data.errors.length; i < len; i++) {
                        var err = data.errors[i];
                        var editor = self.editor_instances[err.filename];
                        var line = editor.getLineHandle(err.line_no - 1); // code mirror starts at line 0

                        editor.addLineClass(line, "wrap", "error-bg");
                        CodeMirror.on(line, "delete", function() {
                            delete self.error_widget_instances[i];
                        });
                        self.addEditorErrorWidget(editor, i, line, err.error_msg);

                        editor.refresh();
                    }
                });
                
                var socket_closed_subscription = topic.subscribe("ws/connection/closed", function() {
                    //topic.publish("notify/disconnected");
                    self.disconnected_dialog.show();
                });
                
                baseUnload.addOnUnload(window, function() { 
                    socket_closed_subscription.remove();
                });
                
                topic.subscribe("ui/dialogs/disconnected/reconnect", function() {
                    RayageWebsocket.connect();
                });
                
                topic.subscribe("ws/connection/opened", function() {
                    self.disconnected_dialog.hide();
                });
                
                RayageWebsocket.connect();
            },
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
            }
        });
});
