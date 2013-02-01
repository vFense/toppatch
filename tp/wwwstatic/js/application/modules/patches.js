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
                    this.status = this.status || '';
                    this.searchQuery = this.searchQuery || '';
                    this.searchBy = this.searchBy || '';
                    this.severity = this.severity || '';
                    this.date = this.date || '';

                    this.query = '?count=' + this.getCount + '&offset=' + this.offset;
                    this.query += this.date ? '&date=' + this.date + '&installed=true' : '';
                    this.query += this.status ? '&status=' + this.status : '';
                    this.query += this.searchQuery ? '&query=' + this.searchQuery : '';
                    this.query += this.searchBy ? '&searchby=' + this.searchBy : '';
                    this.query += this.severity ? '&severity=' + this.severity : '';
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
                    this.collection.offset = 0;
                    this.collection.initialize();
                    this.updateList();
                },
                filterbytype: function (evt) {
                    this.collection.status = $(evt.target).val() === 'none' ? '' : $(evt.target).val();
                    this.collection.searchBy = '';
                    this.collection.searchQuery = '';
                    this.collection.offset = 0;
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
                    var items, prevLink, nextLink, temp, $small, $prevEle, $nextEle, $div,
                        getCount = +collection.getCount,
                        offset = +collection.offset,
                        start = +collection.offset + 1,
                        end = +collection.offset + collection.length,
                        prevEnable = +collection.offset > 0,
                        nextEnable = +collection.offset + collection.length + 1 < +collection.recordCount,
                        view = collection.view,
                        $el = view.$el,
                        $list = $el.find('.items'),
                        $footer = $el.find('footer'),
                        newElement = function (element) {
                            return $(document.createElement(element));
                        };
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
                    //render new footer
                    temp = offset - getCount;
                    prevLink = '#patches?count=' + getCount + '&offset=' + (temp < 0 ? 0 : temp);
                    prevLink += collection.searchQuery ? '&query=' + collection.searchQuery : '';
                    prevLink += collection.searchBy ? '&searchby=' + collection.searchBy : '';

                    temp = offset + getCount;
                    nextLink = '#patches?count=' + getCount + '&offset=' + temp;
                    nextLink += collection.searchQuery ? '&query=' + collection.searchQuery : '';
                    nextLink += collection.searchBy ? '&searchby=' + collection.searchBy : '';

                    $small = newElement('small').html('Viewing ' + start + ' – ' + end + ' of ' + collection.recordCount + ' Patches');
                    $div = newElement('div').addClass('pull-right hidden-print');
                    $prevEle = newElement('a').addClass('btn btn-mini').html('Previous');
                    $nextEle = newElement('a').addClass('btn btn-mini').html('Next');
                    if (!prevEnable) {
                        $prevEle.addClass('disabled').attr('href', 'javascript:;');
                    } else {
                        $prevEle.attr('href', prevLink);
                    }
                    if (!nextEnable) {
                        $nextEle.addClass('disabled').attr('href', 'javascript:;');
                    } else {
                        $nextEle.attr('href', nextLink);
                    }
                    $div.append($prevEle, $nextEle);
                    $footer.append($small, $div);
                    $footer.find("a.disabled").on("click", false);
                    view.collection.bind('reset', view.render, view);
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
                            status: this.collection.status,
                            severity: this.collection.severity,
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
                    payload.prevLink +=  payload.status ? '&status=' + payload.status : '';
                    payload.prevLink += payload.searchQuery ? '&query=' + payload.searchQuery : '';
                    payload.prevLink += payload.searchBy ? '&searchby=' + payload.searchBy : '';
                    payload.prevLink += payload.severity ? '&severity=' + payload.severity : '';

                    temp = payload.offset + payload.getCount;
                    payload.nextLink = '#patches?count=' + payload.getCount + '&offset=' + temp;
                    payload.nextLink += payload.status ? '&status=' + payload.status : '';
                    payload.nextLink += payload.searchQuery ? '&query=' + payload.searchQuery : '';
                    payload.nextLink += payload.searchBy ? '&searchby=' + payload.searchBy : '';
                    payload.nextLink += payload.severity ? '&severity=' + payload.severity : '';

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
