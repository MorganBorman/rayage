require(["dojo/parser", "dojo/on", "dojo/topic", "dijit/registry", "dojo/data/ObjectStore", "dojo/store/Memory", "dojo/store/Observable", "dijit/tree/ObjectStoreModel", 
         "dijit/Tree", "dijit/layout/ContentPane", "dojo/domReady!", "dijit/MenuBar", "dijit/PopupMenuBarItem", "dijit/MenuItem", "dijit/DropDownMenu", 
         "dijit/layout/BorderContainer", "dijit/layout/TabContainer", "dijit/Dialog", "dijit/form/Select", "dijit/TooltipDialog", "dijit/form/TextBox"],
function(parser, on, topic, registry, ObjectStore, Memory, Observable, ObjectStoreModel, Tree, ContentPane){
    parser.parse();
    
    rayage_ui = new Object();
    
    rayage_ui.nav_pane = registry.byId("ui_nav_pane");
    rayage_ui.tab_container = registry.byId("ui_admin_tab_container");
    
    var ui_admin_module_store = new Memory({
        data: [{ id: 'admin_modules', name:'Admin Modules', type:'folder'}],
        getChildren: function(object){
            return this.query({parent: object.id});
        }
    });
    
    var ui_admin_module_store_ob = new Observable(ui_admin_module_store);

    // Create the model
    var ui_admin_module_store_model = new ObjectStoreModel({
        store: ui_admin_module_store_ob,
        query: {id: 'admin_modules'}
    });
    
    var ui_admin_module_tree = new Tree({
        model: ui_admin_module_store_model,
        getIconClass: function(/*dojo.store.Item*/ item, /*Boolean*/ opened){
            return "rayage_icon rayage_icon_admin_" + item.iconClass;
        },
        onClick: function(item) {
            topic.publish("ui/nav_menu/click", item);
        },
    });
    ui_admin_module_tree.placeAt(rayage_ui.nav_pane);
    ui_admin_module_tree.startup();
    
    ui_admin_module_store_ob.setData = function(data) {
        dojo.forEach(data, function(item) {
		    ui_admin_module_store_ob.put(item, {overwrite: true});
	    });
	};
    
    rayage_ui.module_tree = {
        store: ui_admin_module_store_ob,
        model: ui_admin_module_store_model,
        tree: ui_admin_module_tree,
    };
    
    console.log(rayage_ui.module_tree.store);
    
    // Let the rest of the application know our UI is set up
    topic.publish("ui/ready", rayage_ui);
});
