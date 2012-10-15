// This is where we hook up the correct dojo topics to the pnotify messages.

$.pnotify.defaults.styling = "jqueryui";
$.pnotify.defaults.history = false;
$.pnotify.defaults.width = "500px";

require(["dojo/topic"],
function(topic){
    topic.subscribe("notify/notice", function(message) {
        $(function(){
	        $.pnotify({
	            type: "notice",
		        text: message.message,
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("notify/info", function(message) {
        $(function(){
	        $.pnotify({
	            type: "info",
		        text: message.message,
		        icon: 'rayage_icon rayage_icon_notify_info',
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("notify/success", function(message) {
        $(function(){
	        $.pnotify({
	            type: "success",
		        text: message.message,
		        icon: 'rayage_icon rayage_icon_notify_info',
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("notify/error", function(message) {
        $(function(){
	        $.pnotify({
	            type: "error",
		        text: message.message,
		        icon: 'rayage_icon rayage_icon_notify_error',
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("ws/message/notification", function(message) {
        $(function(){
	        $.pnotify({
	            pnotify_type: message.severity,
		        pnotify_text: message.message,
		        icon: 'rayage_icon rayage_icon_notify_' + message.severity,
		        pnotify_delay: message.duration
	        });
        });
    });
    
    topic.subscribe("notify/disconnected", function(message) {
        $(function(){
	        $.pnotify({
	            type: "error",
		        text: "The connection to the server has been lost.\nTry reloading the page.",
		        icon: 'rayage_icon rayage_icon_socket_disconnected',
		        hide: false
	        });
        });
    });
});
