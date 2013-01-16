/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/11/13
 * Time: 8:30 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/tag.html' ],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/tagging/tagStats',
                url: function () {
                    return this.baseUrl + '?tagid=' + this.id;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    //'click button[name=remove]': 'removeSchedule'
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON()[0];

                    this.$el.empty();

                    this.$el.append(template({data: data}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
