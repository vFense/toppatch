/**
 * Created with PyCharm.
 * User: sergio
 * Date: 9/7/12
 * Time: 2:38 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'd3'],
    function ($, d3) {
        "use strict";
        return function () {
            var tempBar, secondSet, secondRect, label, lines,
                svg, valgroup, rect,
                n = 4, // number of layers
                m = 1,
                margin = 20,
                width = 560,
                height = 230 - 0.5 - margin,
                color = d3.scale.category20(),
                secondColor = d3.scale.category20b(),
                title = "Default",
                barExists = false;

            function chart(selection) {
                selection.each(function (data) {
                    // generate chart here; `d` is the data and `this` is the element
                    $(this).html("");
                    var x, y, y2, stacked, line, data_array, secondStacked,
                        secondLabel, secondLine, txtMask, txtRect, txt,
                        y0 = [],
                        tempData = [],
                        that = this,
                        matches = that.id.match(/\d+$/),
                        widget = "#widget" + matches[0];
                    function textMouseOver(container, d) {
                        var mousePos = d3.mouse(container), textLength;
                        mousePos[0] = mousePos[0] - 10;
                        mousePos[1] = mousePos[1] - 38;
                        txt.text(d.label);
                        textLength = txt.style('width');
                        txtMask.attr({transform: 'translate(' + mousePos + ')'});
                        txtRect.attr({width: parseFloat(textLength) + 2}).style('opacity', '0.3');
                    }
                    function textMouseMove() {
                        var mousePos = d3.mouse(this);
                        mousePos[0] = mousePos[0] - 10;
                        mousePos[1] = mousePos[1] - 38;
                        txtMask.attr({transform: 'translate(' + mousePos + ')'});
                        txtRect.style('opacity', '0.3');
                    }
                    function textMouseOut() {
                        txt.text('');
                        txtRect.style('opacity', '0');
                    }
                    x = d3.scale.ordinal().rangeRoundBands([0, width - 50]);
                    y = d3.scale.linear().range([0, height]);
                    y0[0] = 0;
                    data_array = data.map(function (dat, i) {
                        //console.log(dat);
                        var temp = [];
                        if (i === 0) {
                            y0.push(dat.value);
                        } else {
                            y0.push(y0[i] + dat.value);
                        }
                        temp.push({ x: 0, y: dat.value, y0: y0[i], label: dat.label });
                        return temp;
                    });
                    stacked = d3.layout.stack()(data_array);
                    x.domain(stacked[0].map(function (d) { return d.x; }));
                    y.domain([0, d3.max(stacked[stacked.length - 1], function (d) { return d.y0 + d.y; })]);
                    line = d3.svg.line()
                        .x(function (d) {
                            return d.x;
                        })
                        .y(function (d) {
                            return d.y;
                        });

                    svg = d3.select(this).append("svg:svg")
                        .attr("class", "hi")
                        .attr("width", width + 80)
                        .attr("height", height + 10)
                        .append("svg:g")
                        .attr("transform", "translate(5," + (height + 5) + ")");

                    valgroup = svg.selectAll("g.valgroup")
                        .data(stacked)
                        .enter().append("svg:g")
                        .attr("class", "valgroup")
                        .style("fill", function (d, i) { return color(i); })
                        .style("stroke", function (d, i) { return color(i); });//d3.rgb(z(i)).darker(); });

                    rect = valgroup.selectAll("rect")
                        .data(function (d) { return d; })
                        .enter().append("svg:rect")
                        .attr("x", function (d) { return x(d.x); })
                        .attr("y", function (d) { return -y(d.y0) - y(d.y); })
                        .attr("height", function (d) { return y(d.y); })
                        .attr("width", x.rangeBand() / 4)
                        .on("click", function (d) {
                            var parent = $(this).parent();
                            if (barExists) {
                                tempBar.remove();
                                secondSet.remove();
                            }
                            if (that === this) {
                                label.transition().duration(350)
                                    .attr("x", x.rangeBand() - x.rangeBand() / 6 - 10)
                                    .attr("style", function (d) {
                                        if (x.rangeBand() / 4 > 100) {
                                            return "font-size: 1.2em";
                                        } else {
                                            var fontSize = x.rangeBand() / 4 / 65;
                                            return "font-size: " + fontSize + "em";
                                        }
                                    });
                                lines.transition().duration(350).attr("opacity", 1);
                                that = false;
                            } else {
                                $.getJSON("/api/osData/", {type: d.label}, function (json) {
                                    var json_array = json.map(function (dat, i) {
                                        var temp = [];
                                        if (i === 0) {
                                            y0.push(dat.value);
                                        } else {
                                            y0.push(y0[i] + dat.value);
                                        }
                                        temp.push({ x: 0, y: dat.value, y0: y0[i], label: dat.label });
                                        return temp;
                                    });
                                    y2 = d3.scale.linear().range([0, height]);
                                    secondStacked = d3.layout.stack()(json_array);
                                    y2.domain([0, d3.max(secondStacked[secondStacked.length - 1], function (d) { return d.y0 + d.y; })]);
                                    tempData.push([d]);
                                    tempBar = svg.selectAll('g.temp')
                                        .data(tempData)
                                        .enter()
                                        .append("svg:g")
                                        .attr("class", "temp")
                                        .style("fill", parent.css("fill"))
                                        .style("stroke", parent.css("fill"));
                                    tempBar.selectAll("rect")
                                        .data(function (d) { return d; })
                                        .enter()
                                        .append("svg:rect")
                                        .attr("x", (x.rangeBand() / 4))
                                        .attr("y", -height)
                                        .attr("height", height)
                                        .attr("width", 1);

                                    tempBar.selectAll("rect").transition().duration(500)
                                        .attr("width", (x.rangeBand() / 4) + 10);

                                    secondSet = svg.selectAll('g.secondset')
                                        .data(secondStacked)
                                        .enter().append("svg:g")
                                        .attr("class", "secondset")
                                        .style("fill", function (d, i) { return secondColor(i); })
                                        .style("stroke", function (d, i) { return secondColor(i); });
                                    secondRect = secondSet.selectAll("rect")
                                        .data(function (d) { return d; })
                                        .enter().append("svg:rect")
                                        .style("opacity", 0)
                                        .attr("x", function (d) { return (x.rangeBand() / 4) + 10; })
                                        .attr("y", function (d) { return (-y2(d.y0) - y2(d.y)); })
                                        .attr("height", function (d) { return y2(d.y); })
                                        .attr("width", x.rangeBand() / 4);

                                    secondRect.transition().delay(350).duration(250)
                                        .style("opacity", 1);

                                    secondLabel = secondSet.filter(function (d) { return y2(d[0].y) > 25; })
                                        .selectAll("text")
                                        .data(function (d) { return d; })
                                        .enter().append("svg:text")
                                        .text(function (d) { return d.label; })
                                        .attr("x", function (d) { return x.rangeBand() - x.rangeBand() / 8 + 10; })
                                        .attr("y", function (d) { return -y2(d.y0) - y2(d.y) / 2; })
                                        .attr("opacity", 0)
                                        .attr("style", function (d) {
                                            if (x.rangeBand() / 4 > 100) {
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
                                    secondLine = secondSet.filter(function (d) { return y2(d[0].y) > 25; })
                                        .selectAll("line")
                                        .data(function (d) { return d; })
                                        .enter().append("svg:path").transition().delay(350).duration(500)
                                        .attr("class", "line")
                                        .attr("fill", "black")
                                        .attr("stroke", "black")
                                        .attr("stroke-width", "2")
                                        .attr("d", function (d) {
                                            var array = [];
                                            array[0] = { x: (x.rangeBand() / 2) + 20, y: -y2(d.y0) - y2(d.y) / 2 };
                                            array[1] = { x: x.rangeBand() - x.rangeBand() / 8, y: -y2(d.y0) - y2(d.y) / 2 };
                                            return line(array);
                                        });
                                    label.transition().duration(350).
                                        attr("x", function (d) { return 5; }).
                                        attr("style", function (d) {
                                            if (x.rangeBand() / 4 > 100) {
                                                return "font-size: 1.2em";
                                            } else {
                                                var fontSize = x.rangeBand() / 4 / 80;
                                                return "font-size: " + fontSize + "em";
                                            }
                                        });
                                    lines.transition().duration(100).attr("opacity", 0);
                                    barExists = true;
                                });
                                that = this;
                            }
                        })
                        .on('mouseover', function (d) {
                            textMouseOver(this, d);
                        })
                        .on('mousemove', textMouseMove)
                        .on('mouseout', textMouseOut);
                    label = valgroup.filter(function (d) { return y(d[0].y) > 25; })
                        .selectAll("text").
                        data(function (d) { return d; }).
                        enter().
                        append("svg:text").
                        text(function (d) {
                            var label = d.label.length > 15 ? d.label.substr(0, 15) : d.label;
                            return label;
                        }).
                        attr("x", function (d) { return x.rangeBand() - x.rangeBand() / 6 - 10; }).
                        //attr("dx", "50").
                        attr("y", function (d) { return -y(d.y0) - y(d.y) / 2; }).
                        //attr("dy", "-40").
                        attr("style", function (d) {
                            if (x.rangeBand() / 4 > 100) {
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
                        .data(function (d) { return d; })
                        .enter()
                        .append("svg:path")
                        .attr("class", "line")
                        .attr("fill", "black")
                        .attr("stroke", "black")
                        .attr("stroke-width", "2")
                        .attr("d", function (d) {
                            var array = [];
                            array[0] = { x: x.rangeBand() / 4 + 10, y: -y(d.y0) - y(d.y) / 2 };
                            array[1] = { x: x.rangeBand() - x.rangeBand() / 4, y: -y(d.y0) - y(d.y) / 2 };
                            return line(array);
                        });
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
    }
);