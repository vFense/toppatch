$appName.horizontalBarChart = function () {
	"use strict";
	var margin	= {top: 20, right: 20, bottom: 20, left: 20},
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

	return chart;
};