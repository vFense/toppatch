define(
    ['jquery', 'underscore', 'backbone', 'app'],
    function ($, _, Backbone, app) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'modal',
                _lastURL: '',
                _rendered: false,
                _opened: false,

                // Variables that affect bootstrap-modal functionality
                animate: false,
                keyboard: true,
                backdrop: true,

                events: {
                    'click .confirm': 'confirm',
                    'click [name=confirm]': 'confirm',
                    'click .close_modal': 'close',
                    'click [name=close_modal]': 'close',
                    click: function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                },

                initialize: function () {},

                beforeRender: $.noop,
                onRender: $.noop,

                // Set up the modal DOM, but do not show it in browser
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        $el = this.$el;

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

                    if (this.animate) {
                        $el.addClass('fade');
                    }

                    // bind to all bootstrap events
                    // set value of '_opened' variable
                    $el.bind({
                        show: function () {
                            that._opened = true;
                            that.trigger('show');
                        },
                        shown: function () {
                            that.trigger('shown');
                        },
                        hide: function () {
                            that._opened = false;
                            that.trigger('hide');
                        },
                        hidden: function () {
                            that.trigger('hidden');
                            that.close();
                        }
                    });

                    if (this.onRender !== $.noop) { this.onRender(); }

                    this._rendered = true;

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
                        // If we are routed here from a bookmark,
                        // render the dashboard behind the modal.
                        if (!router.viewManager.get('currentView')) {
                            router.home();
                        }

                        // Save last fragment and go back to it on 'close'
                        var last = router.getLastFragment();
                        if (last === '' || /^testAdmin.*/.test(last)) {
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

                    return this;
                },

                hide: function () {
                    this.$el.modal('hide');
                    return this;
                },

                beforeClose: function () {
                    if (this.isOpen()) { this.hide(); }
                    if (this._contentView) { this._contentView.close(); }
                    if(this._lastURL !== '') {
                        Backbone.history.navigate(this._lastURL, false);
                    } else {
                        Backbone.history.navigate("dashboard", true);
                    }
                }
            })
        };
    }
);
