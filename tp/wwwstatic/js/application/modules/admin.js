define(
    ['jquery', 'backbone', 'text!templates/admin.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection : Backbone.Collection.extend({
                baseUrl: 'api/csrinfo.json/',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
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
                    'submit form' :  'submit',
                    'click #clear' : 'clear',
                    'click #add' :   'add',
                    'click #dow' :   'highlight'
                },
                submit: function (evt) {
                    var form = $(evt.target);
                    if(form.attr('id') == 'password-form') {
                        var password = form.find('input[name=password]'),
                            newpassword = form.find('input[name=new-password]'),
                            oldpassword = form.find('input[name=old-password]'),
                            passwordcontrols = password.parent(),
                            newpasswordcontrols = newpassword.parent(),
                            oldpasswordcontrols = oldpassword.parent(),
                            controlgroup = form.find('.control-group'),
                            helptext = form.find('.help-inline');

                        if(password.val() && newpassword.val() && oldpassword.val()) {
                            if(password.val() === newpassword.val()) {
                                $.post("/adminForm?" + form.serialize(),
                                    function(json) {
                                        console.log(json);
                                        if(json.error) {
                                            controlgroup.removeClass('success').addClass('error');
                                            helptext.remove();
                                            oldpasswordcontrols.append("<span class='help-inline'>Wrong password.</span>");
                                        } else {
                                            controlgroup.removeClass('error').addClass('success');
                                            helptext.remove();
                                            form.append("<span class='help-inline' style='color: #468847'>Password changed&nbsp;<i style='color: green;' class='icon-ok'></i></span>");
                                            password.val('');
                                            newpassword.val('');
                                            oldpassword.val('');
                                        }
                                    }
                                );
                            } else {
                                helptext.remove();
                                controlgroup.removeClass('success').addClass('error');
                                passwordcontrols.append("<span class='help-inline'>Password does not match.</span>");
                                newpasswordcontrols.append("<span class='help-inline'>Password does not match.</span>");
                            }
                        } else {
                            controlgroup.removeClass('success').addClass('error');
                            helptext.remove();
                            if(!password.val()) {
                                passwordcontrols.append("<span class='help-inline'>Password is blank!</span>");
                            }
                            if(!newpassword.val()) {
                                newpasswordcontrols.append("<span class='help-inline'>Password is blank!</span>");
                            }
                            if(!oldpassword.val()) {
                                oldpasswordcontrols.append("<span class='help-inline'>Password is blank!</span>");
                            }
                        }
                    } else {
                        console.log(form.serialize());
                        $.post("/adminForm?" + form.serialize(),
                            function(json) {
                                console.log(json);
                                if(!json.error) {
                                    form.find('input:checked').parents('.item').remove();
                                } else {
                                    console.log('Error while processing the CSRs');
                                }
                            }
                        );
                    }
                    return false;
                },
                add: function (evt) {
                    var from, to, values = $("#dow").data('popover').options.content.val();
                    from = $('select[name=hours]')[0].value + ':' + $('select[name=minutes]')[0].value + ' ' + $('select[name=ampm]')[0].value;
                    to = $('select[name=hours]')[1].value + ':' + $('select[name=minutes]')[1].value + ' ' + $('select[name=ampm]')[1].value;
                    console.log(values);
                    if (values) {
                        $('.items').append('<div class="item">From: ' + from + ' To: ' + to + ' On: '+ $('#dow').html() + '</div>');
                    }
                },
                highlight: function(evt) {
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
                clear: function (evt) {
                    var userName = window.User.get('name');
                    localStorage.removeItem(userName);
                    $('#clear-ok').show();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        that = this,
                        data = this.collection.toJSON();
                    this.$el.empty();

                    this.$el.append(template({data: data}));

                    $("#dow").popover({
                        placement: 'right',
                        title: 'Days of Week',
                        html: true,
                        content: $('#dowselect'),
                        trigger: 'click'
                    });

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
