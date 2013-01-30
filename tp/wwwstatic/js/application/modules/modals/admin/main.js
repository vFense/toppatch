define(
    ['jquery', 'underscore', 'backbone', 'app', 'modals/panel', 'modules/tabNavigation', 'text!templates/modals/admin/main.html'],
    function ($, _, Backbone, app, panel, tabs, myTemplate) {
        "use strict";
        var exports = {},
            View = exports.View = app.createChild(panel.View);

        _.extend(View.prototype, {
            template: myTemplate,
            navigation: new tabs.View({
                tabs: [
                    {text: 'Tags', href: 'admin/managetags'},
                    {text: 'Accept Nodes', href: 'admin/nodes'},
                    {text: 'TimeBlocks', href: 'admin/timeblock'},
                    {text: 'Users', href: 'admin/users'},
                    {text: 'Groups', href: 'admin/groups'},
                    {text: 'Syslog', href: 'admin/syslog'},
                    {text: 'VMware', href: 'admin/vmware'},
                    {text: 'Schedule', href: 'admin/schedule'}
                ]
            }),
            initialize: function (options) {
                View.__super__.initialize.apply(this, arguments);
                this.$el.find('.modal-header').addClass('tabs').html(this.navigation.render().el);
                this.navigation.setActive(app.router.getCurrentFragment());

                var that = this,
                    router = app.router;
                this.listenTo(router, 'route', function () {
                    if (router.adminRoute()) {
                        this.navigation.setActive(router.getCurrentFragment());
                        this.showLoading();
                    }
                });
            },
            showLoading: function () {
                this._pinwheel = this._pinwheel || new app.pinwheel();
                if (!(this._contentView instanceof app.pinwheel)) {
                    this.setContentView(this._pinwheel);
                }
                return this;
            },
            open: function () {
                var router = app.router,
                    last;

                // Save last fragment and go back to it on 'close'
                last = router.getLastFragment();
                if (last === '' || /^admin($|[\/])/.test(last)) {
                    this._lastURL = "dashboard";
                } else {
                    this._lastURL = last;
                }

                View.__super__.open.apply(this, arguments);
            },
            beforeClose: function () {
                View.__super__.beforeClose.apply(this, arguments);
                if (this.navigation) {
                    this.navigation.close();
                }
                if (this._lastURL !== '') {
                    app.router.navigate(this._lastURL);
                } else {
                    app.router.navigate("dashboard", {trigger: true});
                }
            }
        });

        return exports;
    }
);
