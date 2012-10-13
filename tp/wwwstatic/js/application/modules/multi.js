/**
 * Created with PyCharm.
 * User: parallels
 * Date: 10/6/12
 * Time: 12:48 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'backbone', 'app', 'text!templates/multi.html', 'modules/controller', 'modules/detail'],
    function ($, Backbone, app, myTemplate, controller, detail) {
        "use strict";
        var MultiPatch = {},
            form = {'node_id': null, 'install': []},
            formArray = [];
        MultiPatch.View = Backbone.View.extend({
            that: this,
            template: myTemplate,
            initialize: function () {
                this.viewTarget = '#multi-patch';
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});

                this.controller = {
                    viewManager: new app.ViewManager({'selector': '.controller'})
                }

                this.detail = {
                    viewManager: new app.ViewManager({'selector': '.detail'})
                }
            },
            events: {
                'click .id': 'changeView',
                'click input:checkbox': 'addPatch',
                'click #submit': 'submit'
            },
            addPatch: function(event) {
                var id = this.$el.find('.first').attr('id'),
                    found = false;
                formArray.map(function(node){
                    if(id == node.node_id) {
                        if(event.target.checked) {
                            node.data.push(event.target.value);
                        } else {
                            var index = node.data.indexOf(event.target.value);
                            node.data.splice(index,1);
                            if(node.data.length == 0) {
                                index = formArray.indexOf(node);
                                formArray.splice(index, 1);
                            }
                        }
                        found = true;
                    }
                });
                if(found == false) {
                    form = {'node_id': null, 'data': [], 'operation': 'install'}
                    form.node_id = id;
                    form.data.push(event.target.value);
                    formArray.push(form);
                }
                found = false;
            },
            submit: function () {
                var params = JSON.stringify(formArray);
                console.log(params);
                $.post("/submitForm", { params: params },
                    function(json) {
                        console.log(json);
                });
            },
            changeView: function (event) {
                var id = $(event.currentTarget).attr('id')
                this.$el.find('.first').removeClass('first');
                detail.Collection = detail.Collection.extend({id: id, checked: formArray});
                $(event.currentTarget).addClass('first');
                this.detailView = new detail.View({
                    el: this.$el.find('.detail')
                });
            },
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                this.$el.html(_.template(this.template));
                this.controllerView = new controller.View({
                        el: this.$el.find('.controller')
                    });

                this.detailView = new detail.View({
                        el: this.$el.find('.detail')
                    });

                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            }
        });
        return MultiPatch;
    }
);