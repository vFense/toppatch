define(
    ['jquery', 'backbone', 'text!templates/admin.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                },
                events: {
                    'submit form': 'submit',
                    'click #clear': 'clear'
                },
                submit: function (evt) {
                    var form = $(evt.target),
                        password = form.find('input[type=text]'),
                        controlgroup = form.find('.control-group'),
                        controls = form.find('.controls'),
                        helptext = form.find('.help-inline');
                    if(password.val()) {
                        $.post("/adminForm?" + form.serialize(),
                            function(json) {
                                console.log(json);
                                controlgroup.removeClass('error').addClass('success');
                                helptext.remove();
                                controls.append("<span class='help-inline'>Password changed!</span>");
                                password.val('');
                            }
                        );
                    } else {
                        controlgroup.removeClass('success').addClass('error');
                        helptext.remove();
                        controls.append("<span class='help-inline'>Password is blank!</span>");
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
                    this.$el.html('');

                    this.$el.append(template());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);