// Filename: router.js
define(
    ['jquery', 'underscore', 'backbone', 'app' ],
    function ($, _, Backbone, app) {
        "use strict";
        var AppRouter = Backbone.Router.extend({
            routes: {
                // Dashboard
                ''              : 'showDashboard',
                'dashboard'     : 'showDashboard',

                // Nodes
                'nodes'         : 'showNodes',
                'nodes?:query'  : 'showNodes',
                'nodes/:id'     : 'showNode',

                // Patches
                'patches'       : 'showPatches',
                'patches?:query': 'showPatches',
                'patches/:id'   : 'showPatch',

                'tags'          : 'showTags',
                'tags?:query'   : 'showTags',
                'tags/:id'      : 'showTag',

                // MultiPatch Interface
                'multi'         : 'showMulti',

                // Schedule Interface
                'schedule'      : 'showSchedule',

                // Log Interface
                'logs'          : 'showLogs',
                'logs?:query'   : 'showLogs',

                // Account panel
                'account'       : 'showAccount',

                // Administration Panels
                // Notice, update modals/admin/main.js if adding new admin/route
                // Warning, update modals/panel.js open method if changing 'admin'
                // Warning, update route method if changing 'admin'
                'admin/managetags': 'modal/admin/managetags',
                'admin/nodes'     : 'modal/admin/nodes',
                'admin/timeblock' : 'modal/admin/timeblock',
                'admin/listblocks': 'modal/admin/listblocks',
                'admin/syslog'    : 'modal/admin/syslog',
                'admin/vmware'    : 'modal/admin/vmware',
                'admin/groups'    : 'modal/admin/groups',
                'admin/users'     : 'modal/admin/users'

                // Default
                // '*other'        : 'defaultAction'
            },
            navigate: function (fragment, options) {
                this.updateFragments();
                this.constructor.__super__.navigate.call(this, fragment, options);
            },
            initialize: function () {
                var that = this,
                    modals = app.views.modals,
                    adminPattern = /^admin$|\/\w/,
                    adminRoute = false,
                    hashPattern = /[\w\d_\-]+[\?\/]{0,}/,
                    hash;

                // Create a new ViewManager with #dashboard-view as its target element
                // All views sent to the ViewManager will render in the target element
                this.viewTarget = '#dashboard-view';
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});
                this.currentFragment = '';
                this.lastFragment = '';

                this.on("route", function () {
                    // Track current and previous routes
                    that.updateFragments();

                    adminRoute = adminPattern.test(that.currentFragment);

                    if (!adminRoute) {
                        // close any open modals
                        if (modals.admin instanceof Backbone.View && modals.admin.isOpen()) {
                            modals.admin.close();
                        }

                        hash = hashPattern.exec(that.currentFragment) || '';

                        app.vent.trigger('navigation:' + that.viewTarget, '#' + hash);
                    }
                });
            },
            showDashboard: function () {
                this.show({hash: '#dashboard', title: 'Dashboard', view: 'modules/mainDash'});
            },
            showNodes: function (query) {
                var that = this;
                require(['modules/nodes'], function (myView) {
                    if ($.type(query) === 'string') {
                        var params = app.parseQuery(query);
                        myView.Collection = myView.Collection.extend({
                            getCount: params.count,
                            offset: params.offset,
                            by_os: params.by_os,
                            filterby: params.filterby
                        });
                    }
                    that.show({hash: '#nodes', title: 'Nodes', view: new myView.View()});
                });
            },
            showNode: function (id) {
                var that = this;
                require(['modules/node'], function (myView) {
                    myView.Collection = myView.Collection.extend({id: id});
                    myView.VmCollection = myView.VmCollection.extend({id: id});
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
                            status: params.status,
                            getCount: params.count,
                            offset: params.offset,
                            searchQuery: params.query,
                            severity: params.severity,
                            searchBy: params.searchby
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
            showTags: function (query) {
                var that = this,
                    params = '',
                    collection,
                    view;

                require(['modules/tags'], function (myView) {
                    if ($.type(query) === 'string') {
                        params = app.parseQuery(query);
                    }

                    collection = new myView.Collection({
                        params: params
                    });

                    view = new myView.View({collection: collection});

                    that.show({hash: '#tags', title: 'Tags', view: view});
                });
            },
            showTag: function (id) {
                var that = this;
                require(['modules/tag'], function (myView) {
                    myView.Collection = myView.Collection.extend({id: id});
                    that.show({hash: '#tags', title: 'Tag Detail', view: new myView.View()});
                });
            },
            showMulti: function () {
                this.show({hash: '#multi', title: 'Patch Operations', view: 'modules/multi'});
            },
            showSchedule: function () {
                this.show({hash: '#schedule', title: 'Schedule Manager', view: 'modules/schedule'});
            },
            showLogs: function (query) {
                var that = this,
                    params = '',
                    collection,
                    view;

                require(['modules/logs'], function (myView) {
                    if ($.type(query) === 'string') {
                        params = app.parseQuery(query);
                    }

                    collection = new myView.Collection({
                        params: params
                    });

                    view = new myView.View({collection: collection});

                    that.show({hash: '#logs', title: 'Transaction Log', view: view});
                });
            },
            showAccount: function () {
                this.show({hash: '#admin', title: 'Admin Settings', view: 'modules/admin'});
            },
            'modal/admin/managetags': function () {
                this.openAdminModalWithView('modals/admin/managetags');
            },
            'modal/admin/nodes': function () {
                this.openAdminModalWithView('modals/admin/nodes');
            },
            'modal/admin/timeblock': function () {
                this.openAdminModalWithView('modals/admin/timeblock');
            },
            'modal/admin/listblocks': function () {
                this.openAdminModalWithView('modals/admin/listblocks');
            },
            'modal/admin/syslog': function () {
                this.openAdminModalWithView('modals/admin/syslog');
            },
            'modal/admin/vmware': function () {
                this.openAdminModalWithView('modals/admin/vmware');
            },
            'modal/admin/groups': function () {
                this.openAdminModalWithView('modals/admin/groups');
            },
            'modal/admin/users': function () {
                this.openAdminModalWithView('modals/admin/users');
            },
            /*
            defaultAction: function () {
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

                //app.vent.trigger('navigation:' + this.viewTarget, settings.hash);
                //app.vent.trigger('domchange:title', settings.title);

                if ($.type(settings.view) === 'string') {
                    require([settings.view], function (myView) {
                        var view = new myView.View();
                        that.viewManager.showView(view);
                    });
                } else if (settings.view instanceof Backbone.View) {
                    that.viewManager.showView(settings.view);
                }

                return this;
            },

            openAdminModalWithView: function (view) {
                var that = this,
                    modal,
                    adminView;

                // Check for proper admin permissions
                if (app.user.hasPermission('admin')) {
                    modal = app.views.modals.admin;

                    require(
                        ['modals/panel', 'modals/admin/main', view],
                        function (panel, admin, content) {
                            if (!modal || !modal instanceof panel.View || !modal.isOpen()) {
                                app.views.modals.admin = modal = new panel.View({
                                    span: 'span9'
                                });
                            }

                            // Get/Set content view of the modal panel
                            adminView = modal.getContentView();
                            if (!adminView || !adminView instanceof admin.View) {
                                adminView = new admin.View();
                                modal.openWithView(adminView);
                            }

                            // Set content view of the admin view
                            adminView.setContentView(new content.View());
                        }
                    );
                } else {
                    that.navigate("dashboard");
                }
            },

            // Getters/Setters
            updateFragments: function () {
                var newFragment = Backbone.history.getFragment();
                if (this.currentFragment !== newFragment) {
                    this.lastFragment = this.currentFragment;
                    this.currentFragment = newFragment;
                }
            },
            getCurrentFragment: function () { return this.currentFragment; },
            getLastFragment: function () { return this.lastFragment; }
        });
        return {
            initialize: function () {
                app.router = new AppRouter();
                app.startWs();
                Backbone.history.start();
            }
        };
    }
);
