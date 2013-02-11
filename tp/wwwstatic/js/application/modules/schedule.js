define(
    ['jquery', 'underscore', 'backbone', 'text!templates/schedule.html', 'jquery.ui.datepicker', 'jquery.ui.slider'],
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
                        $scheduleDiv = this.$el.find('#scheduleDiv');
                    $scheduleDiv.toggle();
                },
                hideSeverity: function (event) {
                    var option = $(event.currentTarget).val(),
                        $severity = this.$el.find('select[name=severity]').parents('.control-group');
                    if (option === 'reboot') {
                        $severity.hide();
                    } else {
                        $severity.show();
                    }
                },
                addSchedule: function (event) {
                    var $form = $(event.currentTarget).parents('article').first(),
                        that = this,
                        url = 'api/scheduler/recurrent/add',
                        $alert = this.$el.find('.alert'),
                        $inputs = $form.find('input, select:not(:hidden)'),
                        invalid = false,
                        params = {
                            minutes: this.minutes,
                            hours: this.hours
                        };
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
                        $dateInput = $el.find('input[name=start_date]');
                    $el.find('label').show();
                    $slide.slider({
                        min: 0,
                        max: 1439,
                        slide: function (event, ui) {
                            var hours, minutes, startTime;
                            minutes = ui.value % 60;
                            that.minutes = minutes;
                            minutes = minutes < 10 ? '0' + minutes : minutes;
                            hours = Math.floor(ui.value / 60);
                            that.hours = hours;
                            hours = hours < 10 ? '0' + hours : hours;
                            startTime = hours > 12 ? String(hours - 12) : String(hours);
                            startTime = hours >= 12 ? startTime + ':' + minutes + ' PM' : startTime + ':' + minutes + ' AM';
                            $(event.target).siblings('label').html('Time: ' + startTime);
                        }
                    });
                    $dateInput.datepicker();
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
