define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/main.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'admin-main-view',
                initialize: function () {
                    this.template = myTemplate;
                },

                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        template = _.template(this.template),
                        $el = this.$el;

                    $el.empty();
                    $el.html(template({}));

                    if (this.onRender !== $.noop) { this.onRender(); }

                    this.rendered = true;

                    return this;
                }
            })
        };
    }
);
