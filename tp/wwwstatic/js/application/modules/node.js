define(
    ['jquery', 'backbone', 'app', 'text!templates/node.html' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {};
        exports.Collection = Backbone.Collection.extend({
            model: Backbone.Model.extend({}),

            initialize: function () {
                this.show = 'api/nodes.json';
                this.filter = '?id='+this.id;
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