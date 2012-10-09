// Hook up all the subscribers which provide ways to manipulate the websocket here

// Hook up all the publishers which convey information from the websocket to the rest of the application here

require(["dojo/topic"],
function(topic){
    /*
    // published topics
    ws/connection/opened
    ws/connection/closed
    ws/connection/error
    ws/message/<type>
    ws/ready
    
    // subscribed topics
    ws/connect
    ws/disconnect
    ws/send
    */
    
    var ws = null;
    
    topic.subscribe("ws/connect", function(){
    
        ws = new WebSocket("wss://localhost:8080/ws");
    
        ws.onopen = function() {
            topic.publish("ws/connection/opened");
        };
        
        ws.onclose = function() {
            topic.publish("ws/connection/closed");
        };
        
        ws.onerror = function() {
            topic.publish("ws/connection/error");
        };
        
        ws.onmessage = function (event) {
            var msgdata = JSON.parse(event.data);
            var msgtype = msgdata.type
            
            topic.publish("ws/message/" + msgtype, msgdata);
        };
    });
    
    topic.subscribe("ws/disconnect", function(){
        ws.close();
        ws = null;
    });
    
    topic.subscribe("ws/send", function(msgdata){
        if (ws != null) {
            ws.send(JSON.stringify(msgdata));
        } else {
            console.log("Attempted to send data without websocket connection.");
        }
    });
    
    topic.publish("ws/ready");
});
