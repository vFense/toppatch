/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/26/13
 * Time: 11:01 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/schedule.html', 'jquery.ui.datepicker', 'jquery.ui.slider'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: '',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    //this.collection = new exports.Collection();
                    //this.collection.bind('reset', this.render, this);
                    //this.collection.fetch();
                },
                events: {
                    'submit form': 'submit'
                },
                submit: function (event) {
                    var $form = $(event.target),
                        params = {},
                        that = this,
                        url = '',
                        $alert = this.$el.find('.alert'),
                        $inputs = $form.find('input, select'),
                        invalid = false;
                    $inputs.each(function () {
                        if (this.name !== 'start_date') {
                            if (this.value === '-1' || !this.value) {
                                $(this).parents('.control-group').addClass('error');
                                $alert.removeClass('alert-success alert-info').addClass('alert-error').html('Please fill the required fields.').show();
                                invalid = true;
                            } else {
                                $(this).parents('.control-group').removeClass('error');
                                params[this.name] = this.value;
                            }
                        }
                    });
                    window.console.log(params);
                    if (invalid) { return false; }
                    //$alert.removeClass('alert-success alert-error').addClass('alert-info').html('Submitting...');
                    /*$.post(url, function (json) {
                        window.console.log(json);
                        if (!json.pass) {
                            $alert.removeClass('alert-success alert-info').addClass('alert-error').html(json.message);
                        } else {
                            $alert.removeClass('alert-error alert-info').addClass('alert-success').html(json.message);
                        }
                        $alert.show();
                    });*/
                    return false;
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
                            minutes = minutes < 10 ? '0' + minutes : minutes;
                            hours = Math.floor(ui.value / 60);
                            hours = hours < 10 ? '0' + hours : hours;
                            startTime = hours > 12 ? String(hours - 12) : String(hours);
                            startTime = hours >= 12 ? startTime + ':' + minutes + ' PM' : startTime + ':' + minutes + ' AM';
                            $(event.target).siblings('label').html('Time: ' + startTime);
                            that.time = startTime;
                        }
                    });
                    $dateInput.datepicker();
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);
                        //data = this.collection.toJSON()[0];
                    this.$el.empty();

                    this.$el.html(template({}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
