// custom.Rayage
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/Rayage.html",
        "dijit/layout/BorderContainer", "custom/RayageMenu", "dijit/layout/TabContainer", "dijit/layout/ContentPane", "custom/BasicTerminal",
        "custom/RayageNewProjectDialog", "custom/RayageOpenProjectDialog", "custom/RayageNewFileDialog"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.border_container.startup();
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
