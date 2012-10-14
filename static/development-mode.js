/*
 Overwrite the default console.log(), instead displaying
 the output to the console.
 */
var old_log = console.log;

console.log = function() {
    var console_log_arguments = arguments;          
    $(function(){
        $.pnotify({
            type: "info",
	        title: 'console.log',
	        text: [].slice.apply(console_log_arguments).join(" "),
	        icon: 'rayage_icon rayage_icon_console',
	        delay: 2000
        });
    });
                   
    old_log.apply(this,arguments);
};
