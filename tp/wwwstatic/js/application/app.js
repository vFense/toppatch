define(
    ['jquery', 'backbone','utilities/vent', 'utilities/viewManager', 'd3charts/interactiveGraph', 'd3charts/pieCharts', 'd3charts/barCharts', 'd3charts/stackedBarChart', 'd3charts/tableGenerator', 'd3charts/lineChart'],
    function ($, Backbone, vent, ViewManager, interGraph, pieGraph, barGraph, stackedGraph, generateTable, lineGraph) {
        "use strict";
        var osArray = ["Windows 7", "Windows 8", "Windows XP", "Mac OS X", "Linux"];
        var nodeArray=[], Counter = new Object(), win7 = [], win8 = [], winxp = [], macos = [], linux = [];
        Counter.numNodes = Math.floor(Math.random() * 5 + 5);
        Counter.wincounter = 0;
        Counter.win7 = 0;
        Counter.win8 = 0;
        Counter.winxp = 0;
        Counter.lincounter = 0;
        Counter.maccounter = 0;
        Counter.patched = 0;
        Counter.unpatched = 0;
        Counter.failed = 0;
        Counter.pending = 0;
        Counter.available = 0;
        for(var k = 0; k < Counter.numNodes; k++) {
            var patched = Math.floor(Math.random() * 10);
            var unpatched = Math.floor(Math.random() * 5);
            var failed = Math.floor(Math.random() * 2);
            var pending = Math.floor(Math.random() * 5);
            var available = Math.floor(Math.random() * 5);
            var name = "node " + k;
            Counter.patched += patched;
            Counter.unpatched += unpatched;
            Counter.failed += failed;
            Counter.pending += pending;
            Counter.available += available;

            var random = Math.floor(Math.random() * 5);
            if(random < 3) {
                Counter.wincounter++;
                if(random === 0) {
                    Counter.win7++;
                } else if(random === 1) {
                    Counter.win8++;
                } else if(random === 2) {
                    Counter.winxp++;
                }
            }
            else if(random === 3) { Counter.maccounter++; }
            else if(random === 4) { Counter.lincounter++; }
            nodeArray.push({ "name": name, "os": osArray[random], "children": [{"name": "Patches Applied", "size": patched, "graphData": {"label": name, "value": patched}}, {"name": "Patches Available", "size": unpatched, "graphData": {"label": name, "value": unpatched}}, {"name": "Patches Pending", "size": pending, "graphData": {"label": name, "value": pending}},{"name": "Patches Failed", "size": failed, "graphData": {"label": name, "value": failed}}] });
            if(osArray[random] === "Windows 7") {
                win7.push(nodeArray[k]);
            } else if(osArray[random] === "Windows 8") {
                win8.push(nodeArray[k]);
            } else if(osArray[random] === "Windows XP") {
                winxp.push(nodeArray[k]);
            } else if(osArray[random] === "Mac OS X") {
                macos.push(nodeArray[k]);
            } else if(osArray[random] === "Linux") {
                linux.push(nodeArray[k]);
            }
        }
        var tempArray = [], tempData = new Object(), nodeArray = [];
        if(Counter.win7 != 0) {
            tempArray.push({"label": "Windows 7", "value": Counter.win7, "data": win7 });
            for(var z = 0; z < win7.length; z++) {
                nodeArray.push({ "name": win7[z].name, "os": win7[z].os });
            }
        }
        if(Counter.win8 != 0) {
            tempArray.push({"label": "Windows 8", "value": Counter.win8, "data": win8 });
            for(var z = 0; z < win8.length; z++) {
                nodeArray.push({ "name": win8[z].name, "os": win8[z].os });
            }
        }
        if(Counter.winxp != 0) {
            tempArray.push({"label": "Windows XP", "value": Counter.winxp, "data": winxp });
            for(var z = 0; z < winxp.length; z++) {
                nodeArray.push({ "name": winxp[z].name, "os": winxp[z].os });
            }
        }
        if(Counter.maccounter != 0) {
            tempArray.push({"label": "Mac OS X", "value": Counter.maccounter, "data": macos });
            for(var z = 0; z < macos.length; z++) {
                nodeArray.push({ "name": macos[z].name, "os": macos[z].os });
            }
        }
        if(Counter.lincounter != 0) {
            tempArray.push({"label": "Linux", "value": Counter.lincounter, "data": linux });
            for(var z = 0; z < linux.length; z++) {
                nodeArray.push({ "name": linux[z].name, "os": linux[z].os });
            }
        }
        tempData.name = "192.168.1.0";
        tempData.children = [];
        //console.log(Counter);
        for(var j = 0; j < tempArray.length; j++) {
            tempData.children[j] = { "name": tempArray[j].label };
            tempData.children[j].children = [];
            for(var z = 0; z < tempArray[j].data.length; z++) {
                tempData.children[j].children[z] =  { "name": tempArray[j].data[z].name,
                    "children": tempArray[j].data[z].children };
            }
        }

        var app = {
            root: '/'
        };

        _.extend(app, {
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
                osData: tempArray,
                indNodes: nodeArray,
                nodeData: { "Patched": Counter.patched,
                    "Unpatched": Counter.unpatched,
                    "Pending": Counter.pending,
                    "Failed": Counter.failed,
                    "Available": Counter.available,
                    "Nodes": Counter.numNodes },
                overviewData: [
                                        {
                                            "key": "Available Patches",
                                            "data": Counter.available,
                                            "format": [
                                                {
                                                    "rule": "gt",
                                                    "value": 0,
                                                    "style": "info",
                                                    "stop": true
                                                }
                                            ]
                                        },
                                        {
                                            "key": "Scheduled Patches",
                                            "data": Counter.pending,
                                            "format": [
                                                {
                                                    "rule": "gt",
                                                    "value": 0,
                                                    "style": "warning",
                                                    "stop": true
                                                }
                                            ]
                                        },
                                        {
                                            "key": "Completed Patches",
                                            "data": Counter.patched,
                                            "format": [
                                                {
                                                    "rule": "gt",
                                                    "value": 0,
                                                    "style": "success",
                                                    "stop": true
                                                }
                                            ]
                                        },
                                        {
                                            "key": "Failed Patches",
                                            "data": Counter.failed,
                                            "format": [
                                                {
                                                    "rule": "gt",
                                                    "value": 0,
                                                    "style": "error",
                                                    "stop": true
                                                }
                                            ]
                                        }
                                    ],
                summaryData: tempData,
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
