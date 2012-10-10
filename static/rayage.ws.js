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
    */
    
    var rayage_ws = new Object();
    
    rayage_ws.connect = function (){
        rayage_ws.ws = new WebSocket("wss://localhost:8080/ws");
    
        rayage_ws.ws.onopen = function() {
            topic.publish("ws/connection/opened");
        };
        
        rayage_ws.ws.onclose = function() {
            topic.publish("ws/connection/closed");
        };
        
        rayage_ws.ws.onerror = function() {
            topic.publish("ws/connection/error");
        };
        
        rayage_ws.ws.onmessage = function (event) {
            var msgdata = JSON.parse(event.data);
            var msgtype = msgdata.type
            console.log("recieved:", msgtype, " -> ", msgdata);
            topic.publish("ws/message/" + msgtype, msgdata);
        };
    };
   
    rayage_ws.disconnect = function (){
        if (rayage_ws.ws != null) {
            rayage_ws.ws.close();
            rayage_ws.ws = null;
        }
    };
    
    rayage_ws.send = function (msgdata){
        if (rayage_ws.ws != null) {
            var msgstrdata = JSON.stringify(msgdata);
            console.log("sending: ", msgstrdata);
            rayage_ws.ws.send(msgstrdata);
        }
    };
    
    topic.publish("ws/ready", rayage_ws);
});
