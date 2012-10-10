define(
    ['jquery', 'backbone', 'modules/navBar', 'text!templates/pageHeader.html'],
    function ($, Backbone, DashNav, headerTemplate) {
        "use strict";
        var PageHeader = {};
        PageHeader.View = Backbone.View.extend({
            el: $('<header>')
                .attr('id', 'pageHeader'),
            template: headerTemplate,
            initialize: function () {
                this.model = window.User;
            },
            events: {
                'change': 'render'
            },
            render: function () {
                var tmpl = _.template(this.template);
                this.$el.html(tmpl(this.model.toJSON()));
                return this;
            }
        });
        return PageHeader;
    }
);