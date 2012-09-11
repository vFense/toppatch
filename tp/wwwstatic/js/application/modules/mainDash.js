define(
    ['jquery', 'backbone', 'text!templates/mainDash.html', 'modules/overview' ],
    function ($, Backbone, myTemplate, Overview) {
        "use strict";
        var mainDash = {};
        mainDash.Model = Backbone.Model.extend({});
        mainDash.View = Backbone.View.extend({
            initialize: function () {
                //this.model = window.tempModel = new mainDash.Model();
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
        });
        return mainDash;
    }
);