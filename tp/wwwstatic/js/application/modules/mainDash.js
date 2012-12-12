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
            /*
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
            */
            exports = {
                Model: Backbone.Model.extend({}),
                View: Backbone.View.extend({
                    initialize: function () {
                        this.template = myTemplate;
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
                        'click #apply': 'createWidget'
                        //'click #graphtype1': 'pieData',
                        //'click #graphtype2': 'otherData',
                        //'click #graphtype3': 'otherData',
                        //'click #graphtype4': 'otherData'
                    },
                    textSetting: function () {
                        $("#graphSettings").hide();
                        //$("#textSettings").show();
                    },
                    createWidget: function () {
                        $("#widgetProperties").modal('hide');
                        this.widgetrender();
                    },
                    graphSetting: function () {
                        $("#graphSettings").show();
                        $("#textSettings").hide();
                    },
                    hideWidget: function (object) {
                        $(object).parents('.widget').hide();
                    },
                    setProperties: function (obj, param) {
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
                            if ($('#widget5').length !== 0) {
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
                    widgetrender: function () {
                        var that = this;
                        that.current = properties.get("currentWidget");
                        that.type = $('input:radio[name=type]:checked').val();
                        that.title = that.$el.find('#title').val() === "" ? "Default" : that.$el.find('#title').val();
                        properties.set({ widgetTitle: that.title });
                        if (that.current === "new") {
                            that.renderNew();
                        } else {
                            that.renderExisting();
                        }
                    },
                    displayChart: function () {
                        if (this.graphType === "pie") {
                            this.pieGraph(this.graph);
                        } else if (this.graphType === "bar") {
                            this.barGraph(this.graph);
                        } else if (this.graphType === "stacked") {
                            this.stackedGraph(this.graph);
                        } else if (this.graphType === "summary") {
                            this.interactiveGraph(this.graph);
                        } /* else if (that.graphType === "line") {
                            lineGraph(that.graph);
                        } */
                    },
                    renderNew: function () {
                        var variables, index,
                            that = this,
                            self = this;
                        that.widget = "widget" + that.counter;
                        if (that.type === "graph") {
                            that.sizeval = $('input:radio[name=radio]:checked').val();
                            that.graphType = $('input:radio[name=graph]:checked').val();
                            variables = {
                                widget: that.widget,
                                span: "span" + that.sizeval,
                                graphcontainer: "graphcontainer" + that.counter,
                                menu: "menu" + that.counter,
                                graph: "graph" + that.counter,
                                title: that.title,
                                graphType: that.graphType
                            };
                            // Compile the template using underscore
                            that.template = _.template($("#widget_template").html(), variables);
                            // Load the compiled HTML into the Backbone "el"
                            $("#insert").append(that.template);
                            that.graphData = $('input:radio[name=graphdata]:checked').val();
                            that.graph = "#" + $("#" + that.widget).children().children("div").attr("id");
                            that.counter += 1;
                            self.displayChart();
                            self.saveState();
                            $(".properties").click(function () { self.setProperties(this, 'existing'); });
                            $('.remove').click(function () { self.hideWidget(this); });
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
                            that.sizeval = $('input:radio[name=radio]:checked').val();
                            variables = {
                                widget: that.widget,
                                span: "span" + that.sizeval,
                                graphcontainer: "graphcontainer" + that.counter,
                                menu: "menu" + that.counter,
                                graph: "graph" + that.counter,
                                title: that.title,
                                graphType: that.type
                            };
                            that.graphType = that.type;
                            that.graph = "#graph" + that.counter;
                            that.widget = "#" + that.widget;
                            that.template = _.template($("#widget_template").html(), variables);
                            $("#insert").append(that.template);
                            that.counter += 1;
                            self.getTags();
                        }
                    },
                    renderExisting: function () {
                        var variables, index,
                            that = this,
                            self = this;
                        that.widget = "#" + properties.get("widgetName");
                        that.graph = "#" + $(that.widget + " .graph").attr("id");
                        that.title = properties.get('widgetTitle');
                        if (that.type === "graph") {
                            that.myClass = $(that.widget).attr("class");
                            that.sizeval = $('input:radio[name=radio]:checked').val();
                            that.graphType = $('input:radio[name=graph]:checked').val();
                            that.graphData = $('input:radio[name=graphdata]:checked').val();
                            $(that.widget + '-title').html(that.title);
                            $(that.widget).removeClass(that.myClass).addClass("span" + that.sizeval + " widget editable");
                            self.displayChart();
                            self.saveState();
                        } else {
                            that.sizeval = $('input:radio[name=radio]:checked').val();
                            that.graphType = 'tag';
                            that.myClass = $(that.widget).attr("class");
                            $(that.widget + '-title').html(that.title);
                            $(that.widget).removeClass(that.myClass).addClass("span" + that.sizeval + " widget editable");
                            self.getTags();
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
                    saveState: function () {
                        var widgets = window.User.get('widgets'),
                            userName = window.User.get('name'),
                            that = this,
                            matches = that.graph.match(/\d+$/),
                            position = matches[0] - 1;
                        widgets.graph[position] = that.graphType;
                        widgets.spans[position] = that.sizeval;
                        widgets.titles[position] = that.title;
                        window.User.set('widgets', widgets);
                        localStorage.setItem(userName, JSON.stringify(window.User));
                    },
                    getTags: function () {
                        var self = this,
                            that = this,
                            tag_template;
                        $.ajax({
                            url: 'api/tagging/tagStats',
                            dataType: 'json',
                            async: false,
                            success: function (data) {
                                $(that.graph).empty();
                                tag_template = _.template($('#tags_template').html(), {data: data});
                                $(that.graph).html(tag_template);
                                self.saveState();
                            }
                        });
                    },
                    beforeRender: $.noop,
                    onRender: function () {

                        $(document).find("#restore").click(function () { $(".widget").show(); });
                        $(document).find('#addwidget').click(function () { that.setProperties(this, 'new'); });

                        this.$el.find(".movable").sortable({
                            containment: 'body',
                            appendTo: '#dashboard-view',
                            helper: 'clone',
                            connectWith: '.movable',
                            items: 'dl, .widget',
                            distance: 20
                        });
                        this.$el.find("#dashboard-view").sortable({
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
                        this.populateWidgets();
                    },
                    render: function () {
                        if (this.beforeRender !== $.noop) { this.beforeRender(); }

                        var variables,
                            tmpl = _.template(myTemplate),
                            that = this;

                        this.$el.empty();

                        this.overview = new Overview.View({
                            el: $('<div>').addClass('row-fluid clearfix movable').attr('id', 'overview')
                        });
                        this.$el.append(that.overview.render().$el);

                        variables = window.User.get('widgets');

                        this.$el.append(tmpl(variables));

                        app.vent.trigger('domchange:title', 'Dashboard');

                        if (this.onRender !== $.noop) { this.onRender(); }
                        return this;
                    },
                    stackedGraph: function (selection) {
                        //var data = app.data.osData,
                        //title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                        var width = $(selection).width(),
                            stackedChart = app.chart.stackedBar().width(width);
                        $(selection).attr('class', 'stacked graph');
                        d3.json("../api/graphData", function (json) {
                            d3.select(selection).datum(json).call(stackedChart);
                        });
                    },
                    pieGraph: function (selection) {
                        var width = this.$el.find(selection).width(),
                            pieChart = app.chart.pie().width(width);
                        $(selection).attr('class', 'pie graph');
                        d3.json("../api/severity.json", function (json) {
                            d3.select(selection).datum(json).call(pieChart);
                        });
                    },
                    barGraph: function (selection) {
                        var width = $(selection).width();
                        $(selection).attr('class', 'bar graph');
                        d3.json("../api/graphData", function (json) {
                            var barWidth = (width / json.length) - 10,
                                graphBar = app.chart.bar().barWidth(barWidth);
                            d3.select(selection).datum(json).call(graphBar);
                        });
                    },
                    interactiveGraph: function (selection) {
                        var interGraph = app.chart.partition();
                        $(selection).attr('class', 'summary graph');
                        d3.json("../api/summaryData", function (json) {
                            d3.select(selection).datum(json).call(interGraph);
                        });
                    },
                    populateWidgets: function () {
                        var i, variables, template,
                            that = this,
                            widgets = window.User.get('widgets').graph,
                            settings = window.User.get('widgets');

                        setTimeout(function () {
                            for (i = 0; i < widgets.length; i += 1) {
                                if ($('#widget' + (i + 1)).length === 0) {
                                    variables = {
                                        widget: "widget" + (i + 1),
                                        span: "span" + settings.spans[i],
                                        graphcontainer: "graphcontainer" + (i + 1),
                                        menu: "menu" + (i + 1),
                                        graph: "graph" + (i + 1),
                                        title: settings.titles[i],
                                        graphType: widgets[i]
                                    };
                                    template = _.template($("#widget_template").html(), variables);
                                    $("#insert").append(template);
                                }

                                if (widgets[i] === 'pie') {
                                    that.pieGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'bar') {
                                    that.barGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'summary') {
                                    that.interactiveGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'stacked') {
                                    that.stackedGraph('#graph' + (i + 1));
                                } else if (widgets[i] === 'tag') {
                                    that.graph = '#graph' + (i + 1);
                                    that.sizeval = settings.spans[i];
                                    that.title = settings.titles[i];
                                    that.graphType = widgets[i];
                                    that.getTags();
                                }/*else if (widgets[i] === 'line') {
                                 lineGraph('#graph' + (i + 1));
                                 }*/
                            }
                            that.$el.find(".properties").click(function () { that.setProperties(this, 'existing'); });
                            that.$el.find('.remove').click(function () { that.hideWidget(this); });
                        }, 200);
                    }
                })
            };
        return exports;
    }
);
