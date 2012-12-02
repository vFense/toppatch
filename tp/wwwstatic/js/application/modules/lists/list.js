define(
    ['jquery', 'underscore', 'backbone', 'app', 'text!templates/lists/list.html'],
    function ($, _, Backbone, app, myTemplate) {
        "use strict";
        var exports = {
            Collection: app.__subClass(Backbone.Collection).extend({
                baseUrl: '',
                _defaultParams: {},
                params: {},
                url: function () {
                    var query = this.query(),
                        url = this.baseUrl;

                    if (query !== '?') { url += query; }
                    return url;
                },

                query: function () {
                    return '?' + $.param(this.params).trim();
                },

                verboseFetch: function (callBacks) {
                    var that = this;

                    callBacks = callBacks || {};

                    // Add fetch event
                    this.trigger('fetch');

                    // Trigger error event unless other function is provided
                    if (!callBacks || !callBacks.error || _.isFunction(callBacks.error)) {
                        callBacks.error = function (collection, xhr, options) {
                            that.trigger('error', collection, xhr, options);
                        };
                    }

                    // Call original fetch method
                    this.fetch(callBacks);
                },

                parse: function (response) {
                    this.recordCount = parseInt(response.count, 10) || 0;
                    return response.data || response;
                },

                initialize: function (options) {
                    var that = this;

                    if (options && options._defaultParams) {
                        _.defaults(options._defaultParams);
                    }

                    // Reset params to default params
                    this.params = _.clone(this._defaultParams);

                    if (options && options.params) {
                        _.extend(
                            this.params,
                            // Accept only the params defined in this.params
                            // If this.params = {a: 1, b: 2} and options.params = {a: 0, c: 3}
                            // then final this.params is {a: 0, b: 2}. {c: 3} is ignored.
                            _.pick(
                                options.params,
                                _.keys(this.params)
                            )
                        );

                        // Convert numeric params into numbers
                        _.each(this.params, function (param, key) {
                            if ($.isNumeric(param) && $.type(param) === 'string') {
                                that.params[key] = parseInt(param, 10);
                            }
                        });
                    }
                },

                getParameter: function (name) {
                    var out;

                    if (!name) {
                        out = this.params;
                    } else {
                        out = this.params[name];
                    }

                    return out;
                },

                getRecordCount: function () {
                    return this.recordCount;
                }
            }),
            View: app.__subClass(Backbone.View).extend({
                tagName: 'article',
                className: 'row-fluid',
                _template: _.template(myTemplate),

                _rendered: false,

                initialize: function (options) {
                    if (options) {
                        _.extend(this, _.pick(options, ['collection']));
                    }

                    if (!this.collection instanceof exports.Collection) {
                        this.collection =  new exports.Collection();
                    }

                    this.collection.bind('reset', function () {
                        this.updateList({name: 'reset'});
                    }, this);

                    this.collection.bind('fetch', function () {
                        this.updateList({name: 'fetch'});
                    }, this);

                    this.collection.bind('error', function (collection, xhr, options) {
                        this.updateList({name: 'error', response: xhr});
                    }, this);
                },

                events: {
                    'click .disabled': 'stopEvent'
                },

                stopEvent: function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                },

                beforeRender: function () {
                    this._rendered = false;
                },
                onRender: function () {
                    this._rendered = true;
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        $el = this.$el.empty().html(this._template()),
                        $items = $el.find('.items');

                    if (!this._baseItem) {
                        this._baseItem = _.clone($items.find('.item')).empty();
                    }

                    this.collection.verboseFetch();

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },

                // Generic model render method
                // Override for custom look
                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        cellCount = 0,
                        $item = newElement('div').addClass('item'),
                        $row  = newElement('div').addClass('row-fluid'),
                        $cell = newElement('div').addClass('cell');

                    _.each(item.attributes, function (value, key) {
                        if (_.isNumber(value) || _.isString(value)) {
                            $row.append(
                                _.clone($cell).html(
                                    [key, ': ', value].join('')
                                )
                            );
                            cellCount += 1;
                        } else if (_.isBoolean(value)) {
                            $row.append(
                                _.clone($cell).html(
                                    [key, ': ', value ? 'true' : 'false'].join('')
                                )
                            );
                            cellCount += 1;
                        }
                    });

                    $row.find('.cell')
                        .removeClass('cell')
                        .addClass('span' + Math.min(Math.floor(12 / cellCount), 2));

                    return $item.append($row);
                },

                beforeUpdateList: $.noop,
                afterUpdateList: $.noop,

                updateList: function (event) {
                    if (this.beforeUpdateList !== $.noop) { this.beforeUpdateList(); }

                    var that = this,
                        $el = this.$el,
                        $items = $el.find('.items'),
                        $item = this._baseItem,
                        models = this.collection.models;

                    // empty item list
                    $items.empty();

                    if (event.name === 'reset') {
                        if (models.length > 0) {
                            _.each(models, function (model) {
                                $items.append(that.renderModel(model));
                            });
                        } else {
                            $items.html(
                                _.clone($item).empty().html(
                                    'No data available'
                                )
                            );
                        }
                    } else if (event.name === 'fetch') {
                        $items.empty().html(
                            _.clone($item).empty().html(
                                'Loading...'
                            )
                        );
                    } else if (event.name === 'error') {
                        $items.empty().html(
                            _.clone($item).html(
                                ['Error', event.response.status, '-', event.response.statusText].join(' ')
                            )
                        );
                    }

                    if (this.afterUpdateList !== $.noop) { this.afterUpdateList(); }

                    return this;
                },

                updateURL: function () {
                    // Update the URL, but do not cause a route event
                    app.router.navigate('logs' + this.collection.query());

                    return this;
                }
            })
        };
        return exports;
    }
);