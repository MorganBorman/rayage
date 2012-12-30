// custom.UserManager

define(["dojo/_base/declare","dijit/_Widget", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./_UserManager/templates/UserManager.html", 
        "dojo/on", "dojo/_base/lang", "dgrid/OnDemandGrid", "dgrid/Keyboard", "dgrid/Selection", "dojo/store/Cache", "dojo/store/Memory", 
        "custom/debounce", "custom/SingletonWebsocket",  "custom/WebsocketJsonStore", "custom/ObservableWebsocketJsonStore", 
        "custom/_UserManager/UserDialog", "custom/_UserManager/ConfirmDeleteDialog", 
        "dijit/layout/BorderContainer", "dijit/Toolbar", "dijit/ToolbarSeparator", "dijit/form/Button", "dijit/form/TextBox", 
        "dijit/layout/ContentPane", "dijit/Dialog", "dijit/form/Select"],
    function(declare, Widget, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on, lang, OnDemandGrid, Keyboard, Selection, Cache, Memory, 
             debounce, SingletonWebsocket, WebsocketJsonStore, ObservableWebsocketJsonStore) {
    
        return declare([Widget, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "user_manager",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.border_container.startup();
                this.setupGrid();
            },
            
            setupGrid: function() {
                // set up data store
                var userStore = new WebsocketJsonStore({target: "/Users", ws: SingletonWebsocket, idProperty: "id"});
                var cachedUserStore = new Cache(userStore, new Memory());
                var observableCachedUserStore = ObservableWebsocketJsonStore(cachedUserStore, SingletonWebsocket);
                
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
                
                // initialize the declaritive grid with the programmatic parameters
                var grid = new declare([OnDemandGrid, Keyboard, Selection])({
                    columns: {
                        id: { label: "ID" },
                        username: { label: "Username" },
                        permissions: { label: "Permissions", get: formatPermissions }
                    },
                    getBeforePut : false,
                    cellNavigation: false,
                    selectionMode: "extended",
                    pagingDelay: 500,
                    store: observableCachedUserStore
                }, this.userGrid);
                
                grid.startup();
                
                // Handle changes of grid selections
                var countattr = function(obj) {
                    var count = 0;
                    for(var key in obj) count++;
                    return count;
                };
                
                var on_selection_changed = lang.hitch(this, function(event){
                    var selection_count = countattr(grid.selection);
                    
                    if (selection_count > 0) this.delete_button.set("disabled", false);
                    else this.delete_button.set("disabled", true);
                    
                    if (selection_count == 1) this.edit_button.set("disabled", false);
                    else this.edit_button.set("disabled", true);
                });
                
                on(grid, "dgrid-select", function(event){
                    on_selection_changed(event);
                });
                
                on(grid, "dgrid-deselect", function(event){
                    on_selection_changed(event);
                });
                
                // Connect up the toobar buttons
                on(this.add_button, "click", lang.hitch(this, function() {
                    this.user_dialog.addUser();
                }));
                
                on(this.edit_button, "click", lang.hitch(this, function() {
                    for (var id in grid.selection) {
                        if (grid.selection[id]) {
                            var user = grid.row(id).data;
                            this.user_dialog.editUser(user);
                            break;
                        }
                    }
                }));
                
                // Keep track of the users selected for deletion pending user confirmation
                var to_delete = [];
                
                on(this.delete_button, "click", lang.hitch(this, function() {
                    to_delete = [];
                    for (var id in grid.selection) {
                        var user = grid.row(id).data;
                        to_delete.push(user);
                    }
                    
                    if (to_delete.length >= 1) this.confirm_delete_dialog.display(to_delete.length);
                }));
                
                // Connect up the confirm delete dialog events
                on(this.confirm_delete_dialog, "confirm", function(){
                    for(var i = 0; i < to_delete.length; i++) {
                        observableCachedUserStore.remove(to_delete[i].id);
                    }
                    to_delete = [];
                });
                
                on(this.confirm_delete_dialog, "cancel", function(){
                    to_delete = [];
                });
                
                // Debounce a function to set the grid's query when the user stops typing
                var debouncedSetQuery = debounce(function(value) {
                    if (value != "") {
                        grid.set('query', {"op":"any","data":[{"op":"contains","data":[{"op":"string","data":"username","isCol":true},
                                          {"op":"string","data":value,"isCol":false}]}]});
                    }
                    else {
                        grid.set('query', {});
                    }
                }, 1000);
                
                // Connect to changes in the filter text box on the toolbar
                on(this.filter_input, "change", function() {
                    debouncedSetQuery(this.value);
                });
                
                // When save on the user add/edit dialog is clicked push the user up to the store
                on(this.user_dialog, "save", function(user){
                    observableCachedUserStore.put(user);
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
