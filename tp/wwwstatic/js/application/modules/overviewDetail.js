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
                    var tmpl = _.template(this.template);
                    this.$el
                        .html(tmpl(this.model.toJSON()));
                        //.toggleClass(
                        //    this.model.get('accent'),
                        //    this.model.get('accentFn')(this.model.get('data'))
                        //)
                    return this;
                }
            })
        };
        return exports;
    }
);