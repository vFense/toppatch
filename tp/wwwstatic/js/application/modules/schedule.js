define(
    ['jquery', 'underscore', 'backbone', 'text!templates/schedule.html' ],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/scheduler/list.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection =  new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'click button[name=remove]': 'removeSchedule'
                },
                removeSchedule: function (event) {
                    var $removeButton = $(event.currentTarget),
                        jobname = $removeButton.val(),
                        $item = $removeButton.parents('item');
                    window.console.log(jobname);
                    $.post('api/scheduler/remove', {jobname: jobname}, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            $item.remove();
                        } else {
                            window.console.log(json);
                        }
                    });
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON();

                    this.$el.empty();

                    this.$el.append(template({data: data}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);
