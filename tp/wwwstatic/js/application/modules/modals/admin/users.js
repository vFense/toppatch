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
                    var $deleteButton = $(event.currentTarget);
                    window.console.log($deleteButton.val());
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
