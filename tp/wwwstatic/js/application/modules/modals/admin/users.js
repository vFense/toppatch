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
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'click #userEdit': 'displayEdit',
                    'click #doneEdit': 'displayEdit',
                    'click #addUser': 'displayAddUser',
                    'click #cancelNewUser': 'displayAddUser',
                    'click button[name=confirmDelete]': 'confirmDelete',
                    'click button[name=cancelDelete]': 'confirmDelete',
                    'click button[name=deleteUser]': 'deleteUser',
                    'click #submitUser': 'submitNewUser',
                    'submit form': 'submit'
                },
                displayEdit: function (event) {
                    var $editButton = $('#userEdit'),
                        $doneButton = $('#doneEdit');
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
                        $deleteButton = $divConfirm.siblings('button');
                    }
                    $deleteButton.toggle();
                    $divConfirm.toggle();
                },
                deleteUser: function (event) {
                    var $deleteButton = $(event.currentTarget),
                        $userRow = $deleteButton.parents('.item');
                    $.post('api/users/delete', {userid: $deleteButton.val()}, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            $userRow.remove();
                        }
                    });
                },
                submitNewUser: function (event) {
                    var username = this.$el.find('#username').val(),
                        password = this.$el.find('#password').val(),
                        that = this;
                    $.post('signup', {name: username, password: password}, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            window.console.log(json.message);
                            that.collection.fetch();
                        }
                    });
                },
                submit: function (event) {
                    var $form = $(event.target);
                    window.console.log($form);
                    return false;
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
