// custom.RayageSubmitProjectDialog
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageSubmitProjectDialog.html",
        "dojo/on", "dojo/topic", "dojo/data/ObjectStore", "custom/SingletonWebsocket", "custom/WebsocketJsonStore", 'custom/ObservableWebsocketJsonStore',
        "dojo/store/Memory", "dojo/store/Cache",  
        "dijit/Dialog", "dijit/form/TextBox", "dijit/form/FilteringSelect", "dijit/form/Button"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on, topic, ObjectStore, SingletonWebsocket, WebsocketJsonStore, ObservableWebsocketJsonStore,
             Memory, Cache) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_submit_project_dialog",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                on(this.cancel_button, "click", function() {
                   self.dialog.hide();
                });
                
                on(this.new_button, "click", function() {
                    var name = self.project_name_input.get("value");
                    var template_id = self.template_select.get("value");
                    topic.publish("ui/dialogs/submit_project/new", name, template_id);
                });
                
                this.assignmentStore = new WebsocketJsonStore({target:"/Assignments", ws: SingletonWebsocket});
                this.observableAssignmentStore = ObservableWebsocketJsonStore(this.assignmentStore, SingletonWebsocket);
                this.observableAssignmentObjectStore = new ObjectStore({objectStore: this.observableAssignmentStore});
                
                this.template_select.set("searchAttr", "name");
                
                this.template_select.set("store", this.observableAssignmentObjectStore);
            },
            
            startup: function() {
                this.resize();
            },
            
            show: function() {
                this.dialog.show();
            },
            
            hide: function() {
                this.dialog.hide();
            },
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
                
            }
        });
});
