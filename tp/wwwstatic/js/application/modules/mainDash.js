define(
    ['jquery', 'backbone', 'd3', 'app', 'text!templates/testBody.html', 'modules/overview', 'jquery.ui.sortable' ],
    function ($, Backbone, d3, app, myTemplate, Overview) {
        "use strict";
        var properties = new (
                Backbone.Model.extend({
                    defaults: {
                        widgetName: "widget1",
                        currentWidget: "existing",
                        widgetType: "graph",
                        widgetTitle: "Default"
                    },
                    initialize: function () {}
                })
            )(),
            WidgetView = Backbone.View.extend({
                initialize: function () {
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
                        interactiveGraph(this.graph);
                    }
                },
                render: function () {
                    this.current = properties.get("currentWidget");
                    this.type = $('input:radio[name=type]:checked').val();
                    this.title = this.$el.find('#title').val() === "" ? "Default" : this.$el.find('#title').val();
                    properties.set({ widgetTitle: this.title });
                    if (this.current === "new") {
                        this.renderNew();
                    } else {
                        this.renderExisting();
                    }
                },
                renderNew: function () {
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
                renderExisting: function () {
                    var variables, index, parent;
                    this.widget = "#" + properties.get("widgetName");
                    if (this.type === "graph") {
                        this.myClass = $(this.widget).attr("class");
                        this.sizeval = $('input:radio[name=radio]:checked').val();
                        this.graphType = $('input:radio[name=graph]:checked').val();
                        this.graph = "#" + $(this.widget + " .graph").attr("id");
                        this.graphData = $('input:radio[name=graphdata]:checked').val();
                        $(this.widget).removeClass(this.myClass).addClass("span" + this.sizeval + " widget editable");
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
                getOverviewData: function () {
                    var type = $(this.title).val();
                    if (type === "Patched") {
                        return app.data.nodeData.Patched;
                    } else if (type === "Scheduled Patches") {
                        return app.data.nodeData.Unpatched;
                    } else if (type === "Nodes") {
                        return app.data.nodeData.Nodes;
                    } else if (type === "Failed Patches") {
                        return app.data.nodeData.Failed;
                    }
                }
            }),
            widgetview = new WidgetView({ el: 'body' }),
            barGraph = function (selection) {
                //var data = app.data.osData,
                var title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                    width = $(selection).width();
                d3.json("../api/graphData", function(json) {
                    var barWidth = (width / json.length) - 10,
                    graphBar = app.chart.bar().title(title).barWidth(barWidth);
                    d3.select(selection).datum(json).call(graphBar);
                });
            },
            interactiveGraph = function (selection) {
                //var data = app.data.summaryData,
                var title = properties.get('widgetTitle') === 'Default' ? "Summary Chart" : properties.get('widgetTitle'),
                    interGraph = app.chart.partition().chartTitle(title);
                d3.json("../api/summaryData", function(json) {
                    d3.select(selection).datum(json).call(interGraph);
                });
            },
            pieGraph = function (selection) {
                //var data = app.data.osData;
                var title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                    width = $(selection).width(),
                    pieChart = app.chart.pie().title(title).width(width);
                d3.json("../api/graphData", function(json) {
                    d3.select(selection).datum(json).call(pieChart);
                });
            },
            lineGraph = function (selection) {
                var data = [
                        {"label": new Date('1960').getFullYear(), "value": 60},
                        {"label": new Date('1970').getFullYear(), "value": 20},
                        {"label": new Date('1980').getFullYear(), "value": 43},
                        {"label": new Date('1990').getFullYear(), "value": 15},
                        {"label": new Date('2000').getFullYear(), "value": 5},
                        {"label": new Date('2010').getFullYear(), "value": 25},
                        {"label": new Date('2012').getFullYear(), "value": 65}
                    ],
                    title = properties.get('widgetTitle') === 'Default' ? "Line Graph" : properties.get('widgetTitle'),
                    width = $(selection).width(),
                    lineChart = app.chart.line().title(title).width(width);
                d3.select(selection).datum(data).call(lineChart);
            },
            stackedGraph = function (selection) {
                //var data = app.data.osData,
                var title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                    width = $(selection).width(),
                    stackedChart = app.chart.stackedBar().title(title).width(width);
                d3.json("../api/graphData", function(json) {
                    d3.select(selection).datum(json).call(stackedChart);
                });
            },
            setProperties = function (obj, param) {
                if (param === "existing") {
                    var widgetName = $(obj).parents('.widget').attr("id"),
                        title = $("#" + widgetName + "-title").html();
                    properties.set({
                        widgetName: widgetName,
                        currentWidget: "existing",
                        widgetTitle: title
                    });
                    $('#title').val('').attr("placeholder", title);
                } else if (param === "new") {
                    properties.set({
                        currentWidget: "new"
                    });
                    $('#title').val('').attr("placeholder", "Default");
                }
            },
            hideWidget = function (obj) {
                $(obj).parents('.widget').remove();
            },
            exports = {
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
                        //this.$el.append('<header class="page-header"><h1>DASHBOARD <small>Customize your needs</small></h1></header>');
                        this.overview = new Overview.View({
                            el: $('<div>').addClass('row-fluid clearfix movable').attr('id', 'overview')
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
                            $(".movable").sortable({
                                connectWith: '.movable',
                                items: 'dl, .widget',
                                distance: 20
                            });
                            $("#dashboard-view").sortable({
                                items: '.row, .row-fluid',
                                handle: '.row-handle',
                                placeholder: "ui-state-highlight",
                                start: function (event, ui) {
                                    ui.placeholder.css('height', ui.helper.css('height'));
                                    ui.placeholder.css('width', ui.helper.css('width'));
                                },
                                axis: 'y',
                                distance: 20
                            }).disableSelection();
                            $("#restore").click(function () { $(".widget").show(); });
                            $(".properties").click(function () { setProperties(this, 'existing'); });
                            $('#addwidget').click(function () { setProperties(this, 'new'); });
                            $('.remove').click(function () { hideWidget(this); });
                            barGraph("#graph2");
                            interactiveGraph("#graph3");
                            pieGraph("#graph1");
                        }, 200);
                    }
                })
            };
        return exports;
    }
);