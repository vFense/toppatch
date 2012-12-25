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
                height   = 200,
                angle = 30,
                depth = 20;
            function chart(selection) {
                selection.each(function (data) {
                    var svg, frontRect, sideRect, topRect, rightTopTriangle,
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
                    svg = d3.select(this)
                        .append("svg:svg")
                        .attr("width", width)
                        .attr("height", height + depth);

                    topRect = svg.selectAll("svg > top_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "top_rect")
                        .attr("x", function (d, index) { return x(index) + depth; })
                        .attr("y", function (d, index) { return y(d.value) > 15 ? height - y(d.value) - depth : height - y(15); })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15); })
                        .attr("width", barWidth)
                        .attr("stroke", "0")
                        .attr("fill", function (d, index) { return topColor(index); });

                    frontRect = svg.selectAll("svg > front_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "front_rect")
                        .attr("x", function (d, index) { return x(index); })
                        .attr("y", function (d) { return y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth; })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15); })
                        .attr("width", barWidth)
                        .attr("stroke", function (d, index) { return sideColor(index); })//stroke same color as sideRect
                        .attr("fill", function (d, index) { return frontColor(index); });

                    sideRect = svg.selectAll("svg > side_rect")
                        .data(data).enter()
                        .append("svg:rect")
                        .attr("class", "side_rect")
                        .attr("x", function (d, index) { return x(index) + barWidth; })
                        .attr("y", function (d, index) { return y(d.value) > 15 ? height - y(d.value) + depth : height - y(15) + depth; })
                        .attr("height", function (d) { return y(d.value) > 15 ? y(d.value) : y(15); })
                        .attr("width", depth)
                        .attr("stroke", "0")
                        .attr("fill", function (d, index) { return sideColor(index); });

                    rightTopTriangle = svg.selectAll("svg > right_top_triangle")
                        .data(data).enter()
                        .append("svg:path")


                });
            }
            return chart;
        };
    }
);