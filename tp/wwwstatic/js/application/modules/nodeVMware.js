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
                baseUrl: 'api/virtual/node/info',
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
                        url = 'api/virtual/node/snapshots/create',
                        $newSnapDiv = this.$el.find('#newSnapshotDiv'),
                        $inputText = $newSnapDiv.find('input[type=text]'),
                        $inputCheck = $newSnapDiv.find('input[type=checkbox]'),
                        vmName = this.vm_name;
                    params = {
                        vm_name: vmName,
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
                        url = 'api/virtual/node/snapshots/revert',
                        snapName = $button.attr('value');
                    window.console.log(event);
                },
                removeSnapshot: function (event) {
                    var that = this,
                        vmName = this.vm_name,
                        $button = $(event.currentTarget),
                        url = 'api/virtual/node/snapshots/remove',
                        $alert = this.$el.find('div.alert'),
                        snapName = $button.attr('value'),
                        params = {
                            snap_name: snapName,
                            vm_name: vmName
                        };
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
                removeAll: function (event) {
                    var vmName,
                        url = 'api/virtual/node/snapshots/removeAll';
                    window.console.log(event);
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON()[0];
                    this.vm_name = data.vm_name;
                    data.snapshots.sort(function (a, b) { return parseFloat(a.snap_order) - parseFloat(b.snap_order); });

                    this.$el.empty();

                    this.$el.html(template({data: data.snapshots}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
