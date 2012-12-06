define(
    ['jquery', 'underscore', 'backbone'],
    function ($, _, Backbone) {
        "use strict";
        // Based on Coffeescript's class extension methods
        // Adjusted to jsLint compliance
        // Adjusted to require a single argument.
        return function (object) {
            var _sub = {};
            _sub['class'] = function () {
                return _sub['class'].__super__.constructor.apply(this, arguments);
            };
            return (function (_super) {
                (function (child, parent) {
                    var key;
                    for (key in parent) {
                        if (parent.hasOwnProperty(key)) {
                            child[key] = parent[key];
                        }
                    }
                    function Ctor() {
                        this.constructor = child;
                    }
                    Ctor.prototype = parent.prototype;
                    child.prototype = new Ctor();
                    child.__super__ = parent.prototype;
                    return child;
                }(_sub['class'], _super));

                return _sub['class'];
            }(object));
        };
    }
);
