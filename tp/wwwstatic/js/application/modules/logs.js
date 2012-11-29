define(
    ['jquery', 'underscore', 'backbone', 'app', 'text!templates/list.html', 'jquery.ui.datepicker'],
    function ($, _, Backbone, app, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/transactions/getTransactions',
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

                fetch: function () {
                    // Add fetch event
                    this.trigger('fetch');

                    // Call original fetch method
                    return this.constructor.__super__.fetch.apply(this, arguments);
                },

                parse: function (response) {
                    this.recordCount = parseInt(response.count, 10);
                    return response.data || response;
                },

                initialize: function (options) {
                    var that = this;

                    // Set default parameters
                    this.params = {
                        // Paging
                        offset: 0,
                        count: 20
                    };

                    if (options.params) {
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

                    console.log([this.params, name, this.params[name]]);
                    if (!name) {
                        out = this.params;
                    } else {
                        out = this.params[name];
                    }

                    return out;
                },

                getPrevSet: function () {
                    if (this.hasPrev()) {
                        this.params.offset = Math.max(
                            this.params.offset - this.params.count,
                            0
                        );

                        this.fetch();
                    }
                },
                getNextSet: function () {
                    if (this.hasNext()) {
                        this.params.offset += this.params.count;

                        this.fetch();
                    }
                },
                hasPrev: function () {
                    return this.params.offset > 0;
                },
                hasNext: function () {
                    return this.params.offset + this.params.count < (this.recordCount || 0);
                }
            }),
            View: Backbone.View.extend({
                tagName: 'article',
                className: 'row-fluid',

                _rendered: false,

                initialize: function (options) {
                    if (options) {
                        _.extend(this, _.pick(options, ['collection']));
                    }

                    this._template = _.template(myTemplate);

                    if (!this.collection instanceof Backbone.Collection) {
                        this.collection =  new exports.Collection();
                    }

                    this.collection.bind('reset', function () {
                        this.updateList('reset');
                    }, this);

                    this.collection.bind('fetch', function () {
                        this.updateList('fetch');
                    }, this);
                },

                events: {
                    'click .disabled': 'stopEvent',
                    'click #list-pagePrev': 'pagePrev',
                    'click #list-pageNext': 'pageNext'
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

                    this.collection.fetch();

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },

                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        result = item.get('result'),

                        $item       = newElement('div').addClass('item'),
                        $div        = newElement('div').addClass('row-fluid'),
                        $operation  = newElement('small').addClass('span2'),
                        $desc       = newElement('span').addClass('desc span3'),
                        $error      = newElement('small').addClass('span2').html('&nbsp;'),
                        $date       = newElement('span').addClass('float-right offset3 span2 alignRight');

                    $operation.append(item.get('operation').toUpperCase());
                    $desc.html(item.get('node_id'));
                    $date.html(item.get('operation_sent'));

                    if (_.isBoolean(result) && !result) {
                        $div.addClass('fail');
                        $error.append(
                            newElement('a')
                                .attr('rel', 'tooltip')
                                .attr('data-placement', 'right')
                                .attr('data-original-title', item.get('error'))
                                .html('Message').tooltip()
                        );
                    }

                    return $item.append(
                        $div.append($operation, $desc, $error, $date)
                    );
                },

                updateList: function (event) {
                    var that = this,
                        $el = this.$el,
                        $items = $el.find('.items'),
                        $item = this._baseItem,
                        models = this.collection.models;

                    if (event === 'reset') {
                        $items.empty();

                        if (models.length !== 0) {
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

                        this.togglePagerButtons();
                    } else if (event === 'fetch') {
                        $items.empty().html(
                            _.clone($item).html(
                                'Loading...'
                            )
                        );

                        this.togglePagerButtons(true);
                    }



                    return this;
                },

                togglePagerButtons: function (forcedOff) {
                    var $el = this.$el;

                    // Issues with readability. Double negatives get confusing.
                    // Way to improve? Perhaps full if/else statements (WETWET)?
                    $el.find('#list-pageNext').toggleClass('disabled', forcedOff || !this.collection.hasNext());
                    $el.find('#list-pagePrev').toggleClass('disabled', forcedOff || !this.collection.hasPrev());

                    return this;
                },

                pageNext: function () {
                    this.collection.getNextSet();

                    return this.updateURL();
                },
                pagePrev: function () {
                    this.collection.getPrevSet();

                    return this.updateURL();
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