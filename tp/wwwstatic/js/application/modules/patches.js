define(
    ['jquery', 'underscore', 'backbone', 'text!templates/patches.html' ],
    function ($, _, Backbone, myTemplate) {
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
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'change select[name=filter]': 'filterbytype',
                    'keyup input[name=search]': 'searchBy'
                },
                searchBy: function (event) {
                    var query = $(event.currentTarget).val();
                    window.console.log(query);
                },
                filterbytype: function (evt) {
                    this.collection.type = $(evt.target).val() === 'none' ? '' : $(evt.target).val();
                    this.collection.initialize();
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        payload = {
                            type: this.collection.type,
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
                    payload.prevLink +=  payload.type ? '&type=' + payload.type : '';

                    temp = payload.offset + payload.getCount;
                    payload.nextLink = '#patches?count=' + payload.getCount + '&offset=' + temp;
                    payload.nextLink += payload.type ? '&type=' + payload.type : '';

                    this.$el.empty();

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
