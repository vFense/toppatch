define(
    ['jquery', 'backbone', 'module/someModel', 'text!templates/aTemplate.html' ],
    function ($, Backbone, myModel, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                model: myModel.Model
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection(['anArray']);
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var tmpl = _.template(this.template),
                        that = this;

                    this.$el.html('');

                    _.each(this.collection.models, function (item) {
                        that.renderModel(item);
                    }, this);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                renderModel: function (item) {}
            })
        };
        return exports;
    }
);
