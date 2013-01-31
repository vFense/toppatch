define(
    ['jquery', 'underscore', 'backbone', 'app'],
    function ($, _, Backbone, app) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'modal',
                _lastURL: '',
                _opened: false,
                template: null,

                // Variables that affect bootstrap-modal functionality
                animate: false,
                keyboard: true,
                backdrop: true,

                // Variables that affect the modal itself
                span: '', // Leave blank for default bootstrap width

                // White list of variables that are allowed to be set during init
                _allowed: ['animate', 'keyboard', 'backdrop', 'span'],

                events: {
                    'click .confirm': function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        this.confirm();
                    },
                    'click .close_modal': function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        this.hide();
                    }
                },

                initialize: function (options) {
                    var $el = this.$el,
                        that = this;

                    if (options) {
                        _.extend(this, _.pick(options, this._allowed));
                    }

                    this.render().setSpan();

                    if (this.animate) {
                        $el.addClass('fade');
                    }
                },

                beforeRender: $.noop,
                onRender: $.noop,

                // Set up the modal DOM, but do not show it in browser
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var $el = this.$el,
                        $body = $el.find('.modal-body');

                    if ($body.length === 0) {
                        this.layout();
                    }

                    if (this._contentView) {
                        this._contentView.$el.appendTo($el.find('.modal-body').empty() || $el);
                    }

                    if (this.onRender !== $.noop) { this.onRender(); }

                    return this;
                },

                layout: function () {
                    this.$el.empty();

                    if (this.template) {
                        this.$el.html(_.template(this.template));
                    }
                },

                openWithView: function (view) {
                    this.setContentView(view);

                    if (!this.isOpen()) {
                        this.open();
                    }
                },

                setContentView: function (view) {
                    var that = this;

                    // Close the last content view if any.
                    if (this._contentView) {
                        this._contentView.close();
                    }

                    if (view instanceof Backbone.View) {
                        this._contentView = view;

                        this.render();

                        this._contentView.render();
                        this._contentView.delegateEvents();
                    } else if ($.type(view) === 'string') {
                        require([view], function (load) {
                            that._contentView = new load.View();

                            that.render();

                            that._contentView.render();
                            that._contentView.delegateEvents();
                        });
                    }

                    return this;
                },

                getContentView: function () {
                    return this._contentView;
                },

                isOpen: function () {
                    return this._opened;
                },

                // Show the modal in browser
                open: function () {
                    var that = this,
                        $el = this.$el;
                    if (!this.isOpen()) {
                        this.delegateEvents();

                        if (this._contentView) {
                            this._contentView.delegateEvents();
                        }

                        this.listenTo($el, 'hidden', function () {
                            that.trigger('hidden');
                            that._opened = false;
                            that.close();
                        });

                        // Set bootstrap modal options
                        $el.modal({
                            keyboard: this.keyboard,
                            backdrop: this.backdrop
                        });

                        this._opened = true;
                    }

                    return this;
                },

                hide: function () {
                    this.$el.modal('hide');
                    return this;
                },

                confirm: $.noop,

                // optional: span
                // Not fully tested for every case
                setSpan: function (span) {
                    var $el = this.$el,
                        spanNum = /^span[1-9][0-2]{0,1}$/,
                        numeric = /^[1-9][0-2]{0,1}$/;

                    span = (span || this.span).trim();

                    if (spanNum.test(span)) {
                        $el.removeClass(this.span)
                            .addClass(this.span = span);
                    } else if (numeric.test(span)) {
                        $el.removeClass(this.span)
                            .addClass(this.span = 'span' + span);
                    } else {
                        $el.removeClass(this.span);
                        this.span = '';
                    }

                    return this;
                },

                beforeClose: function () {
                    if (this.isOpen()) {
                        this.hide();
                    }
                    if (this._contentView) { this._contentView.close(); }
                }
            })
        };
    }
);
