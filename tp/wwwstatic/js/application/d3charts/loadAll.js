define([
    'd3charts/partition',
    'd3charts/pie',
    'd3charts/bar',
    'd3charts/stackedBar',
    'd3charts/tableGenerator',
    'd3charts/line',
    'd3charts/newpie',
    'd3charts/bar_3d'
], function (partition, pie, bar, stackedBar, tableGenerator, line, newpie, bar_3d) {
    "use strict";
    return {
        "partition": partition,
        "pie": pie,
        "bar": bar,
        "stackedBar": stackedBar,
        "generateTable": tableGenerator,
        "line": line,
        "newpie": newpie,
        "bar_3d": bar_3d
    };
});