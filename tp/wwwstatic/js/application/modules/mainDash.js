define(
    ['jquery', 'backbone', 'd3', 'app', 'text!templates/testBody.html', 'modules/overview', 'jquery.ui.Sortable' ],
    function ($, Backbone, d3, app, myTemplate, Overview) {
        "use strict";
        var Properties = Backbone.Model.extend({
            defaults: {
                widgetName: "widget1",
                currentWidget: "existing",
                widgetType: "graph",
                widgetTitle: "Default"
            },
            initialize: function () {}
        });
        var properties = new Properties();

        var WidgetView = Backbone.View.extend({
            initialize: function () {
                'use strict';
                this.widget = "widget1";
                this.type = "graph";
                this.current = "new";
                this.sizeval = "3";
                this.classType = ["info", "success", "warning", "error"];
                this.counter = 4;
                this.graphType = 'pie';
                this.graph = '#graph1';
                this.graphData = 'os';
                this.template = "";
                this.title = "Default";
                this.myClass = "span";
                this.tempData = "";
                this.title = "Default";
            },
            events: {
                'click #type1': 'graphSetting',
                'click #type2': 'textSetting',
                'click #apply': 'generate',
                'click #graphtype1': 'pieData',
                'click #graphtype2': 'otherData',
                'click #graphtype3': 'otherData',
                'click #graphtype4': 'otherData'
            },
            pieData: function () {
                $("#dataToGraph").show();
            },
            otherData: function () {
                $("#dataToGraph").hide();
            },
            generate: function () {
                $("#widgetProperties").modal('hide');
                this.render();
            },
            graphSetting: function () {
                $("#graphSettings").show();
                $("#textSettings").hide();
            },
            textSetting: function () {
                $("#graphSettings").hide();
                $("#textSettings").show();
            },
            displayChart: function () {
                if (this.graphType === "pie") {
                    pieGraph(this.graph);
                } else if (this.graphType === "bar") {
                    barGraph(this.graph);
                } else if (this.graphType === "line") {
                    lineGraph(this.graph);
                } else if (this.graphType === "time") {
                    cubismGraph(this.graph);
                } else if (this.graphType === "stacked") {
                    stackedGraph(this.graph);
                } else if (this.graphType === "summary") {
                    console.log(this.graphType)
                    interactiveGraph(this.graph);
                }
            },
            render: function () {
                'use strict';
                this.current = properties.get("currentWidget");
                this.type = $('input:radio[name=type]:checked').val();
                this.title = $('#title').val() === "" ? "Default" : $('#title').val();
                properties.set({ widgetTitle: this.title });
                if (this.current === "new") {
                    this.renderNew();
                } else {
                    this.renderExisting();
                }
            },
            renderNew: function() {
                var variables, index;
                this.widget = "widget" + this.counter;
                if (this.type === "graph") {
                    this.sizeval = $('input:radio[name=radio]:checked').val();
                    variables = {
                        widget: this.widget,
                        span: "span" + this.sizeval,
                        graphcontainer: "graphcontainer" + this.counter,
                        menu: "menu" + this.counter,
                        graph: "graph" + this.counter
                    };
                    this.graphType = $('input:radio[name=graph]:checked').val();
                    // Compile the template using underscore
                    this.template = _.template($("#widget_template").html(), variables);
                    // Load the compiled HTML into the Backbone "el"
                    $("#insert").append(this.template);
                    this.graphData = $('input:radio[name=graphdata]:checked').val();
                    this.graph = "#" + $("#" + this.widget).children().children("div").attr("id");
                    this.counter += 1;
                    this.displayChart();
                    $(".properties").click(function () { setProperties(this, 'existing'); });
                    $('.remove').click(function () { hideWidget(this); });
                } else {
                    this.sizeval = "3";
                    this.title = $('input:radio[name=param]:checked');
                    index =  $("input:radio[name='param']").index(this.title);
                    this.tempData = this.getOverviewData();
                    variables = {
                        widget: this.widget,
                        span: "span" + this.sizeval,
                        type: this.classType[index],
                        title: this.title.val(),
                        data: this.tempData
                    };
                    this.template = _.template($("#text_template").html(), variables);
                    $("#insert").append(this.template);
                    this.counter += 1;
                }
            },
            renderExisting: function() {
                var variables, index, parent;
                this.widget = "#" + properties.get("widgetName");
                if (this.type === "graph") {
                    this.myClass = $(this.widget).attr("class");
                    this.sizeval = $('input:radio[name=radio]:checked').val();
                    this.graphType = $('input:radio[name=graph]:checked').val();
                    this.graph = "#" + $(this.widget).children().children("div").attr("id");
                    this.graphData = $('input:radio[name=graphdata]:checked').val();
                    $(this.widget).removeClass(this.myClass);
                    $(this.widget).addClass("span" + this.sizeval + " widget");
                    this.displayChart();
                } else {
                    parent = $(this.widget).parent();
                    this.title = $('input:radio[name=param]:checked');
                    index =  $("input:radio[name='param']").index(this.title);
                    this.tempData = this.getOverviewData();
                    this.sizeval = "3";
                    variables = {
                        widget: this.widget,
                        span: "span" + this.sizeval,
                        title: this.title.val(),
                        type: this.classType[index],
                        data: this.tempData
                    };
                    this.template = _.template($("#text_template").html(), variables);
                    $(this.widget).remove();
                    $(parent).append(this.template);
                }
            },
            getOverviewData: function() {
                var type = $(this.title).val();
                console.log(type);
                if(type === "Patched") {
                    return app.data.nodeData.Patched;
                } else if(type === "Scheduled Patches") {
                    return app.data.nodeData.Unpatched;
                } else if(type === "Nodes") {
                    return app.data.nodeData.Nodes;
                } else if(type === "Failed Patches") {
                    return app.data.nodeData.Failed;
                }
            }
        });
        var widgetview = new WidgetView({ el: 'body' });

        function barGraph(selection) {
            var data = app.data.osData,
                title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                width = $(selection).width(),
                barWidth = (width / data.length ) - 10;
            var graphBar = app.chart.barGraph().title(title).barWidth(barWidth);
            d3.select(selection).datum(data).call(graphBar);
        }
        function interactiveGraph(selection) {
            var data = app.data.summaryData;
            var title = properties.get('widgetTitle') === 'Default' ? "Summary Chart" : properties.get('widgetTitle');
            var interGraph = app.chart.interGraph().chartTitle(title);
            d3.select(selection).datum(data).call(interGraph);
        }
        function pieGraph(selection) {
            var title, data, width, pieChart;
            data = app.data.osData;
            title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle');
            width = $(selection).width();
            pieChart = app.chart.pieGraph().title(title).width(width);
            d3.select(selection).datum(data).call(pieChart);
        }
        function lineGraph(selection) {
            var data = [{"label": new Date('1960').getFullYear(), "value":60},
                    {"label": new Date('1970').getFullYear(), "value":20},
                    {"label": new Date('1980').getFullYear(), "value":43},
                    {"label": new Date('1990').getFullYear(), "value":15},
                    {"label": new Date('2000').getFullYear(), "value":5},
                    {"label": new Date('2010').getFullYear(), "value":25},
                    {"label": new Date('2012').getFullYear(), "value":65}],
                title = properties.get('widgetTitle') === 'Default' ? "Line Graph" : properties.get('widgetTitle'),
                width = $(selection).width();
            var lineChart = app.chart.lineGraph().title(title).width(width);
            d3.select(selection).datum(data).call(lineChart);
        }
        function stackedGraph(selection) {
            var data = app.data.osData,
                title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                width = $(selection).width(),
                stackedChart = app.chart.stackedGraph().title(title).width(width);
            d3.select(selection).datum(data).call(stackedChart);
        }
        function setProperties(obj, param) {
            'use strict';
            if (param === "existing") {
                var widgetName = $(obj).parent().parent().parent().parent().parent().parent().attr("id"),
                    title = $("#" + widgetName + "-title").html();
                properties.set({
                    widgetName: widgetName,
                    currentWidget: "existing"
                });
                $('#title').val('');
                $('#title').attr("placeholder", title);
            } else if (param === "new") {
                properties.set({
                    currentWidget: "new"
                });
                $('#title').val('');
                $('#title').attr("placeholder", "Default");
            }
        }
        function hideWidget(obj) {
            'use strict';
            $(obj).parent().parent().parent().parent().parent().parent().hide();
        }
        var exports = {
            Model: Backbone.Model.extend({}),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var tmpl = _.template(this.template),
                        that = this;

                    this.$el.html('');
                    this.$el.append('<header class="page-header"><h1>DASHBOARD <small>Customize your needs</small></h1></header>');
                    this.overview = new Overview.View({
                        el: $('<summary>').addClass('row-fluid clearfix movable')
                    });
                    this.$el.append(that.overview.render().$el);

                    this.$el.append(tmpl());

                    this.test();

                    app.vent.trigger('domchange:title', 'Dashboard');

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                test: function () {
                    setTimeout(function () {
                        $(".dropdown-toggle").dropdown();
                        $(".movable").sortable({ connectWith: '.movable' });
                        $("#restore").click(function () { $(".widget").show(); });
                        $(".properties").click(function () { setProperties(this, 'existing'); });
                        $('#addwidget').click(function () { console.log('new'); setProperties(this, 'new'); });
                        $('.remove').click(function () { hideWidget(this); });
                        $(".movable").sortable({ connectWith: '.movable' });
                        barGraph("#graph2");
                        interactiveGraph("#graph3");
                        pieGraph("#graph1");
                    }, 100);
                }
            })
        };
        return exports;
    }
);