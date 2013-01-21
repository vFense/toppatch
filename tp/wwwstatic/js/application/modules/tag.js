/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/11/13
 * Time: 8:30 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/tag.html', 'jquery.ui.datepicker'],
    function ($, _, Backbone, myTemplate) {
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
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.statscollection =  new exports.StatsCollection();
                    this.statscollection.bind('reset', this.render, this);
                    this.statscollection.fetch();

                    this.patchcollection = new exports.PatchCollection();
                    this.patchcollection.bind('reset', this.render, this);
                    this.patchcollection.fetch();
                },
                events: {
                    'click a.accordion-toggle': 'toggleAccordion',
                    'click .toggle-all': 'toggleAllInputs',
                    'submit form': 'submitOperation'
                },
                toggleAllInputs: function (event) {
                    var status = event.target.checked,
                        form = $(event.target).parents('form');
                    $(form).find(":checkbox[name=patches]").each(function () {
                        $(this).attr("checked", status);
                    });
                },
                toggleAccordion: function (event) {
                    var $href = $(event.currentTarget),
                        $icon = $href.find('i'),
                        $parent = $href.parents('.accordion-group'),
                        $body = $parent.find('.accordion-body').first(),
                        $popover = $body.find('input[name=schedule]');
                    event.preventDefault();
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
                },
                submitOperation: function (event) {
                    var $scheduleForm, patches,
                        that = this,
                        $form = $(event.target),
                        $schedule = $form.find('input[name=schedule]'),
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
                    patches = $form.find('input[name="patches"]:checked');
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
                    window.console.log(patches);

                    this.$el.empty();

                    this.$el.append(template({data: data, patches: patches}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
