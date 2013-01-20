define(
    ['jquery', 'underscore', 'backbone'],
    function ($, _, Backbone) {
        "use strict";
        return {
            View: Backbone.View.extend({
                initialize: function () {
                    this.render();
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this,
                        $el = this.$el;

                    $el.empty();

                    if (!this.$pinwheel) {
                        this.$pinwheel = $(document.createElement("div")).addClass('pinwheel');

                        if (Modernizr.cssanimations) {
                            this.$pinwheel.html([
                                '<div class="pinwheel animated infinite linear spin">',
                                '<div class="pinwheel animated infinite linear spin reverse doubleTime">',
                                '&nbsp;',
                                '</div>',
                                '</div>'
                            ].join('\n'));
                        } else {
                            this.$pinwheel.html('Loading ...');
                        }
                    }

                    $el.append(this.$pinwheel);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
    }
);
