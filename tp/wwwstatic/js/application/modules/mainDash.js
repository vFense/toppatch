define(
    ['jquery', 'underscore', 'backbone', 'd3', 'app', 'text!templates/mainDash.html', 'modules/overview', 'jquery.ui.sortable' ],
    function ($, _, Backbone, d3, app, myTemplate, Overview) {
        "use strict";
        var exports = {
                Model: Backbone.Model.extend({}),
                View: Backbone.View.extend({
                    initialize: function () {
                        this.template = myTemplate;
                        this.widget = "widget1";
                        this.type = "graph";
                        this.current = "new";
                        this.sizeval = 3;
                        this.counter = 4;
                        this.graphType = 'pie';
                        this.graph = '#graph1';
                        this.graphData = 'os';
                        this.template = "";
                        this.title = "Default";
                        this.myClass = "span";
                        this.tempData = "";
                        this.title = "Default";
                        this.spanCounter = 0;
                        this.properties = {
                            widgetName: "widget1",
                            currentWidget: "existing",
                            widgetType: "graph",
                            widgetTitle: "Default"
                        };
                        window.User.set('properties', this.properties);
                    },
                    events: {
                        'click #type1': 'graphSetting',
                        'click #type2': 'textSetting',
                        'click input[name=graph]': 'selectGraphType',
                        'click #apply': 'createWidget'
                    },
                    selectGraphType: function () {
                        var type = this.$el.find('input[name=graph]:checked').val(),
                            areaSettings = this.$el.find('#areaSettings');
                        if (type === 'area') {
                            areaSettings.show();
                        } else {
                            areaSettings.hide();
                        }
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
                                graph = $('select[name=graph] option[value=' + graphType + ']'),
                                size = $('input:radio[name=radio]'),
                                widgetType = $("#" + widgetName).find('.graph').attr('value');
                            this.properties.widgetName = widgetName;
                            this.properties.currentWidget = 'existing';
                            this.properties.widgetTitle = title;
                            window.User.set('properties', this.properties);
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
                                graph.attr('selected', 'selected');
                                $('#graphSettings').show();
                            }
                            if (graphType === 'area') {
                                this.selectGraphType();
                            }
                            $('#title').val(title).attr("placeholder", title);
                        } else if (param === "new") {
                            if ($('#widget6').length !== 0) {
                                window.console.log('too many widgets');
                                setTimeout(function () { $('#widgetProperties').modal('hide'); }, 50);
                            }
                            this.properties.currentWidget = 'new';
                            window.User.set('properties', this.properties);
                            $("#graphSettings").hide();
                            $('INPUT:text, SELECT', '#properties-form').val('');
                            $('INPUT:checkbox, INPUT:radio', '#properties-form').removeAttr('checked').removeAttr('selected');
                            $('#title').val('').attr("placeholder", "Default");
                        }
                    },
                    widgetrender: function () {
                        var that = this;
                        that.current = window.User.get('properties').currentWidget;
                        that.type = $('input:radio[name=type]:checked').val();
                        that.title = that.$el.find('#title').val() === "" ? "Default" : that.$el.find('#title').val();
                        this.properties.widgetTitle = that.title;
                        window.User.set('properties', this.properties);
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
                        } else if (this.graphType === "area_1") {
                            this.stackedAreaGraph(this.graph, true);
                        } else if (this.graphType === 'area_2') {
                            this.stackedAreaGraph(this.graph, false);
                        }
                    },
                    renderNew: function () {
                        var variables, $rowDiv,
                            newElement = function (element) {
                                return $(document.createElement(element));
                            },
                            that = this;
                        that.widget = "widget" + that.counter;
                        $rowDiv = newElement('div').addClass('row-fluid clearfix movable');
                        if (that.type === "graph") {
                            that.sizeval = parseInt($('input:radio[name=radio]:checked').val(), 10);
                            that.graphType = $('select[name=graph] option:selected').val();
                            variables = {
                                widget: that.widget,
                                span: "span" + that.sizeval,
                                graphcontainer: "graphcontainer" + that.counter,
                                menu: "menu" + that.counter,
                                graph: "graph" + that.counter,
                                title: that.title,
                                graphType: that.graphType
                            };
                            that.template = _.template($("#widget_template").html(), variables);
                            $rowDiv.append(that.template);
                            that.$el.append($rowDiv);
                            that.graphData = $('input:radio[name=graphdata]:checked').val();
                            that.graph = "#" + $("#" + that.widget).children().children("div").attr("id");
                            that.counter += 1;
                            that.displayChart();
                            that.saveState();
                            $(".properties").click(function () { that.setProperties(this, 'existing'); });
                            $('.remove').click(function () { that.hideWidget(this); });
                        } else {
                            that.sizeval = parseInt($('input:radio[name=radio]:checked').val(), 10);
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
                            $rowDiv.append(that.template);
                            that.$el.append($rowDiv);
                            that.counter += 1;
                            that.getTags(that.graph);
                        }
                    },
                    renderExisting: function () {
                        var variables, index,
                            that = this,
                            self = this;
                        that.widget = "#" + window.User.get('properties').widgetName;//properties.get("widgetName");
                        that.graph = "#" + $(that.widget + " .graph").attr("id");
                        that.title = window.User.get('properties').widgetTitle;//properties.get('widgetTitle');
                        if (that.type === "graph") {
                            that.myClass = $(that.widget).attr("class");
                            that.sizeval = parseInt($('input:radio[name=radio]:checked').val(), 10);
                            that.graphType = $('select[name=graph] option:selected').val();
                            that.graphData = $('input:radio[name=graphdata]:checked').val();
                            $(that.widget + '-title').html(that.title);
                            $(that.widget).removeClass(that.myClass).addClass("span" + that.sizeval + " widget editable");
                            self.displayChart();
                            self.saveState();
                        } else {
                            that.sizeval = parseInt($('input:radio[name=radio]:checked').val(), 10);
                            that.graphType = 'tag';
                            that.myClass = $(that.widget).attr("class");
                            $(that.widget + '-title').html(that.title);
                            $(that.widget).removeClass(that.myClass).addClass("span" + that.sizeval + " widget editable");
                            self.getTags(that.graph);
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
                    getTags: function (selection) {
                        var that = this,
                            url = 'api/tagging/tagStats',
                            tag_template;
                        $.get(url, {}, function (data) {
                            that.$el.find(selection).empty();
                            tag_template = _.template($('#tags_template').html(), {data: data.data || data});
                            that.$el.find(selection).html(tag_template);
                            that.saveState();
                        });
                    },
                    beforeRender: $.noop,
                    onRender: function () {
                        var that = this;
                        this.generateWidgets();

                        $(document).find("#restore").click(function () { $(".widget").show(); });
                        $(document).find('#addwidget').click(function () { that.setProperties(this, 'new'); });

                        this.$el.find('.remove').click(function () { that.hideWidget(this); });
                        this.$el.find(".properties").click(function () { that.setProperties(this, 'existing'); });

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
                    },
                    render: function () {
                        if (this.beforeRender !== $.noop) { this.beforeRender(); }

                        var variables,
                            tmpl = _.template(myTemplate),
                            that = this;

                        this.$el.empty();

                        this.overview = new Overview.View({
                            el: $('<div>').addClass('row-fluid clearfix').attr('id', 'overview')
                        });
                        this.$el.append(that.overview.render().$el);
                        this.$el.append('<br>');

                        variables = window.User.get('widgets');

                        this.$el.append(tmpl(variables));

                        app.vent.trigger('domchange:title', 'Dashboard');

                        if (this.onRender !== $.noop) { this.onRender(); }
                        return this;
                    },
                    getStyleWidth: function (className) {
                        var classes = document.styleSheets[2].rules || document.styleSheets[2].cssRules,
                            x = 0;
                        for (x = 0; x < classes.length; x += 1) {
                            if (classes[x].selectorText === className) {
                                return classes[x].style.width;
                            }
                        }
                    },
                    emToPx: function (input) {
                        var emSize = parseFloat($("body").css("font-size"));
                        return (emSize * input);
                    },
                    stackedGraph: function (selection) {
                        //var data = app.data.osData,
                        //title = properties.get('widgetTitle') === 'Default' ? "Nodes in Network by OS" : properties.get('widgetTitle'),
                        var span = this.$el.find(selection).parents('article').attr('class').split(' ')[0],
                            width = this.emToPx(parseFloat(this.getStyleWidth('.' + span))),
                            stackedChart = app.chart.stackedBar().width(width);
                        this.$el.find(selection).attr('class', 'stacked graph');
                        d3.json("../api/graphData", function (json) {
                            d3.select(selection).datum(json).call(stackedChart);
                        });
                    },
                    pieGraph: function (selection) {
                        var span = this.$el.find(selection).parents('article').attr('class').split(' ')[0],
                            width = this.emToPx(parseFloat(this.getStyleWidth('.' + span))),
                            pieChart = app.chart.newpie().width(width);
                        this.$el.find(selection).attr('class', 'pie graph');
                        d3.json("../api/graphData", function (json) {
                            d3.select(selection).datum(json).call(pieChart);
                        });
                    },
                    barGraph: function (selection) {
                        var span = this.$el.find(selection).parents('article').attr('class').split(' ')[0],
                            width = this.emToPx(parseFloat(this.getStyleWidth('.' + span)));

                        this.$el.find(selection).attr('class', 'bar graph');
                        d3.json("../api/severity.json", function (json) {
                            var barWidth = (width / json.length) - 10,
                                graphBar = app.chart.bar_3d().width(width);//app.chart.bar().barWidth(barWidth);
                            d3.select(selection).datum(json).call(graphBar);
                        });
                    },
                    interactiveGraph: function (selection) {
                        var interGraph = app.chart.partition();
                        this.$el.find(selection).attr('class', 'summary graph');
                        d3.json("../api/summaryData", function (json) {
                            d3.select(selection).datum(json).call(interGraph);
                        });
                    },
                    stackedAreaGraph: function (selection, installed) {
                        var span = this.$el.find(selection).parents('article').attr('class').split(' ')[0],
                            width = this.emToPx(parseFloat(this.getStyleWidth('.' + span))),
                            stackedChart = app.chart.stackedArea().width(width);
                        if (installed) {
                            this.$el.find(selection).attr('class', 'area_1 graph');
                        } else {
                            this.$el.find(selection).attr('class', 'area_2 graph');
                        }
                        d3.json("../api/node/graphs/severity?installed=" + installed, function (json) {
                            d3.select(selection).datum([json]).call(stackedChart);
                        });
                    },/*
                    lineGraph: function (selection) {
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
                    }, */
                    calculateRows: function () {
                        var i, check,
                            that = this,
                            rowArray = [],
                            arrayOfRows = [],
                            settings = window.User.get('widgets'),
                            widgets = settings.graph;
                        for (i = 0; i < widgets.length; i += 1) {
                            check = that.spanCounter + settings.spans[i];
                            if (check < 12) {
                                rowArray.push(settings.spans[i]);
                                that.spanCounter += settings.spans[i];
                                if (check + settings.spans[i + 1] > 12 || isNaN(settings.spans[i + 1])) {
                                    arrayOfRows.push(rowArray);
                                }
                            } else if (check === 12) {
                                rowArray.push(settings.spans[i]);
                                that.spanCounter = 0;
                                arrayOfRows.push(rowArray);
                                rowArray = [];
                            } else if (check > 12) {
                                rowArray = [];
                                rowArray.push(settings.spans[i]);
                                arrayOfRows.push(rowArray);
                                that.spanCounter = 0;
                            }
                        }
                        return arrayOfRows;
                    },
                    generateWidgets: function () {
                        var variables, template, $rowDiv, arrayOfRows,
                            that = this,
                            widgetCounter = 0,
                            widgets = window.User.get('widgets').graph,
                            settings = window.User.get('widgets'),
                            newElement = function (element) {
                                return $(document.createElement(element));
                            };
                        arrayOfRows = this.calculateRows();
                        _.each(arrayOfRows, function (row) {
                            $rowDiv = newElement('div').addClass('row-fluid clearfix movable');
                            _.each(row, function (widget) {
                                variables = {
                                    widget: "widget" + (widgetCounter + 1),
                                    span: "span" + settings.spans[widgetCounter],
                                    graphcontainer: "graphcontainer" + (widgetCounter + 1),
                                    menu: "menu" + (widgetCounter + 1),
                                    graph: "graph" + (widgetCounter + 1),
                                    title: settings.titles[widgetCounter],
                                    graphType: widgets[widgetCounter]
                                };
                                template = _.template($("#widget_template").html(), variables);
                                $rowDiv.append(template);
                                widgetCounter += 1;
                            });
                            that.$el.append($rowDiv);
                            that.counter = widgetCounter  + 1;
                        });
                        this.populateWidgets();
                    },
                    populateWidgets: function () {
                        var i,
                            that = this,
                            widgets = window.User.get('widgets').graph,
                            settings = window.User.get('widgets');

                        for (i = 0; i < widgets.length; i += 1) {
                            if (widgets[i] === 'pie') {
                                that.pieGraph('#graph' + (i + 1));
                            } else if (widgets[i] === 'bar') {
                                that.barGraph('#graph' + (i + 1));
                            } else if (widgets[i] === 'summary') {
                                that.interactiveGraph('#graph' + (i + 1));
                            } else if (widgets[i] === 'stacked') {
                                that.stackedGraph('#graph' + (i + 1));
                            } else if (widgets[i] === 'area_1') {
                                that.stackedAreaGraph('#graph' + (i + 1), true);
                            } else if (widgets[i] === 'area_2') {
                                that.stackedAreaGraph('#graph' + (i + 1), false);
                            } else if (widgets[i] === 'tag') {
                                that.graph = '#graph' + (i + 1);
                                that.sizeval = settings.spans[i];
                                that.title = settings.titles[i];
                                that.graphType = widgets[i];
                                that.getTags('#graph' + (i + 1));
                            }
                        }
                    }
                })
            };
        return exports;
    }
);
