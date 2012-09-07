$application.generateTable = function () {
	"use strict";
	var headerRow = false,
		headerCol = false,
		key = null,
		sort = null,
		style = "table";

	function table(selection) {
		selection.each(function (data) {
			var parentElement = d3.select(this),
				typeOfFirstElement,
				error = false;


			// Validate matching data
			jQuery.each(data, function (k, v) {
				if (!typeOfFirstElement) {
					typeOfFirstElement = jQuery.type(v);
				} else if (typeOfFirstElement !== jQuery.type(v)) {
					error = true;
					return false;
				}
			});
			if (error) {
				if (style === "table") {
					if (!jQuery(parentElement).is("table")) { parentElement = parentElement.append("table"); }
					parentElement.append("tbody").append("tr").append("td").attr("class", "error")
						.text("Data parse error. Expected array of arrays, or array of objects. Found an array mixed with both arrays and objects.");
				} else {
					parentElement.append("div").attr("class", "error")
						.text("Data parse error. Expected array of arrays, or array of objects. Found an array mixed with both arrays and objects.");
				}
				return;
			}

			// Render header row
			if (headerRow) {
				parentElement.append("thead")
					.append("tr")
					.selectAll("td")
					.data(function (data) {
						if (jQuery.isArray(data[0])) { return data[0]; }
						var temp = [];
						jQuery.each(data[0], function (k, v) {
							temp[temp.length] = k;
						});
						return temp;
					})
					.enter()
					.append("th")
					.attr("scope", "colgroup")
					.text(function (d) { return d; });
			}

			parentElement.append("tbody")
				.selectAll("tr")
				.data(data)
				.enter()
				.append("tr")
				.selectAll("td")
				.data(function (data) {
					var temp = [], i, len;
					if (jQuery.isArray(data[0])) {
						for (i = 1, len = data.length; i < len; i += 1) {
							temp[temp.length] = data[i];
						}
					} else {
						jQuery.each(data, function (k, v) {
							temp[temp.length] = v;
						});
					}
					return temp;
				})
				.enter()
				.append("td")
				.text(function (d) { return d; });
		});
	}

	table.headerRow = function (value) {
		if (!arguments.length) { return headerRow; }
		headerRow = value;
		return table;
	};

	table.headerCol = function (value) {
		if (!arguments.length) { return headerCol; }
		headerCol = value;
		return table;
	};

	table.style = function (value) {
		if (!arguments.length) { return style; }
		var lValue = value.toLowerCase();
		if (lValue === "table" || lValue === "div") {
			style = lValue;
		} else {
			throw 'Invalid table style. Expected "table" or "div"';
		}
		return table;
	};

	table.sort = function (value) {
		if (!arguments.length) { return sort; }
		headerCol = sort;
		return table;
	};

	return table;
};