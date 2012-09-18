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
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                var tmpl = _.template(this.template),
                    that = this;

                this.$el.html('');

                this.$el.append(tmpl({ type: "patches", data: app.data.patches }));

                app.vent.trigger('domchange:title', 'Patch Administration');

                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            }
        });
        return exports;
    }
);