require(["dojo/topic"],
function(topic){
    topic.subscribe("ui/ready", function(){
        
        // Hook up all the subscribers which provide ways to manipulate the websocket here
        
        // Hook up all the publishers which convey information from the websocket to the rest of the application here
        
        // Potential topic organization
        /*
        ws/connection/opened
        ws/connection/closed
        ws/connection/error
        ws/message/<type>
        ws/send
        
        ws/ready
        */
    });
    
    
    topic.subscribe("app/ready", function(){
        
        //when the application reports it is ready then we try to connect to the websocket
        var ws = new WebSocket("wss://localhost:8080/ws");
        
        ws.onopen = function() {
            topic.publish("ws/connection/opened");
        };
        
        ws.onclose = function() {
            topic.publish("ws/connection/closed");
        };
        
        ws.onmessage = function (event) {
            var msgdata = JSON.parse(event.data);
            var msgtype = msgdata.type
            
            topic.publish("ws/message/" + msgtype, msgdata);
        };
        
        ws.onerror = function() {
            topic.publish("ws/connection/error");
        };
        
        topic.subscribe("ws/send", function(msgdata){
            ws.send(JSON.stringify(msgdata));
        });
        
        topic.publish("ws/ready");
    });
});
