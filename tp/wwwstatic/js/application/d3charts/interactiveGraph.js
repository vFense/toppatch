/**
 * Created with PyCharm.
 * User: sergio
 * Date: 9/7/12
 * Time: 5:59 PM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery','d3'], function($, d3) {

    return function () {
        "use strict";
        var title = 'Summary Chart',
            chartTitle = title,
            width = 500,
            height = 200;

        function chart(selection) {
            selection.each(function (root) {
                var that = this,
                    matches = that.id.match(/\d+$/),
                    widget = "#widget" + matches[0],
                    firstTitle = false,
                    secondTitle = false,
                    thirdTitle = false,
                    fourthTitle = false;
                $(widget + "-title").html(chartTitle);
                $(this).html("");
                width = $(this).width();
                var x = d3.scale.linear().range([0, width]),
                    y = d3.scale.linear().range([0, height]);
                var vis = d3.select(this)
                    .append("svg:svg")
                    .attr("width", width)
                    .attr("height", height + 20);

                var partition = d3.layout.partition()
                    .value(function(d) { return d.size; });
                //d3.json("flare.json", function(root) {
                var title = vis.selectAll('title')
                    .data(partition.nodes(root))
                    .enter()
                    .append("svg:text")
                    .filter(function (d, i) {
                        return i < 4 ? d : null;
                    })
                    .attr("x", function (d) {
                        return x(d.y) + 8;
                    })
                    .attr("y", height + 10)
                    .attr("dy", ".45em")
                    .style("font-size", "1.3em")
                    .text(function(d) {
                        if(d.depth === 0) {
                            if(firstTitle === false) {
                                firstTitle = true;
                                return "Network";
                            }
                        } else if(d.depth === 1) {
                            if(secondTitle === false) {
                                secondTitle = true;
                                return "OS Name";
                            }
                        } else if(d.depth === 2) {
                            if(thirdTitle === false) {
                                thirdTitle = true;
                                return "Node Name";
                            }
                        } else if(d.depth === 3) {
                            if(fourthTitle === false) {
                                fourthTitle = true;
                                return "Node Stats";
                            }
                        }
                    });
                var g = vis.selectAll("g")
                    .data(partition.nodes(root))
                    .enter().append("svg:g")
                    .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; })
                    .on("click", click);
                var kx = width / root.dx,
                    ky = height;

                g.append("svg:rect")
                    .attr("width", root.dy * kx)
                    .attr("height", function(d) { return d.dx * ky; })
                    .attr("class", function(d) { return d.children ? "tree parent" : "tree child"; });

                g.append("svg:text")
                    .attr("transform", transform)
                    .attr("dy", ".35em")
                    .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
                    .text(function(d) { return d.size ? d.name + ": " + d.size : d.name; });

                d3.select(this)
                    .on("click", function() { click(root); });

                function click(d) {
                    if (!d.children) return;

                    kx = (d.y ? width - 40 : width) / (1 - d.y);
                    ky = height / d.dx;
                    x.domain([d.y, 1]).range([d.y ? 40 : 0, width]);
                    y.domain([d.x, d.x + d.dx]);

                    var titleTrans = title.transition()
                        .duration(d3.event.altKey ? 7500 : 500)
                        .style("opacity", function () {
                            return d.depth === 0 ?  "1" : "0";
                        });

                    var t = g.transition()
                        .duration(d3.event.altKey ? 7500 : 750)
                        .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; });

                    t.select("rect")
                        .attr("width", d.dy * kx)
                        .attr("height", function(d) { return d.dx * ky; });

                    t.select("text")
                        .attr("transform", transform)
                        .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });

                    d3.event.stopPropagation();
                }

                function transform(d) {

                    return "translate(8," + d.dx * ky / 2 + ")";
                }

            });
        }
        chart.title = function (value) {
            if(!arguments.length) { return title; }
            title = value;
            return chart;
        };
        chart.chartTitle = function (value) {
            if(!arguments.length) { return chartTitle; }
            chartTitle = value;
            return chart;
        };
        chart.width = function (value) {
            if(!arguments.length) { return width; }
            width = value;
            return chart;
        };
        chart.height = function (value) {
            if(!arguments.length) { return height; }
            height = value;
            return chart;
        };

        return chart;
    }
});
