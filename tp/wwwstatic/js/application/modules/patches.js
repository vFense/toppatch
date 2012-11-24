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
                    this.baseUrl = this.searchQuery ? 'api/package/searchByPatch' : 'api/patches.json';
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.view = this;
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'change select[name=filter]': 'filterbytype',
                    'keyup input[name=search]': 'debouncedSearch'
                },
                debouncedSearch: _.debounce(function (event) {
                    window.console.log(['debounced', event]);
                    this.searchBy(event);
                }, 300),
                searchBy: function (event) {
                    var searchQuery = $(event.currentTarget).val().trim(),
                        searchBy = this.$el.find('select[name=searchby]').val();
                    if (searchQuery && searchQuery.length >= 2) {
                        this.collection.searchQuery = searchQuery;
                        this.collection.searchBy = searchBy;
                        this.collection.baseUrl = 'api/package/searchByPatch';
                    } else if (!searchQuery) {
                        this.collection.searchQuery = '';
                        this.collection.searchBy = '';
                        this.collection.baseUrl = 'api/patches.json';
                    } else {
                        this.collection.searchQuery = searchQuery;
                        this.collection.searchBy = searchBy;
                    }
                    this.collection.initialize();
                    this.updateList();
                    //this.collection.fetch();
                },
                filterbytype: function (evt) {
                    this.collection.type = $(evt.target).val() === 'none' ? '' : $(evt.target).val();
                    this.collection.initialize();
                    this.collection.fetch();
                },
                updateList: function () {
                    var that = this;
                    this.collection.unbind();
                    this.collection.fetch({
                        success: that.renderList
                    });
                },
                renderList: function (collection, response) {
                    var items,
                        view = collection.view,
                        $el = view.$el,
                        $list = $el.find('.items'),
                        $footer = $el.find('footer');
                    $list.empty();
                    $footer.empty();
                    items = collection.toJSON();
                    if (items.length !== 0) {
                        _.each(items, function (patch, i) {
                            $list.append(view.renderModel(patch));
                        });
                    } else {
                        $list.append(view.renderModel(null));
                    }
                    window.console.log(collection);
                },
                renderModel: function (item) {
                    var $item, $div, $link, $desc, $pend,
                        $spanRight, $done, $need, $fail, $icon,
                        newElement = function (element) {
                            return $(document.createElement(element));
                        };
                    if (item) {
                        $item       = newElement('div').addClass('item linked clearfix');
                        $div        = newElement('div').addClass('row-fluid');
                        $link       = newElement('a').attr('href', '#patches/' + item.id);
                        $desc       = newElement('span').addClass('desc span8').html('<strong>' + item.vendor.name + '</strong> — ' + item.name);
                        $spanRight  = newElement('span').addClass('span4 alignRight').html('&nbsp;');
                        $done       = newElement('span').addClass('done');
                        $pend = newElement('span').addClass('pend');
                        $need = newElement('span').addClass('need');
                        $fail = newElement('span').addClass('fail');
                        $icon = newElement('i').addClass('icon-caret-right');
                        $spanRight.prepend($done, $pend, $need, $fail).append($icon);
                        $link.append($desc, $spanRight);
                        $div.append($link);
                        return $item.append($div);
                    } else {
                        $item = newElement('div').addClass('item clearfix');
                        $desc = newElement('span').addClass('desc').html('<em>No patches.</em>');
                        return $item.append($desc);
                    }
                },
                beforeRender: $.noop,
                onRender: $.noop,
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
