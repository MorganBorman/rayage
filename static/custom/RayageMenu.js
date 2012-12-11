// custom.RayageMenu
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageMenu.html",
        "dojo/on", "dojo/topic", "dijit/registry", "dojo/dom-attr", 
        "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/DropDownMenu", "dijit/MenuItem", "dijit/MenuSeparator", "dijit/MenuBarItem"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template,
             on, topic, registry, domAttr) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_menu",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.menu_bar.startup();
                
                var topic_hookup = function(widget) {
                    on(widget, "click", function() {
                        topic.publish(widget.topic);
                    });
                }
                
                // Recursively searches for all widgets which have a 'topic' attribute
                // and hooks up them to public on clicking.
                var recursive_topic_hookup;
                recursive_topic_hookup = function(widget) {
                    if (typeof widget.topic != "undefined") {
                        topic_hookup(widget);
                    }
                    
                    if (typeof widget.popup != "undefined") {
                        var popupchildren = widget.popup.getChildren();
                        for(var i = 0; i < popupchildren.length; i++) {
                            recursive_topic_hookup(popupchildren[i]);
                        }
                    }
                
                    var subwidgets = registry.findWidgets(widget.domNode);
                    for(var i = 0; i < subwidgets.length; i++) {
                        recursive_topic_hookup(subwidgets[i]);
                    }
                }
                
                recursive_topic_hookup(this.menu_bar);
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
