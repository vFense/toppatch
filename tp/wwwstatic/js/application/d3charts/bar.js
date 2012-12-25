define(
    ['jquery', 'd3'],
    function ($, d3) {
        "use strict";
        return function () {
            var margin   = {top: 20, right: 20, bottom: 20, left: 20},
                barWidth = 70,
                width    = 370,
                height   = 200,
                title    = "Default",
                color = d3.scale.category20();
                //format   = d3.format(",.0f");

            function chart(selection) {
                selection.each(function (data) {
                    // generate chart here; `d` is the data and `this` is the element
                    if (barWidth > 100) {
                        barWidth = 100;
                    }
                    width = (barWidth + 10) * data.length;
                    var txt, txtMask, txtRect, defs, barDemo, mainGradient, shadow, gradients,
                        x = d3.scale.linear().domain([0, data.length]).range([15, width]),
                        y = d3.scale.linear().domain([0, d3.max(data, function (datum) { return datum.value; })]).rangeRound([0, height]),
                        that = this,
                        matches = (that.id || that.attr('id')).match(/\d+$/),
                        widget = "#widget" + matches[0];

                    //$(widget + "-title").html(title);
                    $(this).html("");
                    function getColor(data, index) {
                        return color(index);
                    }
                    // Helper function to extract a darker version of the color
                    function getDarkerColor(data, index) {
                        return d3.rgb(getColor(data, index)).darker();
                    }

                    barDemo = d3.select(this).
                            append("svg:svg").
                            attr("width", width).
                            attr("height", height + 20).
                            style("overflow", "visible");

                    defs = barDemo.append("svg:defs");

                    mainGradient = defs.append("svg:linearGradient")
                        .attr("gradientUnits", "userSpaceOnUse")
                        .attr('x1', 0).attr('y1', 100)
                        .attr('x2', 0).attr('y2', 10)
                        .attr("id", "mastgrad_bar3d");

                    shadow = defs.append("filter").attr("id", "shadow")
                        .attr("filterUnits", "userSpaceOnUse")
                        .attr("x", -1 * (width / 2)).attr("y", -1 * (height / 2))
                        .attr("width", width).attr("height", height);
                    shadow.append("feGaussianBlur")
                        .attr("in", "SourceAlpha")
                        .attr("stdDeviation", "4")
                        .attr("result", "blur");
                    shadow.append("feOffset")
                        .attr("in", "blur")
                        .attr("dx", "4").attr("dy", "4")
                        .attr("result", "offsetBlur");
                    shadow.append("feBlend")
                        .attr("in", "SourceGraphic")
                        .attr("in2", "offsetBlur")
                        .attr("mode", "normal");

                    gradients = defs.selectAll(".gradient").data(data, function (d) { return d; });
                    gradients.enter().append("svg:linearGradient")
                        .attr("id", function (d, i) { return "bargradient" + i; })
                        .attr("class", "gradient")
                        .attr('y1', height)
                        .attr('y2', function (d) { return y(d.value) > 15 ? height - y(d.value) + 15 : height - y(15); })
                        .attr("xlink:href", "#masterbar");

                    gradients.append("svg:stop").attr("offset", "0%").attr("stop-color", getColor);
                    gradients.append("svg:stop").attr("offset", "100%").attr("stop-color", getDarkerColor);

                    barDemo.selectAll("svg > rect")
                        .data(data)
                        .enter()
                        .append("svg:rect")
                        .attr("x", function (datum, index) { return x(index); })
                        .attr("y", function (datum) { return y(datum.value) > 15 ? height - y(datum.value) : height - y(15); })
                        .attr("height", function (datum) { return y(datum.value) > 15 ? y(datum.value) : y(15); })
                        .attr("width", barWidth)
                        .attr("stroke", "white")
                        .attr("fill", function (d, i) { return "url(#bargradient" + i + ")"; })
                        .on('mouseover', function (d) {
                            var mousePos = d3.mouse(this), textLength;
                            mousePos[0] = mousePos[0] + 5;
                            mousePos[1] = mousePos[1] + 5;
                            txt.text(d.label + ': ' + d.value + ' patches.');
                            textLength = txt.style('width');
                            txtMask.attr({transform: 'translate(' + mousePos + ')'});
                            txtRect.attr({width: parseFloat(textLength) + 2}).style('opacity', '0.3');
                        })
                        .on('mousemove', function (d) {
                            var mousePos = d3.mouse(this);
                            mousePos[0] = mousePos[0] + 5;
                            mousePos[1] = mousePos[1] + 5;
                            txtMask.attr({transform: 'translate(' + mousePos + ')'});
                            txtRect.style('opacity', '0.3');
                        })
                        .on('mouseout', function (d) {
                            txt.text('');
                            txtRect.style('opacity', '0');
                        });
                        //.append("svg:title").text(function (d) { return d.label + ": " + d.value; });

                    barDemo.selectAll("svg > text")
                        .data(data)
                        .enter()
                        .append("svg:text")
                        .attr("x", function (datum, index) { return x(index) + barWidth; })
                        .attr("y", function (datum) { return y(datum.value) > 15 ? height - y(datum.value) : height - y(15); })
                        .attr("dx", -barWidth / 2)
                        .attr("dy", "1.2em")
                        .attr("text-anchor", "middle")
                        .attr("style", "font-size: 10")
                        .text(function (datum) {
                            return datum.value;
                        })
                        .attr("fill", "white");

                    barDemo.selectAll("text.yAxis")
                        .data(data)
                        .enter().append("svg:text")
                        .attr("x", function (datum, index) { return x(index) + barWidth - barWidth / 6; })
                        .attr("y", height + 10)
                        .attr("dx", -barWidth / 2)
                        .attr("text-anchor", "middle")
                        .attr("style", "font-size: 10")
                        .text(function (datum) {
                            var label = datum.label.split(' '), osname = '', k;
                            if (label.length > 3) {
                                for (k = 0; k < label.length - 1; k += 1) {
                                    if (label[k] === 'Windows') {
                                        osname += label[k].substring(0, 3) + ' ';
                                    } else {
                                        osname += label[k] + ' ';
                                    }
                                }
                            } else {
                                osname = datum.label;
                            }
                            return osname;
                        })
                        .attr('transform', 'translate(15, 5)')
                        .attr("class", "yAxis");

                    txtMask = barDemo.append('g').attr({width: '100px', height: '30px'});

                    txtRect = txtMask.append('rect')
                        .attr({width: '100px', height: '30px', fill: 'lightblue', stroke: 'black'})
                        .style('opacity', '0');

                    txt = txtMask.append('text')
                        .attr({fill: 'black', dy: '18px'})
                        .style('font-size', '1.3em')
                        .text("");

                    /*barDemo.selectAll("rect")
                        .data(data)
                        .enter().append("svg:title")
                        .text(function (d) { console.log(d.label); return d.label + ": " + d.value; });*/
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

            chart.barWidth = function (value) {
                if (!arguments.length) { return barWidth; }
                barWidth = value;
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