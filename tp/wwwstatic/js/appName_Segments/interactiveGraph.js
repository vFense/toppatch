/**
 * Created with PyCharm.
 * User: sergio
 * Date: 9/7/12
 * Time: 5:59 PM
 * To change this template use File | Settings | File Templates.
 */
$application.interactiveGraph = function () {
    "use strict";
    var title = 'Summary',
        w = 500,
        h = 220;


    function chart(selection) {
        selection.each(function (root, i) {
            var that = this,
                matches = that.id.match(/\d+$/),
                widget = "#widget" + matches[0];
            $(widget + "-title").html(title);
            $(this).html("");
            w = $(this).width();
            var x = d3.scale.linear().range([0, w]),
                y = d3.scale.linear().range([0, h]);
            var vis = d3.select(this)
                .append("svg:svg")
                .attr("width", w)
                .attr("height", h);

            var partition = d3.layout.partition()
                .value(function(d) { return d.size; });
            //d3.json("flare.json", function(root) {
            var g = vis.selectAll("g")
                .data(partition.nodes(root))
                .enter().append("svg:g")
                .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; })
                .on("click", click);
            var kx = w / root.dx,
                ky = h / 1;
            g.append("svg:rect")
                .attr("width", root.dy * kx)
                .attr("height", function(d) { return d.dx * ky; })
                .attr("class", function(d) { return d.children ? "tree parent" : "tree child"; });

            g.append("svg:text")
                .attr("transform", transform)
                .attr("dy", ".35em")
                .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
                .text(function(d) { return d.size ? d.name + ": " + d.size : d.name; })

            d3.select(window)
                .on("click", function() { click(root); })

            function click(d) {
                if (!d.children) return;

                kx = (d.y ? w - 40 : w) / (1 - d.y);
                ky = h / d.dx;
                x.domain([d.y, 1]).range([d.y ? 40 : 0, w]);
                y.domain([d.x, d.x + d.dx]);

                var t = g.transition()
                    .duration(d3.event.altKey ? 7500 : 750)
                    .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; });

                t.select("rect")
                    .attr("width", d.dy * kx)
                    .attr("height", function(d) { return d.dx * ky; });

                t.select("text")
                    .attr("transform", transform)
                    .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });

                d3.event.stopPropagation();
            }

            function transform(d) {

                return "translate(8," + d.dx * ky / 2 + ")";
            }
            //});

        });
    }
    chart.title = function (value) {
        if(!arguments.length) { return title; }
        title = value;
        return chart;
    };

    return chart;
};
