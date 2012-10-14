// This is where we hook up the correct dojo topics to the pnotify messages.

$.pnotify.defaults.styling = "jqueryui";
$.pnotify.defaults.history = false;
$.pnotify.defaults.width = "500px";

require(["dojo/topic"],
function(topic){
    topic.subscribe("console/log", function(message) {
        $(function(){
	        $.pnotify({
	            type: "info",
		        title: 'console.log',
		        text: message.message,
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("notify/error", function(message) {
        $(function(){
	        $.pnotify({
	            type: "error",
		        text: message.message,
		        delay: message.duration
	        });
        });
    });
    
    topic.subscribe("ws/message/notification", function(message) {
        $(function(){
	        $.pnotify({
	            pnotify_type: message.severity,
		        pnotify_text: message.message,
		        pnotify_delay: message.duration
	        });
        });
    });
});
