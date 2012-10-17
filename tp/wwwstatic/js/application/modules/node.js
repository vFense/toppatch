define(
    ['jquery', 'backbone', 'app', 'text!templates/node.html' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
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
                    'click .disabled': function (e) { console.log(['click a.disabled', e]); return false; },
                    'submit form': 'submit'
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON()[0];

                    this.$el.html('');

                    this.$el.append(template({model: data}));

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                submit: function (evt) {
                    var form = $(evt.target),
                        type = form.attr('id'),
                        patches = $(evt.target).find('input[name="patches"]:checked');
                    console.log(form.serialize());
                    $.post("/submitForm?" + form.serialize(),
                        function(json) {
                            console.log(json);
                        });
                    $('.alert').show();
                    patches.each(function () {
                        var item = $(this).parents('.item'),
                            span = $(this).parents('span'),
                            label = $(this).parent(),
                            checkbox = $(this);
                        checkbox.remove();
                        var patch = label.html();
                        span.html(patch);
                        label.remove();
                        if(type == 'available' || type == 'failed') {
                            item.appendTo('#pending');
                            if($('#no-pending')) {
                                $('#no-pending').remove();
                            }
                        } else {
                            item.remove();
                        }
                    });
                    if(form.find('input:checked').attr('checked')) {
                        form.find('input:checked').attr('checked', false);
                    }
                    return false;
                },
                clearFilter: function () {
                    this.collection.filter = '';
                }
            })
        };
        return exports;
    }
);
