define(
    ['jquery', 'underscore', 'backbone'],
    function ($, _, Backbone) {
        "use strict";
        var exports = {};

        exports.Model = Backbone.Model.extend({
            defaults: {
                text: 'tabN',
                href: '',
                icon: '',
                baseHref: '#',
                showIcon: false,
                active: false
            }
        });

        exports.View = Backbone.View.extend({
            tagName: "li",
            className: "",
            initialize: function (args) {
                _.extend(this, args);

                this.content = $(document.createElement('a'));

                this.model.bind('change:icon', this.setIcon, this);
                this.model.bind('change:text', this.setText, this);
                this.model.bind('change:href', this.setHref, this);
                this.model.bind('change:active', this.setActive, this);
            },
            render: function () {
                var $el = this.$el;

                $el.empty();

                this.setHref().setText().setActive();

                if (this.model.get('showIcon')) { this.setIcon(); }

                $el.html(this.content);

                this.delegateEvents();

                return this;
            },
            setIcon: function () {
                var $icon = this.content.find('i[class^="icon"]');

                if ($icon.length === 0) {
                    $icon = $(document.createElement('i')).prependTo(this.content);
                }

                $icon.removeClass().addClass(this.model.get('icon'));
                return this;
            },
            setText: function () {
                var $span = this.content.find('span.text');

                if ($span.length === 0) {
                    $span = $(document.createElement('span')).addClass('text').appendTo(this.content);
                }

                $span.html(this.model.get('text'));
                return this;
            },
            setHref: function () {
                this.content.attr('href', this.model.get('baseHref') + this.model.get('href'));
                return this;
            },
            setActive: function () {
                this.$el.toggleClass('active', this.model.get('active'));
                return this;
            }
        });

        return exports;
    }
);