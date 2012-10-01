/**
 * Created with PyCharm.
 * User: parallels
 * Date: 9/30/12
 * Time: 6:55 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'backbone', 'app', 'text!templates/indPatches.html' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {};
        exports.Collection = Backbone.Collection.extend({
            model: Backbone.Model.extend({}),

            initialize: function () {
                this.show = 'api/patchData';
                this.filter = '';
                this.url = function () {
                    return this.show + this.filter;
                };
            }
        });
        exports.View = Backbone.View.extend({
            initialize: function () {
                var that = this;
                this.template = myTemplate;
                this.collection = new exports.Collection();

                this.collection.bind('all', function (e) { console.log(e); });

                this.collection.fetch({
                    success: function () { that.render(); }
                });
            },
            events: {

            },
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                var tmpl = _.template(this.template),
                    that = this;

                this.$el.html('');

                this.$el.append(tmpl({
                    id: this.id,
                    models: this.collection.models
                }));
                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            },
            renderModel: function (item) {

            },
            setFilter: function (e) {

            },
            clearFilter: function () {
                this.collection.filter = '';
            }
        });
        return exports;
    }
);