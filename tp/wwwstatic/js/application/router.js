// Filename: router.js
define(
    ['jquery', 'backbone', 'app' ],
    function ($, Backbone, app) {
        "use strict";
        var AppRouter = Backbone.Router.extend({
            routes: {
                // Dashboard
                '':           'home',
                'dashboard':  'home',

                // Patch Routes
                'patchAdmin': 'showPatchAdmin',

                // Testers
                'test': 'showTest',
                'testPatch': 'showPatchTest',

                // Default
                '*other':     'defaultAction'
            },
            initialize: function () {
                // Create a new ViewManager with #dashboard-view as its target element
                // All views sent to the ViewManager will render in the target element
                this.vent = app.vent;
                this.viewManager = new app.ViewManager({'selector': '#dashboard-view'});
            },
            home: function () {
                var that = this;
                this.vent.trigger('nav', '#dashboard');

                // Update the main dashboard view
                require(['modules/mainDash'], function (myView) {
                    var view = new myView.View();
                    that.viewManager.showView(view);
                });
            },
            showPatchAdmin: function () {
                var that = this;
                this.vent.trigger('nav', '#patchAdmin');

                // Update the main dashboard view
                require(['modules/patchAdmin'], function (myView) {
                    var view = new myView.View();
                    that.viewManager.showView(view);
                });
            },
            showTest: function () {
                var that = this;
                this.vent.trigger('nav', '#test');

                // Update the main dashboard view
                require(['modules/widget'], function (myView) {
                    var model = new myView.Model({}),
                        view = new myView.View({model: model});
                    that.viewManager.showView(view);
                });
            },
            showPatchTest: function () {
                var that = this;
                this.vent.trigger('nav', '#test');

                // Update the main dashboard view
                require(['utilities/newDataGen'], function (myView) {
                    var view = new myView.View();
                    that.viewManager.showView(view);
                });
            },
            defaultAction: function (other) {
                var that = this;
                this.vent.trigger('nav', '404');

                this.viewManager.showView({ el: '404: Not Found', render: function () { return true; }, close: function () {  return true; }});
            }
        });
        return {
            initialize: function () {
                this.app_router = new AppRouter();
                Backbone.history.start();
            }
        };
    }
);
