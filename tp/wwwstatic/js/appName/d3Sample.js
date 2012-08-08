// D3 Charts
var d3_pie = function (data, domTarget, options) {
	var target = jQuery(domTarget || "body"),
		width = target.empty().width(),
		height = width,
		outerRadius = (width * 0.8) / 2,
		innerRadius = outerRadius * 0.7,
		color = d3.scale.category20(),
		donut = d3.layout.pie(),
		arc = d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius),
		vis, arcs, settings;
	
	settings = jQuery.extend({
		autoResize: true
	}, options);
	
	//target.css("height",width);
	
	vis = d3.select(domTarget)
		.append("svg")
			.data([data])
			.attr("width", width)
			.attr("height", height)
			.attr("preserveAspectRatio","xMinYMin meet")
			.attr("viewbox", "0 0 " + width + " " + height);
	
	arcs = vis.selectAll("g.arc")
		.data(donut)
		.enter().append("g")
			.attr("class", "arc")
			.attr("transform", "translate(" + (width / 2) + "," + (width / 2) + ")");
	
	arcs.append("path")
		.attr("fill", function(d, i) { return color(i); })
		.attr("d", arc);
	
	arcs.append("text")
		.attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
		.attr("dy", ".35em")
		.attr("text-anchor", "middle")
		.attr("display", function(d) { return d.value > 0.15 ? null : "none"; })
		.text(function(d, i) { return d.value; });
};