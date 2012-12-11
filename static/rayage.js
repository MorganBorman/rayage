require(["dojo/parser", "dojo/_base/fx", "dojo/dom-style", "dojo/domReady!", "custom/Rayage"],
function(parser, fx, style){
    parser.parse();
    
    var fadeArgs = {
        node: "preloader",
        duration: 1000
    };
    fx.fadeOut(fadeArgs).play();
    setTimeout(function() {
        style.set("preloader", "display", "none");
    }, 1000)
});
