// custom.LogViewer
define(["dojo/_base/declare", "dijit/_WidgetBase", "dijit/_TemplatedMixin", "dijit/_WidgetsInTemplateMixin", "dojo/text!./templates/LogViewer.html", "dojo/dom-style", 
        "dojo/_base/fx", "dojo/_base/lang", "dojox/timing", "dojo/on", "dgrid/OnDemandGrid", "dgrid/Keyboard", "dgrid/Selection", 
        "dijit/layout/BorderContainer", "dijit/layout/ContentPane", 'custom/ObservableRayageJsonStore', "custom/RayageJsonStore", "dojo/on", 
        "dojox/form/DropDownSelect", "dojo/json"],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, OnDemandGrid, Keyboard, Selection, BorderContainer, ContentPane, ObservableRayageJsonStore, RayageJsonStore, on, DropDownSelect, JSON) {
        return declare([ContentPane, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            // Turn on parsing of subwidgets
            widgetsInTemplate: true,
            
            parseOnLoad: true,
            
            ws: null,
 
            // A class to be applied to the root node in our template
            baseClass: "log_viewer",
            
            // Stuff to do after the widget is created
            postCreate: function(){
            },
            
            startup: function() {
                this.border_container.startup();
                this.resize();
                
                this.setupGrid();
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.logEntryObjectStore = new RayageJsonStore({target:"/LogEntries", ws:this.ws});
                this.observableLogEntryStore = ObservableRayageJsonStore(this.logEntryObjectStore, this.ws);
                
                function formatLevel(object) {
                    var datum = object.level;
                    
                    switch(datum) {
                        case '0':
                        case 0:
                            return "Not Set";
                            break;
                        case '10':
                        case 10:
                            return "Debug";
                            break;
                        case '20':
                        case 20:
                            return "Info";
                            break;
                        case '30':
                        case 30:
                            return "Warning";
                            break;
                        case '40':
                        case 40:
                            return "Error";
                            break;
                        case '50':
                        case 50:
                            return "Critical";
                            break;
                        default:
                            return datum;
                            break;
                    }
                }
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.logGrid = new declare([OnDemandGrid, Keyboard, Selection])({
                    columns: {
                        timestamp: { label: "Date" },
                        level: { label: "Level", get: formatLevel },
                        logger: { label: "Type" },
                        message: { label: "Message" },
                        traceback: { label: "Traceback" }
                    },
                    selectionMode: "single",
                    cellNavigation: false,
                    pagingDelay: 500,
                    store: this.observableLogEntryStore
                }, this.logGridNode);
                
                this.logGrid.startup();
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
