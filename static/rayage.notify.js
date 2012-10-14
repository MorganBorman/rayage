// This is where we hook up the correct dojo topics to the pnotify messages.

require(["dojo/topic"],
function(topic){
    $(function(){
	    $.pnotify({
		    pnotify_title: 'Sticky Notice',
		    pnotify_text: 'I\'m a sticky notice.',
		    pnotify_hide: false
	    });
    });
});
