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
                    window.currentView = this;

                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.nodecollection = new exports.NodeCollection();
                    this.nodecollection.bind('reset', this.render, this);
                    this.nodecollection.fetch();
                },
                events: {
                    'click a.accordion-toggle': 'stoplink',
                    'click button[name=remove]': 'deleteTag'
                },
                stoplink: function (event) {
                    event.preventDefault();
                    var body = $(event.target).parents('.accordion-group').find('.accordion-body');
                    /*
                    var $href = $(event.target),
                        $icon = $href.find('i'),
                        parent = $href.parents('.accordion-group'),
                        body = parent.find('.accordion-body'),
                        popover = body.find('button[name=popover]'),
                        nodelist = $('#nodelist');
                    popover.unbind();
                    body.unbind();
                    if (popover.data('popover')) {
                        popover.popover('destroy');
                    }
                    if ($icon.hasClass('icon-circle-arrow-down')) {
                        $icon.attr('class', 'icon-circle-arrow-up');
                        popover.popover({
                            placement: 'right',
                            title: 'Add Nodes <button type="button" class="btn btn-link pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            content: nodelist.clone(),
                            trigger: 'click'
                        });
                        popover.on('click', this.togglePopup);
                        popover.data('popover').tip().css('z-index', 3000);
                    } else {
                        $icon.attr('class', 'icon-circle-arrow-down');
                    }
                    */
                    body.collapse('toggle');
                    body.on('hidden', function (event) {
                        event.stopPropagation();
                    });
                },
                togglePopup: function (event) {
                    var $checkboxes, $tip, $spans, $close,
                        popover = $(event.target).parent();
                    if (popover.data('popover')) {
                        $tip = popover.data('popover').tip();
                        $spans = popover.parent().find('span');
                        $checkboxes = $tip.find('input[name=nodelist]');
                        $close = $tip.find('button[name=close]');
                        $close.unbind();
                        $checkboxes.unbind();
                        $checkboxes.each(function () {
                            var ip = $(this).parent().attr('name'),
                                that = this;
                            $spans.each(function () {
                                if ($(this).attr('name') === ip) {
                                    that.checked = true;
                                }
                            });
                        });
                        $checkboxes.on('change', popover, window.currentView.toggleNode);
                        $close.on('click', function (event) {
                            event.preventDefault();
                            popover.popover('hide');
                        });
                    }
                },
                toggleNode: function (event) {
                    var params, node_ip, node_id, tag, user, nodelist, empty_div, popover, badge, badgeCounter,
                        checked = event.target.checked;
                    popover = event.data;
                    badge = popover.parents('.accordion-group').find('.badge');
                    badgeCounter = parseInt(badge.html(), 10);
                    nodelist = popover.parent().find('.pull-left');

                    user = window.User.get('name');
                    tag = popover.attr('value');
                    node_id = $(event.target).val();
                    node_ip = $(event.target).parent().attr('name');

                    params = {
                        nodes: [node_id],
                        user: user,
                        tag: tag
                    };
                    if (checked) {
                        //add node to tag
                        empty_div = nodelist.find('em');
                        if (empty_div) { empty_div.remove(); }
                        params.operation = 'add_to_tag';
                        $.post("/api/tagging/addTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    badgeCounter += 1;
                                    nodelist.prepend('<span style="margin-right: 6px" class="label label-info" name="' + node_ip + '">' + node_ip + '</span>');
                                    badge.html(badgeCounter);
                                }
                            });
                    } else {
                        //remove node from tag
                        params.operation = 'remove_from_tag';
                        $.post("/api/tagging/removeTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    badgeCounter -= 1;
                                    nodelist.find('span:contains("' + node_ip + '")').remove();
                                    badge.html(badgeCounter);
                                }
                            });
                    }
                },
                deleteTag: function (event) {
                    event.preventDefault();
                    var params, user,
                        $icon = $(event.target),
                        $item = $icon.parents('.accordion-group'),
                        tag = $icon.parent().attr('id'),
                        popover = $item.find('a[name=popover]');

                    if (popover.data('popover')) { popover.popover('destroy'); }
                    user = window.User.get('name');
                    params = {
                        tag: tag,
                        user: user
                    };
                    window.console.log(params);
                    $.post("/api/tagging/removeTag", { operation: JSON.stringify(params) },
                        function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                $item.remove();
                            }
                        });
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
                    var popover = this.$el.find('button[name=popover]');
                    popover.each(function (i, pop) {
                        if ($(pop).data('popover')) {
                            $(pop).popover('destroy');
                        }
                    });
                }
            })
        };
        return exports;
    }
);
