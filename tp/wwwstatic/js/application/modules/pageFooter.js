define(
    ['jquery', 'underscore', 'backbone', 'text!templates/pageFooter.html'],
    function ($, _, Backbone, footerTemplate) {
        "use strict";
        var PageFooter = {};
        PageFooter.View = Backbone.View.extend({
            tagName: 'footer',
            id: 'pageFooter',
            template: footerTemplate,
            initialize: function () {
                this.model = window.User;
            },
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                var tmpl = _.template(this.template);
                this.$el.html(tmpl(this.model.toJSON()));

                if (this.onRender !== $.noop) { this.onRender(); }

                return this;
            }
        });
        return PageFooter;
    }
);
