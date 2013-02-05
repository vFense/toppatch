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
            title = 'Packages over time',
            severityColors = ['#EAEA4B', '#FF6600', '#FF3030'];//FFFF00

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var svg, xAxis, xAxisText, yAxisLeft, yAxisLeftText, xAxisWidth, xAxisElement,
                    line, graph, point, area, stack, key, legend, legendData, legendBox,
                    txtTop, txtMask, txtRect, txtMiddleTop, txtMiddle, txtMiddleBottom, txtBottom, txtBottomTop,
                    layers = [{name: 'optional'}, {name: 'recommended'}, {name: 'critical'}],
                    color = d3.scale.category20(),
                    maxX = data.length - 1,
                    maxY = 0,
                    that = this;
                function textMouseOver(d, i) {
                    var mousePos = d3.mouse(that), textLength;
                    mousePos[0] = mousePos[0] > (width / 2) ? mousePos[0] - 200 : mousePos[0] - 20;
                    mousePos[1] = mousePos[1] > (height / 2) ? mousePos[1] - 90 : mousePos[1] - 20;
                    txtTop.text('Total Patches: ' + d.accumulated_total);
                    txtMiddleTop.text("Patches: " + d.total);
                    txtMiddle.text('Critical: ' + d.critical);
                    txtMiddleBottom.text('Recommended: ' + d.recommended);
                    txtBottomTop.text('Optional: ' + d.optional);
                    txtBottom.text(d.dateString);
                    textLength = parseFloat(txtTop.style('width')); //> parseFloat(txtBottom.style('width')) ? txtTop.style('width') : txtBottom.style('width');
                    txtMask.attr({transform: 'translate(' + mousePos + ')'});
                    txtRect.attr({width: parseFloat(textLength) + 15}).style('opacity', '0.3');
                }
                function textMouseOut() {
                    txtTop.text('');
                    txtMiddleTop.text('');
                    txtMiddle.text('');
                    txtMiddleBottom.text('');
                    txtBottomTop.text('');
                    txtBottom.text('');
                    txtMask.attr({transform: 'translate(-200,-200)'});
                    txtRect.style('opacity', '0');
                }
                if (data.length) {
                    $(this).html("");
                    height = height < 150 ? 150 : height;
                    height = height > 190 ? 190 : height;
                    width = width < 300 ? 400 : width;
                    legendData = [
                        {title: 'Optional', value: data[0].optional},
                        {title: 'Recommended', value: data[0].recommended},
                        {title: 'Critical', value: data[0].critical}
                    ];
                    data = data[0].dates;
                    _.each(layers, function (layer) {
                        var tempDate,
                            totalToDate = 0,
                            total = 0;
                        layer.values = [];
                        _.each(data, function (date) {
                            for (key in date) {
                                if (date.hasOwnProperty(key) && key === layer.name) {
                                    tempDate = date.date === 'None' ? '0' : date.date;
                                    if (key === 'critical') {
                                        layer.values.push({
                                            dateString: tempDate,
                                            x: new Date(tempDate).getTime(),
                                            y: date['accumulated_' + key],
                                            total: date.total,
                                            accumulated_total: date.accumulated_total,
                                            optional: date.optional,
                                            critical: date.critical,
                                            recommended: date.recommended
                                        });
                                    } else {
                                        layer.values.push({ x: new Date(tempDate).getTime(), y: date['accumulated_' + key]});
                                    }
                                }
                            }
                        });
                    });
                    _.each(data, function (d) {
                        maxY += d.total;
                    });
                    x.range([10, 0.7 * width]).domain(d3.extent(data, function (d) {
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

                    xAxis = d3.svg.axis().scale(x).ticks(8).tickSize(1).tickFormat(function (d) {
                        return new Date(d).toDateString().substring(4, 10);
                    });
                    yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");

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
                        .attr("transform", "translate(" + "-35" + "," + height / 3.5 + ") rotate(-90)")
                        .text('Packages');

                    xAxisElement = svg.append("svg:g")
                        .attr("class", "x axis")
                        .attr("transform", "translate(0," + (0.8 * height) + ")")
                        .style('font-size', 9)
                        .call(xAxis);

                    xAxisText = svg.append("text")
                        .attr("text-anchor", "middle")
                        .attr("dy", ".75em")
                        .attr("x", width / 2.5)
                        .attr("y", 0.89 * height)
                        .style("font-size", "10px")
                        .style("font-weight", "bold")
                        .text(title);


                    svg.append("svg:g")
                        .attr("class", "y axis")
                        .attr("transform", "translate(9,0)")
                        .call(yAxisLeft);
                    point = svg.selectAll('.point')
                        .data(function (d) { return d.values; }).enter()
                        .append("svg:circle")
                        .attr("class", 'point')
                        .attr("r", "4")
                        .attr("cx", function (d) {
                            return x(new Date(d.x).getTime());
                        }).attr("cy", function (d) {
                            return y(d.accumulated_total);
                        }).on('mouseover', function (d, i) {
                            textMouseOver(d, i);
                            return d3.select(this).attr('r', 8);
                        }).on('mouseout', function (d) {
                            textMouseOut(d);
                            return d3.select(this).attr('r', 4);
                        }).on('click', function (d, i) {
                            window.location.hash = '#patches?date=' + d.dateString;
                        });

                    /*point.append("svg:title")
                     .text(function (d, i) { return new Date(d.x) + "- Total Patches: " + (d.count + i + 1); });*/

                    legend = svg.selectAll(".legend")
                        .data(legendData)
                        .enter().append("g")
                        .attr("class", "legend")
                        .attr("transform", function (d, i) {
                            var heights = [0, 20, 40];
                            return "translate(-45, " + heights[i] + ")";
                        });

                    legendBox = legend.append("rect")
                        .attr("x", width - 25)
                        .attr("width", 25)
                        .attr("height", 18)
                        .style("fill", function (d, i) { return severityColors[i]; });
                    legend.append("text")
                        .attr("x", width - 12)
                        .attr("y", 12)
                        .style("fill", "black")
                        .style("font-weight", "bold")
                        .attr("text-anchor", "middle")
                        .text(function (d, i) { return d.value || 0; });
                    legend.append("title").text(function (d, i) { return d.title + ": " + (d.value || 0); });
                    if (width > 500) {
                        legend.append("text")
                            .attr("x", width - 30)
                            .attr("y", 6)
                            .attr("dy", ".75em")
                            .style("font-size", "10px")
                            .style('font-weight', "bold")
                            .style("text-anchor", "end")
                            .text(function (d) { return d.title; });
                    }


                    txtMask = svg.append('g').attr({width: '100px', transform: 'translate(-200,-200)'});

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
                }
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
        chart.title = function (value) {
            if (!arguments.length) { return title; }
            title = value;
            return chart;
        };

        return chart;
    };
});