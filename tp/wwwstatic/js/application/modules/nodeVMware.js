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
                    'click button[name=toggleSnapshot]': 'toggleSnapshot',
                    'click button[name=createSnapshot]': 'createSnapshot'
                },
                toggleSnapshot: function (event) {
                    var $ssdiv = this.$el.find('#newSnapshotDiv');
                    $ssdiv.toggle();
                },
                createSnapshot: function (event) {
                    var params, that = this,
                        $alert = this.$el.find('div.alert'),
                        url = 'api/vmware/snapshots/create',
                        $inputs = this.$el.find('#newSnapshotDiv').find('input');
                    params = {
                        vm_name: '',
                        snap_name: '',
                        memory: '',
                        quiesce: '',
                        snap_description: ''
                    };
                    $inputs.each(function () {
                        params[this.name] = this.value;
                    });
                    window.console.log(params);
                    $.post(url, params, function (json, status) {
                        window.console.log(status);
                        if (json.pass) {
                            that.collection.fetch();
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().html(json.message);
                        }
                    }).error(function (error) {
                        $alert.removeClass('alert-success').addClass('alert-error').show().html('Error code: ' + error.status + ' - ' + error.statusText);
                    });
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
