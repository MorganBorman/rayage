// custom.TestManager
define(["dojo/_base/declare",
        "dijit/_WidgetBase", 
        "dijit/_TemplatedMixin", 
        "dijit/_WidgetsInTemplateMixin", 
        "dojo/text!./templates/TestManager.html", 
        "dojo/dom-style", 
        "dojo/_base/fx", 
        "dojo/_base/lang", 
        "dojox/timing", 
        "dojo/on", 
        "dijit/layout/BorderContainer",
        "dijit/layout/ContentPane", 
        "dijit/layout/AccordionContainer", 
        "dojox/form/Uploader", 
        "dojox/form/uploader/plugins/IFrame", 
        "dijit/form/Button",
        "dojox/form/uploader/FileList",
        "custom/WebsocketJsonStore",
        'dojox/grid/EnhancedGrid', 
        "dojox/grid/enhanced/plugins/Filter", 
        'dojo/data/ObjectStore',
        'custom/ObservableWebsocketJsonStore',
        'dojo/data/ItemFileWriteStore'],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, BorderContainer, ContentPane, AccordionContainer, Uploader, IFrame, Button, FileList, RayageJsonStore, EnhancedGrid, Filter, ObjectStore, ObservableRayageJsonStore, ItemFileWriteStore) {
        return declare([ContentPane, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "test_manager",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                this.setupGrid();

                var uploader = new dojox.form.Uploader({
                    label: "Upload Test",
                    multiple: true,
                    uploadOnSelect: true,
                    url: "/upload/test",
                }, this.uploader);

                var list = new dojox.form.uploader.FileList({uploader:uploader, rowAmt: 0});
                this.filelist.appendChild(list.domNode);
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.testObjectStore = new RayageJsonStore({target:"/Tests", ws:this.ws});
                this.observableTestStore = ObservableRayageJsonStore(this.testObjectStore, this.ws);
                this.testDataStore = new ObjectStore({objectStore: this.observableTestStore});
                
                /*set up layout*/
                var layout = [[
                  {'name': 'Id', 'field': 'id', 'width': '175px'},
                  {'name': 'Name', 'field': 'label', 'width': '175px'}
                ]];
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.testGrid.set("structure", layout);
                this.testGrid.set("selectionMode", "single");
                this.testGrid.startup();
                this.testGrid.setStore(this.testDataStore);
                this.testGrid.showFilterBar(true);
                //this.testGrid.plugins.filter.setupFilterQuery = setupFilter;
                this.testGrid.selection.select(0);
                
                var self = this;
                
                on(this.testGrid, "rowClick", function(e) {
                    var testRow = self.testGrid.getItem(e.rowIndex);
                    console.log(testRow);
                });
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
