define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/timeblock.html', 'jquery.ui.datepicker', 'jquery.ui.slider'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        return {
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.start = '8:00 AM';
                    this.end = '5:00 PM';
                    this.days = '0000000';
                },
                events: {
                    'click #dow' : 'highlight',
                    'click #add' :   'add',
                    'click #dowselect': 'changeselect'
                },
                add: function (evt) {
                    var start_time, end_time, start_date, end_date, params, label, days, startdatestring, enddatestring,
                        values = $("#dow").data('popover').options.content.val() || false,
                        that = this;
                    this.highlight(evt);
                    start_time = this.start;
                    end_time = this.end;
                    //start_date = new Date($('input[name=startdate]').val()).getTime();
                    end_date = $('input[name=enddate]').val() ? new Date($('input[name=enddate]').val()).getTime() : '';
                    label = $('input[name=label]').val();
                    startdatestring = new Date($('input[name=startdate]').val() + ' ' + start_time);
                    enddatestring = new Date($('input[name=startdate]').val() + ' ' + end_time);
                    days = this.days;

                    params = {
                        label: label,
                        enabled: true,
                        start_date: startdatestring.getTime(),
                        end_date: end_date,
                        start_time: startdatestring.getTime(),
                        end_time: enddatestring.getTime(),
                        days: days
                    };
                    if (values) {
                        window.console.log(params);

                        $.post("/api/timeblocker/add", { operation: JSON.stringify(params) },
                            function (result) {
                                window.console.log(result);
                                if (result.pass) {
                                    if ($('#dow').data('popover')) { $('#dow').popover('hide'); }
                                    that.$el.find('.alert').html(result.message).removeClass('alert-error').addClass('alert-success').show();
                                } else {
                                    that.$el.find('.alert').html(result.message).removeClass('alert-success').addClass('alert-error').show();
                                }
                            });
                            
                    } else {
                        that.$el.find('.alert').html('You must select at least one day of the week.').removeClass('alert-success').addClass('alert-error').show();
                    }
                },
                highlight: function (evt) {
                    if ($(evt.target).data('popover')) {
                        $(evt.target).data('popover').tip().css('z-index', 3000);
                    }
                    var values = $("#dowselect").val(), string = '', days = '', i;
                    if (values) {
                        for (i = 0; i < values.length; i += 1) {
                            if (values[i] === 'Su') {
                                string += '<strong>Su</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'Su ';
                                days += '0';
                            }
                            if (values[i] === 'M') {
                                string += '<strong>M</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'M ';
                                days += '0';
                            }
                            if (values[i] === 'Tu') {
                                string += '<strong>Tu</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'Tu ';
                                days += '0';
                            }
                            if (values[i] === 'W') {
                                string += '<strong>W</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'W ';
                                days += '0';
                            }
                            if (values[i] === 'Th') {
                                string += '<strong>Th</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'Th ';
                                days += '0';
                            }
                            if (values[i] === 'F') {
                                string += '<strong>F</strong> ';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'F ';
                                days += '0';
                            }
                            if (values[i] === 'Sa') {
                                string += '<strong>Sa</strong>';
                                days += '1';
                                i += 1;
                            } else {
                                string += 'Sa ';
                                days += '0';
                            }
                        }
                        this.days = days;
                        $("#dow").html(string);
                    }
                },
                beforeRender: $.noop,
                onRender: function () {
                    var that = this,
                        $el = this.$el,

                        // jquery element cache
                        $pop = $el.find('#dow'),
                        $popper = $el.find('#dowselect'),
                        $slide = $el.find("#slider-range"),
                        $startDate = $el.find('input[name="startdate"]'),
                        $endDate = $el.find('input[name="enddate"]');

                    $pop.popover({
                        placement: 'right',
                        title: 'Days of Week',
                        html: true,
                        content: $popper,
                        trigger: 'click'
                    });

                    $slide.slider({
                        range: true,
                        min: 0,
                        max: 1439,
                        values: [ 480, 1020 ],
                        slide: function (event, ui) {
                            var startHours, endHours, startMinutes, endMinutes, startTime, endTime;
                            startMinutes = ui.values[0] % 60;
                            startMinutes = startMinutes < 10 ? '0' + startMinutes : startMinutes;
                            endMinutes = ui.values[1] % 60;
                            endMinutes = endMinutes < 10 ? '0' + endMinutes : endMinutes;
                            startHours = Math.floor(ui.values[0] / 60);
                            endHours = Math.floor(ui.values[1] / 60);
                            startTime = startHours > 12 ? (startHours - 12) + ':' + startMinutes + ' PM' : startHours + ':' + startMinutes + ' AM';
                            endTime = endHours > 12 ? (endHours - 12) + ':' + endMinutes + ' PM' : endHours + ':' + endMinutes + ' AM';
                            $(event.target).siblings('label').html('Time Range: ' + startTime + ' to ' + endTime);
                            that.start = startTime;
                            that.end = endTime;
                        }
                    });

                    $startDate.datepicker({
                        onSelect: this.selectMultiple,
                        option: { view: this }
                    });
                    $endDate.datepicker();
                },
                selectMultiple: function (dateText, object) {
                    window.console.log(object); //object
                    //window.console.log(this);  //html input
                    var date = new Date(dateText),
                        day = date.getDay();
                    $("#dowselect option").each(function (i, option) {
                        option.selected = false;
                        if (i === day) {
                            option.selected = true;
                        }
                    });
                    object.target = this;
                    window.console.log(dateText);
                    object.settings.option.view.highlight(object);
                    //this.highlight(object);
                },
                changeselect: function (event) {
                    window.console.log(event);
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);

                    this.$el.empty();

                    this.$el.html(template());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },

                beforeClose: function () {
                    var $popover = this.$el.find('#dow');
                    if ($popover.data('popover')) {
                        $popover.popover('destroy');
                    }
                }
            })
        };
    }
);
