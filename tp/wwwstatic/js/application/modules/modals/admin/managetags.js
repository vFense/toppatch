define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/managetags.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection : Backbone.Collection.extend({
                baseUrl: 'api/tagging/listByNode.json',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;

                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                },
                events: {
                    'click a.accordion-toggle': 'stoplink',
                    'click a[name=remove]': 'deleteTag'
                },
                stoplink: function (event) {
                    event.preventDefault();
                    var $href = $(event.target),
                        parent = $href.parents('.accordion-group'),
                        body = parent.find('.accordion-body');
                    body.collapse('toggle');
                    body.on('hidden', function (event) {
                        event.stopPropagation();
                    });
                },
                deleteTag: function (event) {
                    var $icon = $(event.target),
                        $item = $icon.parents('.accordion-group'),
                        tag = $icon.parent().attr('id');
                    $item.remove();
                    console.log($(event.target).parent().attr('id'));
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON();

                    this.$el.empty();

                    this.$el.html(template({data: data}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
