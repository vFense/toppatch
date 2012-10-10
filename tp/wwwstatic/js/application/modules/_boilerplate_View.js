define(
    ['jquery', 'backbone', 'text!templates/aTemplate.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            beforeRender: $.noop,
            onRender: $.noop,
            View: Backbone.View.extend({
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var tmpl = _.template(this.template),
                        that = this;

                    this.$el.html('');

                    this.$el.append(tmpl());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);