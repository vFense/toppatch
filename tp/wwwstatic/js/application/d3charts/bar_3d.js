/**
 * Created with PyCharm.
 * User: parallels
 * Date: 12/24/12
 * Time: 9:43 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'd3'],
    function ($, d3) {
        "use strict";
        return function () {
            var width    = 370,
                angle = 30,
                depth = 20,
                height   = 200 - depth;
            function chart(selection) {
                selection.each(function (data) {
                    var svg, frontRect, sideRect, topRect, rightTopTriangle, leftTopTriangle, botWhiteTriangle, txtMask, txtRect, txt,
                        colors = d3.scale.category20(),
                        x = d3.scale.linear().domain([0, data.length]).range([15, width]),
                        y = d3.scale.linear().domain([0, d3.max(data, function (datum) { return datum.value; })]).rangeRound([0, height]),
                        barWidth = width / data.length - (width * 0.1);
                    $(this).html("");
                    function topColor(color) {
                        return colors(color);
                    }
                    function frontColor(color) {
                        return d3.rgb(topColor(color)).darker();
                    }
                    function sideColor(color) {
                        return d3.rgb(frontColor(color)).darker();
                    }
                    function textMouseOver(container, d) {
                        var mousePos = d3.mouse(container), textLength;
                        mousePos[0] = mousePos[0] + 5;
                        mousePos[1] = mousePos[1] + 5;
                        txt.text(d.label + ': ' + d.value + ' patches.');
                        textLength = txt.style('width');
                        txtMask.attr({transform: 'translate(' + mousePos + ')'});
                        txtRect.attr({width: parseFloat(textLength) + 2}).style('opacity', '0.3');
                    }
                    function textMouseMove(container) {
                        var mousePos = d3.mouse(container);
                        mousePos[0] = mousePos[0] + 5;
                        mousePos[1] = mousePos[1] + 5;
                        txtMask.attr({transform: 'translate(' + mousePos + ')'});
                        txtRect.style('opacity', '0.3');
                    }
                    function textMouseOut() {
                        txt.text('');
                        txtRect.style('opacity', '0');
                    }
                    svg = d3.select(this)
                        .append("svg:svg")
                        .attr("width", width)
                        .attr("height", height + depth + 20);

                    topRect = svg.selectAll("svg > top_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "top_rect")
                        .attr("x", function (d, index) { return x(index) + depth - 0.8; })
                        .attr("y", function (d, index) { return y(d.value) > 15 ? height - y(d.value) : height - y(15); })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15) + 3; })
                        .attr("width", barWidth)
                        .attr("stroke", "0")
                        .attr("stroke-width", "0")
                        .attr("fill", function (d, index) { return topColor(index); })
                        .on('mouseover', function (d) {
                            textMouseOver(this, d);
                        })
                        .on('mousemove', function (d) {
                            textMouseMove(this);
                        })
                        .on('mouseout', function (d) {
                            textMouseOut();
                        });

                    sideRect = svg.selectAll("svg > side_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "side_rect")
                        .attr("x", function (d, index) { return x(index) + barWidth; })
                        .attr("y", function (d, index) { return y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth; })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15); })
                        .attr("width", depth)
                        .attr("stroke", "0")
                        .attr("fill", function (d, index) { return sideColor(index); })
                        .on('mouseover', function (d) {
                            textMouseOver(this, d);
                        })
                        .on('mousemove', function (d) {
                            textMouseMove(this);
                        })
                        .on('mouseout', function (d) {
                            textMouseOut();
                        });

                    rightTopTriangle = svg.selectAll("svg > right_top_triangle")
                        .data(data).enter()
                        .append("svg:path")
                        .attr("class", "right_top_triangle")
                        .attr("fill", function (d, index) { return sideColor(index); })
                        .attr("d", function (d, index) {
                            var startX = x(index) + barWidth,
                                startY = y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth,
                                M = startX + ' ' + startY,
                                H = x(index) + barWidth + depth,
                                V = y(d.value) > 15 ? height - y(d.value) : height - y(15),
                                triangle = 'M ' + M + ' ' + ' H ' + H + ' ' + ' V ' + V + ' ' + ' L ' + M;
                            return triangle;
                        });

                    leftTopTriangle = svg.selectAll("svg > left_top_triangle")
                        .data(data).enter()
                        .append("svg:path")
                        .attr("class", "left_top_triangle")
                        .attr("fill", function (d, index) { return topColor(index); })
                        .attr("d", function (d, index) {
                            var startX = x(index) - 0.7,
                                startY = y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth,
                                M = startX + ' ' + startY,
                                H = x(index) + depth - 0.1,
                                V = y(d.value) > 15 ? height - y(d.value) : height - y(15),
                                triangle = 'M ' + M + ' ' + ' H ' + H + ' ' + ' V ' + V + ' ' + ' L ' + M;
                            return triangle;
                        });

                    botWhiteTriangle = svg.selectAll("svg > bot_white_triangle")
                        .data(data).enter()
                        .append("svg:path")
                        .attr("class", "bot_white_triangle")
                        .attr("fill", "white")
                        .attr("d", function (d, index) {
                            var startX = x(index) + barWidth + 1,
                                startY = height + depth,
                                M = startX + ' ' + startY,
                                H = startX + depth,
                                V = height,
                                triangle = 'M ' + M + ' ' + ' H ' + H + ' ' + ' V ' + V + ' ' + ' L ' + M;
                            return triangle;
                        });

                    frontRect = svg.selectAll("svg > front_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "front_rect")
                        .attr("x", function (d, index) { return x(index); })
                        .attr("y", function (d) { return y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth; })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15); })
                        .attr("width", barWidth)
                        .attr("stroke", function (d, index) { return sideColor(index); })//stroke same color as sideRect
                        .attr("fill", function (d, index) { return frontColor(index); })
                        .on('mouseover', function (d) {
                            textMouseOver(this, d);
                        })
                        .on('mousemove', function (d) {
                            textMouseMove(this);
                        })
                        .on('mouseout', function (d) {
                            textMouseOut();
                        });

                    svg.selectAll("svg > text")
                        .data(data)
                        .enter()
                        .append("svg:text")
                        .attr("x", function (datum, index) { return x(index) + barWidth / 2; })
                        .attr("y", function (datum) { return y(datum.value) > 15 ? height - y(datum.value) : height - y(15); })
                        .attr("dy", "33")
                        .attr("text-anchor", "middle")
                        .attr("style", "font-size: 10")
                        .text(function (datum) {
                            return datum.value;
                        })
                        .attr("fill", "white");

                    svg.selectAll("text.yAxis")
                        .data(data)
                        .enter().append("svg:text")
                        .attr("x", function (datum, index) { return x(index) + barWidth / 6; })
                        .attr("y", height + depth + 10)
                        .attr("text-anchor", "middle")
                        .attr("style", "font-size: 10")
                        .attr('transform', 'translate(15, 5)')
                        .attr("class", "yAxis")
                        .text(function (datum) { return datum.label });

                    txtMask = svg.append('g').attr({width: '100px', height: '30px'});

                    txtRect = txtMask.append('rect')
                        .attr({width: '100px', height: '30px', fill: 'lightblue', stroke: 'black', 'rx': '6', 'ry': '6'})
                        .style('opacity', '0');

                    txt = txtMask.append('text')
                        .attr({fill: 'black', dy: '18px'})
                        .style('font-size', '1.3em')
                        .text("");


                });
            }
            return chart;
        };
    }
);