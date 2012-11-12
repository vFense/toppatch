define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/panel.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        return {
            View: Backbone.View.extend({
                className: 'modal',

                events: {
                    'click .close': function(event) {
                        event.preventDefault();

                        this.trigger('close');
                    },
                    'click .cancel': function(event) {
                        event.preventDefault();

                        this.trigger('cancel');
                    },
                    'click .ok': function(event) {
                        event.preventDefault();

                        this.trigger('ok');
                    }
                },

                initialize: function (options) {
                    this.template = myTemplate;
                    this.rendered = false;
                    this.opened = false;
                    this.options = _.extend({
                        okText: 'OK',
                        cancelText: 'Cancel',
                        allowCancel: true,
                        escape: true,
                        animate: false
                    }, options);

                    this.bind('all', function (event) {
                        console.log(event);
                    }, this);

                    this.render();
                },

                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        tmpl = _.template(this.template),
                        $el = this.$el;

                    $el.empty();

                    $el.append(tmpl(this.options));

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

                    var that = this,
                        $el = this.$el;

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
