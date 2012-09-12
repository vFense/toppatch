define(
    ['jquery', 'backbone', 'text!templates/overviewDetail.html'],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Model: Backbone.Model.extend({
                defaults: {
                    key: 'n/a',
                    data: 0
                }
            }),
            View: Backbone.View.extend({
                tagName: 'dl',
                className: '',
                template: myTemplate,
                events: {
                    'change': 'render'
                },
                initialize: function () {},
                render: function () {
                    var tmpl = _.template(this.template),
                        format = this.model.get('format'),
                        that = this;
                    this.$el
                        .html(tmpl(this.model.toJSON()));

                    if (_.isObject(format) && !_.isEmpty(format)) {
                        this.applyFormat();
                    }

                    return this;
                },
                applyFormat: function () {
                    var data = this.model.get('data'),
                        format = this.model.get('format')[0],
                        rule  = format.rule,
                        value = format.value,
                        style = format.style,
                        apply = false;

                    if (rule === 'e') {
                        // If data === value
                        if (data === value) {
                            apply = true;
                        }
                    } else if (rule === 'ne') {
                        // If data !== value
                        if (data !== value) {
                            apply = true;
                        }
                    } else if (rule === 'gt') {
                        // If data > value
                        if (data > value) {
                            apply = true;
                        }
                    } else if (rule === 'lt') {
                        // If data < value
                        if (data < value) {
                            apply = true;
                        }
                    } else if (rule === 'gte') {
                        // If data >= value
                        if (data >= value) {
                            apply = true;
                        }
                    } else if (rule === 'lte') {
                        // If data <= value
                        if (data <= value) {
                            apply = true;
                        }
                    }

                    this.$el.toggleClass(style, apply);
                }
            })
        };
        return exports;
    }
);