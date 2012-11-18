define(
    ['jquery', 'underscore', 'backbone', 'module/someModel', 'text!templates/aTemplate.html' ],
    function ($, _, Backbone, myModel, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/patches.json',
                params: '',
                url: function () {
                    return this.baseUrl + this.query;
                },
                parse: function (response) {
                    this.recordCount = response.count;
                    return response.data;
                },
                initialize: function (options) {
                    this.offset   = this.offset || 0;
                    this.getCount = this.getCount  || 20;
                    this.type = this.type || '';

                    this.query = '?count=' + this.getCount + '&offset=' + this.offset;
                    if (this.type) {
                        this.query += '&type=' + this.type;
                    }
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    if (!this.collection) {
                        this.collection =  new exports.Collection();
                    }
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var tmpl = _.template(this.template),
                        that = this;

                    this.$el.empty();

                    _.each(this.collection.models, function (item) {
                        that.renderModel(item);
                    }, this);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                renderModel: function (item) {
                    $.noop(item);
                }
            })
        };
        return exports;
    }
);