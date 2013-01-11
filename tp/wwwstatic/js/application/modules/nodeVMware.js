/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/9/13
 * Time: 5:25 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/nodeVMware.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/vmware/snapshots/list',
                url: function () {
                    return this.baseUrl + '?node_id=' + this.id;
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
                    'click button[name=toggleSnapshot]' : 'toggleSnapshot',
                    'click button[name=createSnapshot]' : 'createSnapshot',
                    'click button[name=revert]'         : 'revertSnapshot',
                    'click button[name=remove]'         : 'removeSnapshot',
                    'click button[name=removeAll]'      : 'removeAll'
                },
                toggleSnapshot: function (event) {
                    var $ssdiv = this.$el.find('#newSnapshotDiv');
                    $ssdiv.toggle();
                },
                createSnapshot: function (event) {
                    var params, that = this,
                        $alert = this.$el.find('div.alert'),
                        url = 'api/vmware/snapshots/create',
                        $newSnapDiv = this.$el.find('#newSnapshotDiv'),
                        $inputText = $newSnapDiv.find('input[type=text]'),
                        $inputCheck = $newSnapDiv.find('input[type=checkbox]');
                    params = {
                        vm_name: '',
                        snap_name: '',
                        memory: '',
                        quiesce: '',
                        snap_description: ''
                    };
                    $inputText.each(function () {
                        params[this.name] = this.value;
                    });
                    $inputCheck.each(function () {
                        params[this.name] = this.checked;
                    });
                    window.console.log(params);
                    $.post(url, params, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            that.collection.fetch();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().html(json.message);
                        }
                    }).error(function (error) {
                        $alert.removeClass('alert-success').addClass('alert-error').show().html('Error code: ' + error.status + ' - ' + error.statusText);
                    });
                },
                revertSnapshot: function (event) {
                    var vmName, $button = $(event.currentTarget),
                        url = 'api/vmware/snapshots/revert',
                        snapName = $button.attr('value');
                    window.console.log(event);
                },
                removeSnapshot: function (event) {
                    var vmName, $button = $(event.currentTarget),
                        url = 'api/vmware/snapshots/remove',
                        snapName = $button.attr('value');
                    window.console.log(event);
                },
                removeAll: function (event) {
                    var vmName,
                        url = 'api/vmware/snapshots/removeAll';
                    window.console.log(event);
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
