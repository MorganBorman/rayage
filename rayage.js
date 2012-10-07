// Require all the dijit element classes we need and parse the declarative application components
require(["dojo/parser", "dojo/ready", "dijit/registry", "dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "dijit/MenuBar", "dijit/MenuBarItem", "dijit/PopupMenuBarItem", "dijit/DropDownMenu", "dijit/MenuItem", "dijit/TooltipDialog"],
function(parser, ready, registry, BorderContainer, TabContainer, ContentPane){
    ready(function(){
        parser.parse();

        var editor_tabs = registry.byId("rayage_editor_tabs");

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
// Uncomment this to demo the websocket functionality of the backend


var ws = new WebSocket("ws://localhost:8080/ws");
ws.onopen = function() {
   ws.send("Hello, world");
};
ws.onmessage = function (evt) {
   alert("received socket echo: " + evt.data);
};
*/


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
