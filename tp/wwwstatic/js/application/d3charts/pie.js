/**
 * Created with PyCharm.
 * User: parallels
 * Date: 8/26/12
 * Time: 9:27 AM
 * To change this template use File | Settings | File Templates.
 */
define(['jquery','d3'], function($, d3) {

    return function () {
        "use strict";
        var width	= 280,	// Golden Ratio 1000/Phi
            height	= 220,
            r = (width / 3),
            color = d3.scale.category20(),
            title = "Default",
            previousTitle = '',
            previousData = [],
            osData = [],
            graph = this;

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var that = this, link, options,
                    matches = that.id.match(/\d+$/),
                    widget = "#widget" + matches[0];
                //$(widget + "-title").html(title);
                $(this).html("");
                //alert($(this).attr("id"));
                var vis = d3.select(this)
                    .append("svg:svg")              //create the SVG element inside the <body>
                    .data([data])                   //associate our data with the document
                    .attr("width", width)           //set the width and height of our visualization (these will be attributes of the <svg> tag
                    .attr("height", height);
                if(previousData.length != 0) {
                    renderLinks();
                }
                var warning = vis.selectAll('warning')
                    .data(['warning']).enter()
                    .append('svg:text')
                    .attr('x', (width / 4) - 40)
                    .attr('y', height / 2)
                    .style('font-size', '2em')
                    .style('opacity', '0')
                    .text('');

                var container = vis.append("svg:g")                //make a group to hold our pie chart
                    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");  //move the center of the pie chart from 0, 0 to radius, radius

                var arc = d3.svg.arc()              //this will create <path> elements for us using arc data
                    .innerRadius(0)
                    .outerRadius(r);

                var arcOver = d3.svg.arc()
                    .outerRadius(r + 10);
                var arcOut = d3.svg.arc()
                    .outerRadius(1);
                var pie = d3.layout.pie().sort(null)          //this will create arc data for us given a list of values
                    .value(function (d) { return d.value; });    //we must tell it out to access the value of each element in our data array

                var arcs = container.selectAll("g.slice")     //this selects all <g> elements with class slice (there aren't any yet)
                    .data(pie(data))                          //associate the generated pie data (an array of arcs, each having startAngle, endAngle and value properties)
                    .enter()                            //this will create <g> elements for every "extra" data element that should be associated with a selection. The result is creating a <g> for every object in the data array
                    .append("svg:g")                //create a group to hold each slice (we will have a <path> and a <text> element associated with each slice)
                    .attr("class", "slice")    //allow us to style things in the slices (like text)
                    .on("click", function (d, i) {
                        if(d.data.data) {
                            osData = d;
                            disappear('new', d.data.label);
                        }
                    })
                    .on("mouseover", function (d, i) {
                        //console.log(d3.select(this).select("path").transition().attr("fill", color(i + 2)));
                        d3.select(this).select("path").transition().duration(500)
                            //.attr("fill", color(i + 2))
                            .attr("d", arcOver);
                        d3.select(this).select("text").transition().duration(500)
                            .attr("dy", ".35em")
                            .attr("text-anchor", "middle")
                            //.style("font-size", "15px")
                            .style("fill", function () {
                                return "black";
                            })
                            .attr("transform", function(d) {
                                var c = arc.centroid(d),
                                    x = c[0],
                                    y = c[1],
                                    labelr = r / 1.6,
                                // pythagorean theorem for hypotenuse
                                    h = Math.sqrt(x * x + y * y);
                                return "translate(" + (x / h * labelr) + ',' + (y / h * labelr) +  ") rotate(" + angle(d) + ")";
                            })
                            //.attr("transform", "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")")
                            .text(d.data.label);
                    })
                    .on("mouseout", function (d, i) {
                        d3.select(this).select("path").transition()
                            .duration(500)
                            .attr("fill", color(i))
                            .attr("d", arc);
                        d3.select(this).select("text").transition().duration(500)
                            .attr("dy", ".35em")
                            .attr("text-anchor", "middle")
                            .style("font-size", "10px")
                            .style("fill", "black")
                            .attr("transform", "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")")
                            .text(d.data.label);
                    });
                function linkMouseOver(el) {
                    $(el).css('text-decoration', 'underline');
                }
                function linkMouseOut(el) {
                    $(el).css('text-decoration', 'none');
                }
                function disappear(string, type) {
                    arcs.select("text").style('opacity', 0);
                    arcs.select("path").transition().duration(1000).attr("d", arcOut);
                    arcs.select("path").transition().delay(900)
                        .style("opacity", function(d2, i) {
                            if(i === 0) {
                                string === 'previous' ? previousGraph() : newGraph(type);
                            }
                            return "1";
                        });
                }
                function newGraph(type) {
                    var tempData = [], position;
                    $.getJSON("/api/osData/", {type: type}, function(json) {
                        data = previousData.length != 0 ? json : data;
                        title = previousTitle != '' ? previousTitle : title;
                        var pieChart = graph.pie().title(type + " Patch Statistics").previousData(data).previousTitle(title).width(width).osData(osData);
                        if(json[0]['error']) {
                            previousData.length != 0 ? '' : renderLinks();
                            warning.style('opacity', '1').text('No data to display for ' + type + ' Patches');
                            $(widget + "-title").html('No Data Available');
                            arcs.remove();
                        } else {
                            d3.select(that).datum(json).call(pieChart);
                        }
                    });
                }
                function previousGraph() {
                    var tempData, tempTitle;
                    tempData = previousData.length != 0 ? previousData : data;
                    tempTitle = previousTitle != '' ? previousTitle : title;
                    var pieChart = graph.pie().title(tempTitle).width(width);
                    d3.select(that).datum(tempData).call(pieChart);
                }
                function renderLinks() {
                    link = vis.selectAll('link')
                        .data(['Back'])
                        .enter()
                        .append("svg:text")
                        .attr('x', 8)
                        .attr('y', 10)
                        .attr('fill', 'blue')
                        .style('pointer-events', 'all')
                        .text(function(d){ return d; })
                        .on('mouseover', function () { linkMouseOver(this); })
                        .on('mouseout', function () { linkMouseOut(this); })
                        .on("click", function (d) { disappear('previous', 'None') });
                }
                arcs.append("svg:title")
                    .text(function (d, i) { return d.data.label + ": " + d.data.value; });
                arcs.append("svg:path")
                    .attr("fill", function (d, i) { return color(i); }) //set the color for each slice to be chosen from the color function defined above
                    .attr("d", arc);                                    //this creates the actual SVG path using the associated data (pie) with the arc drawing function
                arcs.filter(function (d) { return d.endAngle - d.startAngle > .2; })
                    .append("svg:text")
                    .attr("dy", ".35em")
                    .attr("text-anchor", "middle")
                    .attr("transform", function (d) { return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")"; })
                    .text(function (d) {
                        var label = d.data.label.split(' '), osname = '';
                        if (label.length > 3) {
                            for(var k = 0; k < label.length -1; k++) {
                                if (label[k] == 'Windows') {
                                    osname += label[k].substring(0, 3) + ' ';
                                } else {
                                    osname+= label[k] + ' ';
                                }
                            }
                        } else {
                            osname = d.data.label;
                        }
                        return osname;
                    });

                // Computes the label angle of an arc, converting from radians to degrees.
                function angle(d) {
                    var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
                    return a > 90 ? a - 180 : a;
                }

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
        chart.title = function (value) {
            if(!arguments.length) { return title; }
            title = value;
            return chart;
        };
        chart.previousData = function (value) {
            if(!arguments.length) { return previousData; }
            previousData = value;
            return chart;
        };
        chart.previousTitle = function (value) {
            if(!arguments.length) { return previousTitle; }
            previousTitle = value;
            return chart;
        };
        chart.osData = function (value) {
            if(!arguments.length) { return osData; }
            osData = value;
            return chart;
        };

        return chart;
    }
});