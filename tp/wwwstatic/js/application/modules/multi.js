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
        var MultiPatch = {};
        MultiPatch.View = Backbone.View.extend({
            template: myTemplate,
            initialize: function () {
                this.viewTarget = '#multi-patch';
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});
            },
            updateManager: function (d) {
                this.viewTarget = d;
                this.viewManager = new app.ViewManager({'selector': this.viewTarget});
            },
            events: {
                'click .id': 'changeView'

            },
            changeView: function (event) {
                var id = event.target.id;
                this.detailView = new detail.View({ el: this.$el.find('.detail'), id: id });
                this.updateManager('.detail');
                this.viewManager.showView(this.detailView);
            },
            render: function () {
                var tmpl = _.template(this.template);
                this.$el.html(tmpl());
                var controllerEl = this.$el.find('.controller'),
                    detailEl = this.$el.find('.detail'),
                    controllerView = new controller.View({ el: controllerEl });
                this.detailView = new detail.View({ el: detailEl });
                this.updateManager('.controller');
                this.viewManager.showView(controllerView);
                this.updateManager('.detail');
                this.viewManager.showView(this.detailView);
                return this;
            }
        });
        return MultiPatch;
    }
);