define(
    ['jquery', 'backbone', 'text!templates/pageFooter.html'],
    function ($, Backbone, footerTemplate) {
        "use strict";
        var PageFooter = {};
        PageFooter.View = Backbone.View.extend({
            el: $('<footer>')
                .attr('id', 'pageFooter'),
            template: footerTemplate,
            initialize: function () {
                this.model = window.User;
            },
            render: function () {
                var tmpl = _.template(this.template);
                this.$el.html(tmpl(this.model.toJSON()));
                return this;
            }
        });
        return PageFooter;
    }
);