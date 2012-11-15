define(
    ['jquery', 'backbone', 'app', 'text!templates/node.html', 'jquery.ui.datepicker' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'click .disabled': function (e) { console.log(['click a.disabled', e]); return false; },
                    'click #addTag': 'showtags',
                    'submit form': 'submit'
                },
                beforeRender: $.noop,
                onRender: function () {
                    this.$el.find('#addTag').popover({
                        title: 'Tags Available',
                        html: true,
                        trigger: 'click',
                        content: $('#list-form')
                    });
                    this.$el.find('input[name=schedule]').each(function () {
                        $(this).popover({
                            placement: 'top',
                            title: 'Patch Scheduling',
                            html: true,
                            content: $('#schedule-form').clone(),
                            trigger: 'click'
                        });
                    }).click(function () {
                            if(this.checked) {
                                $(this).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            } else {
                                $(this).data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                            }
                    });
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON()[0];
                    this.$el.html('');
                    this.$el.append(template({model: data}));

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                submit: function (evt) {
                    var $form = $(evt.target),
                        schedule = $form.find('input[name="schedule"]:checked'),
                        time = '',
                        item, span, label, checkbox, $scheduleForm, type, patches, url, date, label;
                    if(schedule.length != 0) {
                        $scheduleForm = schedule.data('popover').options.content;
                        time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        date = new Date(time).getTime();
                        label = $scheduleForm.find('input[name=label]').val() ? $scheduleForm.find('input[name=label]').val() : 'Default';
                    }
                    type = $form.attr('id');
                    patches = $form.find('input[name="patches"]:checked');
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
                    patches.each(function () {
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
                showtags: function (evt) {
                    var popover = $(evt.target).parent().data('popover'), newTag;
                    if(popover) {
                        newTag = popover.$tip.find('a');
                        newTag.show().siblings('div').hide();
                        newTag.bind('click',function() {
                            $(this).hide().siblings('div').show();
                        });
                    }
                    return false;
                },
                beforeClose: function () {
                    var schedule = this.$el.find('input[name="schedule"]:checked');
                    if (schedule.data('popover')) {
                        schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                        schedule.popover('destroy');
                    }
                },
                clearFilter: function () {
                    this.collection.filter = '';
                }
            })
        };
        return exports;
    }
);
