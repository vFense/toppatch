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
                'patches/:id': 'showPatch',
                'patches?:type': 'showOverview',
                'nodes': 'showNodes',
                'nodes?:query': 'showNodes',
                'nodes/:id': 'showNode',

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
            showPatch: function (id) {
                var that = this;
                require(['modules/patch'], function (myView) {
                    var view = new (myView.View.extend({id: id}))()
                    that.show({hash: '#patches', title: 'Patch Info Page', view: view});
                });
            },
            showOverview: function (query) {
                var that = this;
                require(['modules/patchOverview'], function (myView) {
                    if ($.type(query) === 'string') {
                        var params = app.parseQuery(query);
                        myView.Collection = myView.Collection.extend({type: params.type});
                        var view = new myView.View();
                        that.show({hash: '#patches', title: 'Patch Info Page', view: view});
                    } else {
                        this.defaultAction();
                    }
                })
            },
            showNodes: function (query) {
                var that = this;
                require(['modules/nodes'], function (myView) {
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
            showNode: function (id) {
                var that = this;
                require(['modules/node'], function (myView) {
                    myView.Collection = myView.Collection.extend({id: id});
                    var view = new myView.View();
                    that.show({hash: '#nodes', title: 'Nodes', view: view});
                });
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