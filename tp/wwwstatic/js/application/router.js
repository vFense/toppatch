// Filename: router.js
define(
    ['jquery', 'underscore', 'backbone', 'app' ],
    function ($, _, Backbone, app) {
        "use strict";
        var AppRouter = Backbone.Router.extend({
            routes: {
                // Dashboard
                ''              : 'home',
                'dashboard'     : 'home',

                // Nodes
                'nodes'         : 'showNodes',
                'nodes?:query'  : 'showNodes',
                'nodes/:id'     : 'showNode',

                // Patches
                'patches'       : 'showPatches',
                'patches?:query': 'showPatches',
                'patches/:id'   : 'showPatch',

                // MultiPatch Interface
                'multi'         : 'showMulti',

                // Admin panel
                'admin'         : 'showAdmin',

                // Administration Panels
                // Warning, update modals/panel.js open method when changing 'testAdmin'
                'testAdmin'     : 'modal/admin',
                'testAdmin/nodes': 'modal/admin/nodes'

                // Default
                // '*other'        : 'defaultAction'
            },
            route: function (route, name, callback) {
                var modals = app.views.modals;

                // Override the route method
                this.constructor.__super__.route.call(this, route, name, function () {
                    // before route event
                    this.trigger.apply(this, ["beforeRoute"].concat(route, name));

                    // Track current and previous routes
                    this.lastFragment = this.currentFragment;
                    this.currentFragment = Backbone.history.getFragment();

                    // close any open modals
                    // Do not close admin panel if next route uses admin panel
                    if (this.currentFragment.indexOf('testAdmin') !== 0) {
                        if (modals.admin instanceof Backbone.View && modals.admin.isOpen()) {
                            modals.admin.close();
                        }
                    }

                    // run callback
                    callback.apply(this, arguments);

                    // after route event
                    this.trigger.apply(this, ["afterRoute"].concat(route, name));
                });
            },
            initialize: function () {
                // Create a new ViewManager with #dashboard-view as its target element
                // All views sent to the ViewManager will render in the target element
                this.viewTarget = '#dashboard-view';
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});
                this.currentFragment = '';
                this.lastFragment = '';
            },
            home: function () {
                this.show({hash: '#dashboard', title: 'Dashboard', view: 'modules/mainDash'});
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
            showPatches: function (query) {
                var that = this;
                require(['modules/patches'], function (myView) {
                    if ($.type(query) === 'string') {
                        var params = app.parseQuery(query);
                        myView.Collection = myView.Collection.extend({
                            type: params.type,
                            getCount: params.count,
                            offset: params.offset
                        });
                    }
                    that.show({hash: '#patches', title: 'Patches', view: new myView.View()});
                });
            },
            showPatch: function (id) {
                var that = this;
                require(['modules/patch'], function (myView) {
                    myView.Collection = myView.Collection.extend({id: id});
                    that.show({hash: '#patches', title: 'Patch Detail', view: new myView.View()});
                });
            },
            showMulti: function () {
                this.show({hash: '#multi', title: 'Patch Operations', view: 'modules/multi'});
            },
            showAdmin: function () {
                this.show({hash: '#admin', title: 'Admin Settings', view: 'modules/admin'});
            },
            'modal/admin': function () {
                this.openAdminModalWithView('modals/admin/general');
            },
            'modal/admin/nodes': function () {
                this.openAdminModalWithView('modals/admin/nodes');
            },
            /*
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
            */

            // Helper functions
            show: function (options) {
                var that = this,
                    settings = $.extend({
                        hash: null,
                        title: '',
                        view: null
                    }, options);

                app.vent.trigger('navigation:' + this.viewTarget, settings.hash);
                app.vent.trigger('domchange:title', settings.title);
                var schedule = $(document).find('input[name="schedule"]:checked');
                if(schedule.data('popover')) {
                    schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                    schedule.popover('destroy');
                }

                if ($.type(settings.view) === 'string') {
                    require([settings.view], function (myView) {
                        var view = new myView.View();
                        that.viewManager.showView(view);
                    });
                } else if (settings.view instanceof Backbone.View) {
                    that.viewManager.showView(settings.view);
                }
            },

            openAdminModalWithView: function (view) {
                var that = this;

                // Check for proper admin permissions
                if (app.user.hasPermission('admin')) {
                    var modal = app.views.modals.admin,
                        adminView;

                    require(
                        ['modals/panel', 'modals/admin/main', view],
                        function (panel, admin, content) {
                            if (!modal || !modal instanceof panel.View) {
                                app.views.modals.admin = modal = new panel.View({});
                            }

                            // Get/Set content view of the modal panel
                            adminView = modal.getContentView();
                            if (!adminView || !adminView instanceof admin.View) {
                                adminView = new admin.View();
                                modal.setContentView(adminView);
                            }

                            // Set content view of the admin view
                            adminView.setContentView(new content.View());

                            // Open the modal panel
                            modal.open();
                        }
                    );
                } else {
                    that.navigate("dashboard");
                }
            },

            // Getters/Setters
            getCurrentFragment: function () {return this.currentFragment;},
            getLastFragment: function () {return this.lastFragment;}
        });
        return {
            initialize: function () {
                app.router = new AppRouter();
                Backbone.history.start();
            }
        };
    }
);
