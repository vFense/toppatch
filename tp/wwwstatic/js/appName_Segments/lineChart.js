/**
 * Created with PyCharm.
 * User: parallels
 * Date: 8/28/12
 * Time: 12:21 PM
 * To change this template use File | Settings | File Templates.
 */
$application.lineChart = function () {
    "use strict";
    var margin	= [40, 40, 40, 40],
        width = 600 - margin[1] - margin[3],
        height	= 280 - margin[0] - margin[2],
        val_array = new Array(),
        title = "Default",
        max,
        x = d3.scale.linear(),
        y = d3.scale.linear();

    function chart(selection) {
        selection.each(function (data) {
            // generate chart here; `d` is the data and `this` is the element
            var that = this,
                matches = that.id.match(/\d+$/),
                widget = "#widget" + matches[0];
            $(widget + "-title").html(title);
            $(this).html("");
            for (var k = 0; k < data.length; k++) {
                val_array[k] = { x: data[k].label, y: data[k].value };
            }
            //max = d3.max(val_array);
            max = d3.max(val_array, function(d) {
                return d.y;
            });
            x.domain([val_array[0].x, val_array[val_array.length-1].x]).range([0, width - margin[3] - margin[2]]);
            y.domain([0, max]).range([height, 0]);
            var xAxis = d3.svg.axis().scale(x).tickSize(1),
                yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left"),
                line = d3.svg.line()
                    // assign the X function to plot our line as we wish
                    .x(function(d, i) {
                        // verbose logging to show what's actually being done
                        //alert(x(0)+" "+ labels[0]);
                        //console.log('Plotting X value for data point: ' + d.x + ' using index: ' + i + ' to be at: ' + x(d.x) + ' using our xScale.');
                        // return the X coordinate where we want to plot this datapoint
                        //alert(x(i));
                        return x(d.x);
                    })
                    .y(function(d) {
                        // verbose logging to show what's actually being done
                        //console.log('Plotting Y value for data point: ' + d.y + ' to be at: ' + y(d.y) + " using our yScale.");
                        // return the Y coordinate where we want to plot this datapoint
                        return y(d.y);
                    });
            var graph = d3.select(this)
                .append("svg:svg")
                .data([val_array])
                .attr("width", width)
                .attr("height", height + margin[0] + margin[2])
                .append("svg:g")
                .attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");

            graph.append("svg:g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);
            graph.append("svg:g")
                .attr("class", "y axis")
                .attr("transform", "translate(-1,0)")
                .call(yAxisLeft);
            graph.append("svg:path")
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", "2")
                .attr("d", line(val_array));
            //console.log(val_array);
            var point = graph.selectAll('.point')
                .data(val_array, function (d, i) {
                    return d[i];
                })
                .enter().append("svg:circle")
                .attr("class", function (d) {
                    //console.log(d.y + " " + max);
                    if (d.y === max) {
                        return 'point max';
                    } else {
                        return 'point';
                    }
                })
                .attr("r", function (d, i) {
                    if (d === max) {
                        return 6;
                    } else {
                        return 4;
                    }
                }).attr("cx", function(d) {
                    //console.log( x(d.x) );
                    return x(d.x);
                }).attr("cy", function(d) {
                    //console.log( y(d.y) );
                    return y(d.y);
                }).on('mouseover', function() {
                    return d3.select(this).attr('r', 8);
                }).on('mouseout', function() {
                    return d3.select(this).attr('r', 4);
                }).on('click', function(d, i) {
                    console.log(d, i);
                });
            point.append("svg:title")
                .text(function (d, i) { return d.x + ", " + d.y; });
        });
    }

    chart.margin = function (value) {
        if (!arguments.length) { return margin; }
        margin = value;
        return chart;
    };
    chart.width = function (value) {
        if (!arguments.length) { return width; }
        width = value;
        return chart;
    };
    chart.height = function (value) {
        if (!arguments.length) { return height; }
        height = value;
        return chart;
    };
    chart.title = function (value) {
        if(!arguments.length) { return title; }
        title = value;
        return chart;
    };

    return chart;
};