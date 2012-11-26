define(
    ['jquery', 'underscore', 'backbone', 'text!templates/patch.html', 'jquery.ui.datepicker' ],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/patches.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'submit form': 'submit'
                },
                submit: function (evt) {
                    var item, span, label, checkbox, $scheduleForm, type, nodes, url, offset,
                        $form = $(evt.target),
                        schedule = $form.find('input[name="schedule"]:checked'),
                        time = '';
                    if (schedule.length != 0) {
                        $scheduleForm = schedule.data('popover').options.content;
                        time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        label = $scheduleForm.find('input[name=label]').val() || 'Default';
                        offset = $scheduleForm.find('select[name=offset]').val();
                    }
                    type = $form.attr('id');
                    nodes = $form.find('input[name="node"]:checked');
                    url = '/submitForm?' + $form.serialize();
                    url += time ? '&time=' + time + '&label=' + label + '&offset=' + offset : '';
                    window.console.log(url);
                    $.post(url,
                        function (json) {
                            window.console.log(json);
                            if (schedule.data('popover')) {
                                schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                schedule.popover('hide');
                                schedule.attr('checked', false);
                            }
                            if (json.pass) {
                                $('.alert').removeClass('alert-error').addClass('alert-success').show().find('span').html('Operation sent.');
                                nodes.each(function () {
                                    item = $(this).parents('.item');
                                    span = $(this).parents('span');
                                    label = $(this).parent();
                                    checkbox = $(this);
                                    checkbox.remove();
                                    var patch = label.html();
                                    span.html(patch);
                                    label.remove();
                                    if (type === 'available' || type === 'failed') {
                                        item.appendTo($('#pending').children());
                                        if ($('#no-pending')) {
                                            $('#no-pending').remove();
                                        }
                                    } else {
                                        item.remove();
                                    }
                                });
                                if ($form.find('input:checked').attr('checked')) {
                                    $form.find('input:checked').attr('checked', false);
                                }
                            } else {
                                $('.alert').removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                    return false;
                },
                beforeClose: function () {
                    var schedule = this.$el.find('input[name="schedule"]:checked');
                    if (schedule.data('popover')) {
                        schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                        schedule.popover('destroy');
                    }
                },
                beforeRender: $.noop,
                onRender: function () {
                    var close;
                    $('input[name=schedule]').each(function () {
                        $(this).popover({
                            placement: 'top',
                            title: 'Patch Scheduling<button class="btn btn-link pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            content: $('#schedule-form').clone(),
                            trigger: 'click'
                        });
                    }).click(function () {
                        var popover = this;
                        if (popover.checked) {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            close = $(this).data('popover').$tip.find('a[name=close]');
                            close.bind('click', function () {
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
                        data = this.collection.toJSON()[0];

                    this.$el.empty();

                    this.$el.append(template({model: data}));

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
