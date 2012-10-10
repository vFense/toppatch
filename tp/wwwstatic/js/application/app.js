define(
    ['jquery', 'underscore', 'backbone', 'utilities/vent', 'utilities/viewManager', 'utilities/dataGenerator', 'd3charts/loadAll'],
    function ($, _, Backbone, vent, ViewManager, dataGenerator, charts) {
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
                var ws = new WebSocket("wss://localhost:8000/ws");
                ws.onmessage = function(evt) {
                    console.log(evt.data);
                    $.ajax({
                        url: '/api/networkData',
                        dataType: 'json',
                        async: false,
                        success: function (json) {
                            console.log(json)
                            for(var i = 0; i < json.length; i++) {
                                if(json[i].key == 'installed') {
                                    $('.success').children('dd').children().html(json[i].data + 1);
                                    console.log( $('.success').children('dd').children());
                                }
                                if(json[i].key == 'available') {
                                    $('.info').children('dd').children().html(json[i].data - 1);
                                    console.log( $('.info').children('dd').children())
                                }
                                if(json[i].key == 'pending') {
                                    $('.warning').children('dd').children().html(json[i].data);
                                    console.log( $('.warning').children('dd').children());
                                }
                                if(json[i].key == 'failed') {
                                    $('.error').children('dd').children().html(json[i].data);
                                    console.log( $('.error').children('dd').children());
                                }
                            }
                        }
                    });
                };
                ws.onclose = function(evt) {

                };
                ws.onopen = function(evt) {

                };
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
                osData: dataGenerator.tempArray,
                indNodes: dataGenerator.nodeArray,
                nodeData: {
                    "Patched": dataGenerator.counter.patched,
                    "Unpatched": dataGenerator.counter.unpatched,
                    "Pending": dataGenerator.counter.pending,
                    "Failed": dataGenerator.counter.failed,
                    "Available": dataGenerator.counter.available,
                    "Nodes": dataGenerator.counter.numNodes
                },
                overviewData: [
                    {
                        "key": "Available Patches",
                        "link": "available",
                        "data": overviewAvailable.data,//dataGenerator.counter.available,
                        "format": [{"rule": "gt", "value": -1, "style": "info", "stop": true}]
                    },
                    {
                        "key": "Scheduled Patches",
                        "link": "pending",
                        "data": overviewPending.data,//dataGenerator.counter.pending,
                        "format": [{"rule": "gt", "value": -1, "style": "warning", "stop": true}]
                    },
                    {
                        "key": "Completed Patches",
                        "link": "installed",
                        "data": overviewInstalled.data,//dataGenerator.counter.patched,
                        "format": [{"rule": "gt", "value": -1, "style": "success", "stop": true}]
                    },
                    {
                        "key": "Failed Patches",
                        "link": "failed",
                        "data": overviewFailed.data,//dataGenerator.counter.failed,
                        "format": [{"rule": "gt", "value": -1, "style": "error", "stop": true}]
                    }
                ],
                summaryData: dataGenerator.tempData,
                patches: [{ "date": new Date(), "name": "Security Update for Microsoft XML Editor 2010 (KB2251489)", "os": "windows" },
                    { "date": new Date(), "name": "Security Update for Microsoft Visual C++ 2008 Service Pack 1 Redistributable Package (KB2538243)", "os": "windows" },
                    { "date": new Date(), "name": "Security Update for Microsoft Visual Studio 2010 (KB2542054)", "os": "windows" },
                    { "date": new Date(), "name": "Security Update for Microsoft Visual Studio 2008 Service Pack 1 (KB2669970)", "os": "windows" },
                    { "date": new Date(), "name": "Update for Microsoft Tools for Office Runtime Redistributable (KB2525428)", "os": "windows" },
                    { "date": new Date(), "name": "Security Update for Microsoft .NET Framework 4 on XP, Server 2003, Vista, Windows 7, Server 2008, Server 2008 R2 for x64 (KB2604121)", "os": "windows" },
                    { "date": new Date(), "name": "Microsoft Security Essentials - KB2691894", "os": "windows" },
                    { "date": new Date(), "name": "Security Update for Windows 7 for x64-based Systems (KB2731847)", "os": "windows" }]
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