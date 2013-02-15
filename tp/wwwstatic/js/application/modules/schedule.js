define(
    ['jquery', 'underscore', 'backbone', 'text!templates/schedule.html', 'jquery.ui.datepicker', 'jquery.ui.slider', 'jquery.ui.timepicker'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/scheduler/list.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            NodeCollection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
                }
            }),
            TagCollection: Backbone.Collection.extend({
                baseUrl: 'api/tagging/listByTag.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.minutes = '0';
                    this.hours = '0';
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.nodecollection = new exports.NodeCollection();
                    this.nodecollection.bind('reset', this.render, this);
                    this.nodecollection.fetch();

                    this.tagcollection = new exports.TagCollection();
                    this.tagcollection.bind('reset', this.render, this);
                    this.tagcollection.fetch();
                },
                events: {
                    'click button[name=remove]': 'removeSchedule',
                    'change select[name=operation]':    'hideSeverity',
                    'click button[name=toggleAddSchedule]': 'toggleAddSchedule',
                    'click button[name=addSchedule]': 'addSchedule'
                },
                toggleAddSchedule: function (event) {
                    var $button = $(event.currentTarget),
                        $scheduleDiv = this.$el.find('#scheduleDiv'),
                        $form = $scheduleDiv.find('form');
                    event.preventDefault();
                    $scheduleDiv.toggle();
                    $form[0].reset();
                },
                hideSeverity: function (event) {
                    var option = $(event.currentTarget).val(),
                        $select = this.$el.find('select[name=severity]'),
                        $severity = $select.parents('.control-group');
                    if (option === 'reboot') {
                        $select.attr('disabled', true).addClass('disabled');
                    } else {
                        $select.attr('disabled', false).removeClass('disabled');
                    }
                },
                addSchedule: function (event) {
                    var $form = $(event.currentTarget).parents('article').first(),
                        that = this,
                        url = 'api/scheduler/recurrent/add',
                        $alert = this.$el.find('.alert'),
                        $inputs = $form.find('input:not([name=time]), select:not([multiple], :disabled)'),
                        $multiple = $form.find('select[multiple]'),
                        time = $form.find('input[name=time]').val().split(':'),
                        invalid = false,
                        params = {
                            hours: time[0],
                            minutes: time[1]
                        };
                    event.preventDefault();
                    $inputs.each(function () {
                        if (this.name !== 'start_date') {
                            if (this.value === '-1' || !this.value) {
                                $(this).parents('.control-group').addClass('error');
                                invalid = true;
                            } else {
                                $(this).parents('.control-group').removeClass('error');
                                if (this.value !== 'any') {
                                    params[this.name] = this.value;
                                }
                            }
                        }
                    });
                    $multiple.each(function () {
                        var options = $(this).val();
                        if (options && options.length) {
                            if (options[0] === 'any') { options.splice(0, 1); }
                            $(this).parents('.control-group').removeClass('error');
                            if (options.length > 0) {
                                params[this.name] = options;
                            }
                        } else {
                            $(this).parents('.control-group').addClass('error');
                            invalid = true;
                        }
                    });
                    window.console.log(params);
                    if (invalid) {
                        $alert.removeClass('alert-success alert-info').addClass('alert-error').html('Please fill the required fields.').show();
                        return false;
                    }
                    $alert.removeClass('alert-success alert-error').addClass('alert-info').html('Submitting...');
                    $.post(url, params, function (json) {
                        window.console.log(json);
                        if (!json.pass) {
                            $alert.removeClass('alert-success alert-info').addClass('alert-error').html(json.message);
                        } else {
                            $alert.removeClass('alert-error alert-info').addClass('alert-success').html(json.message);
                            that.collection.fetch();
                        }
                        $alert.show();
                    });
                    return false;
                },
                removeSchedule: function (event) {
                    var that = this,
                        $removeButton = $(event.currentTarget),
                        jobname = $removeButton.val(),
                        $item = $removeButton.parents('.item'),
                        $alert = this.$el.find('.alert').first();
                    $.post('api/scheduler/remove', {jobname: jobname}, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            that.collection.fetch();
                        } else {
                            $alert.removeClass('alert-error').addClass('alert-success').html(json.message).show();
                        }
                    });
                },
                beforeRender: $.noop,
                onRender: function () {
                    var $el = this.$el,
                        that = this,
                        $slide = $el.find('#slider-range'),
                        $dateInput = $el.find('input[name=start_date]'),
                        $timeInput = $el.find('input[name=time]');
                    $el.find('label').show();
                    $dateInput.datepicker();
                    $timeInput.timepicker();
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        schedules = this.collection.toJSON(),
                        tags = this.tagcollection.toJSON(),
                        nodes = this.nodecollection.toJSON(),
                        data = {
                            schedules : schedules,
                            tags : tags,
                            nodes: nodes[0]
                        };
                    this.$el.empty();

                    this.$el.append(template({data: data}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
