/**
 * Created with PyCharm.
 * User: sergio
 * Date: 9/7/12
 * Time: 2:38 PM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery','d3'], function($, d3) {
    return function () {
        "use strict";
        var n = 4, // number of layers
            m = 1,
            index = 0,
            tempBar, secondSet, previous, that, secondRect, label, lines,
            margin = 20,
            width = 560,
            height = 230 - .5 - margin,
            color = d3.scale.category20(),
            secondColor = d3.scale.category20b(),
            title = "Default",
            barExists = false;

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                $(this).html("");
                var that = this,
                    matches = that.id.match(/\d+$/),
                    widget = "#widget" + matches[0];
                $(widget + "-title").html(title);
                var x = d3.scale.ordinal().rangeRoundBands([0, width-50]),
                y = d3.scale.linear().range([0, height]);
                var y0 = [],
                    data_array = [];
                y0[0] = 0;
                data_array = data.map(function (dat, i) {
                    //console.log(dat);
                    var temp = [];
                    if(i === 0) {
                        y0.push(dat.value);
                    } else {
                        y0.push(y0[i] + dat.value);
                    }
                    temp.push({ x: 0, y: dat.value, y0: y0[i], label: dat.label });
                    return temp;
                });
                var stacked = d3.layout.stack()(data_array);
                x.domain(stacked[0].map(function(d) { return d.x; }));
                y.domain([0, d3.max(stacked[stacked.length - 1], function(d) { return d.y0 + d.y; })]);
                //console.log("------------------------------------------------------------------");
                var line = d3.svg.line()
                    .x(function (d) {
                        return d.x;
                    })
                    .y(function (d) {
                        return d.y;
                    });
                var svg = d3.select(this).append("svg:svg")
                    .attr("class", "hi")
                    .attr("width", width + 80)
                    .attr("height", height + 10)
                    .append("svg:g")
                    .attr("transform", "translate(5," + (height + 5) + ")");

                var valgroup = svg.selectAll("g.valgroup")
                    .data(stacked)
                    .enter().append("svg:g")
                    .attr("class", "valgroup")
                    .style("fill", function(d, i) { return color(i); })
                    .style("stroke", function(d, i) { return color(i); });//d3.rgb(z(i)).darker(); });

                // Add a rect for each date.
                var rect = valgroup.selectAll("rect")
                    .data(function(d){return d;})
                    .enter().append("svg:rect")
                    .attr("x", function(d) { return x(d.x); })
                    .attr("y", function(d) { return -y(d.y0) - y(d.y); })
                    .attr("height", function(d) { return y(d.y); })
                    .attr("width", x.rangeBand() / 4)
                    .on("click", function(d) {
                        if(barExists) {
                            tempBar.remove();
                            secondSet.remove();
                        }
                        if (that === this) {
                            label.transition().duration(350)
                                .attr("x", x.rangeBand() - x.rangeBand() / 8 + 10)
                                .attr("style",function(d) {
                                    if(x.rangeBand() / 4 > 100) {
                                        return "font-size: 1.2em";
                                    } else {
                                        var fontSize = x.rangeBand() / 4 / 65;
                                        return "font-size: " + fontSize + "em";
                                    }
                                });
                            lines.transition().duration(350).attr("opacity", 1);
                            that = false;
                        } else {
                            var secondData = [];
                            for(var k = 0; k < data.length; k++) {
                                if(data[k].label === d.label) {
                                    for(var j = 0; j < data[k].data.length; j++) {
                                        secondData.push(data[k].data[j].children[0].graphData);
                                    }
                                }
                            }
                            var secondy0 = [],
                                y2 = d3.scale.linear().range([0, height]);
                            secondy0[0] = 0;
                            var tempArray = secondData.map(function (dat, i) {
                                var temp = [];
                                if(i === 0) {
                                    secondy0.push(dat.value);
                                } else {
                                    secondy0.push(secondy0[i] + dat.values);
                                }
                                temp.push({ x: x.rangeBand() / 2.5, y: dat.value, y0: secondy0[i], label: dat.label });
                                return temp;
                            });
                            var secondStacked = d3.layout.stack()(tempArray);
                            y2.domain([0, d3.max(secondStacked[secondStacked.length-1], function (d) { return d.y0 + d.y; })])
                            var tempData = new Array();
                            tempData.push([d]);
                            //console.log(y0);
                            //console.log(-y0[y0.length-1]-y0[y0.length-2]);
                            tempBar = svg.selectAll('g.temp')
                                .data(tempData)
                                .enter()
                                .append("svg:g")
                                .attr("class", "temp")
                                .style("fill", $(this).parent().css("fill"))
                                .style("stroke", $(this).parent().css("fill"));
                            //console.log(y0[y0.length-1]+y0[y0.length-2]);
                            tempBar.selectAll("rect")
                                .data(function (d) { return d; })
                                .enter()
                                .append("svg:rect")
                                .attr("x", (x.rangeBand() / 4))
                                .attr("y",-height)
                                .attr("height", height)
                                .attr("width", 1 );

                            tempBar.selectAll("rect").transition().duration(500)
                                .attr("width", (x.rangeBand() / 4) + 10);

                            secondSet = svg.selectAll('g.secondset')
                                .data(secondStacked)
                                .enter().append("svg:g")
                                .attr("class", "secondset")
                                .style("fill", function(d, i) { return secondColor(i); })
                                .style("stroke", function(d, i) { return secondColor(i); });
                            secondRect = secondSet.selectAll("rect")
                                .data(function(d){ return d;})
                                .enter().append("svg:rect")
                                .style("opacity", 0)
                                .attr("x", function(d) { return (x.rangeBand() / 4) + 10; })
                                .attr("y", function(d) { return (-y2(d.y0) - y2(d.y)); })
                                .attr("height", function(d) { return y2(d.y); })
                                .attr("width", x.rangeBand() / 4);

                            secondRect.transition().delay(350).duration(250)
                                .style("opacity", 1);

                            var secondLabel = secondSet.filter(function (d) { return y2(d[0].y) > 25; })
                                .selectAll("text")
                                .data(function (d) { return d; })
                                .enter().append("svg:text")
                                .text(function (d) { return d.label })
                                .attr("x", function(d) { return x.rangeBand() - x.rangeBand() / 8 + 10; })
                                .attr("y", function(d) { return -y2(d.y0) - y2(d.y) / 2; })
                                .attr("opacity", 0)
                                .attr("style", function(d) {
                                    if(x.rangeBand() / 4 > 100) {
                                        return "font-size: 1.2em";
                                    } else {
                                        var fontSize = x.rangeBand() / 4 / 65;
                                        return "font-size: " + fontSize + "em";
                                    }
                                })
                                .attr("stroke", "none")
                                .attr("fill", "black");
                            secondLabel.transition().delay(350).duration(500)
                                .attr("opacity", 1);
                            var secondLine = secondSet.filter(function (d) { return y2(d[0].y) > 25; })
                                .selectAll("line")
                                .data(function(d) { return d; })
                                .enter().append("svg:path").transition().delay(350).duration(500)
                                .attr("class", "line")
                                .attr("fill", "black")
                                .attr("stroke", "black")
                                .attr("stroke-width", "2")
                                .attr("d", function (d) {
                                    var array = new Array();
                                    array[0] = { x: (x.rangeBand() / 2) + 20, y: -y2(d.y0) - y2(d.y) / 2 };
                                    array[1] = { x: x.rangeBand() - x.rangeBand() / 8, y: -y2(d.y0) - y2(d.y) / 2 };
                                    return line(array);
                                });
                            label.transition().duration(350).
                                attr("x", function(d) { return 5; }).
                                attr("style", function(d) {
                                    if(x.rangeBand() / 4 > 100) {
                                        return "font-size: 1.2em";
                                    } else {
                                        var fontSize = x.rangeBand() / 4 / 80;
                                        return "font-size: " + fontSize + "em";
                                    }
                                });
                            lines.transition().duration(100).attr("opacity", 0);
                            barExists = true;
                            that = this;
                        }
                    });
                label = valgroup.filter(function (d) { return y(d[0].y) > 25; })
                    .selectAll("text").
                    data(function(d){ return d; }).
                    enter().
                    append("svg:text").
                    text(function(d) {  return d.label; }).
                    attr("x", function(d) { return x.rangeBand() - x.rangeBand() / 8 + 10; }).
                    //attr("dx", "50").
                    attr("y", function(d) { return -y(d.y0) - y(d.y) / 2; }).
                    //attr("dy", "-40").
                    attr("style", function(d) {
                        if(x.rangeBand() / 4 > 100) {
                            return "font-size: 1.2em";
                        } else {
                            var fontSize = x.rangeBand() / 4 / 65;
                            return "font-size: " + fontSize + "em";
                        }
                    }).
                    attr("stroke", "none").
                    attr("fill", "black");

                lines = valgroup.filter(function (d) { return y(d[0].y) > 25; })
                    .selectAll("line")
                    .data(function(d) { return d; })
                    .enter()
                    .append("svg:path")
                    .attr("class", "line")
                    .attr("fill", "black")
                    .attr("stroke", "black")
                    .attr("stroke-width", "2")
                    .attr("d", function (d) {
                        var array = new Array();
                        array[0] = { x: x.rangeBand() / 4 + 10, y: -y(d.y0) - y(d.y) / 2 };
                        array[1] = { x: x.rangeBand() - x.rangeBand() / 8, y: -y(d.y0) - y(d.y) / 2 };
                        return line(array);
                    });
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
            if(!arguments.length) { return title; }
            title = value;
            return chart;
        };

        return chart;
    }
});