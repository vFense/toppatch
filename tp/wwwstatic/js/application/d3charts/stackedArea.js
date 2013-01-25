/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/24/13
 * Time: 3:04 PM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery', 'd3', 'underscore'], function ($, d3, _) {
    'use strict';
    return function () {
        var width     = 600,
            height    = 280,
            x = d3.scale.linear(),
            y = d3.scale.linear(),
            severityColors = ['#FFFF00', '#FF6600', '#FF3030'];

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var svg, xAxis, xAxisText, yAxisLeft, yAxisLeftText, line, graph, point, area, stack, key,
                    txtTop, txtMask, txtRect, txtMiddleTop, txtMiddle, txtMiddleBottom, txtBottom, txtBottomTop,
                    layers = [{name: 'optional'}, {name: 'recommended'}, {name: 'critical'}],
                    color = d3.scale.category20(),
                    maxY = 0,
                    maxX = data.length - 1,
                    that = this;

                function textMouseOver(d, i) {
                    var mousePos = d3.mouse(that), textLength,
                        date = new Date(d.x),
                        dateString = date.toDateString() + ' ' + date.toTimeString().split(' ')[0];//Wed Jan 23 2013 00:28:12
                    mousePos[0] = mousePos[0] - 20;
                    mousePos[1] = mousePos[1] > (height / 2) ? mousePos[1] - 80 : mousePos[1] - 20;
                    txtTop.text("Patches installed: " + (d.total));
                    txtMiddleTop.text('Total Patches: ' + d.totalToDate);
                    txtMiddle.text('Critical: ' + d.critical);
                    txtMiddleBottom.text('Recommended: ' + d.recommended);
                    txtBottomTop.text('Optional: ' + d.optional);
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
                    txtTop.text('');
                    txtMiddleTop.text('');
                    txtMiddle.text('');
                    txtMiddleBottom.text('');
                    txtBottomTop.text('');
                    txtBottom.text('');
                    txtMask.attr({transform: 'translate(0,0)'});
                    txtRect.style('opacity', '0');
                }
                _.each(layers, function (layer) {
                    var tempDate,
                        totalToDate = 0,
                        total = 0;
                    layer.values = [];
                    _.each(data, function (date) {
                        for (key in date) {
                            if (date.hasOwnProperty(key) && key === layer.name) {
                                tempDate = date.date === 'None' ? '0' : date.date;
                                total += date[key];
                                totalToDate += date.total;
                                if (key === 'critical') {
                                    layer.values.push({
                                        x: new Date(tempDate).getTime(),
                                        y: total,
                                        total: date.total,
                                        totalToDate: totalToDate,
                                        optional: date.optional,
                                        critical: date.critical,
                                        recommended: date.recommended
                                    });
                                } else {
                                    layer.values.push({ x: new Date(tempDate).getTime(), y: total });
                                }
                            }
                        }
                    });
                });
                _.each(data, function (d) {
                    maxY += d.total;
                });
                x.range([0, 0.7 * width]).domain(d3.extent(data, function (d) {
                    var tempDate;
                    tempDate = d.date === 'None' ? '0' : d.date;
                    return new Date(tempDate).getTime();
                }));
                y.range([(0.8 * height), 0]).domain([0, maxY]);
                area = d3.svg.area()
                    .x(function (d) { return x(new Date(d.x).getTime()); })
                    .y0(function (d) { return y(d.y0); })
                    .y1(function (d) { return y(d.y0 + d.y); });

                stack = d3.layout.stack()
                    .values(function (d) { return d.values; })(layers);

                xAxis = d3.svg.axis().scale(x).tickSize(1).tickFormat(function (d) {
                    return new Date(d).toDateString().substring(4, 10);
                });

                yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");

                line = d3.svg.line()
                    .x(function (d, i) { return x(d.x); })
                    .y(function (d) { return y(d.y); });
                svg = d3.select(this)
                    .append("svg:svg")
                    .data([stack[2]])
                    .attr("width", width)
                    .attr("height", height + 10)// + margin[0] + margin[2])
                    .style('overflow', 'visible')
                    .append("svg:g")
                    .attr("transform", "translate(" + 35 + "," + 15 + ")");

                graph = svg.selectAll('severity')
                    .data(stack).enter()
                    .append("svg:path")
                    .attr("stroke", "none")
                    .attr("fill", function (d, i) { return severityColors[i]; })
                    .attr("d", function (d) { return area(d.values); });

                yAxisLeftText = svg.append("text")
                    .attr("text-anchor", "end")
                    .attr("dy", ".75em")
                    .style("font-size", "10px")
                    .style("font-weight", "bold")
                    .attr("transform", "translate(" + "-30" + "," + height / 3.5 + ") rotate(-90)")
                    .text('Packages');

                xAxisText = svg.append("text")
                    .attr("text-anchor", "end")
                    .attr("dy", ".75em")
                    .style("font-size", "10px")
                    .style("font-weight", "bold")
                    .attr("transform", "translate(" + width / 2 + "," + 0.88 * height + ")")
                    .text('Packages installed over time');

                svg.append("svg:g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + (0.8 * height) + ")")
                    .style('font-size', 9)
                    .call(xAxis);
                svg.append("svg:g")
                    .attr("class", "y axis")
                    .attr("transform", "translate(-1.2,0)")
                    .call(yAxisLeft);
                point = svg.selectAll('.point')
                    .data(function (d) { return d.values; }).enter()
                    .append("svg:circle")
                    .attr("class", 'point')
                    .attr("r", "4")
                    .attr("cx", function (d) {
                        return x(new Date(d.x).getTime());
                    }).attr("cy", function (d) {
                        return y(d.totalToDate);
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

                txtMask = svg.append('g').attr({width: '100px'});

                txtRect = txtMask.append('rect')
                    .attr({width: '100px', height: '115px', fill: 'lightblue', stroke: 'black', 'rx': '6', 'ry': '6'})
                    .style('opacity', '0');

                txtTop = txtMask.append('text')
                    .attr({fill: 'black', dy: '18px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('text-wrap', 'normal')
                    .text("");
                txtMiddleTop = txtMask.append('text')
                    .attr({fill: 'black', dy: '36px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
                txtMiddle = txtMask.append('text')
                    .attr({fill: 'black', dy: '54px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
                txtMiddleBottom = txtMask.append('text')
                    .attr({fill: 'black', dy: '72px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
                txtBottomTop = txtMask.append('text')
                    .attr({fill: 'black', dy: '90px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
                txtBottom = txtMask.append('text')
                    .attr({fill: 'black', dy: '108px', width: '100px'})
                    .style('font-size', '1.3em')
                    .style('overflow', 'hidden')
                    .text("");
            });
        }
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

        return chart;
    };
});