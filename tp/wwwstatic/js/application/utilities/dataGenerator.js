define([], function () {
    "use strict";
    var osArray   = ["Windows 7", "Windows 8", "Windows XP", "Mac OS X", "Linux"],
        nodeArray = [],
        counter   = {},
        win7      = [],
        win8      = [],
        winxp     = [],
        macos     = [],
        linux     = [],
        tempArray = [],
        tempData  = {},

        k;

    _.extend(counter, {
        numNodes: Math.floor(Math.random() * 5 + 5),
        wincounter: 0,
        win7: 0,
        win8: 0,
        winxp: 0,
        lincounter: 0,
        maccounter: 0,
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
        var name = "node " + k;
        counter.patched += patched;
        counter.unpatched += unpatched;
        counter.failed += failed;
        counter.pending += pending;
        counter.available += available;

        var random = Math.floor(Math.random() * 5);
        if (random < 3) {
            counter.wincounter += 1;
            if (random === 0) {
                counter.win7 += 1;
            } else if (random === 1) {
                counter.win8 += 1;
            } else if (random === 2) {
                counter.winxp += 1;
            }
        }
        else if (random === 3) { counter.maccounter += 1; }
        else if (random === 4) { counter.lincounter += 1; }
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
        } else if (osArray[random] === "Windows 8") {
            win8.push(nodeArray[k]);
        } else if (osArray[random] === "Windows XP") {
            winxp.push(nodeArray[k]);
        } else if (osArray[random] === "Mac OS X") {
            macos.push(nodeArray[k]);
        } else if (osArray[random] === "Linux") {
            linux.push(nodeArray[k]);
        }
    }

    if (counter.win7 !== 0) {
        tempArray.push({"label": "Windows 7", "value": counter.win7, "data": win7 });
        for (var z = 0; z < win7.length; z++) {
            nodeArray.push({ "name": win7[z].name, "os": win7[z].os });
        }
    }
    if (counter.win8 !== 0) {
        tempArray.push({"label": "Windows 8", "value": counter.win8, "data": win8 });
        for (var z = 0; z < win8.length; z++) {
            nodeArray.push({ "name": win8[z].name, "os": win8[z].os });
        }
    }
    if (counter.winxp !== 0) {
        tempArray.push({"label": "Windows XP", "value": counter.winxp, "data": winxp });
        for (var z = 0; z < winxp.length; z++) {
            nodeArray.push({ "name": winxp[z].name, "os": winxp[z].os });
        }
    }
    if (counter.maccounter !== 0) {
        tempArray.push({"label": "Mac OS X", "value": counter.maccounter, "data": macos });
        for (var z = 0; z < macos.length; z++) {
            nodeArray.push({ "name": macos[z].name, "os": macos[z].os });
        }
    }
    if (counter.lincounter !== 0) {
        tempArray.push({"label": "Linux", "value": counter.lincounter, "data": linux });
        for (var z = 0; z < linux.length; z++) {
            nodeArray.push({ "name": linux[z].name, "os": linux[z].os });
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