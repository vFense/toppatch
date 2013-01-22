define(
    ['jquery', 'underscore', 'backbone', './tabButton'],
    function ($, _, Backbone, button) {
        "use strict";
        var exports = {};

        exports.Collection = Backbone.Collection.extend({
            model: button.Model
        });

        exports.View = Backbone.View.extend({
            tagName: 'ul',
            className: 'nav nav-tabs',

            initialize: function (args) {
                _.extend(this, args);
                this.collection = new exports.Collection(this.tabs);
                this.lastTarget = '';
            },

            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                var $el = this.$el,
                    that = this;

                $el.empty();

                _.each(this.collection.models, function (model) {
                    that.renderTab(model);
                }, this);

                this.delegateEvents();

                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            },

            renderTab: function (model) {
                if (!(model.get('view') instanceof Backbone.View)) {
                    model.set('view', new button.View({
                        model: model
                    }));
                }

                this.$el.append(model.get('view').render().el);

                return this;
            },

            setActive: function (hrefTarget) {
                if (this.lastTarget !== hrefTarget) {
                    this.lastTarget = hrefTarget;
                    _.each(this.collection.models, function (model) {
                        model.set('active', model.get('href') === hrefTarget);
                    });
                }
                return this;
            }
        });

        return exports;
    }
);
