define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/lists/list', 'text!templates/lists/pageable.html'],
    function ($, _, Backbone, app, list, myTemplate) {
        "use strict";
        return {
            Collection: app.__subClass(list.Collection).extend({
                baseUrl: '',
                _defaultParams: {
                    offset: 0,
                    count: 20
                },

                fetchPrevSet: function () {
                    if (this.hasPrev()) {
                        this.params.offset = Math.max(
                            this.params.offset - this.params.count,
                            0 // Prevent going into negative offsets
                        );

                        this.verboseFetch();
                    }
                },
                fetchNextSet: function () {
                    if (this.hasNext()) {
                        this.params.offset += this.params.count;

                        this.verboseFetch();
                    }
                },
                hasPrev: function () {
                    return this.params.offset > 0;
                },
                hasNext: function () {
                    return (this.params.offset + this.params.count) < this.recordCount;
                }
            }),
            View: app.__subClass(list.View).extend({
                _template: _.template(myTemplate),

                initialize: function (options) {
                    // No super reference.
                    // Super references cause infinite loops after a few inherits
                    // Use the class that was subClassed above
                    // In this case, list.View
                    list.View.prototype.initialize.call(this, options);

                    this.listenTo(this.collection, 'reset', function () {
                        this.togglePagerButtons();
                        this.setFooterContent('reset');
                    }, this);

                    this.listenTo(this.collection, 'fetch', function () {
                        this.togglePagerButtons(true);
                        this.setFooterContent('fetch');
                    }, this);

                    this.listenTo(this.collection, 'error', function (collection, response, options) {
                        this.togglePagerButtons(true);
                        this.setFooterContent('error');
                    }, this);
                },

                events: {
                    'click .disabled': 'stopEvent',
                    'click #list-pagePrev': 'pagePrev',
                    'click #list-pageNext': 'pageNext'
                },

                beforeUpdateList: $.noop,
                afterUpdateList: $.noop,

                setFooterContent: function (event) {
                    var $el = this.$el,
                        $footer = $el.find('footer'),
                        col = this.collection,
                        models = col.models;

                    if (event === 'reset') {
                        (function () {
                            var start = 1 + col.getParameter('offset'),
                                end = start + models.length - 1,
                                total = col.getRecordCount(),
                                out = ['Showing', start, '-', end, 'of', total, 'records.'].join(' ');

                            $footer.find('.pull-left').text(out);
                        }());
                    } else {
                        $footer.find('.pull-left').html('&nbsp;');
                    }
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
                    this.collection.fetchNextSet();

                    return this.updateURL();
                },
                pagePrev: function () {
                    this.collection.fetchPrevSet();

                    return this.updateURL();
                }
            })
        };
    }
);