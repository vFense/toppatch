define(
    ['jquery', 'backbone', 'text!templates/mainDash.html'],
    function ($, Backbone, myTemplate) {
        "use strict";
        var exports = {};
        exports.Model = Backbone.Model.extend({});
        exports.View = Backbone.View.extend({
            template: myTemplate,
            initialize: function () {
                this.model = exports.Model;
            },
            render: function () {
                var tmpl = _.template(this.template);
                this.$el.html(tmpl(
                    //this.model.toJSON()
                ));
                return this;
            }
        });
        return exports;
    }
);