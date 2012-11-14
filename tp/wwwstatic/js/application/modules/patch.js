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
                    var $form = $(evt.target),
                        schedule = $form.find('input[name="schedule"]:checked'),
                        time = '',
                        item, span, label, checkbox, $scheduleForm, type, nodes, url, date, label;
                    if(schedule.length != 0) {
                        $scheduleForm = schedule.data('popover').options.content;
                        time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        date = new Date(time).getTime();
                        label = $scheduleForm.find('input[name=label]').val() ? $scheduleForm.find('input[name=label]').val() : 'Default';
                    }
                    type = $form.attr('id');
                    nodes = $form.find('input[name="node"]:checked');
                    url = '/submitForm?' + $form.serialize();
                    url += time ? '&time=' + date + '&label=' + label: '';
                    console.log(url);
                    $.post(url,
                        function(json) {
                            console.log(json);
                            if(schedule.data('popover')) {
                                schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                schedule.popover('hide');
                            }
                            $('.alert').show();
                        });
                    nodes.each(function () {
                        item = $(this).parents('.item');
                        span = $(this).parents('span');
                        label = $(this).parent();
                        checkbox = $(this);
                        checkbox.remove();
                        var patch = label.html();
                        span.html(patch);
                        label.remove();
                        if(type == 'available' || type == 'failed') {
                            item.appendTo($('#pending').children());
                            if($('#no-pending')) {
                                $('#no-pending').remove();
                            }
                        } else {
                            item.remove();
                        }
                    });
                    if($form.find('input:checked').attr('checked')) {
                        $form.find('input:checked').attr('checked', false);
                    }
                    return false;
                },
                beforeRender: $.noop,
                onRender: $.noop,
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
