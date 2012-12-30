// custom.ConfirmDeleteDialog
define(["dojo/_base/declare","dijit/_Widget", "dojo/Evented", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/ConfirmDeleteDialog.html",
        "dojo/on", 
        "dijit/Dialog", "dijit/form/Button"],
    function(declare, Widget, Evented, TemplatedMixin, WidgetsInTemplateMixin, template, 
             on) {
        return declare([Widget, Evented, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            // Parse the template on loading
            parseOnLoad: true,
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                on(this.confirm_button, "click", function() {
                   self.emit("confirm", {});
                   self.dialog.hide();
                });
                
                on(this.cancel_button, "click", function() {
                   self.emit("cancel", {});
                   self.dialog.hide();
                });
            },
            
            startup: function() {
                this.resize();
            },
            
            display: function(user_count) {
                if (user_count == 1) {
                    this.message.innerHTML = "Are you sure you wish to delete the selected user?";
                }
                else if (user_count > 1) {
                    this.message.innerHTML = "Are you sure you wish to delete the " + user_count + " selected users?";
                }
                this.dialog.show();
            },
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
            }
        });
});
