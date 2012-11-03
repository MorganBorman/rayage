var icon_mimes = ["text-x-csrc", "text-x-chdr", "text-x-cppsrc", "text-x-cpphdr", "text-x-generic"];

//Gets the rayage icon class based on the mimetype
var get_icon_class = function(mimetype) {
    var safemime = mimetype.replace("/", "-").replace("+", "p");
    
    if ($.inArray(safemime, icon_mimes) == -1) {
        safemime = "text-x-generic";
    }
    
    return 'rayage_icon rayage_icon_src_' + safemime;
}

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
        
        rayage_ui.menus.edit.menu.set("disabled", true);
        rayage_ui.menus.project.menu.set("disabled", true);
        
        rayage_ui.menus.project.new_file.set("disabled", true);
        rayage_ui.menus.project.delete_file.set("disabled", true);
        rayage_ui.menus.project.close_project.set("disabled", true);
        rayage_ui.menus.project.delete_project.set("disabled", true);
        rayage_ui.menus.build.set("disabled", true);
        rayage_ui.menus.run.set("disabled", true);
        
        topic.subscribe("ws/message/redirect", function(data) {
            window.location = data.target;
        });
        
        topic.subscribe("ui/menus/logout", function() {
            window.location = "/logout";
        });
        
        topic.subscribe("ui/menus/project/new_project", function() {
        	rayage_ws.send({"type": "template_list_request"});
        });
        
        topic.subscribe("ui/menus/project/new_file", function() {
        	rayage_ws.send({"type": "file_type_list_request"});
        });

        topic.subscribe("ui/menus/project/delete_project", function() {
            if (confirm("Do you really want to delete this project?")) {
                // delete it!
                rayage_ws.send({"type": "delete_project_request"});
            }
        });

        topic.subscribe("ui/menus/project/delete_file", function(filename) {
            // TODO: Synchronize project state (before tabs refresh)
            if (confirm("Do you really want to delete " + filename + "?")) {
                // delete it!
                rayage_ws.send({"type": "delete_file_request", "file": filename});
            }
        });
        
        topic.subscribe("ws/message/file_type_list", function(data) {
            rayage_ui.dialogs.new_file.setSelections(data.types);
            rayage_ui.dialogs.new_file.dialog.show();
        });
        
        topic.subscribe("ui/menus/edit/undo", function() {
        	var editor = rayage_ui.editor.tab_container.selectedChildWidget.editor;
        	editor.undo();
        });
        
        topic.subscribe("ui/menus/edit/redo", function() {
        	var editor = rayage_ui.editor.tab_container.selectedChildWidget.editor;
        	editor.redo();
        });
        
        topic.subscribe("ui/menus/edit/select_all", function() {
        	var editor = rayage_ui.editor.tab_container.selectedChildWidget.editor;
        	var lines = editor.lineCount();
        	
        	start = {line: 0, ch: 0};
        	end = {line: lines, ch: 0};
        	
        	editor.setSelection(start, end);
        });
        

        topic.subscribe("ui/dialogs/new_file/new", function(name, type) {
            // TODO: synchronize the project state (get latest undo state)
            rayage_ws.send({"type": "new_file_request", "name": name, "filetype": type});
            rayage_ui.dialogs.new_file.dialog.hide();
        });
        
        topic.subscribe("ui/dialogs/new_project/new", function(name, template) {
            rayage_ws.send({"type": "new_project_request", "name": name, "template": template});
            rayage_ui.dialogs.new_project.dialog.hide();
        });
        
        topic.subscribe("ws/message/template_list", function(data) {
            rayage_ui.dialogs.new_project.setSelections(data.templates);
            rayage_ui.dialogs.new_project.dialog.show();
        });
        
        topic.subscribe("ui/menus/project/close_project", function() {
            rayage_ws.send({"type": "close_project_request"});
        });
        
        topic.subscribe("ui/editor/tab_change", function(current_tab) {
            window.setTimeout(function(){
                var disable_edit_menu = (current_tab.editor == undefined);
                rayage_ui.menus.edit.menu.set("disabled", disable_edit_menu);
            }, 1);
        });
        
        topic.subscribe("ws/message/close_project_acknowledge", function() {
            var editor_tab_children = rayage_ui.editor.tab_container.getChildren();
            for(var i = 0; i < editor_tab_children.length; i++) {
                rayage_ui.editor.tab_container.removeChild(editor_tab_children[i]);
            }
        
            rayage_ui.editor.tab_container.addChild(rayage_ui.editor.welcome_tab);
            
            rayage_ui.menus.project.new_file.set("disabled", true);
            rayage_ui.menus.project.delete_file.set("disabled", true);
            rayage_ui.menus.project.close_project.set("disabled", true);
            rayage_ui.menus.project.delete_project.set("disabled", true);
            rayage_ui.menus.build.set("disabled", true);
            rayage_ui.menus.run.set("disabled", true);
        });
        
        topic.subscribe("ui/menus/project/open_project", function() {
            rayage_ws.send({"type": "project_list_request"});
        });
        
        topic.subscribe("ws/message/project_state", function(data) {
            var editor_tab_children = rayage_ui.editor.tab_container.getChildren();

            for(var i = 0; i < editor_tab_children.length; i++) {
                rayage_ui.editor.tab_container.removeChild(editor_tab_children[i]);
            }
            rayage_ui.editor.editor_instances = {};
        
            var project_id = data.id;
            var files = data.files;
            
            for(var i = 0; i < files.length; i++) {
                var iconClass = get_icon_class(files[i].mimetype);
                
                rayage_ui.editor.addEditorTab(files[i].filename, files[i].data, iconClass);
            }
            
            rayage_ui.dialogs.open_project.dialog.hide();
            rayage_ui.dialogs.new_project.dialog.hide();
            
            rayage_ui.menus.project.new_file.set("disabled", false);
            rayage_ui.menus.project.delete_file.set("disabled", false);
            rayage_ui.menus.project.close_project.set("disabled", false);
            rayage_ui.menus.project.delete_project.set("disabled", false);
            rayage_ui.menus.build.set("disabled", false);
            rayage_ui.menus.run.set("disabled", false);
        });

        topic.subscribe("ui/dialogs/open_project/open", function(data) {
            rayage_ws.send({"type": "open_project_request", 'id': data});
        });

        topic.subscribe("ui/menus/build", function() {
            rayage_ws.send({"type": "build_project_request"});
        });

        topic.subscribe("ui/menus/run", function() {
            rayage_ws.send({"type": "run_project_request", "args": []});
        });
        
        topic.subscribe("ui/output/terminal/input_line", function(data) {
            rayage_ws.send({"type": "run_stdin_data", "data": data});
        });
        
        topic.subscribe("ws/message/run_stdout_data", function(data) {
            rayage_ui.output.terminal.outputOutLine(data.data);
        });
        
        topic.subscribe("ws/message/run_stderr_data", function(data) {
            rayage_ui.output.terminal.outputErrLine(data.data);
        });

        topic.subscribe("ws/message/project_list", function(data) {
            rayage_ui.dialogs.open_project.setSelections(data.projects);

            // Toggle Project List form between projects and no projects state
            var open = rayage_ui.dialogs.open_project.open;
            var selection = rayage_ui.dialogs.open_project.selection;
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

            rayage_ui.dialogs.open_project.dialog.show();
        });
        
        topic.subscribe("ws/message/login_success", function() {
            rayage_ui.menus.project.menu.set("disabled", false);
        });

        topic.subscribe("ws/message/build_error_list", function(data) {
            for(var i=0, len=data.errors.length; i < len; i++) {
                var err = data.errors[i];
                var editor = rayage_ui.editor.editor_instances[err.filename];
                var line = editor.getLineHandle(err.line_no - 1); // code mirror starts at line 0

                editor.setLineClass(line, "error-text error-text-"+i, "error-bg error-bg-"+i);
                CodeMirror.on(line, "delete", function() {
                    delete rayage_ui.editor.error_widget_instances[i];
                });
                rayage_ui.editor.addEditorErrorWidget(editor, i, line, err.error_msg);

                editor.refresh();
            }
        });
        
        topic.subscribe("ws/connection/closed", function() {
            topic.publish("notify/disconnected");
        });
    };
});
