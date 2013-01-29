define(
    ['jquery', 'underscore', 'backbone', 'app'],
    function ($, _, Backbone, app) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'modal',
                _lastURL: '',
                _opened: false,

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
                        this.close();
                    }
                },

                initialize: function (options) {
                    _.extend(this, _.pick(options, this._allowed));
                },

                beforeRender: $.noop,
                onRender: function () {
                    var $el = this.$el,
                        that = this;

                    if (this.animate) {
                        $el.addClass('fade');
                    }

                    // bind to all bootstrap events
                    // set value of '_opened' variable
                    $el.bind({
                        show: function () {
                            that.trigger('show');
                        },
                        shown: function () {
                            that.trigger('shown');
                        },
                        hide: function () {
                            that.trigger('hide');
                        },
                        hidden: function () {
                            that.trigger('hidden');
                            that.close();
                        }
                    });
                },

                // Set up the modal DOM, but do not show it in browser
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var $el = this.$el;

                    $el.empty();

                    if (this._contentView) {
                        $el.append(this._contentView.el);
                    } else {
                        $el.append(
                            '<div class="modal-body">' +
                                '\t<div class="row-fluid">' +
                                '\t\t<div class="span10">No Content...</div>' +
                                '\t\t<div class="btn span2 close_modal">Close</div>' +
                                '\t</div>' +
                                '</div>'
                        );
                    }

                    this.setSpan();

                    if (this.onRender !== $.noop) { this.onRender(); }

                    return this;
                },

                openWithView: function (view) {
                    this.setContentView(view);

                    if (!this.isOpen()) {
                        this.open();
                    }
                },

                setContentView: function (view) {
                    // Close the last content view if any.
                    if (this._contentView) {
                        this._contentView.close();
                    }

                    if (view instanceof Backbone.View) {
                        this._contentView = view;

                        this.render();

                        this._contentView.render();
                        this._contentView.delegateEvents();
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
                    var router = app.router,
                        last;
                    if (!this.isOpen()) {
                        // Save last fragment and go back to it on 'close'
                        last = router.getLastFragment();
                        if (last === '' || /^admin($|[\/])/.test(last)) {
                            this._lastURL = "dashboard";
                        } else {
                            this._lastURL = last;
                        }

                        this.render();
                        this.delegateEvents();

                        if (this._contentView) {
                            this._contentView.delegateEvents();
                        }

                        // Set bootstrap modal options
                        this.$el.modal({
                            keyboard: this.keyboard,
                            backdrop: this.backdrop
                        });
                    }

                    this._opened = true;

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
                    if (this.isOpen()) { this.hide(); }
                    if (this._contentView) { this._contentView.close(); }
                    if (this._lastURL !== '') {
                        app.router.navigate(this._lastURL);
                    } else {
                        app.router.navigate("dashboard", {trigger: true});
                    }
                    this._opened = false;
                }
            })
        };
    }
);
