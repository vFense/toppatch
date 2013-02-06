/**
 * Created with PyCharm.
 * User: parallels
 * Date: 2/6/13
 * Time: 8:00 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/tabNavigation', 'modules/modals/admin/syslog', 'modules/modals/admin/vmware', 'text!templates/modals/admin/services.html'],
    function ($, _, Backbone, app, tabNav, syslogView, virtualView, myTemplate) {
        "use strict";
        var exports = {
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this._currentTab = '#syslog';
                    /*this.navigation = new tabNav.View({
                        stacked: true,
                        tabs: [
                            {text: 'Syslog', href: 'modal/admin/services/syslog'},
                            {text: 'Virtual', href: 'modal/admin/services/virtual'},
                            {text: 'Email', href: 'modal/admin/services/email'}
                        ]
                    });*/
                    //this.collection = new exports.Collection();
                    //this.collection.bind('reset', this.render, this);
                    //this.collection.fetch();
                },
                events: {
                    'click li a': 'changeView'
                },
                beforeRender: $.noop,
                onRender: $.noop,
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var $header, $body, template = _.template(this.template);

                    this.$el.empty();

                    this.$el.html(template());

                    $body = this.$el.find('.tab-content');

                    this.syslogView = new syslogView.View({
                        el: $body
                    });

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                showLoading: function (el) {
                    var $el = this.$el,
                        $div = $el.find(el);
                    this._pinwheel = new app.pinwheel();
                    $div.empty().append(this._pinwheel.el);
                },
                changeView: function (event) {
                    var $tab = $(event.currentTarget),
                        view = $tab.attr('href'),
                        $body = this.$el.find('.tab-content');
                    event.preventDefault();
                    if (this._currentTab !== view) {
                        this._currentTab = view;
                        this.showLoading('.tab-content');
                        if (view === '#syslog') {
                            if (this.syslogView) {
                                this.syslogView.render();
                            } else {
                                this.syslogView = new syslogView.View({
                                    el: $body
                                });
                            }
                        } else if (view === '#virtual') {
                            if (this.virtualView) {
                                this.virtualView.render();
                            } else {
                                this.virtualView = new virtualView.View({
                                    el: $body
                                });
                            }
                        } else if (view === '#email') {
                            $body.html('working on this!');
                        }
                    }
                    window.console.log(view);
                }
            })
        };
        return exports;
    }
);
