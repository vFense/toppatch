define(
    ['jquery', 'backbone', 'text!templates/admin.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.fetch();
                },
                events: {
                    'submit form' :  'submit',
                    'click #clear' : 'clear'
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
                    }
                    return false;
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
                        that = this;
                    this.$el.empty();

                    this.$el.append(template());


                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
