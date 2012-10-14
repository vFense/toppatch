define(
    ['jquery', 'underscore', 'backbone', 'utilities/vent', 'utilities/viewManager', 'd3charts/loadAll'],
    function ($, _, Backbone, vent, ViewManager, charts) {
        "use strict";

        var app = window.app = {
            root: '/'
        }, overviewInstalled = {'data': 0}, overviewPending = {'data': 0}, overviewAvailable = {'data': 0}, overviewFailed = {'data': 0};
        $.ajax({
            url: '/api/networkData',
            dataType: 'json',
            async: false,
            success: function (json) {
                if(json.length != 0) {
                    overviewInstalled = json[0];
                    overviewAvailable = json[1];
                    overviewPending = json[2];
                    overviewFailed = json[3];
                }
            }
        });

        _.extend(app, {
            $doc: $(document),
            title: $(document).attr('title'),
            vent: vent,
            ViewManager: ViewManager,
            views: {},
            startWs: function () {
                var ws = new WebSocket("wss://" + window.location.host + "/ws");
                ws.onmessage = function(evt) {
                    var message = evt.data;
                    console.log(message);
                    $.ajax({
                        url: '/api/networkData',
                        dataType: 'json',
                        async: false,
                        success: function (json) {
                            console.log(json)
                            for(var i = 0; i < json.length; i++) {
                                if(json[i].key == 'installed') {
                                    $('.success').children('dd').children().html(json[i].data);
                                }
                                if(json[i].key == 'available') {
                                    $('.info').children('dd').children().html(json[i].data);
                                }
                                if(json[i].key == 'pending') {
                                    $('.warning').children('dd').children().html(json[i].data);
                                }
                                if(json[i].key == 'failed') {
                                    $('.error').children('dd').children().html(json[i].data);
                                }
                            }
                        }
                    });
                };
                ws.onclose = function(evt) {
                    console.log(evt);
                    console.log('connection closed');
                };
                ws.onopen = function(evt) {
                    console.log('connection opened');
                };
                ws.onerror = function(evt) {
                    console.log('Error: ' + evt);
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
                        "key": "Completed Patches",
                        "link": "installed",
                        "data": overviewInstalled.data,
                        "format": [{"rule": "gt", "value": -1, "style": "info", "stop": true}]
                    },
                    {
                        "key": "Pending Patches",
                        "link": "pending",
                        "data": overviewPending.data,
                        "format": [{"rule": "gt", "value": -1, "style": "success", "stop": true}]
                    },
                    {
                        "key": "Available Patches",
                        "link": "available",
                        "data": overviewAvailable.data,
                        "format": [{"rule": "gt", "value": -1, "style": "warning", "stop": true}]
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
