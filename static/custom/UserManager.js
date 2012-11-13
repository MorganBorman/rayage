// custom.UserManager
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/UserManager.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", 'dojox/grid/EnhancedGrid', "dojox/grid/enhanced/plugins/Filter", 'dojo/data/ObjectStore', 
        'dojo/data/ItemFileWriteStore', "dijit/layout/BorderContainer", "dijit/layout/ContentPane", 'custom/ObservableRayageJsonStore', "custom/RayageJsonStore", "dojo/on", 
        "dojox/form/DropDownSelect", "dojo/json"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, EnhancedGrid, Filter, ObjectStore, ItemFileWriteStore, BorderContainer, ContentPane, ObservableRayageJsonStore, RayageJsonStore, on, DropDownSelect, JSON) {
        return declare([ContentPane, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
            
            ws: null,
 
            // A class to be applied to the root node in our template
            baseClass: "user_manager",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            current_user: undefined,
            
            startup: function() {
                this.border_container.startup();
                this.resize();
                
                this.setupGrid();
            },
            
            click_change_permissions: function() {
                
                if (typeof this.current_user != "undefined") {
                    this.current_user.permissions = this.user_info_permissions.get('value');
                    this.userObjectStore.put(this.current_user);
                    //this.observableUserStore.put(this.current_user);
                }
                
                //this.current_user.permissions = this.user_info_permissions.get('value');
                //var obj = {type: "RayageJsonStore/Users", deferredId: "101_0", action: "PUT", id: this.current_user.id, objectData: JSON.stringify(this.current_user), options: {}};
		        //this.ws.send(obj);
            },
            
            updateUserInfo: function(userRow) {
                if (typeof userRow != "undefined") {
                    this.user_info_username.innerHTML = userRow.username;
                    this.user_info_permissions.set('value', userRow.permissions);
                    this.current_user = userRow;
                }
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.userObjectStore = new RayageJsonStore({target:"/Users", ws:this.ws});
                this.observableUserStore = ObservableRayageJsonStore(this.userObjectStore);
                this.userDataStore = new ObjectStore({objectStore: this.observableUserStore});
                
                function formatPermissions(datum) {
                    
                    switch(datum) {
                        case '0':
                        case 0:
                            return "None";
                            break;
                        case '1':
                        case 1:
                            return "User";
                            break;
                        case '2':
                        case 2:
                            return "TA";
                            break;
                        case '3':
                        case 3:
                            return "Professor";
                            break;
                        case '4':
                        case 4:
                            return "Admin";
                            break;
                        default:
                            return datum;
                            break;
                    }
                }
                
                /*set up layout*/
                var layout = [[
                  {'name': 'Id', 'field': 'id', 'width': '60px'},
                  {'name': 'Username', 'field': 'username', 'width': '175px'},
                  {'name': 'Permissions', 'field': 'permissions', 'width': '125px', formatter: formatPermissions}
                ]];
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.userGrid.set("structure", layout);
                this.userGrid.set("selectionMode", "single");
                this.userGrid.startup();
                this.userGrid.setStore(this.userDataStore);
                this.userGrid.showFilterBar(true);
                //this.userGrid.plugins.filter.setupFilterQuery = setupFilter;
                this.userGrid.selection.select(0);
                
                var self = this;
                
                // This is a hack, it shouldn't be necessary to do this.
                //dojo.connect(this.observableUserStore, 'notify', function(){ self.userGrid._refresh(); });
                
                on(this.userGrid, "rowClick", function(e) {
                    var userRow = self.userGrid.getItem(e.rowIndex);
                    self.updateUserInfo(userRow);
                });
            },
            
            // The constructor
            constructor: function(args) {
            
                this.onClose = function() {
                    return true;
                };
                
                dojo.safeMixin(this, args);
                
            },
        });
});
