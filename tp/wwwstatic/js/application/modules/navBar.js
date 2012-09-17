define(
    ['jquery', 'backbone', 'app', './navButton'],
    function ($, Backbone, app, navButton) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                model: navButton.Model
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.collection =  new exports.Collection(window.User.get('access'));
                    this.vent = app.vent;
                    this.vent.bind('nav', this.setActive, this);
                    this.render();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this;
                    this.$el.html('');
                    _.each(this.collection.models, function (item) {
                        that.renderButton(item);
                    }, this);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                renderButton: function (item) {
                    var buttonView = new navButton.View({
                        model: item
                    });
                    this.$el.append(buttonView.render().el);
                },
                setActive: function (hrefTarget) {
                    _.each(this.collection.models, function (model) {
                        //console.log(model.get('href') === hrefTarget);
                        model.set('active', model.get('href') === hrefTarget);
                    });
                }
            })
        };
        return exports;
    }
);