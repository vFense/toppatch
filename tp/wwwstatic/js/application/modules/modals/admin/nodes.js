define(
    ['jquery', 'underscore', 'backbone', 'text!templates/modals/admin/approveNodes.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection : Backbone.Collection.extend({
                baseUrl: 'api/csrinfo.json/',
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
                    'submit form': 'submit'
                },
                submit: function (evt) {
                    var form = $(evt.target),
                        that = this;
                    console.log(form.serialize());
                    $.post("/adminForm?" + form.serialize(),
                        function(json) {
                            console.log(json);
                            if (!json.error) {
                                form.find('input:checked').parents('.item').remove();
                                that.$el.find('.alert').show();
                            } else {
                                console.log('Error while processing the CSRs');
                            }
                        }
                    );
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
