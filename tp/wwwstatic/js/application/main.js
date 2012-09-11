require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        var User = {},
            deferred;
        User.Model = Backbone.Model.extend({
            defaults: {
                name: 'Luis',
                show: {
                    brandHeader: true,
                    dashNav: true,
                    copyFooter: true
                },
                access: [
                    { name: 'Dashboard', href: '#dashboard', active: false },
                    { name: 'Patches', href: '#patchAdmin', active: false }
                ]
            }
        });
        window.User = new User.Model();

        // Load jQueryUI and Bootstrap
        require(['jquery.ui', 'jquery.bootstrap']);

        deferred = new $.Deferred();
        require(['modules/pageHeader', 'modules/navBar'], function (PageHeader, DashNav) {
            var pageHeader = app.views.pageHeader = new PageHeader.View();
            $('body').prepend(pageHeader.render().$el);
            app.views.dashNav = new (DashNav.View.extend({
                onRender: function () { deferred.resolve(); }
            }))({
                el: $('<ul>').addClass('nav').appendTo(pageHeader.$('#dashboardNav'))
            });
        });
        require(['modules/pageFooter'], function (PageFooter) {
            var pageFooter = new PageFooter.View();
            $('body').append(pageFooter.render().$el);
        });
        deferred.done(function () {
            require(['router'], function (Router) {
                Router.initialize();
            });
        });
    }
);