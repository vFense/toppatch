define(
    ['jquery', 'underscore', 'backbone', 'text!templates/list.html', 'jquery.ui.datepicker'],
    function ($, _, Backbone, myTemplate) {
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
                    return response.data[0] || response;
                },
                initialize: function (options) {
                    if (options.params) {
                        _.extend(
                            this.params,
                            _.pick(
                                options.params,
                                _.keys(this.params)
                            )
                        );
                    }
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

                    this.updateList('fetch');
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

                    /*
                     $date.html(
                        $.datepicker.formatDate(
                            'mm-dd-yy',
                            $.datepicker.parseDate(
                                'mm/dd/yy',
                                item.get('operation_sent')
                            )
                        )
                    );
                    */

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
                    } else if (event === 'fetch') {
                        $items.empty().html(
                            _.clone($item).html(
                                'Loading...'
                            )
                        );
                    }
                }
            })
        };
        return exports;

    }
);