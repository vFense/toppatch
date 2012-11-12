define(
    ['jquery', 'underscore', 'backbone', 'app'],
    function ($, _, Backbone, app) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'modal',
                rendered: false,
                opened: false,
                animate: false,
                keyboard: true,
                backdrop: true,

                initialize: function () {},

                beforeRender: $.noop,
                onRender: $.noop,

                // Set up the modal DOM, but do not show it in browser
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        $el = this.$el;

                    $el.empty();

                    $el.append('test');

                    if (this.options.animate) {
                        $el.addClass('fade');
                    }

                    // Add references to different parts of the panel
                    _.extend(this, {
                        '$header': $el.find('.modal-header'),
                        '$body'  : $el.find('.modal-body'),
                        '$footer': $el.find('.modal-footer')
                    });

                    // bind to all bootstrap events
                    // set value of 'opened' variable
                    $el.bind({
                        show: function () {
                            that.opened = true;
                            that.trigger('show');
                        },
                        shown: function () {
                            that.trigger('shown');
                        },
                        hide: function () {
                            that.opened = false;
                            that.trigger('hide');
                        },
                        hidden: function () {
                            that.trigger('hidden');
                        }
                    });

                    if (this.onRender !== $.noop) { this.onRender(); }

                    this.rendered = true;

                    return this;
                },

                openWithView: function (view) {
                    var that = this;
                    if (view instanceof Backbone.View) {
                        view.$el = that.$body;

                        view.render();

                        that.open();
                    }
                },

                isOpen: function () {
                    return this.opened;
                },

                open: function () {
                    if (!this.rendered) {
                        this.render();
                    }

                    var $el = this.$el;

                    $el.modal({
                        keyboard: this.options.allowCancel,
                        backdrop: this.options.allowCancel ? true : 'static'
                    });

                    return this;
                },

                setContentView: $.noop,
                getContentView: $.noop,

                hide: function () {
                    this.$el.modal('hide');
                    return this;
                },

                beforeClose: function () {
                    this.hide();
                }
            })
        };
    }
);
