define([
    'd3charts/partition',
    'd3charts/pie',
    'd3charts/bar',
    'd3charts/stackedBar',
    'd3charts/tableGenerator',
    'd3charts/line'
], function (partition, pie, bar, stackedBar, tableGenerator, line) {
    "use strict";
    return {
        "partition": partition,
        "pie": pie,
        "bar": bar,
        "stackedBar": stackedBar,
        "generateTable": tableGenerator,
        "line": line
    };
});