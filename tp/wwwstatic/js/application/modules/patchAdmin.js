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
                var tmpl = _.template(this.template),
                    that = this;

                this.$el.html('');

                this.$el.append(tmpl({ type: "patches", data: app.data.patches }));

                return this;
            }
        });
        return exports;
    }
);