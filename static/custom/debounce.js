// custom.debounce

// Used to debounce a given function preventing it from being called to frequently

define([], function() {
    var debounce = function(func, threshold) {
        var timeout;

        return function debounced() {
            var obj = this, args = arguments;
            function delayed() {
                func.apply(obj, args);
                timeout = null;
            }
            if (timeout) {
                window.clearTimeout(timeout);
            }
            timeout = window.setTimeout(delayed, threshold);
        };
    };
    return debounce;
});
