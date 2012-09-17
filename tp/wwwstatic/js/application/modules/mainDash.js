define(
    ['jquery', 'backbone', 'app', 'text!templates/testBody.html', 'modules/overview', 'jquery.ui', 'jquery.bootstrap' ],
    function ($, Backbone, app, myTemplate, Overview) {
        "use strict";
        /*
        function onInitFs (fs) {

            fs.root.getFile('data.json', {create: false}, function(fileEntry) {
                fileEntry.remove(function() {
                    console.log('File removed.');
                }, errorHandler);
            }, errorHandler);

            setTimeout(function () {
                fs.root.getFile('data.json', {create: true}, function(fileEntry) {

                    // Create a FileWriter object for our FileEntry (log.txt).
                    fileEntry.createWriter(function(fileWriter) {

                        fileWriter.onwriteend = function(e) {
                            console.log('Write completed.');
                        };

                        fileWriter.onerror = function(e) {
                            console.log('Write failed: ' + e.toString());
                        };

                        // Create a new Blob and write it to log.txt.
                        var osData = globalData.get("summaryData");
                        console.log(osData);
                        var jsonData = JSON.stringify(osData);//globalData.get("osData").toString();
                        var blob = new Blob([jsonData], {type: 'application/json'});
                        fileWriter.write(blob);

                    }, errorHandler);

                    fileEntry.file(function(file) {
                        var reader = new FileReader();

                        reader.onloadend = function(e) {
                            var txtArea = document.createElement('textarea');
                            txtArea.value = this.result;
                            document.body.appendChild(txtArea);
                        };

                        reader.readAsText(file);
                    }, errorHandler);

                }, errorHandler);
            }, 100);

        }
        function errorHandler(e) {
            var msg = '';

            switch (e.code) {
                case FileError.QUOTA_EXCEEDED_ERR:
                    msg = 'QUOTA_EXCEEDED_ERR';
                    break;
                case FileError.NOT_FOUND_ERR:
                    msg = 'NOT_FOUND_ERR';
                    break;
                case FileError.SECURITY_ERR:
                    msg = 'SECURITY_ERR';
                    break;
                case FileError.INVALID_MODIFICATION_ERR:
                    msg = 'INVALID_MODIFICATION_ERR';
                    break;
                case FileError.INVALID_STATE_ERR:
                    msg = 'INVALID_STATE_ERR';
                    break;
                default:
                    msg = 'Unknown Error';
                    break;
            };

            console.log('Error: ' + msg);
        } */
        var Properties = Backbone.Model.extend({
            defaults: {
                widgetName: "widget1",
                currentWidget: "existing",
                widgetType: "graph"
                //widgetGraph: "pie"
            },
            initialize: function () {
                'use strict';
            }
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
                title = "OS types in Network",
                width = $(selection).width(),
                barWidth = (width / data.length ) - 10;
            var graphBar = app.chart.barGraph().title(title).barWidth(barWidth);
            d3.select(selection).datum(data).call(graphBar);
        }
        function interactiveGraph(selection) {
            var data = app.data.summaryData;
            var interGraph = app.chart.interGraph();
            d3.select(selection).datum(data).call(interGraph);
        }
        function pieGraph(selection) {
            var title, data, width, pieChart;
            data = app.data.osData;
            title = "OS types in Network";
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
                title = "Line Chart",
                width = $(selection).width();
            var lineChart = app.chart.lineGraph().title(title).width(width);
            d3.select(selection).datum(data).call(lineChart);
        }
        function stackedGraph(selection) {
            var data = app.data.osData;
            var title = "OS in Network";
            var width = $(selection).width();
            var stackedChart = app.chart.stackedGraph().title(title).width(width);
            d3.select(selection).datum(data).call(stackedChart);
        }
        function setProperties(obj, param) {
            'use strict';
            if (param === "existing") {
                properties.set({
                    widgetName: $(obj).parent().parent().parent().parent().parent().parent().attr("id"),
                    currentWidget: "existing"
                });
            } else if (param === "new") {
                properties.set({
                    currentWidget: "new"
                });
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
                render: function () {
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

                    return this;
                },
                test: function () {
                    setTimeout(function () {
                        $(".dropdown-toggle").dropdown();
                        $(".movable").sortable({ connectWith: '.movable' });
                        $("#restore").click(function () { $(".widget").show(); });
                        $(".properties").click(function () { setProperties(this, 'existing'); });
                        $('#addwidget').click(function () { setProperties(this, 'new'); });
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