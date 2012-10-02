require(
    ['jquery', 'backbone', 'app'],
    function ($, Backbone, app) {
        "use strict";

        var User = {},
            userSettings,
            deferred;
        $.getJSON("/api/userInfo", function(json) {
            userSettings = json;
            User.Model = Backbone.Model.extend({
                defaults: {
                    name: userSettings['name'],
                    show: {
                        brandHeader: true,
                        dashNav: true,
                        copyFooter: true
                    },
                    access: [
                        { name: 'Dashboard', href: '#dashboard', active: false },
                        { name: 'Nodes', href: '#nodes', active: false },
                        { name: 'Patches', href: '#patches', active: false }
                    ]
                }
            });
            window.User = new User.Model();
        });

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

        app.vent.on("domchange:title", function (title) {
            app.$doc.attr('title', app.title + ': ' + title);
        });

        deferred.done(function () {
            require(['router'], function (Router) {
                Router.initialize();
            });
        });
    }
);