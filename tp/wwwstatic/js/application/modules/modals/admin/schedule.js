/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/26/13
 * Time: 11:01 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/schedule.html', 'jquery.ui.slider'],
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
                        that = this,
                        url = '',
                        $alert = this.$el.find('.alert');
                    console.log($form);
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
                        $slide = $el.find('#slider-range');
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
                },//$.noop,
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
