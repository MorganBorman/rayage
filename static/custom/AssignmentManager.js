// custom.AssignmentManager
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/AssignmentManager.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", "dgrid/OnDemandGrid", "dgrid/Keyboard", "dgrid/Selection", "dgrid/extensions/DijitRegistry", "dijit/Toolbar",
        "dojo/data/ObjectStore", "custom/SingletonWebsocket", "custom/WebsocketJsonStore", 'custom/ObservableWebsocketJsonStore', "dijit/form/TimeTextBox", "dijit/form/DateTextBox", 
        "dijit/layout/BorderContainer", "dijit/layout/ContentPane", "dojo/on", 
        "dojox/form/DropDownSelect", "dojo/json", "dijit/form/Button", "dijit/Dialog", "dijit/form/TextBox", "dijit/form/FilteringSelect"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, 
             baseFx, lang, timing, on, OnDemandGrid, Keyboard, Selection, DijitRegistry, Toolbar, 
             ObjectStore, RayageWebsocket, RayageJsonStore, ObservableRayageJsonStore, TimeTextBox, DateTextBox, 
             BorderContainer, ContentPane, on, 
             DropDownSelect, JSON, Button, Dialog, TextBox, FilteringSelect) {
        return declare([ContentPane, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
            
            ws: null,
            
            currently_editing_assignment_id: null,
 
            // A class to be applied to the root node in our template
            baseClass: "assignment_manager",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.border_container.startup();
                this.resize();
                
                this.setupGrid();
                
                var self = this;
                
                this.edit_button.set("disabled", true);
                this.delete_button.set("disabled", true);
                this.download_button.set("disabled", true);
                
                on(this.add_button, "click", function() {
                    self.addAssignment();
                });
                
                on(this.edit_button, "click", function() {
                    for (var id in self.assignmentGrid.selection) {
                        if (self.assignmentGrid.selection[id]) {
                            //console.log(id, self.assignmentGrid.row(id).data);
                            var assignment = self.assignmentGrid.row(id).data;
                            self.editAssignment(assignment);
                            break;
                        }
                    }
                });
                
                on(this.delete_button, "click", function() {
                    for (var id in self.assignmentGrid.selection) {
                        if (self.assignmentGrid.selection[id]) {
                            self.assignmentObjectStore.remove(id);
                            break;
                        }
                    }
                });
                
                this.templateObjectStore = new RayageJsonStore({target:"/Templates", ws:this.ws});
                this.observableTemplateStore = ObservableRayageJsonStore(this.templateObjectStore, this.ws);
                this.templateDataStore = new ObjectStore({objectStore: this.observableTemplateStore});
                
                this.template_select.set("searchAttr", "label");
                
                this.template_select.set("store", this.templateDataStore);
                
                on(this.save_button, "click", function() {
                    var obj = {};
                
                    obj["id"] = self.currently_editing_assignment_id;
                    obj["name"] = self.name_input.get("value");
                    obj["template"] = self.template_select.get("value");
                    
                    var date = self.date_input.get("value");
                    var time = self.time_input.get("value");
                    
                    date.setHours(time.getHours());
                    date.setMinutes(time.getMinutes());
                    date.setSeconds(time.getSeconds());
                    
                    obj["due_date"] = (date.getTime() / 1000);
                    
                    self.assignmentObjectStore.add(obj);
                });
            },
            
            addAssignment: function() {
                this.currently_editing_assignment_id = null;
                
                this.create_assignment_dialog.set("title", "Add Assignment");
                
                var d = new Date();
                
                this.name_input.set("value", "");
                this.template_select.set("value", "");
                this.date_input.set("value", d);
                this.time_input.set("value", d);
                
                this.create_assignment_dialog.show();
            },
            
            editAssignment: function(assignment) {
                this.currently_editing_assignment_id = assignment.id;
                
                this.create_assignment_dialog.set("title", "Edit Assignment");
                
                var d = new Date(assignment.due_date*1000);
                
                this.name_input.set("value", assignment['name']);
                this.template_select.set("value", assignment.template);
                this.date_input.set("value", d);
                this.time_input.set("value", d);
                
                this.create_assignment_dialog.show();
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.assignmentObjectStore = new RayageJsonStore({target:"/Assignments", ws:this.ws});
                this.observableAssignmentStore = ObservableRayageJsonStore(this.assignmentObjectStore, this.ws);
                
                var formatDueDate = function(object) {
                    var d = object.due_date;
                    return (new Date(d*1000)).toString();
                };
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.assignmentGrid = new declare([OnDemandGrid, Keyboard, Selection, DijitRegistry])({
                    columns: {
                        name: { label: "Name" },
                        template: { label: "Template"},
                        due_date: { label: "Due Date", get: formatDueDate }
                    },
                    selectionMode: "single",
                    cellNavigation: false,
                    pagingDelay: 500,
                    store: this.observableAssignmentStore
                }, this.assignmentGridNode);
                
                this.assignmentGrid.startup();
                
                var self = this;
                
                this.assignmentGrid.on("dgrid-select", function(event){
                    var assignmentRow = event.rows[0].data;
                    console.log("assignment clicked: ", assignmentRow);
                    
                    self.edit_button.set("disabled", false);
                    self.delete_button.set("disabled", false);
                    self.download_button.set("disabled", false);
                });
                
                this.assignmentGrid.on("dgrid-deselect", function(event){
                    self.edit_button.set("disabled", true);
                    self.delete_button.set("disabled", true);
                    self.download_button.set("disabled", true);
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
