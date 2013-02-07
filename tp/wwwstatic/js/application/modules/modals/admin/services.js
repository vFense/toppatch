/**
 * Created with PyCharm.
 * User: parallels
 * Date: 2/6/13
 * Time: 8:00 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/tabNavigation', 'modules/modals/admin/syslog', 'modules/modals/admin/vmware', 'modules/modals/admin/email', 'text!templates/modals/admin/services.html'],
    function ($, _, Backbone, app, tabNav, syslogView, virtualView, emailView, myTemplate) {
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
                onRender: function () {
                    var $body = this.$el.find('.tab-content');

                    this.syslogView = new syslogView.View({
                        el: $body
                    });
                    this.updateHeight();
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template);

                    this.$el.empty();

                    this.$el.html(template());

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                updateHeight: function () {
                    var height, $navTabs = this.$el.find('.nav-tabs'),
                        $body = this.$el.find('.tab-content');
                    setTimeout(function () {
                        height = $body.height() > 150 ? $body.height() : 150;
                        $navTabs.css('height', height);
                    }, 50);
                },
                showLoading: function (el) {
                    var $el = this.$el,
                        $div = $el.find(el);
                    this._pinwheel = new app.pinwheel();
                    $div.empty().append(this._pinwheel.el);
                },
                changeView: function (event) {
                    var $currentTab = $(event.currentTarget),
                        view = $currentTab.attr('href'),
                        $body = this.$el.find('.tab-content'),
                        $navTabs = this.$el.find('.nav-tabs');
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
                            if (this.emailView) {
                                this.emailView.render();
                            } else {
                                this.emailView = new emailView.View({
                                    el: $body
                                });
                            }
                        }
                        this.updateHeight();
                    }
                }
            })
        };
        return exports;
    }
);
