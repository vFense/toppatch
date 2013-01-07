/**
 * Created with PyCharm.
 * User: parallels
 * Date: 12/2/12
 * Time: 3:43 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/users.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/users/list',
                filter: '',
                url: function () {
                    return this.baseUrl + this.filter;
                }
            }),
            GroupCollection: Backbone.Collection.extend({
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

                    this.groupCollection = new exports.GroupCollection();
                    this.groupCollection.bind('reset', this.render, this);
                    this.groupCollection.fetch();

                    this.nodeCollection = new exports.NodeCollection();
                    this.nodeCollection.bind('reset', this.render, this);
                    this.nodeCollection.fetch();

                    this.tagCollection = new exports.TagCollection();
                    this.tagCollection.bind('reset', this.render, this);
                    this.tagCollection.fetch();
                },
                events: {
                    'click #addUser': 'displayAddUser',
                    'click #cancelNewUser': 'displayAddUser',
                    'click button[name=confirmDelete]': 'confirmDelete',
                    'click button[name=cancelDelete]': 'confirmDelete',
                    'click button[name=deleteUser]': 'deleteUser',
                    'click button[name=groups]': 'showGroups',
                    'click button[name=globalacl]': 'showAclPopover',
                    'click #submitUser': 'submitNewUser',
                    'click button[name=toggleAcl]': 'toggleAclAccordion',
                    'click button[name=showAcl]': 'toggleAclDiv',
                    'click button[name=hideAcl]': 'toggleAclDiv',
                    'click button[name=submitAclNode]': 'submitAcl',
                    'click button[name=submitAclTag]': 'submitAcl',
                    'click button[name=removeAclTag]': 'removeAcl',
                    'click button[name=removeAclNode]': 'removeAcl',
                    'submit form': 'submit'
                },
                displayAddUser: function (event) {
                    var $addUserDiv = this.$el.find('div[name=newUserDiv]');
                    $addUserDiv.toggle();
                },
                confirmDelete: function (event) {
                    var $deleteButton, $divConfirm;
                    if ($(event.currentTarget).attr('name') === 'confirmDelete') {
                        $deleteButton = $(event.currentTarget);
                        $divConfirm = $deleteButton.siblings('div');
                    } else {
                        $divConfirm = $(event.currentTarget).parent();
                        $deleteButton = $divConfirm.siblings('button[name=confirmDelete]');
                    }
                    $deleteButton.toggle();
                    $divConfirm.toggle();
                },
                deleteUser: function (event) {
                    var $deleteButton = $(event.currentTarget),
                        $userRow = $deleteButton.parents('.item'),
                        $alert = this.$el.find('div.alert'),
                        that = this;
                    $.post('api/users/delete', {userid: $deleteButton.val()}, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            $userRow.remove();
                            $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html(json.message);
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
                },
                submitNewUser: function (event) {
                    var username = this.$el.find('#username').val(),
                        password = this.$el.find('#password').val(),
                        group = this.$el.find('select[name=groups]').val(),
                        $alert = this.$el.find('div.alert'),
                        params = {
                            name: username,
                            password: password,
                            group: group
                        },
                        that = this;
                    window.console.log(params);
                    $.post('signup', params, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            window.console.log(json.message);
                            that.collection.fetch();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
                },
                showGroups: function (event) {
                    var $popoverLink = $(event.currentTarget),
                        userId = parseInt($popoverLink.val(), 10),
                        userData = this.collection.toJSON(),
                        $popover = $popoverLink.data('popover'),
                        $close = $popover.tip().find('button[name=close]'),
                        $list = $popover.tip().find('.list'),
                        $inputs = $popover.options.content.find('input[type=checkbox]');
                    _.each(userData, function (user) {
                        if (user.id === userId) {
                            _.each(user.groups, function (group) {
                                $inputs.each(function () {
                                    if (this.value === group) {
                                        this.checked = true;
                                    }
                                });
                            });
                        }
                    });
                    $list.data('user', userId);
                    $inputs.unbind();
                    $close.unbind();
                    $close.on('click', function () {
                        $popoverLink.popover('hide');
                    });
                    $inputs.on('change', this, this.toggleGroup);
                },
                toggleGroup: function (event) {
                    var action, params,
                        user = $(this).parents('.list').data('user'),
                        $checkbox = $(this),
                        $alert = event.data.$el.find('div.alert'),
                        checked = this.checked;
                    if (checked) {
                        action = 'add';
                    } else {
                        action = 'remove';
                    }
                    params = {
                        user_id: user,
                        groupname: $checkbox.val(),
                        action: action
                    };
                    $.post('api/users/toggleGroup', params, function (json) {
                        if (json.pass) {
                            $alert.hide();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
                },
                showAclPopover: function (event) {
                    var aclExists = false,
                        that = this,
                        $popoverLink = $(event.currentTarget),
                        userId = parseInt($popoverLink.val(), 10),
                        userData = this.collection.toJSON(),
                        $popover = $popoverLink.data('popover'),
                        $newAclButton = $popover.tip().find('button[name=newAclButton]'),
                        $close = $popover.tip().find('button[name=close]'),
                        $cancelButton = $popover.tip().find('button[name=cancelAcl]'),
                        $submitButton = $popover.tip().find('button[name=submitAcl]'),
                        $list = $popover.tip().find('.list'),
                        $inputs = $list.find('input[type=checkbox]');
                    _.each(userData, function (user) {
                        if (user.id === userId) {
                            if (user.global_acls.length !== 0) {
                                aclExists = true;
                                $list.find('div[name=newacl]').hide();
                                $list.find('div.items').show();
                                $list.find('button[name=cancelAcl]').remove();
                                $inputs.each(function () {
                                    if (user.global_acls[0][this.name]) {
                                        this.checked = true;
                                    }
                                });
                            }
                        }
                    });
                    $newAclButton.unbind();
                    $cancelButton.unbind();
                    $submitButton.unbind();
                    $close.unbind();
                    $close.on('click', function () {
                        $popoverLink.popover('hide');
                    });
                    $newAclButton.on('click', this, this.showAclList);
                    $cancelButton.on('click', this, this.showAclList);
                    $submitButton.on('click', {view: this, aclExists: aclExists, user_id: userId, checkboxes: $inputs}, this.submitGlobalAcl);
                },
                showAclList: function (event) {
                    var $newAclButton = $(event.currentTarget),
                        $newAclDiv = $newAclButton.parents('div.list').find('div[name=newacl]'),
                        $newAclList = $newAclDiv.siblings('div.items');
                    $newAclDiv.toggle();
                    $newAclList.toggle();
                },
                submitGlobalAcl: function (event) {
                    var params,
                        aclExists = event.data.aclExists,
                        userId = event.data.user_id,
                        $alert = event.data.view.$el.find('div.alert'),
                        acl = { user_id: userId },
                        $checkboxes = event.data.checkboxes,
                        aclType = 'global_user',
                        aclAction = aclExists ? 'modify' : 'create',
                        url = aclExists ? 'api/acl/modify' : 'api/acl/create';
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
                            event.data.view.collection.fetch();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
                },
                toggleAclAccordion: function (event) {
                    var $href = $(event.currentTarget),
                        $icon = $href.find('i'),
                        $accordionParent = $href.parents('.accordion-group'),
                        $accordionBody = $accordionParent.find('.accordion-body');
                    $accordionBody.unbind();
                    if ($icon.hasClass('icon-circle-arrow-down')) {
                        $icon.attr('class', 'icon-circle-arrow-up');
                        $accordionBody.collapse('show');
                    } else {
                        $icon.attr('class', 'icon-circle-arrow-down');
                        $accordionBody.collapse('hide');
                    }
                    $accordionBody.on('hidden', function (event) {
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
                        userId = $button.attr('value'),
                        type = $button.attr('name'),
                        $aclOptionsDiv = $button.parents('div[name=aclOptions]'),
                        $alert = $aclOptionsDiv.find('.alert'),
                        aclId = $aclOptionsDiv.find('select').val(),
                        $checkboxes = $aclOptionsDiv.find('input[type=checkbox]'),
                        acl = { user_id: userId },
                        url = 'api/acl/create';
                    if (aclId !== "0") {
                        if (type === 'submitAclNode') {
                            aclType = 'node_user';
                            acl.node_id = aclId;
                        } else {
                            aclType = 'tag_user';
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
                        //$aclOptionsDiv = $button.parents('div[name=aclOptions]'),
                        //$alert = $aclOptionsDiv.find('.alert'),
                        that = this,
                        type = $button.attr('name'),
                        userId = $button.attr('value'),
                        aclId = $button.parents('.item').attr('name'),
                        acl = { user_id : userId },
                        acl_action = 'delete',
                        url = 'api/acl/delete';
                    if (type === 'removeAclNode') {
                        acl.node_id = aclId;
                        acl_type = 'node_user';
                    } else {
                        acl.tag_id = aclId;
                        acl_type = 'tag_user';
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
                        } /*else {
                            //$alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        } */
                    });
                },
                submit: function (event) {
                    var $form = $(event.target);
                    window.console.log($form);
                    return false;
                },
                beforeRender: $.noop,
                onRender: function () {
                    var that = this;
                    this.$el.find('button[name=groups]').each(function () {
                        $(this).popover({
                            placement: 'right',
                            title: '<div class="alignLeft"><span>Groups</span><button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button></div>',
                            html: true,
                            content: that.$el.find('#grouplist').clone(),
                            trigger: 'click'
                        });
                    });
                    this.$el.find('button[name=globalacl]').each(function () {
                        $(this).popover({
                            placement: 'right',
                            title: '<div class="alignLeft"><span>Global User Acl</span><button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button></div>',
                            html: true,
                            content: that.$el.find('#globalacl').clone(),
                            trigger: 'click'
                        });
                    });
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        groups = this.groupCollection.toJSON(),
                        nodes = this.nodeCollection.toJSON()[0],
                        tags = this.tagCollection.toJSON();

                    this.$el.empty();

                    this.$el.html(template({data: data, groups: groups, nodes: nodes, tags: tags}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
