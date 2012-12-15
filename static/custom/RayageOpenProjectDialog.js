// custom.RayageOpenProjectDialog
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageOpenProjectDialog.html",
        "dojo/on", "dojo/topic", "dojo/data/ObjectStore", "dojo/store/Memory", 
        "dijit/Dialog", "dijit/form/Select", "dijit/form/Button"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on, topic, ObjectStore, Memory) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
            
            selection_store: null,
            selection_object_store: null,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_open_project_dialog",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                on(this.cancel_button, "click", function() {
                   self.dialog.hide();
                });
                
                on(this.open_button, "click", function() {
                    var project_id = self.project_select.get("value");
                    topic.publish("ui/dialogs/open_project/open", project_id);
                });
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
            
            setSelections: function(selections) {
                this.selection_store.setData(selections);
                this.project_select.setStore(this.selection_object_store);
            },
            
            // The constructor
            constructor: function(args) {
                this.selection_store = new Memory({data: []});
                this.selection_object_store = new ObjectStore({ objectStore: this.selection_store });
                
                dojo.safeMixin(this, args);
                
            },
        });
});
