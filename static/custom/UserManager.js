// custom.UserManager
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/UserManager.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", "dgrid/OnDemandGrid", "dgrid/Keyboard", "dgrid/Selection", 
        "dijit/layout/BorderContainer", "dijit/layout/ContentPane", 'custom/ObservableRayageJsonStore', "custom/RayageJsonStore", "dojo/on", 
        "dojox/form/DropDownSelect", "dojo/json", "custom/debounce"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, OnDemandGrid, Keyboard, Selection, BorderContainer, ContentPane, ObservableRayageJsonStore, RayageJsonStore, on, DropDownSelect, JSON, debounce) {
    
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
                this.setupQueryFilter();
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
                    
                    var user_since = new Date(userRow.user_since*1000);
                    this.user_info_user_since.innerHTML = "User since: " + user_since.toString();
                    
                    if (typeof userRow.last_online != "undefined" && userRow.last_online != null && userRow.last_online != -1) {
                        if (userRow.last_online != 0) {
                            var last_online = new Date(userRow.last_online*1000);
                            this.user_info_last_online.innerHTML = "Last online: " + last_online.toString();
                        } else {
                            this.user_info_last_online.innerHTML = "Last online: Now";
                        }
                    } else {
                        this.user_info_last_online.innerHTML = "Last online: Never";
                    }
                    
                    this.current_user = userRow;
                }
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.userObjectStore = new RayageJsonStore({target:"/Users", ws:this.ws});
                this.observableUserStore = ObservableRayageJsonStore(this.userObjectStore, this.ws);
                //this.userDataStore = new ObjectStore({objectStore: this.observableUserStore});
                
                function formatPermissions(object) {
                    var datum = object.permissions;
                    
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
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.userGrid = new declare([OnDemandGrid, Keyboard, Selection])({
                    columns: {
                        id: { label: "ID" },
                        username: { label: "Username" },
                        permissions: { label: "Permissions", get: formatPermissions }
                    },
                    selectionMode: "single",
                    cellNavigation: false,
                    pagingDelay: 500,
                    store: this.observableUserStore
                }, this.userGrid);
                
                this.userGrid.startup();
                
                var self = this;
                
                this.userGrid.on("dgrid-select", function(event){
                    var userRow = event.rows[0].data;
                    console.log(userRow);
                    self.updateUserInfo(userRow);
                });
            },
            
            debouncedSetQuery: debounce(function(self, value) {
                        self.userGrid.set('query', {"op":"any","data":[{"op":"contains","data":[{"op":"string","data":"username","isCol":true},
                                                    {"op":"string","data":value,"isCol":false}]}]});
            }, 1000),
            
            setupQueryFilter: function() {
                var self = this;
                on(this.filterQuery, "change", function() {
                    self.debouncedSetQuery(self, this.value);
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
