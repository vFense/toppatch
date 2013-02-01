/**
 * Created with PyCharm.
 * User: parallels
 * Date: 12/19/12
 * Time: 2:17 AM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery', 'd3'], function ($, d3) {
    "use strict";
    return function () {
        var width	= 280,	// Golden Ratio 1000/Phi
            height	= 220,
            r = (width / 3),
            colors = d3.scale.category20(),
            severityColors = ['#FFC125', '#FF3030', '#FF6600'];

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var gradients, _current, slice, paths, labels, txtMask, txtRect, txt, x, y,
                    that = this,
                    matches = that.id.match(/\d+$/),
                    widget = "#widget" + matches[0],
                    svg = d3.select(this).html('').append("svg").attr("width", width).attr("height", height).style('overflow', 'visible'),
                    defs = svg.append("svg:defs"),
                    pieChart = d3.layout.pie().sort(null).value(function (d) { return d.value; }),
                    arc = d3.svg.arc().innerRadius(0).outerRadius(r),
                // Declare a main gradient with the dimensions for all gradient entries to refer
                    mainGrad = defs.append("svg:radialGradient")
                    .attr("gradientUnits", "userSpaceOnUse")
                    .attr("cx", 0).attr("cy", 0).attr("r", r).attr("fx", 0).attr("fy", 0)
                    .attr("id", "master"),
                // The pie sectors container
                    arcGroup = svg.append("svg:g")
                    .style('width', width)
                    .style('height', height)
                    .attr("class", "arcGroup")
                    //.attr("filter", "url(#shadow)")
                    .attr("transform", "translate(" + (width / 2) + "," + (height / 2) + ")"),
                // Header text
                    //header = svg.append("text").text("Parent")
                    //.attr("transform", "translate(10, 20)").attr("class", "header"),
                // Declare shadow filter
                    shadow = defs.append("filter").attr("id", "shadow")
                    .attr("filterUnits", "userSpaceOnUse")
                    .attr("x", -1 * (width / 2)).attr("y", -1 * (height / 2))
                    .attr("width", width).attr("height", height);
                function angle(d) {
                    var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
                    return a > 90 ? a - 180 : a;
                }
                // "Fold" pie sectors by tweening its current start/end angles
                // into 2*PI
                function tweenOut(data) {
                    data.startAngle = data.endAngle = (2 * Math.PI);
                    var interpolation = d3.interpolate(_current, data);
                    _current = interpolation(0);
                    return function (t) {
                        return arc(interpolation(t));
                    };
                }
                // "Unfold" pie sectors by tweening its start/end angles
                // from 0 into their final calculated values
                function tweenIn(data) {
                    var interpolation = d3.interpolate({startAngle: 0, endAngle: 0}, data);
                    _current = interpolation(0);
                    return function (t) {
                        return arc(interpolation(t));
                    };
                }
                // Helper function to extract color from data object
                function getColor(data, index) {
                    return colors(index);//index <= 2 ? d3.rgb(severityColors[index]).brighter() : colors(index);
                }
                // Helper function to extract a darker version of the color
                function getDarkerColor(data, index) {
                    return d3.rgb(getColor(data, index)).darker();
                }
                function textMouseOver(d) {
                    var mousePos = d3.mouse(that), textLength;
                    mousePos[0] = mousePos[0] - 10;
                    mousePos[1] = mousePos[1] - 38;
                    txt.text(d.data.label + ": " + d.data.value + ' nodes.');
                    textLength = txt.style('width');
                    txtMask.attr({transform: 'translate(' + mousePos + ')'});
                    txtRect.attr({width: parseFloat(textLength) + 20}).style('opacity', '0.3');
                }
                function textMouseMove() {
                    var mousePos = d3.mouse(that);
                    mousePos[0] = mousePos[0] - 10;
                    mousePos[1] = mousePos[1] - 38;
                    txtMask.attr({transform: 'translate(' + mousePos + ')'});
                    txtRect.style('opacity', '0.3');
                }
                function textMouseOut() {
                    txtMask.attr({transform: 'translate(' + width + ', ' + height + ')'});
                    txt.text('');
                    txtRect.style('opacity', '0');
                }
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
                // Create a gradient for each entry (each entry identified by its unique category)
                gradients = defs.selectAll(".gradient").data(data, function (d) { return d.label; });
                gradients.enter().append("svg:radialGradient")
                    .attr("id", function (d, i) { return "gradient" + i; })
                    .attr("class", "gradient")
                    .attr("xlink:href", "#master");

                gradients.append("svg:stop").attr("offset", "0%").attr("stop-color", getColor);
                gradients.append("svg:stop").attr("offset", "90%").attr("stop-color", getColor);
                gradients.append("svg:stop").attr("offset", "100%").attr("stop-color", getDarkerColor);

                // Create a sector for each entry in the enter selection
                slice = arcGroup.selectAll('g.slice')
                    .data(pieChart(data)).enter().append('svg:g').attr('class', 'slice');
                paths = slice.append("svg:path").attr("class", "sector");
                    //.data(pieChart(currData), function (d) { return d.data.label; }),
                labels = slice.append("svg:text");

                //paths.enter().append("svg:path").attr("class", "sector");

                //labels.enter().append("svg:text").attr("class", "label");

                // Each sector will refer to its gradient fill
                paths.attr("fill", function (d, i) { return "url(#gradient" + i + ")"; })
                    .transition().duration(1000).attrTween("d", tweenIn).each("end", function () {
                        this._listenToEvents = true;
                    });

                txtMask = svg.append('g').attr({width: '100px', height: '30px'});

                txtRect = txtMask.append('rect')
                    .attr({width: '100px', height: '30px', fill: 'lightblue', stroke: 'black', 'rx': '6', 'ry': '6'})
                    .style('opacity', '0');

                txt = txtMask.append('text')
                    .attr({fill: 'black', dy: '18px'})
                    .style('font-size', '1.3em')
                    .text("");

                // Mouse interaction handling
                paths.on("click", function (d) {
                    window.location.hash = '#nodes?by_os=' + d.data.label;
                })
                    .on("mouseover", function (d) {
                        var ang;
                        textMouseOver(d);
                        // Mouseover effect if no transition has started
                        if (this._listenToEvents) {
                            // Calculate angle bisector
                            ang = d.startAngle + (d.endAngle - d.startAngle) / 2;
                            // Transformate to SVG space
                            ang = (ang - (Math.PI / 2)) * -1;
                            // Calculate a 10% radius displacement
                            x = Math.cos(ang) * r * 0.1;
                            y = Math.sin(ang) * r * -0.1;

                            d3.select(this).transition()
                                .duration(300).attr("transform", "translate(" + x + "," + y + ")");
                            d3.select(this.parentNode).select("text").transition().duration(300)
                                .attr("transform", function (data) {
                                    var c = arc.centroid(d),
                                        x = c[0],
                                        y = c[1],
                                        labelr = r / 1.6,
                                    // pythagorean theorem for hypotenuse
                                        h = Math.sqrt(x * x + y * y);
                                    return "translate(" + (x / h * labelr) + ',' + (y / h * labelr) +  ") rotate(" + angle(d) + ")";
                                });
                        }
                    })
                    .on('mousemove', textMouseMove)
                    .on("mouseout", function (d) {
                        // Mouseout effect if no transition has started
                        textMouseOut();
                        if (this._listenToEvents) {
                            d3.select(this).transition()
                                .duration(0).attr("transform", "translate(0,0)");
                            d3.select(this.parentNode).select("text").transition().duration(0)
                                .attr("transform", "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")");
                        }
                    });
                labels.filter(function (d) { return d.endAngle - d.startAngle > 0.2; })
                    .attr("dy", ".35em")
                    .style("font-size", "10px")
                    .style("font-family", "Arial")
                    .attr("text-anchor", "middle")
                    .attr("transform", function (d) { return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")"; })
                    .text(function (d) {
                        var osname = d.data.label.substr(0, 10) + ' - ' + Math.floor((d.endAngle - d.startAngle) / (2 * Math.PI) * 100) + '%';
                        return osname;
                    });
                /*
                // Collapse sectors for the exit selection
                slice.exit().transition()
                    .duration(1000)
                    .attrTween("d", tweenOut).remove();
                    */

                /*
                function findChildenByCat(cat) {
                    var i;
                    for (i = -1; i++ < data.length - 1;) {
                        if (data[i].cat == cat){
                            return data[i].children;
                        }
                    }
                    return data;
                }
                */
            });
        }
        chart.r = function (value) {
            if (!arguments.length) { return r; }
            r = value;
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

        return chart;
    };
});