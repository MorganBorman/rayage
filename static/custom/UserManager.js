// custom.UserManager
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/UserManager.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", 'dojox/grid/EnhancedGrid', "dojox/grid/enhanced/plugins/Filter", 'dojo/data/ObjectStore', 
        'dojo/data/ItemFileWriteStore', "dijit/layout/BorderContainer", "dijit/layout/ContentPane", "custom/RayageJsonStore", "dojo/on", "dojox/form/DropDownSelect"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, EnhancedGrid, Filter, ObjectStore, ItemFileWriteStore, BorderContainer, ContentPane, RayageJsonStore, on, DropDownSelect) {
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
            
            startup: function() {
                this.border_container.startup();
                this.resize();
                
                this.setupGrid();
            },
            
            updateUserInfo: function(userRow) {
                if (typeof userRow != "undefined") {
                    this.user_info_username.innerHTML = userRow.username;
                    this.user_info_permissions.set('value', userRow.permissions);
                }
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.userObjectStore = new RayageJsonStore({target:"/Users", ws:this.ws});
                this.userDataStore = new ObjectStore({objectStore: this.userObjectStore});
                
                /*set up layout*/
                var layout = [[
                  {'name': 'Id', 'field': 'id', 'width': '60px'},
                  {'name': 'Username', 'field': 'username', 'width': '175px'},
                  {'name': 'Permissions', 'field': 'permissions', 'width': '125px'}
                ]];
                

                
                console.log(this.userGrid);
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.userGrid.set("structure", layout);
                this.userGrid.set("selectionMode", "single");
                this.userGrid.startup();
                this.userGrid.setStore(this.userDataStore);
                this.userGrid.showFilterBar(true);
                //this.userGrid.plugins.filter.setupFilterQuery = setupFilter;
                this.userGrid.selection.select(0);
                
                var self = this;
                
                on(this.userGrid, "rowClick", function(e) {
                    var userRow = self.userGrid.getItem(e.rowIndex);
                    console.log("A row was clicked: ", userRow);
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
