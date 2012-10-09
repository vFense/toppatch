define(
    ['jquery', 'underscore', 'backbone', 'utilities/vent', 'utilities/viewManager', 'd3charts/loadAll'],
    function ($, _, Backbone, vent, ViewManager, charts) {
        "use strict";

        var app = window.app = {
            root: '/'
        }, overviewInstalled = {}, overviewPending = {}, overviewAvailable = {}, overviewFailed = {};

        $.ajax({
            url: '/api/networkData',
            dataType: 'json',
            async: false,
            success: function (json) {
                overviewInstalled = json[0];
                overviewAvailable = json[1];
                overviewPending = json[2];
                overviewFailed = json[3];
            }
        });

        _.extend(app, {
            $doc: $(document),
            title: $(document).attr('title'),
            vent: vent,
            ViewManager: ViewManager,
            views: {},
            parseQuery: function (query) {
                var params = {};
                _.each(query.split('&'), function (value) {
                    var param = value.split('=');
                    params[param[0]] = param[1];
                });
                return params;
            },
            chart: {
                partition: charts.partition,
                pie: charts.pie,
                bar: charts.bar,
                stackedBar: charts.stackedBar,
                generateTable: charts.generateTable,
                line: charts.line
            },
            data: {
                overviewData: [
                    {
                        "key": "Available Patches",
                        "link": "available",
                        "data": overviewAvailable.data,
                        "format": [{"rule": "gt", "value": -1, "style": "info", "stop": true}]
                    },
                    {
                        "key": "Scheduled Patches",
                        "link": "pending",
                        "data": overviewPending.data,
                        "format": [{"rule": "gt", "value": -1, "style": "warning", "stop": true}]
                    },
                    {
                        "key": "Completed Patches",
                        "link": "installed",
                        "data": overviewInstalled.data,
                        "format": [{"rule": "gt", "value": -1, "style": "success", "stop": true}]
                    },
                    {
                        "key": "Failed Patches",
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
                { name: 'Multi-Patcher', href: '#multi' }
            ]
        });

        return app;
    }
);
