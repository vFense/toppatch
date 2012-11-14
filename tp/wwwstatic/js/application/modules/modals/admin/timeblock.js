define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/timeblock.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        return {
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                },
                events: {
                    'click #dow' : 'highlight',
                    'click #add' :   'add'
                },
                add: function (evt) {
                    var from, to, values = $("#dow").data('popover').options.content.val();
                    from = $('select[name=hours]')[0].value + ':' + $('select[name=minutes]')[0].value + ' ' + $('select[name=ampm]')[0].value;
                    to = $('select[name=hours]')[1].value + ':' + $('select[name=minutes]')[1].value + ' ' + $('select[name=ampm]')[1].value;
                    console.log(values);
                    if (values) {
                        //$('.items').append('<div class="item">From: ' + from + ' To: ' + to + ' On: '+ $('#dow').html() + '</div>');
                        console.log('From: ' + from + ' To: ' + to + ' On: '+ $('#dow').html())
                    }
                    this.highlight(evt);
                    if ($('#dow').data('popover')) { $('#dow').popover('hide'); }
                },
                highlight: function (evt) {
                    var values = $("#dowselect").val(), string = '';
                    if(values) {
                        for(var i = 0; i < values.length; i++) {
                            if(values[i] == 'M') {
                                string += '<strong>M</strong> ';
                                i++;
                            } else {
                                string += 'M '
                            }
                            if(values[i] == 'Tu') {
                                string += '<strong>Tu</strong> ';
                                i++;
                            } else {
                                string += 'Tu '
                            }
                            if(values[i] == 'W') {
                                string += '<strong>W</strong> ';
                                i++;
                            } else {
                                string += 'W '
                            }
                            if(values[i] == 'Th') {
                                string += '<strong>Th</strong> ';
                                i++;
                            } else {
                                string += 'Th '
                            }
                            if(values[i] == 'F') {
                                string += '<strong>F</strong> ';
                                i++;
                            } else {
                                string += 'F '
                            }
                            if(values[i] == 'Sa') {
                                string += '<strong>Sa</strong> ';
                                i++;
                            } else {
                                string += 'Sa '
                            }
                            if(values[i] == 'Su') {
                                string += '<strong>Su</strong>';
                                i++;
                            } else {
                                string += 'Su '
                            }
                        }
                        $("#dow").html(string);
                    }
                },
                beforeRender: $.noop,
                onRender: function () {
                    this.$el.find('#dow').popover({
                        placement: 'right',
                        title: 'Days of Week',
                        html: true,
                        content: this.$el.find('#dowselect'),
                        trigger: 'click'
                    });
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);

                    this.$el.empty();

                    this.$el.html(template());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
    }
);
