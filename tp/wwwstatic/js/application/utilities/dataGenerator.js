define(['underscore'], function (_) {
    "use strict";
    var osArray   = ["Windows 7", "Windows 2K8", "Windows XP", "Windows 2K3", "Windows Vista"],
        nodeArray = [],
        counter   = {},
        win7      = [],
        win2008      = [],
        winxp     = [],
        win2003     = [],
        winVis     = [],
        tempArray = [],
        tempData  = {},
        ipData    = _.shuffle(_.range(2, 254)),
        k;

    _.extend(counter, {
        numNodes: Math.floor(Math.random() * 10 + 10),
        wincounter: 0,
        win7: 0,
        winS2008: 0,
        winVista: 0,
        winS2003: 0,
        winxp: 0,
        patched: 0,
        unpatched: 0,
        failed: 0,
        pending: 0,
        available: 0
    });

    for (k = 0; k < counter.numNodes; k += 1) {
        var patched = Math.floor(Math.random() * 10);
        var unpatched = Math.floor(Math.random() * 5);
        var failed = Math.floor(Math.random() * 2);
        var pending = Math.floor(Math.random() * 5);
        var available = Math.floor(Math.random() * 5);
        var name = "192.168.1." + ipData[k];
        counter.patched += patched;
        counter.unpatched += unpatched;
        counter.failed += failed;
        counter.pending += pending;
        counter.available += available;

        var random = Math.floor(Math.random() * 5);

        counter.wincounter += 1;
        if (random === 0) {
            counter.win7 += 1;
        } else if (random === 1) {
            counter.winS2008 += 1;
        } else if (random === 2) {
            counter.winxp += 1;
        } else if (random === 3) {
            counter.winS2003 += 1;
        } else if (random === 4) {
            counter.winVista += 1;
        }

        nodeArray.push({
            "name": name,
            "os": osArray[random],
            "children": [
                { "name": "Patches Applied", "size": patched, "graphData": {"label": name, "value": patched}},
                { "name": "Patches Available", "size": unpatched, "graphData": {"label": name, "value": unpatched}},
                { "name": "Patches Pending",   "size": pending,   "graphData": {"label": name, "value": pending}},
                { "name": "Patches Failed",    "size": failed,    "graphData": {"label": name, "value": failed}}
            ]
        });
        if (osArray[random] === "Windows 7") {
            win7.push(nodeArray[k]);
        } else if (osArray[random] === "Windows 2K8") {
            win2008.push(nodeArray[k]);
        } else if (osArray[random] === "Windows XP") {
            winxp.push(nodeArray[k]);
        } else if (osArray[random] === "Windows 2K3") {
            win2003.push(nodeArray[k]);
        } else if (osArray[random] === "Windows Vista") {
            winVis.push(nodeArray[k]);
        }
    }

    if (counter.win7 !== 0) {
        tempArray.push({"label": "Windows 7", "value": counter.win7, "data": win7 });
        for (var z = 0; z < win7.length; z++) {
            nodeArray.push({ "name": win7[z].name, "os": win7[z].os });
        }
    }
    if (counter.winS2008 !== 0) {
        tempArray.push({"label": "Win2K8", "value": counter.winS2008, "data": win2008 });
        for (var z = 0; z < win2008.length; z++) {
            nodeArray.push({ "name": win2008[z].name, "os": win2008[z].os });
        }
    }
    if (counter.winVista !== 0) {
        tempArray.push({"label": "Vista", "value": counter.winVista, "data": winVis });
        for (var z = 0; z < winVis.length; z++) {
            nodeArray.push({ "name": winVis[z].name, "os": winVis[z].os });
        }
    }
    if (counter.winxp !== 0) {
        tempArray.push({"label": "Windows XP", "value": counter.winxp, "data": winxp });
        for (var z = 0; z < winxp.length; z++) {
            nodeArray.push({ "name": winxp[z].name, "os": winxp[z].os });
        }
    }
    if (counter.winS2003 !== 0) {
        tempArray.push({"label": "Win2K3", "value": counter.winS2003, "data": win2003 });
        for (var z = 0; z < win2003.length; z++) {
            nodeArray.push({ "name": win2003[z].name, "os": win2003[z].os });
        }
    }
    tempData.name = "192.168.1.0";
    tempData.children = [];

    for (var j = 0; j < tempArray.length; j++) {
        tempData.children[j] = { "name": tempArray[j].label };
        tempData.children[j].children = [];
        for (var z = 0; z < tempArray[j].data.length; z++) {
            tempData.children[j].children[z] =  { "name": tempArray[j].data[z].name,
                "children": tempArray[j].data[z].children };
        }
    }

    return {
        "tempArray": tempArray,
        "tempData": tempData,
        "nodeArray": nodeArray,
        "counter": counter
    };
});