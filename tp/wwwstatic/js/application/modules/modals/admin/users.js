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
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.groupCollection = new exports.GroupCollection();
                    this.groupCollection.bind('reset', this.render, this);
                    this.groupCollection.fetch();
                },
                events: {
                    'click #userEdit': 'displayEdit',
                    'click #doneEdit': 'displayEdit',
                    'click #addUser': 'displayAddUser',
                    'click #cancelNewUser': 'displayAddUser',
                    'click button[name=confirmDelete]': 'confirmDelete',
                    'click button[name=cancelDelete]': 'confirmDelete',
                    'click button[name=deleteUser]': 'deleteUser',
                    'click button[name=groups]': 'showGroups',
                    'click #submitUser': 'submitNewUser',
                    'submit form': 'submit'
                },
                displayEdit: function (event) {
                    var $editButton = $('#userEdit'),
                        $doneButton = $('#doneEdit'),
                        $alert = this.$el.find('div.alert');
                    $alert.hide();
                    $editButton.toggle();
                    $doneButton.toggle();
                    $('div[name=edit]').toggle();
                },
                displayAddUser: function (event) {
                    var $addButton = $('#addUser'),
                        $addUserDiv = this.$el.find('div[name=newUserDiv]');
                    $addButton.toggle();
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
                    $.post('api/users/toggleGroup', params, function (json) {\
                        if (json.pass) {
                            $alert.hide();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
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
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON(),
                        groups = this.groupCollection.toJSON();

                    this.$el.empty();

                    this.$el.html(template({data: data, groups: groups}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
