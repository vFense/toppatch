$application.horizontalBarChart = function () {
	"use strict";
	var margin	= {top: 20, right: 20, bottom: 20, left: 20},
        barWidth = 70,
		width	= 618,	// Golden Ratio 1000/Phi
		height	= 1000,
		format	= d3.format(",.0f"),
		xScale	= d3.scale.linear().range([0, width]),
		yScale	= d3.scale.ordinal().rangeRoundBands([0, height], 0.1),
		xAxis	= d3.svg.axis().scale(xScale).orient("top").tickSize(-6, 0),
		yAxis	= d3.svg.axis().scale(yScale).orient("left").tickSize(0);

	function chart(selection) {
		selection.each(function (d, i) {
			// generate chart here; `d` is the data and `this` is the element

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

	return chart;
};
$application.verticalBarChart = function () {
    "use strict";
    var margin	= {top: 20, right: 20, bottom: 20, left: 20},
        barWidth = 70,
        width	= 400,	// Golden Ratio 1000/Phi
        height	= 200,
        title = "Default",
        format	= d3.format(",.0f");
    /*
        xScale	= d3.scale.linear().range([0, width]),
        yScale	= d3.scale.ordinal().rangeRoundBands([0, height], 0.1),
        xAxis	= d3.svg.axis().scale(xScale).orient("top").tickSize(-6, 0),
        yAxis	= d3.svg.axis().scale(yScale).orient("left").tickSize(0); */

    function chart(selection) {
        selection.each(function (data) {
            // generate chart here; `d` is the data and `this` is the element
            width = (barWidth + 10) * data.length;
            var x = d3.scale.linear().domain([0, data.length]).range([0, width]),
                y = d3.scale.linear().domain([0, d3.max(data, function(datum) { return datum.value; })]).rangeRound([0, height]),
                that = this,
                matches = that.id.match(/\d+$/),
                widget = "#widget" + matches[0];
            $(widget + "-title").html(title);
            $(this).html("");

            var barDemo = d3.select(this).
                append("svg:svg").
                attr("width", width).
                attr("height", height+20);

            barDemo.selectAll("rect").
                data(data).
                enter().
                append("svg:rect").
                attr("x", function(datum, index) { return x(index); }).
                attr("y", function(datum) { return height - y(datum.value); }).
                attr("height", function(datum) { return y(datum.value); }).
                attr("width", barWidth).
                attr("fill", "#2d578b").
                append("svg:title").text(function (d) { console.log(d.label); return d.label + ": " + d.value; });

            barDemo.selectAll("text").
                data(data).
                enter().
                append("svg:text").
                attr("x", function(datum, index) { return x(index) + barWidth; }).
                attr("y", function(datum) { return height - y(datum.value); }).
                attr("dx", -barWidth/2).
                attr("dy", "1.2em").
                attr("text-anchor", "middle").
                attr("style", "font-size: 10").
                text(function(datum) { return datum.value;}).
                attr("fill", "white");

            barDemo.selectAll("text.yAxis")
                .data(data)
                .enter().append("svg:text")
                .attr("x", function(datum, index) { return x(index) + barWidth - barWidth/4; })
                .attr("y", height+10)
                .attr("dx", -barWidth/2)
                .attr("text-anchor", "middle")
                .attr("style", "font-size: 10")
                .text(function(datum) { return datum.label;})
                .attr('transform', 'translate(15, 5)')
                .attr("class", "yAxis");

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
        if(!arguments.length) { return title; }
        title = value;
        return chart;
    };

    return chart;
};