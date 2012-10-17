define(
    ['underscore', 'backbone'],
    function (_, Backbone) {
        "use strict";
        var vent = _.extend({}, Backbone.Events);
        return vent;
    }
);