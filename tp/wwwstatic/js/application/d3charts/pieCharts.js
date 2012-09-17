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
            r = width / 3,
            color = d3.scale.category20(),
            title = "Default",
            graph = this;

        function chart(selection) {
            selection.each(function (data) {
                // generate chart here; `d` is the data and `this` is the element
                var that = this,
                    matches = that.id.match(/\d+$/),
                    widget = "#widget" + matches[0];
                $(widget + "-title").html(title);
                $(this).html("");
                //alert($(this).attr("id"));
                var vis = d3.select(this)
                    .append("svg:svg")              //create the SVG element inside the <body>
                    .data([data])                   //associate our data with the document
                    .attr("width", width)           //set the width and height of our visualization (these will be attributes of the <svg> tag
                    .attr("height", height)
                    .append("svg:g")                //make a group to hold our pie chart
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

                var arcs = vis.selectAll("g.slice")     //this selects all <g> elements with class slice (there aren't any yet)
                    .data(pie(data))                          //associate the generated pie data (an array of arcs, each having startAngle, endAngle and value properties)
                    .enter()                            //this will create <g> elements for every "extra" data element that should be associated with a selection. The result is creating a <g> for every object in the data array
                    .append("svg:g")                //create a group to hold each slice (we will have a <path> and a <text> element associated with each slice)
                    .attr("class", "slice")    //allow us to style things in the slices (like text)
                    .on("click", function (d, i) {
                        if(d.data.data) {
                            d3.selectAll(this.parentNode.childNodes).select("text").text("");
                            d3.selectAll(this.parentNode.childNodes).select("path").transition().duration(1000).attr("d", arcOut);
                            d3.selectAll(this.parentNode.childNodes).select("path").transition().delay(900)
                                .style("opacity", function() { newgraph(d); return "1"; });
                        }
                    })
                    .on("mouseover", function (d, i) {
                        //console.log(d3.select(this).select("path").transition().attr("fill", color(i + 2)));
                        d3.select(this).select("path").transition().duration(500)
                            .attr("fill", color(i + 2))
                            .attr("d", arcOver);
                        d3.select(this).select("text").transition().duration(500)
                            .attr("dy", ".35em")
                            .attr("text-anchor", "middle")
                            .style("font-size", "15px")
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
                function newgraph(d) {
                    var tempData = [];
                    if(d.data.data.length){
                        for(var i = 0; i < d.data.data.length; i++){
                            //console.log(d.data.data[i].children[0].graphData);
                            tempData.push(d.data.data[i].children[0].graphData);
                        }
                        var pieChart = graph.pieGraph().title(d.data.data[0].children[0].name + " nodes in " + d.data.data[0].os);
                        //console.log(pieChart);
                        d3.select(that).datum(tempData).call(pieChart);
                    }
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
                    .text(function (d) { return d.data.label; });

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
        }

        return chart;
    }
});