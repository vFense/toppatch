define(
    ['jquery', 'underscore', 'backbone', 'd3', 'app', 'text!templates/mainDash.html', 'modules/overview', 'jquery.ui.sortable' ],
    function ($, _, Backbone, d3, app, myTemplate, Overview) {
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
            barGraph = function (selection) {
                var width = $(selection).width();
                $(selection).attr('class', 'bar graph');
                d3.json("../api/graphData", function (json) {
                    var barWidth = (width / json.length) - 10,
                        graphBar = app.chart.bar().barWidth(barWidth);
                    d3.select(selection).datum(json).call(graphBar);
                });
            },
            interactiveGraph = function (selection) {
                var interGraph = app.chart.partition();
                $(selection).attr('class', 'summary graph');
                d3.json("../api/summaryData", function (json) {
                    d3.select(selection).datum(json).call(interGraph);
                });
            },
            pieGraph = function (selection) {
                var width = $(selection).width(),
                    pieChart = app.chart.pie().width(width);
                $(selection).attr('class', 'pie graph');
                d3.json("../api/severity.json", function (json) {
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
                    width = $(selection).width(),
                    lineChart = app.chart.line().width(width);
                $(selection).attr('class', 'line graph');
                //title = properties.get('widgetTitle') === 'Default' ? "Line Graph" : properties.get('widgetTitle'),
                d3.select(selection).datum(data).call(lineChart);
            },
            stackedGraph = function (selection) {
                //var data = app.data.osData,
                //title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                var width = $(selection).width(),
                    stackedChart = app.chart.stackedBar().width(width);
                $(selection).attr('class', 'stacked graph');
                d3.json("../api/graphData", function (json) {
                    d3.select(selection).datum(json).call(stackedChart);
                });
            },
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
                    //$("#textSettings").show();
                },
                displayChart: function () {
                    if (this.graphType === "pie") {
                        pieGraph(this.graph);
                    } else if (this.graphType === "bar") {
                        barGraph(this.graph);
                    } else if (this.graphType === "line") {
                        lineGraph(this.graph);
                    } else if (this.graphType === "stacked") {
                        stackedGraph(this.graph);
                    } else if (this.graphType === "summary") {
                        interactiveGraph(this.graph);
                    }
                },
                render: function () {
                    this.current = properties.get("currentWidget");
                    this.type = $('input:radio[name=type]:checked').val();
                    window.console.log(this.type);
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
                            graph: "graph" + this.counter,
                            title: this.title
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
                        this.saveState();
                        $(".properties").click(function () { setProperties(this, 'existing'); });
                        $('.remove').click(function () { hideWidget(this); });
                    } else {
                        /*
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
                        */
                        this.sizeval = $('input:radio[name=radio]:checked').val();
                        variables = {
                            widget: this.widget,
                            span: "span" + this.sizeval,
                            graphcontainer: "graphcontainer" + this.counter,
                            menu: "menu" + this.counter,
                            graph: "graph" + this.counter,
                            title: this.title
                        };
                        this.graph = "#graph" + this.counter;
                        this.widget = "#" + this.widget;
                        this.template = _.template($("#widget_template").html(), variables);
                        $("#insert").append(this.template);
                        this.counter += 1;
                        this.getTags();
                    }
                },
                renderExisting: function () {
                    var variables, index, parent;
                    this.widget = "#" + properties.get("widgetName");
                    this.graph = "#" + $(this.widget + " .graph").attr("id");
                    this.title = properties.get('widgetTitle');
                    if (this.type === "graph") {
                        this.myClass = $(this.widget).attr("class");
                        this.sizeval = $('input:radio[name=radio]:checked').val();
                        this.graphType = $('input:radio[name=graph]:checked').val();
                        this.graphData = $('input:radio[name=graphdata]:checked').val();
                        $(this.widget + '-title').html(this.title);
                        $(this.widget).removeClass(this.myClass).addClass("span" + this.sizeval + " widget editable");
                        this.displayChart();
                        this.saveState();
                    } else {
                        this.sizeval = $('input:radio[name=radio]:checked').val();
                        this.graphType = 'tag';
                        this.myClass = $(this.widget).attr("class");
                        $(this.widget + '-title').html(this.title);
                        $(this.widget).removeClass(this.myClass).addClass("span" + this.sizeval + " widget editable");
                        this.getTags();
                        //text widget block
                        /*
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
                        */
                    }
                },
                getTags: function () {
                    var that = this, tag_template;
                    $.ajax({
                        url: 'api/tagging/tagStats',
                        dataType: 'json',
                        async: false,
                        success: function (data) {
                            $(that.graph).empty();
                            tag_template = _.template($('#tags_template').html(), {data: data});
                            $(that.graph).html(tag_template);
                            that.saveState();
                        }
                    });
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
                },
                saveState: function () {
                    var widgets = window.User.get('widgets'),
                        userName = window.User.get('name'),
                        matches = this.graph.match(/\d+$/),
                        position = matches[0] - 1;
                    widgets.graph[position] = this.graphType;
                    widgets.spans[position] = this.sizeval;
                    widgets.titles[position] = this.title;
                    window.User.set('widgets', widgets);
                    localStorage.setItem(userName, JSON.stringify(window.User));
                }
            }),
            widgetview = new WidgetView({ el: 'body' }),
            setProperties = function (obj, param) {
                if (param === "existing") {
                    var widgetName = $(obj).parents('.widget').attr("id"),
                        title = $("#" + widgetName + "-title").html(),
                        span = $("#" + widgetName).attr('class').split(' ')[0].match(/\d+$/)[0],
                        graphType = $("#" + widgetName).find('.graph').attr('class').split(' ')[0],
                        graph = $('input:radio[name=graph]'),
                        size = $('input:radio[name=radio]'),
                        widgetType = $("#" + widgetName).find('.graph').attr('value');
                    properties.set({
                        widgetName: widgetName,
                        currentWidget: "existing",
                        widgetTitle: title
                    });
                    size.each(function () {
                        if ($(this).val() === span) {
                            $(this).attr('checked', true);
                        } else {
                            $(this).attr('checked', false);
                        }
                    });
                    if (widgetType === 'tag') {
                        $('input:radio[name=type]').each(function () {
                            if ($(this).val() === widgetType) {
                                $(this).attr('checked', true);
                            } else {
                                $(this).attr('checked', false);
                            }
                        });
                        $('#graphSettings').hide();
                    } else {
                        $('input:radio[name=type]').each(function () {
                            if ($(this).val() === 'graph') {
                                $(this).attr('checked', true);
                            } else {
                                $(this).attr('checked', false);
                            }
                        });
                        graph.each(function () {
                            if ($(this).val() === graphType) {
                                $(this).attr('checked', true);
                            } else {
                                $(this).attr('checked', false);
                            }
                        });
                        $('#graphSettings').show();
                    }
                    $('#title').val(title).attr("placeholder", title);
                    //widgetview.graphSetting();
                } else if (param === "new") {
                    if (widgetview.counter > 5) {
                        window.console.log('too many widgets');
                        setTimeout(function () { $('#widgetProperties').modal('hide'); }, 50);
                    }
                    properties.set({
                        currentWidget: "new"
                    });
                    $("#graphSettings").hide();
                    $('INPUT:text, SELECT', '#properties-form').val('');
                    $('INPUT:checkbox, INPUT:radio', '#properties-form').removeAttr('checked').removeAttr('selected');
                    $('#title').val('').attr("placeholder", "Default");
                }
            },
            hideWidget = function (obj) {
                $(obj).parents('.widget').hide();
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

                        var variables,
                            tmpl = _.template(this.template),
                            that = this;

                        this.$el.empty();

                        this.overview = new Overview.View({
                            el: $('<div>').addClass('row-fluid clearfix movable').attr('id', 'overview')
                        });
                        this.$el.append(that.overview.render().$el);

                        variables = window.User.get('widgets');
                        this.$el.append(tmpl(variables));
                        this.test();

                        app.vent.trigger('domchange:title', 'Dashboard');

                        if (this.onRender !== $.noop) { this.onRender(); }
                        return this;
                    },
                    test: function () {
                        setTimeout(function () {
                            $(".movable").sortable({
                                containment: 'body',
                                appendTo: '#dashboard-view',
                                helper: 'clone',
                                connectWith: '.movable',
                                items: 'dl, .widget',
                                distance: 20
                            });
                            $("#dashboard-view").sortable({
                                containment: 'body',
                                appendTo: '#dashboard-view',
                                helper: 'clone',
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
                            var i, variables, template,
                                widgets = window.User.get('widgets').graph,
                                settings = window.User.get('widgets');
                            for (i = 0; i < widgets.length; i += 1) {
                                if ($('#widget' + (i + 1)).length === 0) {
                                    variables = {
                                        widget: "widget" + (i + 1),
                                        span: "span" + settings.spans[i],
                                        graphcontainer: "graphcontainer" + (i + 1),
                                        menu: "menu" + (i + 1),
                                        graph: "graph" + (i + 1),
                                        title: settings.titles[i]
                                    };
                                    template = _.template($("#widget_template").html(), variables);
                                    $("#insert").append(template);
                                    widgetview.counter += 1;
                                }

                                if (widgets[i] === 'pie') {
                                    pieGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'bar') {
                                    barGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'summary') {
                                    interactiveGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'stacked') {
                                    stackedGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'line') {
                                    lineGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'tag') {
                                    widgetview.graph = '#graph' + (i + 1);
                                    widgetview.sizeval = settings.spans[i];
                                    widgetview.title = settings.titles[i];
                                    widgetview.graphType = widgets[i];
                                    widgetview.getTags();
                                }
                            }
                            $(".properties").click(function () { setProperties(this, 'existing'); });
                            $('.remove').click(function () { hideWidget(this); });
                        }, 200);
                    }
                })
            };
        return exports;
    }
);
