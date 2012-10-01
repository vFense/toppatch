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

                // New Pages
                'nodes': 'showNodes',
                'nodes?:query': 'showNodes',

                // Testers
                'test': 'showTest',
                'testPatch': 'showPatchTest',

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
            showNodes: function (query) {
                var that = this;
                require(['modules/showNodes'], function (myView) {
                    if ($.type(query) === 'string') {
                        var params = app.parseQuery(query);
                        myView.Collection = myView.Collection.extend({
                            getCount: params.count,
                            offset: params.offset
                        });
                    }
                    that.show({hash: '#nodes', title: 'Nodes', view: new myView.View()});
                });
            },
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
                app.router = new AppRouter();
                Backbone.history.start();
            }
        };
    }
);
