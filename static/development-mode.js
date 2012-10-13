/*
 Overwrite the default console.log(), instead displaying
 the output to the console.
 */
var old_log = console.log;

console.log = function() {
    dojo.publish("console/log", 
                 [{
                    message: [].slice.apply(arguments).join(" "),
                    duration: 2000
                   }]);
    old_log.apply(this,arguments);
};