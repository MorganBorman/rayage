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
        topic.subscribe("ui/dialogs/new_project/new", function(name, template) {
            rayage_ws.send({"type": "new_project_request", "name": name, "template": template});
            rayage_ui.dialogs.new_project.dialog.hide();
        });
        
        topic.subscribe("ws/message/template_list", function(data) {
            rayage_ui.dialogs.new_project.setSelections(data.templates);
            rayage_ui.dialogs.new_project.dialog.show();
        });
        
        topic.subscribe("ui/menus/project/open_project", function() {
            rayage_ws.send({"type": "project_list_request"});
        });
        
        topic.subscribe("ws/message/project_state", function(data) {
            var project_id = data.id;
            var files = data.files;
            
            for(var i = 0; i < files.length; i++) {
                rayage_ui.editor.addEditorTab(files[i].filename, files[i].data);
            }
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
        
        topic.subscribe("ws/message/login_failure", function() {
            alert("login failed, try again.");
        });
        
        topic.subscribe("ws/message/logout_acknowledge", function() {
            rayage_ui.menus.project.menu.set("disabled", true);
            rayage_ui.menus.logout.setVisible(false);
            rayage_ui.menus.login.menu.setVisible(true);
            
            cookie("rayage_session", null, { expires: -1, secure: true });
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


// Ignore everything below here for now
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// Stuff below here is just kept for examples of how to work with dojo programmatically
/*
require(["dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "dojo/ready"],
function(BorderContainer, TabContainer,ContentPane, ready){
	ready(function(){
		// create the BorderContainer and attach it to our appLayout div
		var appLayout = new BorderContainer({
			design: "headline"
		}, "appLayout");


		// create the TabContainer
		var contentTabs = new TabContainer({
			region: "center",
			id: "contentTabs",
			tabPosition: "top",
			"class": "centerPanel"
		});

		// add the TabContainer as a child of the BorderContainer
		appLayout.addChild( contentTabs );

		// create and add the BorderContainer edge regions
		appLayout.addChild(
			new ContentPane({
				region: "top",
				"class": "edgePanel",
				content: "maybe a toolbar/ribbon goes here"
			})
		);
		appLayout.addChild(
			new ContentPane({
				region: "left",
				id: "leftCol", "class": "edgePanel",
				content: "Maybe a project tree view goes here.",
				splitter: true
			})
		);
        
        var delem = document.createElement('div');

        var code = "#include <iostream>\nusing namespace std;\n\nint main ()\n{\n\tcout << \"Hello World!\";     // prints Hello World!\n\tcout << \"I'm a C++ program\"; // prints I'm a C++ program\n\treturn 0;\n}\n";

		contentTabs.addChild(
            new ContentPane({
				title: "hello_world.cpp",
				content: delem,
			})
		);

		// start up and do layout
		appLayout.startup();

        var editor = CodeMirror(delem, {
            value: code,
            lineNumbers: true,
            matchBrackets: true,
            mode: "clike",
            theme: "neat",
            minHeight: "100%",
        });
	});
});

*/
