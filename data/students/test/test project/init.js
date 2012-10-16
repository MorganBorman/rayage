window.termbuffer = "55";
window.termbufferindex = 0;

window.Module = {
    noInitialRun: true,
    noFSInit: false,
    print: function(text) {
          window.term.echo(text);
    },
    printErr: function(text) {
          window.term.error(text);
    },
    stdin: function() {
        var chr = window.termbuffer.charCodeAt(window.termbufferindex) || null;
        window.termbufferindex = Math.min(window.termbufferindex+1, window.termbuffer.length);
        console.log(chr);
        return chr;
    },
};

jQuery(function($, undefined) {
    var termopts = {
        name: 'js_demo',
        height: 200,
        prompt: '',
        greetings: ''
    };

    window.term = $('#term_demo').terminal(function(command, term) {
        window.termbuffer += command;
    }, termopts);
    
    //window.FS.init();
    
    window.Module.run();
});
