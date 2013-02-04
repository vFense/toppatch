define(
    [
        'jquery',
        'underscore',
        'backbone',
        'utilities/vent',
        'utilities/viewManager',
        'utilities/propogate',
        'utilities/pinwheel',
        'd3charts/loadAll'
    ],
    function (
        $,
        _,
        Backbone,
        vent,
        ViewManager,
        propogate,
        pinwheel,
        charts
    ) {
        "use strict";

        var app = {},
            overviewInstalled = {'data': 0},
            overviewPending = {'data': 0},
            overviewAvailable = {'data': 0},
            overviewFailed = {'data': 0};

        $.ajax({
            url: '/api/networkData',
            dataType: 'json',
            async: false,
            success: function (json) {
                if (json.length !== 0) {
                    overviewInstalled = json[0];
                    overviewAvailable = json[1];
                    overviewPending = json[2];
                    overviewFailed = json[3];
                }
            }
        });

        // Vars and Functions
        _.extend(app, {
            root: '/',
            $doc: $(document),
            title: $(document).attr('title'),
            vent: vent,
            ViewManager: ViewManager,
            views: {
                modals: {
                    admin: undefined
                }
            },
            parseQuery: function (query) {
                var params = {};
                _.each(query.split('&'), function (value) {
                    var param = value.split('=');
                    params[param[0]] = param[1];
                });
                return params;
            },
            pinwheel: pinwheel.View,
            inherit: propogate.inherit,
            createChild: propogate.createChild
        });

        // WebSockets
        _.extend(app, {
            startWs: function () {
                var i, ws = new window.WebSocket("wss://" + window.location.host + "/ws");
                ws.onmessage = function (evt) {
                    window.console.log(['websocket', 'message', evt]);
                    $.get('/api/networkData', {}, function (json) {
                        if (json.length) {
                            _.each(json, function (status) {
                                if (status.key === 'installed') {
                                    $('.success').children('dd').children().html(status.data);
                                } else if (status.key === 'available') {
                                    $('.warning').children('dd').children().html(status.data);
                                } else if (status.key === 'pending') {
                                    $('.info').children('dd').children().html(status.data);
                                } else if (status.key === 'failed') {
                                    $('.error').children('dd').children().html(status.data);
                                }
                            });
                        }
                    });
                };
                ws.onclose = function (evt) {
                    window.console.log(['websocket', 'closed', evt]);
                };
                ws.onopen = function (evt) {
                    window.console.log(['websocket', 'opened', evt]);
                };
                ws.onerror = function (evt) {
                    window.console.log(['websocket', 'error', evt]);
                };
            },
            chart: {
                partition: charts.partition,
                pie: charts.pie,
                bar: charts.bar,
                stackedBar: charts.stackedBar,
                generateTable: charts.generateTable,
                line: charts.line,
                newpie: charts.newpie,
                bar_3d: charts.bar_3d,
                stackedArea: charts.stackedArea
            },
            getUserSettings: function () {
                var userSettings, userName,
                    User = {};
                $.ajax({
                    url: '/api/userInfo',
                    dataType: 'json',
                    async: false,
                    success: function (json) {
                        userSettings = json;
                        userName = userSettings.name;
                        if (localStorage.getItem(userName) === null) {
                            User.Model = Backbone.Model.extend({
                                defaults: {
                                    name: userName,
                                    show: {
                                        brandHeader: true,
                                        dashNav: true,
                                        copyFooter: true
                                    },
                                    widgets: {
                                        'graph': ['pie', 'bar', 'tag', 'area_2'],
                                        'spans': [4, 4, 4, 12],
                                        'titles': ['Nodes in Network by OS', 'Updates by Severity', 'Tags', 'Packages Available in Network']//'Packages Installed in Network',
                                    }
                                }
                            });
                            window.User = new User.Model();
                            localStorage.setItem(userName, JSON.stringify(window.User));
                        } else {
                            var test = JSON.parse(localStorage.getItem(userName));
                            User.Model = Backbone.Model.extend({
                                defaults: {
                                    name: test.name,
                                    show: test.show,
                                    widgets: test.widgets,
                                    access: test.access
                                }
                            });
                            window.User = new User.Model();
                        }

                    }
                });
            },
            data: {
                overviewData: [
                    {
                        "key": "Applications Installed",
                        "link": "installed",
                        "data": overviewInstalled.data,
                        "format": [{"rule": "gt", "value": -1, "style": "success", "stop": true}]
                    },
                    {
                        "key": "Operations Pending",
                        "link": "pending",
                        "data": overviewPending.data,
                        "format": [{"rule": "gt", "value": -1, "style": "info", "stop": true}]
                    },
                    {
                        "key": "Updates Available",
                        "link": "available",
                        "data": overviewAvailable.data,
                        "format": [{"rule": "gt", "value": -1, "style": "warning", "stop": true}]
                    },
                    {
                        "key": "Updates Failed",
                        "link": "failed",
                        "data": overviewFailed.data,
                        "format": [{"rule": "gt", "value": -1, "style": "error", "stop": true}]
                    }
                ]
            },
            locations: [
                { name: 'Dashboard', href: '#dashboard' },
                { name: 'Nodes', href: '#nodes' },
                { name: 'Patches', href: '#patches' },
                { name: 'Tags', href: '#tags' },
                { name: 'Multi-Patcher', href: '#multi' },
                { name: 'Schedules', href: '#schedule' },
                { name: 'Logs', href: '#logs'}
            ]
        });

        // Extend app with user information here
        // We will want to merge code from application/main.js here.
        _.extend(app, {
            user: {
                permission: 'admin', // Default to admin for now
                hasPermission: function (need) {
                    var permission = this.permission;
                    switch (need) {
                    case "admin":
                        return permission === "admin";
                    case "read_write":
                        return permission === "admin" || permission === "read_write";
                    default:
                        return true;
                    }
                }
            }
        });

        return app;
    }
);
