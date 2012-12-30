// custom.RayageAdmin
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageAdmin.html",
        "dojo/topic", "custom/SingletonWebsocket", "dijit/layout/ContentPane", "custom/debounce", "dojo/on", "dojo/dom-attr", "dojo/dom-construct", 
        
        "dojo/_base/unload", "dojo/store/Memory", "dojo/store/Observable", "dijit/tree/ObjectStoreModel", "dojo/Deferred", "dgrid/extensions/DijitRegistry", 
        
        "dgrid/List", "dgrid/OnDemandGrid", "dgrid/tree", "dgrid/Selection", "dgrid/Keyboard", "dojo/store/util/QueryResults", "put-selector/put", 
        
        "dijit/layout/BorderContainer", "custom/RayageAdminMenu", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "custom/BasicTerminal",
        "custom/RayageNewProjectDialog", "custom/RayageOpenProjectDialog", "custom/RayageNewFileDialog", "custom/RayageDisconnectedDialog"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             topic, SingletonWebsocket, ContentPane, debounce, on, domAttr, domConstruct,
             baseUnload, Memory, Observable, ObjectStoreModel, Deferred, DijitRegistry, 
             List, Grid, tree, Selection, Keyboard, QueryResults, put) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_admin",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            reconnect: function(){
                SingletonWebsocket.connect();
            },
            
            startup: function() {
                this.border_container.startup();
                
                var self = this;
                
                SingletonWebsocket.url = "wss://" + document.location.hostname + ":" + document.location.port + "/ws";
                
                topic.subscribe("ws/message/redirect", function(data) {
                    window.location = data.target;
                });
                
                topic.subscribe("ws/message/login_success", function() {
                });
                
                topic.subscribe("ui/menus/open_rayage", function() {
                    window.open("/");
                });
                
                topic.subscribe("ui/menus/logout", function() {
                    window.location = "/logout";
                });
                
                var socket_closed_subscription = topic.subscribe("ws/connection/closed", function() {
                    self.disconnected_dialog.show();
                });
                
                baseUnload.addOnUnload(window, function() { 
                    socket_closed_subscription.remove();
                });
                
                topic.subscribe("ui/dialogs/disconnected/reconnect", function() {
                    SingletonWebsocket.connect();
                });
                
                topic.subscribe("ws/connection/opened", function() {
                    self.disconnected_dialog.hide();
                    SingletonWebsocket.send({type: 'admin_module_tree_request'});
                });
                
                SingletonWebsocket.connect();
                
                this.setupNavPane();
            },
            
            setupNavPane: function() {
                var self = this;
                
                var module_store = Observable(new Memory({
                    data: [
                        { id: 'admin_modules', name:'Admin Modules', type:'folder', parent: 'NA'}
                    ],
                    getChildren: function(parent, options){
                        return this.query({parent: parent.id}, options);
                    },
                    mayHaveChildren: function(parent){
                        return parent.type == "folder";
                    },
                    query: function(query, options){
                        var def = new Deferred();
                        var immediateResults = this.queryEngine(query, options)(this.data);
                        setTimeout(function(){
                            def.resolve(immediateResults);
                        }, 200);
                        var results = QueryResults(def.promise);
                        return results;
                    }
                }));
                
                var renderCell = function(object, value, node, options){
                    var outerNode = document.createElement('div');
                    
                    var iconNode = document.createElement('div');
                    iconNode.setAttribute('class', "rayage_icon rayage_icon_admin_" + object.iconClass);
                    iconNode.setAttribute('style', "float: left;");
                    outerNode.appendChild(iconNode);
                    
                    var textNode = document.createTextNode(value);
                    outerNode.appendChild(textNode);
                    
                    return outerNode;
                };
                
				var nav_tree = new declare([Grid, Selection, DijitRegistry, Keyboard])({
					store: module_store,
					query: {type: "folder"},
					selectionMode: "single",
					showHeader: false,
					columns: {
						name: tree({label:'Name', 
						            sortable: false,
						            renderCell: renderCell,
						            shouldExpand: function(row, level, previouslyExpanded){
						                return true;
						            }
					              })
					}
				}, this.nav_pane);
                
                nav_tree.startup();
                
                on(nav_tree, ".dgrid-cell:click", function(event){
                    var cell = nav_tree.cell(event);
                    var item = cell.row.data;
                    
                    if (item.type == "folder") return; // Don't do anything when they click on folders
                    
                    var open_modules = self.tab_container.getChildren();
                    
                    // if the tab for that nav item is already open, switch to it
                    var module_open = false;
                    dojo.forEach(open_modules, function(module) {
                        if (module.id == item.id) {
                            self.tab_container.selectChild(module);
                            module_open = true;
                        }
                    });
                    
                    if (module_open) return;
                    
                    // otherwise open it (instantiate the dojo module of that type with the parameters specified)
                    require([item.type], function(module) {
                        var instantiation_params = jQuery.extend(true, {}, item.params);
                        instantiation_params.id = item.id;
                        instantiation_params.title = item.name;
                        instantiation_params.closable = true;
                        instantiation_params.iconClass = "rayage_icon rayage_icon_admin_" + item.iconClass;
                        instantiation_params.ws = SingletonWebsocket;
                        
                        var module_instance = module(instantiation_params);
                        
                        self.tab_container.addChild(module_instance);
                        self.tab_container.selectChild(module_instance);
                    });
                });
	            
                topic.subscribe("ws/message/admin_module_tree", function(data) {
                    dojo.forEach(data.modules, function(item) {
		                module_store.put(item, {overwrite: true});
	                });
                });
            },
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
            }
        });
});
