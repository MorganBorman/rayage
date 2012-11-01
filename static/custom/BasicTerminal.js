// custom.BasicTerminal
define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dojo/text!./templates/BasicTerminal.html", "dojo/dom-style", "dojo/_base/fx", "dojo/_base/lang",
        "dojox/timing", "dojo/Evented", "dojo/on"],
    function(declare, WidgetBase, TemplatedMixin, template, domStyle, baseFx, lang, timing, Evented, on){
        return declare([WidgetBase, TemplatedMixin, Evented], {
            _cursor_timer: new dojox.timing.Timer(750),
            _cursor_inverted: false,
            
            _focused: false,
            
            focus_terminal: function() {
                this.clipboardNode.focus();
            },
            
            render_clipboard: function(clipboard_value) {
                var output = "";
                
                for (var i=0; i<clipboard_value.length; i++) {
                    switch(clipboard_value[i]) {
                        case ' ':
                          output += "&nbsp;";
                          break;
                        default:
                          output += clipboard_value[i];
                          break;
                    }
                }
                
                return output;
            },
            
            clipboard_onkeyup: function(evt) {
                //console.log(evt.keyCode, String.fromCharCode(evt.keyCode));
                //http://dojotoolkit.org/api/1.8/dojo/keys
                
                this.clipdataNode.innerHTML = this.render_clipboard(this.clipboardNode.value);
                
                switch(evt.keyCode) {
                    case dojo.keys.ENTER:
                      this.outputNode.innerHTML += this.clipdataNode.innerHTML + "<br>";
                      this.clipdataNode.innerHTML = "";
                      data = this.clipboardNode.value
                      this.clipboardNode.value = "";
                      this._onInputLine({'data': data});
                      break;
                    default:
                      break;
                }
                
            },
            
            _onInputLine: function( /*Event*/ e){
              this.emit('inputLine', e);
            },
            
            // Our template - important!
            templateString: template,
 
            // A class to be applied to the root node in our template
            baseClass: "terminal",
            
            postCreate: function(){
                var self = this;
                
                self.clipboardNode.onfocus =  function() {
                    self.cursorNode.className = "cursor inverted";
                    self._cursor_inverted = false;
                };
                
                self.clipboardNode.onblur =  function() {
                    self.cursorNode.className = "cursor boxed";
                    self._cursor_inverted = false;
                };
                
                this._cursor_timer.onTick = function(){
                    if(self.clipboardNode == document.activeElement) {
                        self.cursorNode.className = self._cursor_inverted ? "cursor" : "cursor inverted";
                        self._cursor_inverted = (!self._cursor_inverted);
                    }
                };
                
                this._cursor_timer.start();
            }
        });
});
