define(
    ['jquery', 'underscore', 'backbone', 'modules/navBar', 'text!templates/pageHeader.html'],
    function ($, _, Backbone, DashNav, headerTemplate) {
        "use strict";
        var PageHeader = {};
        PageHeader.View = Backbone.View.extend({
            tagName: 'header',
            id: 'pageHeader',
            template: headerTemplate,
            initialize: function () {
                this.model = window.User;
            },
            events: {
                'change': 'render'
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
        return PageHeader;
    }
);
