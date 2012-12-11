// custom.RayageMenu
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/RayageMenu.html",
        "dojo/on", "dojo/topic", "dijit/registry", "dojo/dom-attr", "dojo/_base/lang", "dojo/_base/array", 
        "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/DropDownMenu", "dijit/MenuItem", "dijit/MenuSeparator", "dijit/MenuBarItem"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template,
             on, topic, registry, domAttr, lang, array) {
        return declare([WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "rayage_menu",
            
            functionalityGroups: {},
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.menu_bar.startup();
                
                // Hook up topic publishing for any which have a topic attribute
                var topic_hookup = function(widget) {
                    if (typeof widget.topic != "undefined") {
                        on(widget, "click", function() {
                            topic.publish(widget.topic);
                        });
                    }
                }
                
                var self = this;
                var assign_to_functionality_groups = function(widget) {
                    if (widget.hasOwnProperty("functionality-groups")) {
                        var fngroups = widget["functionality-groups"].split(',');
                        fngroups.push("all");
                        
                        // Loop through the functionality groups for this widget
                        for(var i = 0; i < fngroups.length; i++) {
                            var fngroup = lang.trim(fngroups[i]);
                        
                            // Add the functionality group if it doesn't exist
                            if(!self.functionalityGroups.hasOwnProperty(fngroup)) {
                                self.functionalityGroups[fngroup] = [];
                            }
                            
                            // Add this widget to the functionality group
                            self.functionalityGroups[fngroup].push(widget);
                        }
                    }
                }
                
                this.applyRecursively([topic_hookup, assign_to_functionality_groups]);
                
                // Example of setting the menus to a particular state.
                //this.setFunctionalityGroups(["all"], "disabled", true);
                //this.setFunctionalityGroups(["user"], "disabled", false);
                //this.setFunctionalityGroups(["project"], "disabled", true);
                //this.setFunctionalityGroups(["file"], "disabled", true);
            },
            
            // Recursively searches the menu structure and applies each function in functions on each node.
            applyRecursively: function(functions) {
                var recursive_apply;
                recursive_apply = function(widget) {
                    for(var i = 0; i < functions.length; i++) {
                        functions[i](widget)
                    }
                    
                    if (typeof widget.popup != "undefined") {
                        var popupchildren = widget.popup.getChildren();
                        for(var i = 0; i < popupchildren.length; i++) {
                            recursive_apply(popupchildren[i]);
                        }
                    }
                
                    var subwidgets = registry.findWidgets(widget.domNode);
                    for(var i = 0; i < subwidgets.length; i++) {
                        recursive_apply(subwidgets[i]);
                    }
                }
                
                recursive_apply(this.menu_bar);
            },
            
            // Set a property on all widgets which have any of the specified functionalityGroups
            setFunctionalityGroups: function(groups, attribute, value) {
                // Build a list of the widgets of which we will set the property
                var target_widgets = [];
                for(var i = 0; i < groups.length; i++) {
                    var group = groups[i];
                    
                    if (this.functionalityGroups.hasOwnProperty(group)) {
                        var widget_list = this.functionalityGroups[group];
                        
                        for(var w = 0; w < widget_list.length; w++) {
                            // Ensure each widget only appears once
                            if (array.indexOf(target_widgets, widget_list[w]) < 0) {
                                target_widgets.push(widget_list[w]);
                            }
                        }
                    }
                }
                
                // Actually set the property
                for(var i = 0; i < target_widgets.length; i++) {
                    target_widgets[i].set(attribute, value);
                }
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
