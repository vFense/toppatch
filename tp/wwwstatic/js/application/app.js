define(
    ['jquery', 'backbone', 'utilities/vent', 'utilities/viewManager'],
    function ($, Backbone, vent, ViewManager) {
        "use strict";

        var app = {
            root: '/'
        };

        _.extend(app, {
            vent: vent,
            ViewManager: ViewManager,
            views: {},
            chart: {}
        });

        return app;
    }
);
