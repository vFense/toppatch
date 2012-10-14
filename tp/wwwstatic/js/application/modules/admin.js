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
                    var form = $(evt.target);
                    $.post("/adminForm?" + form.serialize(),
                        function(json) {
                            console.log(json);
                            form.find('.control-group').addClass('success');
                            form.find('.controls').append("<span class='help-inline'>Password changed!</span>");
                            form.find('input[type=text]').val('');
                        }
                    );
                    return false;
                },
                clear: function (evt) {
                    var userName = window.User.get('name');
                    localStorage.removeItem(userName);
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