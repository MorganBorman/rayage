// custom.TemplateManager
define(["dojo/_base/declare",
        "dijit/_WidgetBase", 
        "dijit/_TemplatedMixin", 
        "dijit/_WidgetsInTemplateMixin", 
        "dojo/text!./templates/TemplateManager.html", 
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
        "custom/RayageJsonStore",
        'dojox/grid/EnhancedGrid', 
        "dojox/grid/enhanced/plugins/Filter", 
        'dojo/data/ObjectStore',
        'custom/ObservableRayageJsonStore',
        'dojo/data/ItemFileWriteStore'],
    function(declare, WidgetBase, TemplatedMixin, WidgetsInTemplateMixin, template, domStyle, baseFx, lang, timing, on, BorderContainer, ContentPane, AccordionContainer, Uploader, IFrame, Button, FileList, RayageJsonStore, EnhancedGrid, Filter, ObjectStore, ObservableRayageJsonStore, ItemFileWriteStore) {
        return declare([ContentPane, TemplatedMixin, WidgetsInTemplateMixin], {
            // Our template - important!
            templateString: template,
            
            widgetsInTemplate: true,
            
            parseOnLoad: true,
 
            // A class to be applied to the root node in our template
            baseClass: "template_manager",
            
            // Stuff to do after the widget is created
            postCreate: function(){
                var self = this;
                
                this.setupGrid();

                var uploader = new dojox.form.Uploader({
                    label: "Upload Template",
                    multiple: true,
                    uploadOnSelect: true,
                    url: "/upload/template",
                }, this.uploader);

                var list = new dojox.form.uploader.FileList({uploader:uploader, rowAmt: 0});
                this.filelist.appendChild(list.domNode);
            },
            
            setupGrid: function() {
                /*set up data store*/
                this.templateObjectStore = new RayageJsonStore({target:"/Templates", ws:this.ws});
                this.observableTemplateStore = ObservableRayageJsonStore(this.templateObjectStore, this.ws);
                this.templateDataStore = new ObjectStore({objectStore: this.observableTemplateStore});
                
                /*set up layout*/
                var layout = [[
                  {'name': 'Id', 'field': 'id', 'width': '175px'},
                  {'name': 'Name', 'field': 'name', 'width': '175px'}
                ]];
                
                /*initialize the declaritive grid with the programmatic parameters*/
                this.templateGrid.set("structure", layout);
                this.templateGrid.set("selectionMode", "single");
                this.templateGrid.startup();
                this.templateGrid.setStore(this.templateDataStore);
                this.templateGrid.showFilterBar(true);
                //this.templateGrid.plugins.filter.setupFilterQuery = setupFilter;
                this.templateGrid.selection.select(0);
                
                var self = this;
                
                on(this.templateGrid, "rowClick", function(e) {
                    var templateRow = self.templateGrid.getItem(e.rowIndex);
                    console.log(templateRow);
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
