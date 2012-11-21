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
                this.collection =  new exports.Collection(this.tabs);
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
                var tabView = new button.View({
                    model: model
                });
                this.$el.append(tabView.render().el);
            },

            setActive: function (hrefTarget) {
                _.each(this.collection.models, function (model) {
                    model.set('active', model.get('href') === hrefTarget);
                });
            }
        });

        return exports;
    }
);
