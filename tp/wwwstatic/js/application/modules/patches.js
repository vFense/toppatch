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
                    this.searchQuery = this.searchQuery || '';
                    this.searchBy = this.searchBy || '';

                    this.query = '?count=' + this.getCount + '&offset=' + this.offset;
                    this.query += this.type ? '&type=' + this.type : '';
                    this.query += this.searchQuery ? '&query=' + this.searchQuery : '';
                    this.query += this.searchBy ? '&searchby=' + this.searchBy : '';
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
                    var searchquery = $(event.currentTarget).val(),
                        searchby = this.$el.find('select[name=searchby]').val();

                    this.collection.searchQuery = searchquery;
                    this.collection.searchBy = searchby;

                    this.collection.initialize();
                    this.collection.fetch();
                },
                filterbytype: function (evt) {
                    this.collection.type = $(evt.target).val() === 'none' ? '' : $(evt.target).val();
                    this.collection.initialize();
                    this.collection.fetch();
                },
                beforeRender: $.noop,
                onRender: function () {
                    var search = this.$el.find('input[name=search]'),
                        that = this;
                    if (this.collection.searchQuery) {
                        //search.on('blur', );
                        search.focus(function (event) {
                            this.value = this.value || '';
                        }).focus();

                    }
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        payload = {
                            searchQuery: this.collection.searchQuery,
                            searchBy: this.collection.searchBy,
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
                        //$el = this.$el.empty().html(template()),
                        //$items = $el.find('.items'),
                        temp;
                    temp = payload.offset - payload.getCount;
                    payload.prevLink = '#patches?count=' + payload.getCount + '&offset=' + (temp < 0 ? 0 : temp);
                    payload.prevLink +=  payload.type ? '&type=' + payload.type : '';
                    payload.prevLink += payload.searchQuery ? '&query=' + payload.searchQuery : '';
                    payload.prevLink += payload.searchBy ? '&searchby=' + payload.searchBy : '';

                    temp = payload.offset + payload.getCount;
                    payload.nextLink = '#patches?count=' + payload.getCount + '&offset=' + temp;
                    payload.nextLink += payload.type ? '&type=' + payload.type : '';
                    payload.nextLink += payload.searchQuery ? '&query=' + payload.searchQuery : '';
                    payload.nextLink += payload.searchBy ? '&searchby=' + payload.searchBy : '';

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
