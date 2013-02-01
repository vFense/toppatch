define(
    ['jquery', 'underscore', 'backbone', 'text!templates/nodes.html' ],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: '/api/nodes.json',
                query: '',
                url: function () {
                    return this.baseUrl + this.query;
                },
                parse: function (response) {
                    this.recordCount = response.count;
                    return response.nodes;
                },
                initialize: function () {
                    this.offset   = this.offset || 0;
                    this.getCount = this.getCount  || 10;
                    this.filterby = this.filterby || '';
                    this.by_os = this.by_os || '';
                    this.query    = '?' +
                        'count=' + this.getCount +
                        '&offset=' + this.offset;
                    this.query += this.filterby ? '&filterby=' + this.filterby : '';
                    this.query += this.by_os ? '&by_os=' + this.by_os : '';
                }
            }),
            TagCollection: Backbone.Collection.extend({
                baseUrl: '/api/tagging/listByTag.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.tagcollection = new exports.TagCollection();
                    this.tagcollection.bind('reset', this.render, this);
                    this.tagcollection.fetch();
                },
                events: {
                    'change select[name=filter]': 'filterbytag'
                },
                filterbytag: function (evt) {
                    this.collection.filterby = $(evt.target).val() === 'none' ? '' : $(evt.target).val();
                    this.collection.initialize();
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        tagdata = this.tagcollection.toJSON(),
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
                            data: data,
                            tagdata: tagdata,
                            by_os: this.collection.by_os,
                            severity: this.collection.severity,
                            filter: this.collection.filterby
                        },
                        temp;
                    temp = payload.offset - payload.getCount;
                    payload.prevLink = '#nodes?count=' + payload.getCount + '&offset=' + (temp < 0 ? 0 : temp);
                    payload.prevLink += payload.filter ? '&filterby=' + payload.filter : '';
                    payload.prevLink += payload.by_os ? '&by_os=' + payload.by_os : '';

                    temp = payload.offset + payload.getCount;
                    payload.nextLink = '#nodes?count=' + payload.getCount + '&offset=' + temp;
                    payload.nextLink += payload.filter ? '&filterby=' + payload.filter : '';
                    payload.nextLink += payload.by_os ? '&by_os=' + payload.by_os : '';

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
