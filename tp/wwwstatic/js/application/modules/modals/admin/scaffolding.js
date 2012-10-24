define(
    ['jquery', 'underscore', 'backbone', 'bootstrap-modal', 'text!templates/modals/admin/scaffolding.html'],
    function ($, _, Backbone, modal, myTemplate) {
        "use strict";
        var exports = {
            Model: Backbone.Model.extend({
                defaults: {
                    views: {
                        'approveSSL' : true,
                        'nodeGroups' : false,
                        'userGroups' : false,
                        'users'      : false
                    }
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this._template = _.template(this.template);
                    this.model = exports.Model;
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var that = this;

                    this.$el.html('');

                    console.log(Backbone.history);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
