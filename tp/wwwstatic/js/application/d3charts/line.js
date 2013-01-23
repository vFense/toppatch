/**
 * Created with PyCharm.
 * User: parallels
 * Date: 8/28/12
 * Time: 12:21 PM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery', 'd3', 'underscore'], function ($, d3, _) {
    'use strict';
    return function () {
        var margin    = [40, 40, 40, 40],
            width     = 600 - margin[1] - margin[3],
            height    = 280 - margin[0] - margin[2],
            val_array = [],
            title     = "Default",
            max,
            x = d3.scale.linear(),
            y = d3.scale.linear();

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var k, xAxis, yAxisLeft, line, graph, point, txt, txtMask, txtRect, txtMiddle, txtBottom,
                    that = this;
                function textMouseOver(d, i) {
                    var mousePos = d3.mouse(that), textLength,
                        date = new Date(d.x),
                        dateString = date.toDateString() + ' ' + date.toTimeString().split(' ')[0];//Wed Jan 23 2013 00:28:12
                    mousePos[0] = mousePos[0] - 20;
                    mousePos[1] = mousePos[1] > (height / 2) ? mousePos[1] - 80 : mousePos[1] - 20;
                    txt.text("Total Patches: " + (d.count + i + 1));
                    txtMiddle.text(d.patch_name);
                    txtBottom.text(dateString);
                    textLength = parseFloat(txtMiddle.style('width')) > parseFloat(txtBottom.style('width')) ? txtMiddle.style('width') : txtBottom.style('width');
                    txtMask.attr({transform: 'translate(' + mousePos + ')'});
                    txtRect.attr({width: parseFloat(textLength) + 2}).style('opacity', '0.3');
                }
                function textMouseMove() {
                    var mousePos = d3.mouse(that);
                    mousePos[0] = mousePos[0] - 10;
                    mousePos[1] = mousePos[1] - 38;
                    txtMask.attr({transform: 'translate(' + mousePos + ')'});
                    txtRect.style('opacity', '0.3');
                }
                function textMouseOut() {
                    txt.text('');
                    txtMiddle.text('');
                    txtBottom.text('');
                    txtMask.attr({transform: 'translate(0,0)'});
                    txtRect.style('opacity', '0');
                }
                _.each(data, function (object) {
                    val_array.push({ x: object.label || 0, y: object.value, count: object.count, patch_name: object.patch_name });
                });
                max = d3.max(val_array, function (d) {
                    return d.y;
                });
                x.domain([val_array[0].x, val_array[val_array.length - 1].x]).range([0, 0.7 * width]);
                y.domain([0, max]).range([(0.8 * height), 0]);
                xAxis = d3.svg.axis().scale(x).tickSize(1).tickFormat(function (d, i) {
                    return new Date(d).toDateString().substring(4, 10);
                });
                yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");
                line = d3.svg.line()
                    .x(function (d, i) { return x(d.x); })
                    .y(function (d) { return y(d.y); });
                graph = d3.select(this)
                    .append("svg:svg")
                    .data([val_array])
                    .attr("width", width)
                    .attr("height", height)// + margin[0] + margin[2])
                    .style('overflow', 'visible')
                    .append("svg:g")
                    .attr("transform", "translate(" + 35 + "," + 15 + ")");

                graph.append("svg:g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + (0.8 * height) + ")")
                    .style('font-size', 9)
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
                point = graph.selectAll('.point')
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
                    }).attr("cx", function (d) {
                        //console.log( x(d.x) );
                        return x(d.x);
                    }).attr("cy", function (d) {
                        //console.log( y(d.y) );
                        return y(d.y);
                    }).on('mouseover', function (d, i) {
                        textMouseOver(d, i);
                        return d3.select(this).attr('r', 8);
                    }).on('mouseout', function (d) {
                        textMouseOut(d);
                        return d3.select(this).attr('r', 4);
                    }).on('click', function (d, i) {
                        window.console.log(d, i);
                    });

                /*point.append("svg:title")
                    .text(function (d, i) { return new Date(d.x) + "- Total Patches: " + (d.count + i + 1); });*/

                txtMask = graph.append('g').attr({width: '100px'});

                txtRect = txtMask.append('rect')
                    .attr({width: '100px', height: '60px', fill: 'lightblue', stroke: 'black', 'rx': '6', 'ry': '6'})
                    .style('opacity', '0');

                txt = txtMask.append('text')
                    .attr({fill: 'black', dy: '18px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('text-wrap', 'normal')
                    .text("");
                txtMiddle = txtMask.append('text')
                    .attr({fill: 'black', dy: '36px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
                txtBottom = txtMask.append('text')
                    .attr({fill: 'black', dy: '54px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
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
            if (!arguments.length) { return title; }
            title = value;
            return chart;
        };

        return chart;
    };
});