/**
 * Created with PyCharm.
 * User: parallels
 * Date: 10/6/12
 * Time: 2:54 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'backbone', 'text!templates/detail.html'],
    function ($, Backbone, myTemplate) {
        "use strict";
        var Detail = {};
        Detail.View = Backbone.View.extend({
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
        return Detail;
    }
);