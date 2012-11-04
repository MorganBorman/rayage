// custom.UserManager
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/UserManager.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", 'dojox/grid/EnhancedGrid', "dojox/grid/enhanced/plugins/Filter", 'dojo/data/ObjectStore', 
        'dojo/data/ItemFileWriteStore', "dijit/layout/BorderContainer", "dijit/layout/ContentPane", "custom/RayageJsonStore"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, EnhancedGrid, Filter, ObjectStore, ItemFileWriteStore, BorderContainer, ContentPane, RayageJsonStore) {
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
                
                this.createGrid();
            },
            
            createGrid: function() {
                /*set up data store*/
                var objectStore = new RayageJsonStore({target:"/Users", ws:this.ws});
                var dataStore = new ObjectStore({objectStore: objectStore});
                
                /*set up layout*/
                var layout = [[
                  {'name': 'Id', 'field': 'id', 'width': '60px'},
                  {'name': 'Username', 'field': 'username', 'width': '175px'},
                  {'name': 'Permissions', 'field': 'permissions', 'width': '125px'}
                ]];
                /*
                /*create a new grid*
                var grid = new EnhancedGrid({
                    id: 'grid',
                    store: dataStore,
                    structure: layout,
                    autoHeight: true,
                    autoWidth: true,
                    rowsPerPage: 30,
                    rowSelector: '20px',
                    plugins: {
                        filter: {
                            // Show the closeFilterbarButton at the filter bar
                            closeFilterbarButton: false,
                            // Set the maximum rule count to 5
                            ruleCount: 5,
                            // Set the name of the items
                            itemsName: "users"
                        }
                    }});
                    
                    //grid.showFilterBar(true);

                    /*append the new grid to the div*
                    grid.placeAt(this.userList);
                */
                
                this.userGrid.set("structure", layout);
                
                this.userGrid.set("plugins", {filter: {closeFilterbarButton: false, itemsName: "users"}});
                
                /*Call startup() to render the grid*/
                this.userGrid.startup();
                
                this.userGrid.setStore(dataStore);
                
                this.userGrid.showFilterBar(true);
                //this.userGrid.set("query", "");
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
