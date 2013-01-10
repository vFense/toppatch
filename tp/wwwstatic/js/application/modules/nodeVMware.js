/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/9/13
 * Time: 5:25 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/nodeVMware.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: '',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.render();
                    //this.collection = new exports.Collection();
                    //this.collection.bind('reset', this.render, this);
                    //this.collection.fetch();
                },
                events: {
                    //'submit form': 'submit'
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);
                        //data = this.collection.toJSON()[0];

                    this.$el.empty();

                    this.$el.html(template());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
