var icon_mimes = ["text-x-csrc", "text-x-chdr", "text-x-cppsrc", "text-x-cpphdr", "text-x-generic"];

//Gets the rayage icon class based on the mimetype
var get_icon_class = function(mimetype) {
    var safemime = mimetype.replace("/", "-").replace("+", "p");
    
    if ($.inArray(safemime, icon_mimes) == -1) {
        safemime = "text-x-generic";
    }
    
    return 'rayage_icon rayage_icon_src_' + safemime;
}

require(["dojo/topic", "dojo/cookie"],
function(topic, cookie){
    
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
        rayage_ui.menus.logout.setVisible(false);
        
        topic.subscribe("ui/menus/login", function(username, password) {
            var pwhash = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
            rayage_ws.send({"type": "login_request",
                             "username": username,
                             "password": pwhash});
        });
        
        topic.subscribe("ui/menus/logout", function() {
            rayage_ws.send({"type": "logout_request"});
        });
        
        topic.subscribe("ui/menus/project/new_project", function() {
        	rayage_ws.send({"type": "template_list_request"});
        });
        
        topic.subscribe("ui/menus/project/new_file", function() {
        	rayage_ws.send({"type": "file_type_list_request"});
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
        });
        
        topic.subscribe("ui/menus/project/open_project", function() {
            rayage_ws.send({"type": "project_list_request"});
        });
        
        topic.subscribe("ws/message/project_state", function(data) {
            var editor_tab_children = rayage_ui.editor.tab_container.getChildren();
            for(var i = 0; i < editor_tab_children.length; i++) {
                rayage_ui.editor.tab_container.removeChild(editor_tab_children[i]);
            }
        
            var project_id = data.id;
            var files = data.files;
            
            for(var i = 0; i < files.length; i++) {
                var iconClass = get_icon_class(files[i].mimetype);
                
                rayage_ui.editor.addEditorTab(files[i].filename, files[i].data, iconClass);
            }
            
            rayage_ui.dialogs.open_project.dialog.hide();
            rayage_ui.dialogs.new_project.dialog.hide();
        });

        topic.subscribe("ui/dialogs/open_project/open", function(data) {
            rayage_ws.send({"type": "open_project_request", 'id': data});
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
        
        topic.subscribe("ws/message/login_success", function(data) {
            rayage_ui.menus.project.menu.set("disabled", false);
            rayage_ui.menus.logout.setVisible(true);
            rayage_ui.menus.login.menu.setVisible(false);
            
            var expiry_date = new Date( data.session_timeout*1000);
            cookie("rayage_session", data.session_cookie, { expires: expiry_date, secure: true });
        });
        
        topic.subscribe("ws/message/logout_acknowledge", function() {
            rayage_ui.menus.project.menu.set("disabled", true);
            rayage_ui.menus.logout.setVisible(false);
            rayage_ui.menus.login.menu.setVisible(true);
            
            cookie("rayage_session", null, { expires: -1, secure: true });
        });
        
        topic.subscribe("ws/connection/closed", function() {
            topic.publish("notify/disconnected");
        });
        
        topic.subscribe("ws/connection/opened", function() {
            var session_cookie = cookie("rayage_session");
            
            if (session_cookie != null) {
                var continue_session = {"type": "continue_session",
                                        "cookie_value": session_cookie};
                cookie("rayage_session", null, { expires: -1, secure: true });
                rayage_ws.send(continue_session);
            }
        });
    };
});
