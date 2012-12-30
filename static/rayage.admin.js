require(["dojo/parser", "dojo/_base/fx", "dojo/dom-style", "dojo/domReady!", "custom/RayageAdmin"],
function(parser, fx, style){
    parser.parse();
    
    var fadeArgs = {
        node: "preloader",
        duration: 1000,
        onEnd: function(node) {
            style.set(node, "display", "none");
        }
    };
    fx.fadeOut(fadeArgs).play();
});
