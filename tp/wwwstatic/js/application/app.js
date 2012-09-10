define(
    ['jquery', 'backbone', 'modules/vent', 'modules/ViewManager'],
    function ($, Backbone, vent, ViewManager) {
        "use strict";

        var app = {
            root: '/'
        };

        _.extend(app, {
            vent: vent,
            ViewManager: ViewManager,
            views: {}
        });

        return app;
    }
);
