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
                    }, this)

                    this.render();
                },

                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var tmpl = _.template(this.template),
                        $el = this.$el;

                    this.$el.empty();

                    this.$el.append(tmpl(this.options));

                    if (this.options.animate) {
                        $el.addClass('fade');
                    }

                    // Add references to different parts of the panel
                    _.extend(this, {
                        '$header': $el.find('.modal-header'),
                        '$body'  : $el.find('.modal-body'),
                        '$footer': $el.find('.modal-footer')
                    });

                    if (this.onRender !== $.noop) { this.onRender(); }

                    this.rendered = true;

                    return this;
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

                    this.on('cancel', function() {
                        that.close();
                    });

                    return this;
                },

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
