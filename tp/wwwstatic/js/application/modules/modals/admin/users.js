/**
 * Created with PyCharm.
 * User: parallels
 * Date: 12/2/12
 * Time: 3:43 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/users.html'],
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
                    //this.collection = new exports.Collection();
                    //this.collection.bind('reset', this.render, this);
                    //this.collection.fetch();
                },
                events: {
                    'submit form': 'submit'
                },
                submit: function (event) {
                    var $form = $(event.target);
                    window.console.log($form);
                    return false;
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);
                    //data = this.collection.toJSON();

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
