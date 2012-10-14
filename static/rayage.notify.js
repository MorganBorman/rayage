// This is where we hook up the correct dojo topics to the pnotify messages.

$.pnotify.defaults.styling = "jqueryui";
$.pnotify.defaults.history = false;

require(["dojo/topic"],
function(topic){
    topic.subscribe("console/log", function(message) {
        $(function(){
	        $.pnotify({
	            pnotify_type: "info",
		        pnotify_title: 'console.log',
		        pnotify_text: message.message,
		        pnotify_delay: message.duration,
		        pnotify_width: "500px"
	        });
        });
    });
});
