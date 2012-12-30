// custom.ConfirmDeleteDialog
define(["dojo/_base/declare","dijit/_Widget", "dojo/Evented", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/UserDialog.html",
        "dojo/on", "dojo/_base/lang", 
        "dijit/Dialog", "dijit/form/Button"],
    function(declare, Widget, Evented, TemplatedMixin, WidgetsInTemplateMixin, template,
             on, lang) {
        return declare([Widget, Evented, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            // Parse the template on loading
            parseOnLoad: true,
            
            // The id of the current user being edited
            _id: null,
            
            // Stuff to do after the widget is created
            postCreate: function(){
                on(this.save_button, "click", lang.hitch(this, function() {
                    var user = {id: this._id,
                                username: this.name_input.get('value'),
                                permissions: this.permission_input.get('value')};
                    this.emit("save", user);
                    this._id = null;
                    this.dialog.hide();
                }));
                
                on(this.cancel_button, "click", lang.hitch(this, function() {
                    this.emit("cancel", {});
                    this._id = null;
                    this.dialog.hide();
                }));
            },
            
            addUser: function(){
                this.dialog.set("title", "Add User");
                this._id = null;
                this.name_input.set("value", "");
                this.permission_input.set("value", 0);
                this.dialog.show();
            },
            
            editUser: function(user){
                this.dialog.set("title", "Edit User");
                this._id = user.id;
                this.name_input.set("value", user.username);
                this.permission_input.set("value", user.permissions);
                this.dialog.show();
            },
            
            startup: function() {
                this.resize();
            },
            
            // The constructor
            constructor: function(args) {
                dojo.safeMixin(this, args);
            }
        });
});
