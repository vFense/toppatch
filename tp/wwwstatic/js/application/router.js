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
                'patchAdmin': 'patchAdmin',

                // Testers
                'test': 'showTest',
                'testPatch': 'showPatchTest',
                'patches': 'showPatches',
                'patches/:id': 'showPatchesById',
                'patches-overview/:type': 'showOverview',

                // Default
                '*other':     'defaultAction'
            },
            initialize: function () {
                // Create a new ViewManager with #dashboard-view as its target element
                // All views sent to the ViewManager will render in the target element
                this.viewTarget = '#dashboard-view';
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});
            },
            home: function () {
                this.show({hash: '#dashboard', title: 'Dashboard', view: 'modules/mainDash'});
            },
            patchAdmin: function () {
                this.show({hash: '#patchAdmin', title: 'Patch Administration', view: 'modules/patchAdmin'});
            },
            showTest: function () {
                this.show({hash: '#test', title: 'Test Page', view: 'modules/widget'});
            },
            showPatchTest: function () {
                this.show({hash: '#testPatch', title: 'Patch Test Page', view: 'utilities/newDataGen'});
            },
            showPatches: function () {
                this.show({hash: '#patches', title: 'Patch Info Page', view: 'modules/patches'});
            },
            showPatchesById: function (id) {
                var that = this;
                require(['modules/indPatches'], function (myView) {
                    var view = new (myView.View.extend({id: id}))()
                    that.show({hash: '#patches', title: 'Patch Info Page', view: view});
                });
            },
            showOverview: function (type) {
                var that = this;
                require(['modules/patchOverview'], function (myView) {
                    var collection = new (myView.Collection.extend({type: type}))()
                    var view = new (myView.View.extend({collection: collection}))()
                    that.show({hash: '#patches', title: 'Patch Info Page', view: view});
                })
            },
            defaultAction: function (other) {
                this.show(
                    {
                        hash: '#404',
                        title: 'Page Not Found',
                        view: new (Backbone.View.extend({
                            render: function () {
                                this.$el.html('<h1>404: <small>Not Found</small></h1>');
                                return this;
                            }
                        }))()
                    }
                );
            },
            show: function (options) {
                var that = this,
                    settings = $.extend({
                        hash: null,
                        title: null,
                        view: null
                    }, options);

                app.vent.trigger('navigation:' + this.viewTarget, settings.hash);
                app.vent.trigger('domchange:title', settings.title);

                if ($.type(settings.view) === 'string') {
                    require([settings.view], function (myView) {
                        var view = new myView.View();
                        that.viewManager.showView(view);
                    });
                } else if (settings.view instanceof Backbone.View) {
                    that.viewManager.showView(settings.view);
                }
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