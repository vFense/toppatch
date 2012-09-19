define(
    ['jquery', 'backbone', 'text!templates/widget.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var currentSpan = 0,
            exports = {
                Model: Backbone.Model.extend({
                    defaults: {
                        span: 6,
                        showMenu: false
                    },
                    validate: function (attrs) {
                        if (attrs.span < 1 || attrs.span > 12) {
                            return "Unexpected span size. Expected: 1 <= span <=  12.";
                        }
                    }
                }),
                View: Backbone.View.extend({
                    tagName: 'article',
                    className: 'widget',
                    initialize: function () {
                        this.template = myTemplate;
                        this.model.bind('change:span', this.renderSpan, this);
                    },
                    beforeRender: $.noop,
                    onRender: $.noop,
                    render: function () {
                        if (this.beforeRender !== $.noop) { this.beforeRender(); }

                        var tmpl = _.template(this.template),
                            that = this;

                        window.view = this;

                        this.$el.html('');

                        this.$el.append(tmpl(this.model.toJSON()));

                        this.renderSpan();

                        if (this.onRender !== $.noop) { this.onRender(); }
                        return this;
                    },
                    renderSpan: function () {
                        var newSpan = this.model.get('span');
                        this.$el.toggleClass(
                            'span' + currentSpan,
                            false
                        ).toggleClass(
                            'span' + this.model.get('span'),
                            true
                        );
                        currentSpan = newSpan;
                    }
                })
            };
        return exports;
    }
);