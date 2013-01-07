/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/6/13
 * Time: 9:45 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/groups.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/groups/list',
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
            TagCollection: Backbone.Collection.extend({
                baseUrl: 'api/tagging/listByTag.json',
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

                    this.nodeCollection = new exports.NodeCollection();
                    this.nodeCollection.bind('reset', this.render, this);
                    this.nodeCollection.fetch();

                    this.tagCollection = new exports.TagCollection();
                    this.tagCollection.bind('reset', this.render, this);
                    this.tagCollection.fetch();
                },
                events: {
                    'click a.accordion-toggle': 'toggleAccordion',
                    'click button[name=showAcl]': 'toggleAclDiv',
                    'click button[name=hideAcl]': 'toggleAclDiv',
                    'click button[name=submitAclNode]': 'submitAcl',
                    'click button[name=submitAclTag]': 'submitAcl',
                    'click button[name=removeAclTag]': 'removeAcl',
                    'click button[name=removeAclNode]': 'removeAcl'
                },
                toggleAccordion: function (event) {
                    var $href = $(event.currentTarget),
                        $icon = $href.find('i'),
                        $parent = $href.parents('.accordion-group'),
                        $body = $parent.find('.accordion-body');
                    event.preventDefault();
                    $body.unbind();
                    if ($icon.hasClass('icon-circle-arrow-down')) {
                        $icon.attr('class', 'icon-circle-arrow-up');
                        $body.collapse('show');
                    } else {
                        $body.collapse('hide');
                        $icon.attr('class', 'icon-circle-arrow-down');
                    }
                    $body.on('hidden', function (event) {
                        event.stopPropagation();
                    });
                },
                toggleAclDiv: function (event) {
                    var $aclDiv, $aclButton = $(event.currentTarget);
                    if ($aclButton.attr('name') === 'showAcl') {
                        $aclDiv = $aclButton.siblings('div[name=aclOptions]');
                        $aclDiv.toggle();
                        $aclButton.toggle();
                    } else {
                        $aclDiv = $aclButton.parents('div[name=aclOptions]');
                        $aclDiv.siblings('button').toggle();
                        $aclDiv.toggle();

                    }
                },
                submitAcl: function (event) {
                    var params, aclType,
                        that = this,
                        $button = $(event.currentTarget),
                        aclAction = 'create',
                        groupId = $button.attr('value'),
                        type = $button.attr('name'),
                        $aclOptionsDiv = $button.parents('div[name=aclOptions]'),
                        $alert = $aclOptionsDiv.find('.alert'),
                        aclId = $aclOptionsDiv.find('select').val(),
                        $checkboxes = $aclOptionsDiv.find('input[type=checkbox]'),
                        acl = { group_id: groupId },
                        url = 'api/acl/create';
                    if (aclId !== "0") {
                        if (type === 'submitAclNode') {
                            aclType = 'node_group';
                            acl.node_id = aclId;
                        } else {
                            aclType = 'tag_group';
                            acl.tag_id = aclId;
                        }
                        $checkboxes.each(function () {
                            acl[this.name] = this.checked;
                        });
                        params = {
                            acl_type: aclType,
                            acl_action: aclAction,
                            acl: JSON.stringify(acl)
                        };
                        $.post(url, params, function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                $alert.hide();
                                that.collection.fetch();
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                        window.console.log(params);
                    } else {
                        $alert.removeClass('alert-success').addClass('alert-error').show().html('Please select an option.');
                    }
                },
                removeAcl: function (event) {
                    var acl_type, params,
                        $button = $(event.currentTarget),
                        that = this,
                        type = $button.attr('name'),
                        groupId = $button.attr('value'),
                        aclId = $button.parents('.item').attr('name'),
                        acl = { group_id : groupId },
                        acl_action = 'delete',
                        url = 'api/acl/delete';
                    if (type === 'removeAclNode') {
                        acl.node_id = aclId;
                        acl_type = 'node_group';
                    } else {
                        acl.tag_id = aclId;
                        acl_type = 'tag_group';
                    }
                    params = {
                        acl_type: acl_type,
                        acl_action: acl_action,
                        acl: JSON.stringify(acl)
                    };
                    window.console.log(params);
                    $.post(url, params, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            that.collection.fetch();
                        }
                    });
                },
                beforeRender: $.noop,
                onRender: function () { this.$el.find('label').show(); },//$.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        nodes = this.nodeCollection.toJSON()[0],
                        tags = this.tagCollection.toJSON();

                    this.$el.empty();
                    window.console.log(data);
                    this.$el.html(template({data: data, nodes: nodes, tags: tags}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
