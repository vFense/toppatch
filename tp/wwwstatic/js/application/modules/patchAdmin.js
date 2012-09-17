define(
    ['jquery', 'backbone', 'app', 'text!templates/patchAdmin.html' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {};
        exports.Model = Backbone.Model.extend({});
        exports.View = Backbone.View.extend({
            initialize: function () {
                this.template = myTemplate;
            },
            render: function () {
                var data = app.data.patches;

                var variables = { type: "patches", data: data };

                var tmpl = _.template(this.template, variables),
                    that = this;

                this.$el.html('');

                this.$el.append(tmpl);

                return this;
            }
        });
        return exports;
    }
);