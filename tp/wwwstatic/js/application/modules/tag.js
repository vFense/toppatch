/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/11/13
 * Time: 8:30 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'd3', 'app', 'text!templates/tag.html', 'jquery.ui.datepicker'],
    function ($, _, Backbone, d3, app, myTemplate) {
        "use strict";
        var exports = {
            StatsCollection: Backbone.Collection.extend({
                baseUrl: 'api/tagging/tagStats',
                url: function () {
                    return this.baseUrl + '?tagid=' + this.id;
                }
            }),
            PatchCollection: Backbone.Collection.extend({
                baseUrl: 'api/tags.json',
                url: function () {
                    return this.baseUrl + '?tag_id=' + this.id;
                }
            }),/*
            GraphCollection: Backbone.Collection.extend({
                baseUrl: 'api/node/graphs/severity',
                installed: 'true',
                url: function () {
                    return this.baseUrl + '?tagid=' + this.id + '&installed=' + this.installed;
                }
            }),*/
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.statscollection =  new exports.StatsCollection();
                    this.statscollection.bind('reset', this.render, this);
                    this.statscollection.fetch();

                    this.id = this.statscollection.id;

                    this.patchcollection = new exports.PatchCollection();
                    this.patchcollection.bind('reset', this.render, this);
                    this.patchcollection.fetch();

                    /*this.graphcollection = new exports.GraphCollection();
                    this.graphcollection.bind('reset', this.render, this);
                    this.graphcollection.fetch();*/

                    $.ajaxSetup({ traditional: true });
                },
                events: {
                    'click a.accordion-toggle'          : 'toggleAccordion',
                    'click .toggle-all'                 : 'toggleAllInputs',
                    'click button[name=reboot]'         : 'rebootNodes',
                    'click select[name=severityFilter]'   : 'filterBySeverity',
                    'submit form'                       : 'submitOperation'
                },
                showLoading: function (el) {
                    var $el = this.$el,
                        $div = $el.find(el);
                    this._pinwheel = new app.pinwheel();
                    $div.empty().append(this._pinwheel.el);
                },
                stackedAreaGraph: function (event) {
                    var //data = this.graphcollection.toJSON(),
                        id = this.id,
                        installedGraph = '#installedGraph',
                        availableGraph = '#availableGraph',
                        $graphDiv = this.$el.find(installedGraph),
                        width = $graphDiv.width(),
                        height = $graphDiv.parent().height(),
                        stackedChart = app.chart.stackedArea().width(width).height(height);
                    this.showLoading(installedGraph);
                    this.showLoading(availableGraph);
                    d3.json("../api/node/graphs/severity?tagid=" + id + "&installed=true", function (json) {
                        d3.select(installedGraph).datum([json]).call(stackedChart.title('Installed packages over time'));
                    });
                    d3.json("../api/node/graphs/severity?tagid=" + id + "&installed=false", function (json) {
                        d3.select(availableGraph).datum([json]).call(stackedChart.title('Available packages over time'));
                    });/*
                    if (data.length) {
                        d3.select(graphId).datum(data).call(stackedChart);
                    }*/
                },
                toggleAllInputs: function (event) {
                    var status = event.target.checked,
                        group = $(event.target).parents('.accordion-group'),
                        items = group.find('.items');
                    $(items).find("input[type=checkbox]").each(function () {
                        $(this).attr("checked", status);
                    });
                },
                toggleAccordion: function (event) {
                    var $href = $(event.currentTarget),
                        $click = $(event.target),
                        $icon = $href.find('i'),
                        $parent = $href.parents('.accordion-group'),
                        $body = $parent.find('.accordion-body').first(),
                        $popover = $body.find('input[name=schedule]');
                    event.preventDefault();
                    if ($click.attr('name') !== 'severityFilter') {
                        if ($icon.hasClass('icon-circle-arrow-down')) {
                            $icon.attr('class', 'icon-circle-arrow-up');
                            $body.collapse('show');
                            setTimeout(function () {
                                $body.css('overflow', 'visible');
                            }, 300);
                        } else {
                            if ($popover.data('popover')) {
                                $popover.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                $popover.popover('hide');
                                $popover.attr('checked', false);
                            }
                            $icon.attr('class', 'icon-circle-arrow-down');
                            $body.collapse('hide');
                            $body.css('overflow', 'hidden');
                        }
                    }
                },
                rebootNodes: function (event) {
                    var $scheduleForm, $button = $(event.currentTarget),
                        $group = $button.parents('.accordion-group'),
                        $nodes = $group.find('input[name=node]:checked'),
                        $schedule = $group.find('input[name=schedule]'),
                        tag = $group.find('input[name=tag]').val(),
                        $alert = this.$el.find('.alert').first(),
                        that = this,
                        url = 'submitForm',
                        operation = 'reboot',
                        params = {
                            tag: tag,
                            operation: operation,
                            node: []
                        };
                    if ($schedule.is(':checked')) {
                        $scheduleForm = $schedule.data('popover').options.content;
                        params.time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        params.label = $scheduleForm.find('input[name=label]').val() || 'Default';
                        params.offset = $scheduleForm.find('select[name=offset]').val();
                    }
                    if ($nodes.length) {
                        $nodes.each(function () {
                            params.node.push(this.value);
                        });
                        window.console.log(params);
                        $.post(url, params, function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                that.PatchCollection.fetch();
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').html(json.message).show();
                            }
                        });
                    } else {
                        $alert.removeClass('alert-success').addClass('alert-error').html('Please select a node.').show();
                    }
                },
                filterBySeverity: function (event) {
                    var patchName, severity, patchId, $itemDiv, $div, $descSpan, $label, $input, $rightSpan, $href,
                        option = $(event.currentTarget).val(),
                        $accordion = $(event.currentTarget).parents('.accordion-group'),
                        $badge = $(event.currentTarget).siblings('span'),
                        $items = $accordion.find('.items'),
                        patchNeed = this.patchcollection.toJSON()[0].packages_available,
                        newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        i = 0,
                        counter = 0;
                    $items.empty();
                    for (i = 0; i < patchNeed.length; i += 1) {
                        if (option === patchNeed[i].severity) {
                            patchName = patchNeed[i].name;
                            severity = patchNeed[i].severity;
                            patchId = patchNeed[i].id;
                            $itemDiv = newElement('div').addClass('item clearfix').attr('title', patchName);
                            $div = newElement('div').addClass('row-fluid');
                            $descSpan = newElement('span').addClass('desc span8');
                            $label = newElement('label').addClass('checkbox inline').html(patchName);
                            $input = newElement('input').attr({type: 'checkbox', name: 'patches', value: patchId, id: patchId});
                            $rightSpan = newElement('span').addClass('span4 alignRight');
                            $href = newElement('a').attr('href', '#patches/' + patchId).html('More information');
                            $rightSpan.append($href);
                            $descSpan.append($label.prepend($input));
                            $itemDiv.append($div.append($descSpan, $rightSpan));
                            $items.append($itemDiv);
                            counter += 1;
                        } else if (option === 'None') {
                            patchName = patchNeed[i].name;
                            severity = patchNeed[i].severity;
                            patchId = patchNeed[i].id;
                            $itemDiv = newElement('div').addClass('item clearfix').attr('title', patchName);
                            $div = newElement('div').addClass('row-fluid');
                            $descSpan = newElement('span').addClass('desc span8');
                            $label = newElement('label').addClass('checkbox inline').html(patchName);
                            $input = newElement('input').attr({type: 'checkbox', name: 'patches', value: patchId, id: patchId});
                            $rightSpan = newElement('span').addClass('span4 alignRight');
                            $href = newElement('a').attr('href', '#patches/' + patchId).html('More information');
                            $rightSpan.append($href);
                            $descSpan.append($label.prepend($input));
                            $itemDiv.append($div.append($descSpan, $rightSpan));
                            $items.append($itemDiv);
                            counter += 1;
                        }
                    }
                    if (counter === 0) {
                        $itemDiv = newElement('div').addClass('item clearfix');
                        $div = newElement('div').addClass('row-fluid');
                        $descSpan = newElement('span').addClass('desc span8').html('<em>No patches to display</em>');
                        $itemDiv.append($div.append($descSpan));
                        $items.append($itemDiv);
                    }
                    $badge.html(counter);
                },
                submitOperation: function (event) {
                    var $scheduleForm,
                        that = this,
                        $form = $(event.target),
                        $schedule = $form.find('input[name=schedule]'),
                        patches = $form.find('input[name="patches"]:checked'),
                        tag = $form.find('input[name=tag]').val(),
                        throttle = $form.find('select[name=throttle]').val(),
                        operation = $form.find('select[name=operation]').val(),
                        url = '/submitForm',
                        params = {
                            operation: operation,
                            tag: tag,
                            patches: []
                        };
                    if (throttle) {
                        params.throttle = throttle;
                    }
                    if ($schedule.is(':checked')) {
                        $scheduleForm = $schedule.data('popover').options.content;
                        params.time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        params.label = $scheduleForm.find('input[name=label]').val() || 'Default';
                        params.offset = $scheduleForm.find('select[name=offset]').val();
                    }
                    if (patches.length) {
                        patches.each(function () {
                            params.patches.push(this.value);
                        });
                        window.console.log(params);
                        $.post(url, params, function (json) {
                            window.console.log(json);
                            /*
                            if (schedule.data('popover')) {
                                schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                schedule.popover('hide');
                                schedule.attr('checked', false);
                            }
                            */
                            if (json.pass) {
                                that.PatchCollection.fetch();
                            } else {
                                that.$el.find('.alert').first().removeClass('alert-success').addClass('alert-error').html(json.message).show();
                            }
                        });
                    } else {
                        that.$el.find('.alert').first().removeClass('alert-success').addClass('alert-error').html('Please select a patch.').show();
                    }
                    return false;
                },
                beforeRender: $.noop,
                onRender: function () {
                    var $el = this.$el;
                    $el.find('input[name=schedule]').each(function () {
                        $(this).popover({
                            placement: 'top',
                            title: 'Patch Scheduling<button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            content: $el.find('#schedule-form').clone(),
                            trigger: 'click'
                        });
                    }).click(function () {
                        var close, popover = this;
                        if (popover.checked) {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            close = $(this).data('popover').$tip.find('button[name=close]');
                            close.unbind();
                            close.bind('click', function (event) {
                                event.preventDefault();
                                $(popover).data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                $(popover).popover('hide');
                                popover.checked = false;
                            });
                        } else {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                        }
                    });
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.statscollection.toJSON()[0],
                        patches = this.patchcollection.toJSON()[0];

                    this.$el.empty();

                    this.$el.append(template({data: data, patches: patches}));
                    if (!patches) {
                        this.showLoading('#loading');
                        this.showLoading('#installedGraph');
                        this.showLoading('#availableGraph');
                    } else {
                        this.stackedAreaGraph();
                    }

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);