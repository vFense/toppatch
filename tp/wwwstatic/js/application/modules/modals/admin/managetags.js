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
            NodeCollection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
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

                    this.nodecollection = new exports.NodeCollection();
                    this.nodecollection.bind('reset', this.render, this);
                    this.nodecollection.fetch();
                },
                events: {
                    'click a.accordion-toggle': 'stoplink',
                    'click a[name=remove]': 'deleteTag'
                },
                stoplink: function (event) {
                    event.preventDefault();
                    var $href = $(event.target),
                        parent = $href.parents('.accordion-group'),
                        body = parent.find('.accordion-body'),
                        popover = body.find('a[name=popover]'),
                        nodelist = $('#nodelist');
                    popover.unbind();
                    popover.on('click', this.togglePopup);
                    popover.popover({
                        placement: 'right',
                        title: 'Add Nodes <a href="javascript:;" class="pull-right" name="close"><i class="icon-remove"></i></a>',
                        html: true,
                        content: nodelist.clone(),
                        trigger: 'manual'
                    });
                    body.collapse('toggle');
                    if (popover.data('popover')) {
                        popover.data('popover').tip().css('z-index', 3000);
                        popover.popover('hide');
                    }
                    body.on('hidden', function (event) {
                        event.stopPropagation();
                    });
                },
                togglePopup: function (event) {
                    var popover = $(event.target).parent(),
                        $tip = popover.data('popover').$tip;
                    popover.popover('toggle');
                    $tip.find('a[name=close]').on('click', function (event) { popover.popover('hide'); });
                },
                deleteTag: function (event) {
                    var $icon = $(event.target),
                        $item = $icon.parents('.accordion-group'),
                        tag = $icon.parent().attr('id'),
                        popover = $item.find('a[name=popover]');
                    if (popover.data('popover')) { popover.popover('destroy'); }
                    $item.remove();
                    window.console.log($(event.target).parent().attr('id'));
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        nodelist = this.nodecollection.toJSON()[0];

                    this.$el.empty();

                    if (nodelist) {
                        this.$el.html(template({data: data, nodelist: nodelist}));
                    }

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                beforeClose: function (event) {
                    var popover = this.$el.find('a[name=popover]');
                    if (popover.data('popover')) { popover.popover('destroy'); }
                }
            })
        };
        return exports;
    }
);
