define(
    ['jquery', 'backbone', 'app', 'text!templates/node.html' ],
    function ($, Backbone, app, myTemplate) {
        "use strict";
        var exports = {};
        exports.Collection = Backbone.Collection.extend({
            model: Backbone.Model.extend({}),

            initialize: function () {
                this.show = 'api/nodes.json';
                this.filter = '?id='+this.id;
                this.url = function () {
                    return this.show + this.filter;
                };
            }
        });
        exports.View = Backbone.View.extend({
            initialize: function () {
                var that = this;
                this.template = myTemplate;
                this.collection = new exports.Collection();

                this.collection.bind('all', function (e) { console.log(e); });

                this.collection.fetch({
                    success: function () { that.render(); }
                });
            },
            events: {
                'submit form': 'submit'
            },
            submit: function (evt) {
                var form = $(evt.target),
                    type = form.attr('id'),
                    controlCheckbox = form,
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
                        label = $(this).parent();
                    $(this).remove();
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
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                var tmpl = _.template(this.template),
                    that = this;

                this.$el.html('');
                this.$el.append(tmpl({
                    models: this.collection.models
                }));
                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            },
            renderModel: function (item) {

            },
            setFilter: function (e) {

            },
            clearFilter: function () {
                this.collection.filter = '';
            }
        });
        return exports;
    }
);