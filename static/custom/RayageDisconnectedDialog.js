// custom.RayageDisconnectedDialog
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageDisconnectedDialog.html",
        "dojo/on", "dojo/topic", 
        "dijit/Dialog", "dijit/form/Button"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on, topic) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_disconnected_dialog",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                // Based on blog post at 
                // http://blog.ecafechat.com/disable-x-in-dojo-dialog/
                this.dialog.closeButtonNode.style.display = "none";
                this.dialog._onKey = function(evt){
                    key = evt.keyCode;            
                    if (key == dojo.keys.ESCAPE) {
                        dojo.stopEvent(evt);
                    }
                };
                
                on(this.reconnect_button, "click", function() {
                    topic.publish("ui/dialogs/disconnected/reconnect");
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
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
                
            }
        });
});
