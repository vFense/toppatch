define(
    ['jquery', 'underscore', 'backbone'],
    function ($, _, Backbone) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/transactions/getTransactions',
                params: {
                    // defaults
                    offset: 0,
                    count: 20
                },
                url: function () {
                    var query = '?' + $.param(this.params).trim(),
                        url = this.baseUrl;

                    if (query !== '?') { url += query; }

                    return url;
                },
                parse: function (response) {
                    this.recordCount = response.count;
                    return response.data;
                },
                initialize: function (options) {
                    console.log('init constructor');
                    if (options.params) {
                        _.extend(this.params, _.pick(options.params, _.keys(this.params)));
                    }
                }
            }),
            View: Backbone.View.extend({
                initialize: function (options) {
                    console.log('init view');
                    if (options) {
                        _.extend(this, _.pick(options, ['collection']));
                    }

                    if (!this.collection instanceof Backbone.Collection) {
                        this.collection =  new exports.Collection();
                    }

                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this;

                    this.$el.empty();
                    this.$el.html('hello world');

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