// This file will contain publishers and subscriber to topics for all direct manipulation of the UI (that is the public interface to the UI)

require(["dojo/parser", "dojo/ready", "dojo/topic"],
function(parser, ready, topic){
    ready(function(){
        parser.parse();
        
        // Hook up all the subscribers which provide ways to manipulate the UI here
        
        // Hook up all the publishers which convey information from the UI to the rest of the application here
        
        // Potential topic organization
        /*
        ui/menus/project/create_project
        ui/menus/project/open_project
        ui/menus/project/create_file
        
        ui/menus/edit/copy
        ui/menus/edit/cut
        ui/menus/edit/paste
        ui/menus/edit/select_all
        ui/menus/edit/find
        
        ui/menus/login
        ui/menus/logout
        
        ui/dialogs/open_project/accept
        ui/dialogs/open_project/show
        ui/dialogs/open_project/hide
        
        ui/ready
        
        */
    });
});
