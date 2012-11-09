define(
    ['jquery', 'underscore', 'backbone', 'modals/panel'],
    function ($, _, Backbone, panel) {
        "use strict";
        return {
            View: Backbone.View.extend({
                initialize: function (options) {
                    this.panel = new panel.View({
                        okText: 'Done'
                    });

                    this.panel.bind('ok', this.hide, this);
                    this.panel.bind('close', this.hide, this);

                    this.options = _.extend({
                        // Defaults here
                    }, options);
                },

                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    // Render a blank panel
                    this.panel.render();

                    var that    = this,
                        $body   = this.panel.$body,
                        $header = this.panel.$header,
                        $footer = this.panel.$footer;


                    $body.html('hello world');

                    if (this.onRender !== $.noop) { this.onRender(); }

                    this.rendered = true;

                    return this;
                },

                show: function () {
                    // Render the content first
                    if (!this.rendered) {
                        this.render();
                    }

                    // Show the complete panel
                    this.panel.show();

                    return this;
                },

                hide: function () {
                    var that = this;

                    // Wait for the panel to hide
                    // Then destroy the related objects
                    this.panel.$el.bind('hidden', function () {
                        that.panel.close();
                        that.close();
                    });

                    // Hide the panel
                    this.panel.hide();

                    // do not return 'this'
                    // object is being destroyed
                }
            })
        };
    }
);
