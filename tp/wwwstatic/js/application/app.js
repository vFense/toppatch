define(
    ['jquery', 'backbone', 'utilities/vent', 'utilities/viewManager', 'd3charts/interactiveGraph', 'd3charts/pieCharts', 'd3charts/barCharts', 'd3charts/stackedBarChart', 'd3charts/tableGenerator', 'd3charts/lineChart'],
    function ($, Backbone, vent, ViewManager, interGraph, pieGraph, barGraph, stackedGraph, generateTable, lineGraph) {
        "use strict";

        var app = {
            root: '/'
        };

        _.extend(app, {
            $doc: $(document),
            title: $(document).attr('title'),
            vent: vent,
            ViewManager: ViewManager,
            views: {},
            chart: {
                interGraph: interGraph,
                pieGraph: pieGraph,
                barGraph: barGraph,
                stackedGraph: stackedGraph,
                generateTable: generateTable,
                lineGraph: lineGraph
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
                        "data": dataGenerator.counter.available,
                        "format": [{"rule": "gt", "value": 0, "style": "info", "stop": true}]
                    },
                    {
                        "key": "Scheduled Patches",
                        "data": dataGenerator.counter.pending,
                        "format": [{"rule": "gt", "value": 0, "style": "warning", "stop": true}]
                    },
                    {
                        "key": "Completed Patches",
                        "data": dataGenerator.counter.patched,
                        "format": [{"rule": "gt", "value": 0, "style": "success", "stop": true}]
                    },
                    {
                        "key": "Failed Patches",
                        "data": dataGenerator.counter.failed,
                        "format": [{"rule": "gt", "value": 0, "style": "error", "stop": true}]
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
            }
        });

        return app;
    }
);
