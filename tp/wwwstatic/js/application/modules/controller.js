/**
 * Created with PyCharm.
 * User: parallels
 * Date: 10/6/12
 * Time: 2:02 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'backbone', 'text!templates/controller.html'],
    function ($, Backbone, myTemplate) {
        "use strict";
        var Controller = {};
        Controller.View = Backbone.View.extend({
            template: myTemplate,
            initialize: function () {

            },
            events: {

            },
            render: function () {
                var tmpl = _.template(this.template);
                this.$el.html(tmpl());
                return this;
            }
        });
        return Controller;
    }
);