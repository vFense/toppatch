define(
    ['jquery', 'backbone', 'text!templates/patches.html' ],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/patches.json',
                query: '',
                url: function () {
                    return this.baseUrl + this.query;
                },
                parse: function (response) {
                    this.recordCount = response.count;
                    return response.data;
                },
                initialize: function () {
                    this.offset   = this.offset || 0;
                    this.getCount = this.getCount  || 10;
                    this.query = this.type ?
                    '?' + 'type=' + this.type
                        + '&count=' + this.getCount
                        + '&offset=' + this.offset :
                    '?' + '&count=' + this.getCount
                        + '&offset=' + this.offset;

                    window.myCollection = this;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        payload = {
                            getCount: +this.collection.getCount,
                            offset: +this.collection.offset,
                            start: +this.collection.offset + 1,
                            end: +this.collection.offset + data.length,
                            prevEnable: +this.collection.offset > 0,
                            nextEnable: +this.collection.offset + data.length + 1 < +this.collection.recordCount,
                            prevLink: '',
                            nextLink: '',
                            recordCount: this.collection.recordCount,
                            data: data
                        },
                        that = this,
                        temp;

                    temp = payload.offset - payload.getCount;
                    payload.prevLink = '#patches?count=' + payload.getCount + '&offset=' + (temp < 0 ? 0 : temp);

                    temp = payload.offset + payload.getCount;
                    payload.nextLink = '#patches?count=' + payload.getCount + '&offset=' + temp;

                    this.$el.html('');

                    this.$el.append(template(payload));

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
