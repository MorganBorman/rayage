// custom.RayageNewProjectDialog
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageNewProjectDialog.html",
        "dojo/on", "dojo/topic", "dojo/data/ObjectStore", "custom/SingletonWebsocket", "custom/WebsocketJsonStore", 'custom/ObservableWebsocketJsonStore', 
        "dijit/Dialog", "dijit/form/TextBox", "dijit/form/FilteringSelect", "dijit/form/Button"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on, topic, ObjectStore, RayageWebsocket, RayageJsonStore, ObservableRayageJsonStore) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_new_project_dialog",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                on(this.cancel_button, "click", function() {
                   self.dialog.hide();
                });
                
                on(this.new_button, "click", function() {
                    var name = self.project_name_input.get("value");
                    var template_id = self.template_select.get("value");
                    topic.publish("ui/dialogs/new_project/new", name, template_id);
                });
                
                this.templateObjectStore = new RayageJsonStore({target:"/Templates", ws:RayageWebsocket});
                this.observableTemplateStore = ObservableRayageJsonStore(this.templateObjectStore, RayageWebsocket);
                this.templateDataStore = new ObjectStore({objectStore: this.observableTemplateStore});
                
                this.template_select.set("searchAttr", "label");
                
                this.template_select.set("store", this.templateDataStore);
            },
            
            startup: function() {
                //this.border_container.startup();
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
