define(
    ['jquery', 'backbone', 'text!templates/mainDash.html', 'modules/overview' ],
    function ($, Backbone, myTemplate, Overview) {
        "use strict";
        var exports = {
            Model: Backbone.Model.extend({}),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                },
                render: function () {
                    var tmpl = _.template(this.template),
                        that = this;

                    this.$el.html('');

                    this.overview = new Overview.View({
                        el: $('<summary>').addClass('row-fluid clearfix')
                    });
                    this.$el.append(that.overview.render().$el);

                    this.$el.append(tmpl());

                    return this;
                }
            })
        };
        return exports;
    }
);