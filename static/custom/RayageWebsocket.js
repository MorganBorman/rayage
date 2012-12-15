// custom.RayageWebsocket

/* published topics
ws/connection/opened
ws/connection/closed
ws/connection/error
ws/message/<type>
*/

define(["dojo/topic", "dojo/json"], 
function(topic, JSON){
    Singleton = {
        ws: null,
        url: "",
        connect: function() {
            this.ws = new WebSocket(this.url);
            this.ws.onopen = function() {
                topic.publish("ws/connection/opened");
            };
            this.ws.onclose = function() {
                topic.publish("ws/connection/closed");
            };
            this.ws.onerror = function() {
                topic.publish("ws/connection/error");
            };
            this.ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                console.log("recieved: ", data.type, " -> ", data, event);
                topic.publish("ws/message/" + data.type, data, event);
            };
        },
        disconnect: function() {
            if (this.ws != null) {
                this.ws.close();
                this.ws = null;
            }
        },
        send: function(message){
            if (this.ws != null) {
                var message_data = JSON.stringify(message);
                console.log("sending: ", message_data);
                this.ws.send(message_data);
            }
        },
    };
    return Singleton;
});
