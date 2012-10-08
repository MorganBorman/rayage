var ws = new WebSocket("wss://localhost:8080/ws");
ws.onopen = function() {
   console.log("Websocket connection established.");
};

var login = function (){};
var logout = function(){};
var open_project = function(){};

// Require all the dijit element classes we need and parse the declarative application components
require(["dojo/parser", "dojo/ready", "dijit/registry", "dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "dijit/Dialog", "dijit/form/Select", "dijit/MenuBar", "dijit/MenuBarItem", "dijit/PopupMenuBarItem", "dijit/DropDownMenu", "dijit/MenuItem", "dijit/TooltipDialog"],
function(parser, ready, registry, BorderContainer, TabContainer, ContentPane, Dialog, Select){
    ready(function(){
        parser.parse();

        var rayage_project_menu = registry.byId("rayage_project_menu");
        var rayage_edit_menu = registry.byId("rayage_edit_menu");
        var rayage_login_menu = registry.byId("rayage_login_menu");
        var rayage_logout_button = registry.byId("rayage_logout_button");
        
        rayage_logout_button.domNode.style.display = "none";
        
        open_project = function() {
            var project_list_request = {"type": "project_list_request"};
            
            ws.send(JSON.stringify(project_list_request));
        }
        
        ws.onmessage = function (evt) {
            var msg = JSON.parse(evt.data);
            switch(msg.type) {
                case "login_success":
                    rayage_edit_menu.set("disabled", false);
                    rayage_project_menu.set("disabled", false);
                    
                    rayage_login_menu.domNode.style.display = "none";
                    rayage_logout_button.domNode.style.display = "inline";
                    
                    break;
                case "login_failure":
                    alert("login failed, try again.");
                    break;
                case "logout_acknowledge":
                    rayage_edit_menu.set("disabled", true);
                    rayage_project_menu.set("disabled", true);
                    
                    rayage_login_menu.domNode.style.display = "inline";
                    rayage_logout_button.domNode.style.display = "none";
                
                    break;
                case "project_list":
                    //actually update the list of available projects here
                    open_project_dialog.show();
                    break;
                default:
                    console.log("Unknown message type receivied: " + msg.type);
                    break
            }
        };
        
        login = function() {
            var login_username = registry.byId("rayage_login_username");
            var login_password = registry.byId("rayage_login_password");
            
            var login_message = {"type": "login_request",
                                 "username": login_username.value,
                                 "password": login_password.value};
        
            ws.send(JSON.stringify(login_message));
        }
        
        logout = function() {
            var logout_message = {"type": "logout_request"};
            
            ws.send(JSON.stringify(logout_message));
        }

        function addEditorTab(pane) {
            editor_tabs.addChild(pane);
            editor_tabs.selectChild(pane);
        }

        /*
        // Uncomment this block to see a demo editor pane
        
        
        var delem = document.createElement('div');
        
        var pane = new ContentPane({ title:"hello.cpp", content: delem, iconClass:'rayage_icon rayage_icon_src_cpp' });
        addEditorTab(pane);
        
        var code = "#include <iostream>\nusing namespace std;\n\nint main ()\n{\n\tcout << \"Hello World!\";     // prints Hello World!\n\tcout << \"I'm a C++ program\"; // prints I'm a C++ program\n\treturn 0;\n}\n";
        
        var editor = CodeMirror(delem, {
            value: code,
            lineNumbers: true,
            matchBrackets: true,
            mode: "clike",
            theme: "neat",
        });
        */
    });
});

/*
// Stuff below here is just kept for examples of how to work with dojo programmatically

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

require(["dojo/ready", "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/Menu", "dijit/MenuItem", "dijit/DropDownMenu"], function(ready, MenuBar, PopupMenuBarItem, Menu, MenuItem, DropDownMenu){
    ready(function(){
        var pMenuBar = new MenuBar({});

        var pSubMenu = new DropDownMenu({});
        pSubMenu.addChild(new MenuItem({
            label: "File item #1"
        }));
        pSubMenu.addChild(new MenuItem({
            label: "File item #2"
        }));
        pMenuBar.addChild(new PopupMenuBarItem({
            label: "File",
            popup: pSubMenu
        }));

        var pSubMenu2 = new DropDownMenu({});
        pSubMenu2.addChild(new MenuItem({
            label: "Cut",
            iconClass: "dijitEditorIcon dijitEditorIconCut"
        }));
        pSubMenu2.addChild(new MenuItem({
            label: "Copy",
            iconClass: "dijitEditorIcon dijitEditorIconCopy"
        }));
        pSubMenu2.addChild(new MenuItem({
            label: "Paste",
            iconClass: "dijitEditorIcon dijitEditorIconPaste"
        }));
        pMenuBar.addChild(new PopupMenuBarItem({
            label: "Edit",
            popup: pSubMenu2
        }));

        pMenuBar.placeAt("wrapper");
        pMenuBar.startup();
    });
});
*/
